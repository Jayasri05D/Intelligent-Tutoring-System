

"""
Question-Aware Logical Error Detection Engine  v3.0
=====================================================
Detects LOGICAL errors in student code by understanding:
  - What the QUESTION is asking (parsed from problem statement)
  - What the student's CODE is doing (AST analysis)
  - How the OUTPUT differs from expected (test case diffing)

100% offline — no LLM API required.

Flow:
  Stage 1 — QuestionAnalyzer    : reads problem text → detects operation, expected concepts, edge cases
  Stage 2 — CodeStructureAnalyzer: reads student code → detects loops, recursion, accumulators, comparisons
  Stage 3 — OutputDiffer        : compares actual vs expected → diagnoses HOW it's wrong
  Stage 4 — MismatchDetector    : question needs vs code does → produces specific LogicalErrors
  Stage 5 — FeedbackEngine      : emits what/where/why/hint per error
"""

import re
import ast
import math
import subprocess
import tempfile
import os
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tree_sitter import Parser
from tree_sitter_languages import get_language

app = FastAPI(title="Question-Aware Logical Error Detector", version="3.0.0")


# =========================================================
# REQUEST MODEL
# =========================================================
class EvaluationRequest(BaseModel):
    studentId: int
    questionId: str
    problem_statement: str   # e.g. "Write a function to find the maximum element in a list"
    code: str
    test_cases: list[dict]   # [{"input": "5\n1 2 3 4 5", "expected_output": "5"}]
    language: str = "python"


# =========================================================
# TREE-SITTER SETUP
# =========================================================
PY_LANGUAGE = get_language("python")
_ts_parser = Parser()
_ts_parser.set_language(PY_LANGUAGE)


# =========================================================
# DATA STRUCTURES
# =========================================================

@dataclass
class QuestionProfile:
    """What a question EXPECTS the solution to implement."""
    raw_text: str
    expected_operation: str = "unknown"
    expected_concepts: list[str] = field(default_factory=list)
    expected_return_type: str = "unknown"
    input_structure: str = "unknown"
    edge_cases: list[str] = field(default_factory=list)


@dataclass
class CodeProfile:
    """What the student code actually does (extracted from AST)."""
    has_loop: bool = False
    has_nested_loop: bool = False
    has_recursion: bool = False
    has_return: bool = False
    has_if: bool = False
    has_accumulator: bool = False
    has_comparison: bool = False
    has_sort_call: bool = False
    has_index_access: bool = False
    loop_count: int = 0
    function_count: int = 0
    max_nesting_depth: int = 0
    accumulator_vars: list[str] = field(default_factory=list)
    comparison_operators: list[str] = field(default_factory=list)
    called_builtins: list[str] = field(default_factory=list)
    return_lines: list[int] = field(default_factory=list)


@dataclass
class TestDiff:
    """Diagnosis of a single failed test case."""
    test_index: int
    input_val: str
    expected: str
    actual: str
    passed: bool
    match_type: str
    diff_diagnosis: str = ""
    runtime_error: str = ""


@dataclass
class LogicalError:
    """A fully diagnosed logical error with what/where/why/hint."""
    error_id: str
    severity: str           # critical / warning / info
    category: str           # algorithm / loop / condition / variable / output
    line: object            # int or None
    code_snippet: str
    what: str
    where: str
    why: str
    hint: str
    confidence: float
    related_test_cases: list[int] = field(default_factory=list)


# =========================================================
# STAGE 1: QUESTION ANALYZER
# =========================================================

OPERATION_KEYWORDS = {
    "find_max":      ["maximum", "largest", "greatest", "max", "biggest", "highest"],
    "find_min":      ["minimum", "smallest", "least", "min", "lowest"],
    "sum":           ["sum", "total", "add all", "accumulate", "aggregate"],
    "count":         ["count", "how many", "number of", "frequency", "occurrences"],
    "search":        ["search", "find", "locate", "exists", "contains", "present"],
    "sort":          ["sort", "order", "arrange", "ascending", "descending"],
    "reverse":       ["reverse", "reversed", "backward", "flip"],
    "palindrome":    ["palindrome", "reads same"],
    "prime":         ["prime", "prime number"],
    "factorial":     ["factorial"],
    "fibonacci":     ["fibonacci", "fib"],
    "average":       ["average", "mean", "arithmetic mean"],
    "binary_search": ["binary search"],
    "two_sum":       ["two sum", "pair that adds"],
    "unique":        ["unique", "distinct", "duplicates"],
    "matrix":        ["matrix", "2d array", "grid"],
    "string_ops":    ["string", "substring", "character", "vowel", "consonant"],
    "gcd_lcm":       ["gcd", "lcm", "greatest common", "least common multiple"],
    "power":         ["power", "exponent", "raise to"],
}

OPERATION_TO_CONCEPTS = {
    "find_max":      ["loop", "comparison", "variable_tracking"],
    "find_min":      ["loop", "comparison", "variable_tracking"],
    "sum":           ["loop", "accumulator"],
    "count":         ["loop", "condition", "accumulator"],
    "search":        ["loop", "condition"],
    "sort":          ["nested_loop_or_builtin", "comparison"],
    "reverse":       ["loop_or_slicing"],
    "palindrome":    ["string_indexing_or_reverse", "comparison"],
    "prime":         ["loop", "condition", "divisibility"],
    "factorial":     ["loop_or_recursion", "accumulator"],
    "fibonacci":     ["loop_or_recursion", "two_variables"],
    "average":       ["loop", "accumulator", "division"],
    "binary_search": ["loop_or_recursion", "mid_calculation", "comparison"],
    "two_sum":       ["loop", "condition"],
    "unique":        ["loop", "set_or_dict"],
    "matrix":        ["nested_loop", "index_access"],
    "string_ops":    ["loop_or_slicing", "string_methods"],
    "gcd_lcm":       ["loop_or_recursion", "modulo"],
    "power":         ["loop_or_recursion", "accumulator"],
}

OPERATION_TO_RETURN = {
    "find_max":      "single_value",
    "find_min":      "single_value",
    "sum":           "single_value",
    "count":         "single_value",
    "search":        "boolean_or_index",
    "sort":          "list",
    "reverse":       "list_or_string",
    "palindrome":    "boolean",
    "prime":         "boolean",
    "factorial":     "single_value",
    "fibonacci":     "single_value_or_list",
    "average":       "float",
    "binary_search": "index_or_boolean",
    "two_sum":       "pair_or_list",
    "unique":        "list_or_count",
    "matrix":        "varies",
    "string_ops":    "string_or_value",
    "gcd_lcm":       "single_value",
    "power":         "single_value",
}

INPUT_STRUCTURE_KEYWORDS = {
    "array":  ["list", "array", "elements", "sequence", "numbers"],
    "string": ["string", "word", "sentence", "character"],
    "matrix": ["matrix", "grid", "2d", "rows", "columns"],
    "number": ["number", "integer", "digit", "value"],
}

EDGE_CASE_PATTERNS = {
    "empty_list":     ["empty", "no elements"],
    "single_element": ["single", "one element"],
    "negative":       ["negative"],
    "zero":           ["zero"],
    "all_same":       ["all same", "identical", "duplicates"],
}


def analyze_question(problem_statement: str) -> QuestionProfile:
    text = problem_statement.lower()
    profile = QuestionProfile(raw_text=problem_statement)

    for op, keywords in OPERATION_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            profile.expected_operation = op
            break

    profile.expected_concepts = OPERATION_TO_CONCEPTS.get(
        profile.expected_operation, ["loop", "condition"])
    profile.expected_return_type = OPERATION_TO_RETURN.get(
        profile.expected_operation, "unknown")

    for structure, keywords in INPUT_STRUCTURE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            profile.input_structure = structure
            break

    for edge_case, patterns in EDGE_CASE_PATTERNS.items():
        if any(p in text for p in patterns):
            profile.edge_cases.append(edge_case)

    return profile


# =========================================================
# STAGE 2: CODE STRUCTURE ANALYZER
# =========================================================

def analyze_code_structure(code: str) -> CodeProfile:
    profile = CodeProfile()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return profile

    max_depth = [0]

    def walk(node, loop_depth=0):
        if isinstance(node, (ast.For, ast.While)):
            profile.loop_count += 1
            profile.has_loop = True
            loop_depth += 1
            max_depth[0] = max(max_depth[0], loop_depth)
            if loop_depth >= 2:
                profile.has_nested_loop = True

        if isinstance(node, ast.FunctionDef):
            profile.function_count += 1
            fname = node.name
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == fname:
                    profile.has_recursion = True

        if isinstance(node, ast.Return):
            profile.has_return = True
            profile.return_lines.append(node.lineno)

        if isinstance(node, ast.If):
            profile.has_if = True

        if isinstance(node, ast.AugAssign):
            profile.has_accumulator = True
            if isinstance(node.target, ast.Name):
                profile.accumulator_vars.append(node.target.id)

        if isinstance(node, ast.Compare):
            profile.has_comparison = True
            for op in node.ops:
                profile.comparison_operators.append(type(op).__name__)

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("sort", "sorted"):
                profile.has_sort_call = True
            if isinstance(node.func, ast.Name):
                n = node.func.id
                profile.called_builtins.append(n)
                if n == "sorted":
                    profile.has_sort_call = True

        if isinstance(node, ast.Subscript):
            profile.has_index_access = True

        for child in ast.iter_child_nodes(node):
            walk(child, loop_depth)

    walk(tree)
    profile.max_nesting_depth = max_depth[0]
    return profile


# =========================================================
# STAGE 3: OUTPUT DIFFER
# Diagnoses HOW the output is wrong, not just THAT it's wrong.
# =========================================================

def diagnose_output_diff(expected: str, actual: str, operation: str) -> tuple[str, str]:
    """Returns (match_type, human_readable_diagnosis)."""
    exp = expected.strip()
    act = actual.strip()

    if exp == act:
        return "exact", ""

    if not act:
        return "empty", (
            "Your code produced NO output. "
            "This usually means a missing `print()`, a missing `return`, "
            "or the function was defined but never called."
        )

    if any(kw in act.lower() for kw in ["error", "traceback", "exception"]):
        return "runtime_error", (
            "Your code crashed with a runtime error instead of producing output. "
            "Fix the error first, then check your logic."
        )

    # Numeric comparison
    try:
        exp_num = float(exp)
        act_num = float(act)
        diff = act_num - exp_num

        if abs(diff) == 1:
            direction = "too high by 1" if diff > 0 else "too low by 1"
            return "off_by_one", (
                f"Your answer is {direction}. "
                "This is a classic off-by-one error — check your loop range "
                "(`range(n)` vs `range(n+1)`) or your starting/ending index."
            )

        if exp_num != 0 and abs(act_num) == abs(exp_num) and act_num == -exp_num:
            return "wrong_sign", (
                "Your answer has the correct magnitude but the wrong sign. "
                "Check if you are subtracting when you should add, "
                "or if a comparison operator (`>` / `<`) is reversed."
            )

        if act_num == 0 and exp_num != 0:
            return "zero_output", (
                "Your answer is 0 but should be non-zero. "
                "The most common cause: your accumulator is reset to 0 inside "
                "the loop instead of before it, or it is never updated."
            )

        # Operation-specific
        if op in ("find_max", "find_min"):
            word = "maximum" if op == "find_max" else "minimum"
            comp = ">" if op == "find_max" else "<"
            wrong = "<" if op == "find_max" else ">"
            if (op == "find_max" and act_num < exp_num) or (op == "find_min" and act_num > exp_num):
                return "wrong_comparison_direction", (
                    f"You returned {act} but the {word} is {exp}. "
                    f"Your comparison operator may be `{wrong}` when it should be `{comp}`, "
                    f"or your initial tracker value is wrong (e.g. `= 0` instead of `= arr[0]`)."
                )

        if op == "average" and exp_num != 0:
            if math.isclose(act_num, exp_num * 2, rel_tol=0.05):
                return "forgot_division", (
                    "Your result is about double the expected average. "
                    "Did you multiply instead of divide, or divide by the wrong count?"
                )
            # Check if they returned the sum instead of average
            # (can't know exact n, but diagnose directionally)

        return "wrong_value", (
            f"Expected `{exp}` but got `{act}` (difference: {diff:+.4g}). "
            "Trace through your logic manually with this input."
        )

    except (ValueError, TypeError):
        pass

    # String / list comparison
    if act == exp[::-1]:
        return "reversed", (
            "Your output is the exact reverse of the expected output. "
            "Check if you are iterating backward when you should go forward, "
            "or if you're building the result in reverse."
        )

    common = os.path.commonprefix([exp, act])
    if len(common) > max(len(exp), 1) * 0.5:
        return "partial", (
            f"Your output starts correctly (`{common[:30]}`) but ends differently. "
            "Your loop may be stopping too early — check your termination condition."
        )

    if exp.lower() == act.lower():
        return "case_mismatch", (
            "Right content, wrong case (uppercase/lowercase). "
            "Check any `.upper()` / `.lower()` calls."
        )

    return "failed", (
        f"Expected `{exp}` but got `{act}`. "
        "Your logic produces a completely different result. "
        "Try tracing through the failing input step by step."
    )


# =========================================================
# STAGE 4: MISMATCH DETECTOR
# Compares question expectations vs code structure vs output diffs
# =========================================================

def detect_logical_errors(
    question: QuestionProfile,
    code_profile: CodeProfile,
    test_diffs: list[TestDiff],
    code_lines: list[str],
) -> list[LogicalError]:

    errors: list[LogicalError] = []
    failed = [d for d in test_diffs if not d.passed]
    failed_idx = [d.test_index for d in failed]

    if not failed:
        return []  # All tests passed — no errors to report

    op = question.expected_operation

    # ── helpers ──────────────────────────────────────────────────

    def snippet(line, ctx=1):
        if line is None or line < 1:
            return ""
        start = max(0, line - 1 - ctx)
        end = min(len(code_lines), line + ctx)
        return "\n".join(f"  {start+i+1}: {l}" for i, l in enumerate(code_lines[start:end]))

    def find_line(pattern):
        for i, ln in enumerate(code_lines, 1):
            if re.search(pattern, ln):
                return i
        return None

    def error(eid, sev, cat, what, where, why, hint, conf, line=None):
        errors.append(LogicalError(
            error_id=eid, severity=sev, category=cat,
            line=line, code_snippet=snippet(line),
            what=what, where=where, why=why, hint=hint,
            confidence=conf, related_test_cases=failed_idx
        ))

    # ════════════════════════════════════════════════════════════
    # GROUP A — Operation-specific mismatch rules
    # ════════════════════════════════════════════════════════════

    # ── find_max / find_min ──────────────────────────────────────
    if op in ("find_max", "find_min"):
        word = "maximum" if op == "find_max" else "minimum"
        need_op  = "Gt" if op == "find_max" else "Lt"   # ast class name
        wrong_op = "Lt" if op == "find_max" else "Gt"
        need_sym  = ">"  if op == "find_max" else "<"
        wrong_sym = "<"  if op == "find_max" else ">"

        if not code_profile.has_comparison:
            error("Q-MISSING-COMPARISON-01", "critical", "condition",
                  f"No comparison found — finding the {word} requires comparing elements.",
                  "Inside the loop body",
                  f"Without comparing each element to the current best, you can't find the {word}.",
                  f"Add: `if element {need_sym} current_best: current_best = element`",
                  0.92)

        elif wrong_op in code_profile.comparison_operators and need_op not in code_profile.comparison_operators:
            line = find_line(re.escape(wrong_sym))
            error("Q-WRONG-COMPARISON-01", "critical", "condition",
                  f"Your comparison uses `{wrong_sym}` but for `{op}` you need `{need_sym}`.",
                  f"Line {line}" if line else "Comparison condition",
                  f"Using `{wrong_sym}` means you update your tracker when you find a "
                  f"{'smaller' if op == 'find_max' else 'larger'} element — "
                  f"so you end up with the {'minimum' if op == 'find_max' else 'maximum'} instead.",
                  f"Change `{wrong_sym}` to `{need_sym}` in your `if` condition.",
                  0.94, line)

        # Check initialization: `max_val = 0` is wrong if list can have all negatives
        init_line = find_line(r'(max_val|max_num|result|best|largest|smallest|min_val)\s*=\s*0\b')
        if init_line:
            error("Q-WRONG-INIT-01", "warning", "variable",
                  f"You initialized your tracker to `0`, which is wrong if all elements are negative.",
                  f"Line {init_line}",
                  f"If every element in the list is negative, your tracker stays at 0 "
                  f"and you return 0 instead of the actual {word}.",
                  f"Initialize to the first element instead: `best = arr[0]`",
                  0.80, init_line)

    # ── sum / count / average ────────────────────────────────────
    if op in ("sum", "count", "average"):
        if not code_profile.has_accumulator:
            error("Q-MISSING-ACCUMULATOR-01", "critical", "variable",
                  f"No accumulator (`+=`) found — '{op}' requires building a running total.",
                  "Loop body",
                  "Without `total += element`, your loop iterates but discards every value.",
                  "Add `total = 0` before the loop, then `total += element` inside it.",
                  0.93)

        else:
            # Check if accumulator is reset inside the loop
            for var in code_profile.accumulator_vars:
                reset_line = find_line(rf'\b{re.escape(var)}\s*=\s*(0|0\.0|\[\]|{{}})')
                if reset_line:
                    ln_content = code_lines[reset_line - 1]
                    indent = len(ln_content) - len(ln_content.lstrip())
                    if indent >= 4:
                        error("Q-ACCUMULATOR-RESET-01", "critical", "variable",
                              f"Variable `{var}` is reset to 0 INSIDE the loop.",
                              f"Line {reset_line}",
                              "Every iteration resets the running total, so at the end "
                              "you only have the last element's value, not the full sum.",
                              f"Move `{var} = 0` to BEFORE the `for` loop.",
                              0.95, reset_line)

        if op == "average":
            if not find_line(r'[/]'):
                error("Q-MISSING-DIVISION-01", "critical", "algorithm",
                      "No division found — computing an average requires dividing by the count.",
                      "After the loop",
                      "Without dividing, you return the sum instead of the average.",
                      "After the loop: `return total / len(numbers)` (or `/ n`).",
                      0.90)

        if op == "count":
            if not code_profile.has_if:
                error("Q-MISSING-CONDITION-01", "critical", "condition",
                      "No `if` condition found — counting requires checking each element.",
                      "Inside the loop",
                      "Without a condition, you count ALL elements rather than the matching ones.",
                      "Add a condition: `if element == target: count += 1`",
                      0.88)

    # ── sort ─────────────────────────────────────────────────────
    if op == "sort":
        if not code_profile.has_sort_call and not code_profile.has_nested_loop:
            error("Q-SORT-NO-LOGIC-01", "critical", "algorithm",
                  "No sorting logic found (no `.sort()`, no `sorted()`, no nested loop).",
                  "Function body",
                  "Without sort logic, the output order is unchanged.",
                  "Either use `return sorted(arr)` or implement a sort with nested loops.",
                  0.88)

    # ── factorial / fibonacci ─────────────────────────────────────
    if op in ("factorial", "fibonacci"):
        if code_profile.has_recursion and not code_profile.has_if:
            error("Q-MISSING-BASE-CASE-01", "critical", "algorithm",
                  f"Recursive `{op}` function has no base case (no `if` statement).",
                  "Function definition",
                  "Without a base case, the recursion never stops → RecursionError.",
                  "Add: `if n == 0: return 1` (factorial) or `if n <= 1: return n` (fibonacci).",
                  0.93)

        if op == "fibonacci" and code_profile.has_loop:
            # Check they have two variables (common mistake: only tracking one)
            assign_lines = [ln for ln in code_lines if re.match(r'\s*\w+\s*=\s*\w+', ln)]
            if len(assign_lines) < 2:
                error("Q-FIBONACCI-ONE-VAR-01", "warning", "variable",
                      "Fibonacci requires tracking two previous values, but only one assignment found.",
                      "Variable declarations",
                      "You need both `a` and `b` (or `prev` and `curr`) to compute fibonacci.",
                      "Start with `a, b = 0, 1` and update both: `a, b = b, a + b`.",
                      0.72)

    # ── search ────────────────────────────────────────────────────
    if op == "search":
        if not code_profile.has_return:
            error("Q-SEARCH-NO-RETURN-01", "critical", "output",
                  "Search function has no `return` statement.",
                  "Function body",
                  "Without returning `True`/`False` or an index, the caller gets `None`.",
                  "Return `True` (or the index) when found inside the loop, `False` after it.",
                  0.90)

        if code_profile.has_loop and not code_profile.has_if:
            error("Q-SEARCH-NO-CONDITION-01", "critical", "condition",
                  "Loop found but no `if` condition — how are you checking for the target?",
                  "Inside the loop",
                  "Without `if element == target`, you loop but never actually compare.",
                  "Add: `if element == target: return True` inside the loop.",
                  0.88)

    # ── prime ─────────────────────────────────────────────────────
    if op == "prime":
        mod_line = find_line(r'%')
        if not mod_line:
            error("Q-PRIME-NO-MODULO-01", "critical", "algorithm",
                  "No modulo operator (`%`) found — prime checking requires divisibility test.",
                  "Loop body",
                  "Without `n % i == 0`, you can't check if a number divides evenly.",
                  "Use: `if n % i == 0: return False` inside a loop from 2 to sqrt(n).",
                  0.90)

    # ── binary_search ─────────────────────────────────────────────
    if op == "binary_search":
        mid_line = find_line(r'(mid|middle)\s*=')
        if not mid_line:
            error("Q-BSEARCH-NO-MID-01", "critical", "algorithm",
                  "No `mid` variable found — binary search requires computing a midpoint.",
                  "Inside the loop",
                  "Without a midpoint, you can't split the search space in half.",
                  "Add: `mid = (left + right) // 2` inside your while loop.",
                  0.88)

        # Check for / instead of // in mid calculation
        div_float = find_line(r'(left\s*\+\s*right|lo\s*\+\s*hi)\s*/[^/]')
        if div_float:
            error("Q-BSEARCH-FLOAT-MID-01", "warning", "arithmetic",
                  "Midpoint uses `/` (float division) instead of `//` (integer division).",
                  f"Line {div_float}",
                  "A float index like `5.0` will raise a TypeError when used as a list index.",
                  "Change `/` to `//`: `mid = (left + right) // 2`",
                  0.90, div_float)

    # ════════════════════════════════════════════════════════════
    # GROUP B — Universal rules (apply to all question types)
    # ════════════════════════════════════════════════════════════

    # Missing return when question expects a value
    if question.expected_return_type not in ("unknown",) and not code_profile.has_return:
        error("Q-NO-RETURN-01", "critical", "output",
              "Function never returns a value.",
              "End of function",
              f"This question expects a `{question.expected_return_type}`. "
              "Without `return`, the caller receives `None`.",
              "Add `return result` at the end of your function.",
              0.85)

    # Return inside loop (exits on first iteration)
    early_return = _find_return_inside_loop(code_lines)
    if early_return:
        error("Q-EARLY-RETURN-01", "critical", "loop",
              "Function returns inside the loop — exits after the FIRST iteration only.",
              f"Line {early_return}",
              "The loop body executes once then immediately exits. "
              "The remaining elements are never processed.",
              "Move `return` to AFTER the loop finishes.",
              0.91, early_return)

    # Diagnose specific output diff patterns
    for diff_type, message, eid, sev in [
        ("off_by_one",    "Output is off by exactly 1.", "Q-OFF-BY-ONE-01",   "warning"),
        ("wrong_sign",    "Output has right magnitude but wrong sign.", "Q-WRONG-SIGN-01", "warning"),
        ("empty",         "Code produced no output.", "Q-NO-OUTPUT-01",      "critical"),
        ("zero_output",   "Output is 0 when it should not be.", "Q-ZERO-OUTPUT-01", "critical"),
        ("reversed",      "Output is the reverse of expected.", "Q-REVERSED-OUTPUT-01", "warning"),
        ("wrong_comparison_direction", "Comparison direction is wrong.", "Q-COMPARISON-DIR-01", "critical"),
    ]:
        matching = [d for d in failed if d.match_type == diff_type]
        if matching:
            diag = matching[0].diff_diagnosis
            line = None
            if diff_type == "off_by_one":
                line = find_line(r'range\s*\(')
            elif diff_type in ("wrong_sign", "wrong_comparison_direction"):
                line = find_line(r'[><]')

            errors.append(LogicalError(
                error_id=eid, severity=sev, category="output",
                line=line, code_snippet=snippet(line),
                what=message,
                where=f"Line {line}" if line else "Output logic",
                why=diag,
                hint="Trace through the failing input manually, checking each step.",
                confidence=0.88,
                related_test_cases=[d.test_index for d in matching]
            ))

    # Some tests pass, some fail → edge case
    passed_set = {d.test_index for d in test_diffs if d.passed}
    if passed_set and failed_idx:
        failing_inputs = [test_diffs[i].input_val[:40] for i in failed_idx[:3]]
        error("Q-EDGE-CASE-01", "warning", "algorithm",
              "Code passes some tests but fails others — likely an edge case bug.",
              "Condition or boundary handling",
              "Your logic works for typical inputs but breaks on boundaries "
              "(e.g. empty list, single element, all-same values, negatives).",
              f"Test manually with: {failing_inputs}",
              0.78)

    return errors


def _find_return_inside_loop(code_lines: list[str]) -> object:
    """
    Detect a bare `return` directly in a loop body (not inside an `if`).
    Returns the line number or None.
    """
    in_loop = False
    loop_indent = -1
    for i, line in enumerate(code_lines, 1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if re.match(r'(for|while)\s', stripped):
            in_loop = True
            loop_indent = indent
        if in_loop and indent <= loop_indent and i > 1 and not re.match(r'(for|while)\s', stripped):
            in_loop = False
            loop_indent = -1
        if in_loop and re.match(r'return\s', stripped) and indent == loop_indent + 4:
            return i
    return None


# =========================================================
# SAFE EXECUTION
# =========================================================

DANGEROUS_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "socket", "requests",
    "urllib", "ctypes", "multiprocessing", "threading", "importlib", "pickle"
}


def check_safety(code: str) -> list[str]:
    issues = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] in DANGEROUS_IMPORTS:
                        issues.append(f"Dangerous import: `{a.name}`")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in DANGEROUS_IMPORTS:
                    issues.append(f"Dangerous import: `{node.module}`")
    except SyntaxError:
        pass
    if len(code) > 10_000:
        issues.append("Code exceeds 10,000 character limit.")
    return issues


def execute_code(code: str, stdin_input: str = "") -> dict:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
            f.write(code)
            path = f.name
        result = subprocess.run(
            ["python", path], input=stdin_input,
            capture_output=True, text=True, timeout=5
        )
        os.remove(path)
        return {"output": result.stdout.strip(), "error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Execution timed out"}
    except Exception as e:
        return {"output": "", "error": str(e)}


# =========================================================
# SMART COMPARISON
# =========================================================

def smart_compare(actual: str, expected: str) -> tuple[bool, str]:
    if actual.strip() == expected.strip():
        return True, "exact"
    if " ".join(actual.split()) == " ".join(expected.split()):
        return True, "normalized_whitespace"
    try:
        if math.isclose(float(actual.strip()), float(expected.strip()), rel_tol=1e-6):
            return True, "float_tolerance"
    except (ValueError, TypeError):
        pass
    a_set = {l.strip() for l in actual.strip().splitlines() if l.strip()}
    e_set = {l.strip() for l in expected.strip().splitlines() if l.strip()}
    if a_set == e_set:
        return True, "unordered_lines"
    return False, "failed"


# =========================================================
# MAIN ENDPOINT
# =========================================================

@app.post("/analyze")
def evaluate(request: EvaluationRequest):

    safety_issues = check_safety(request.code)
    if safety_issues:
        raise HTTPException(status_code=400, detail={
            "error": "Code blocked.", "issues": safety_issues
        })

    # Stage 1: understand the question
    q_profile = analyze_question(request.problem_statement)

    # Stage 2: understand the code
    c_profile = analyze_code_structure(request.code)
    code_lines = request.code.splitlines()

    # Stage 3: run tests and collect diffs
    test_diffs: list[TestDiff] = []
    for i, tc in enumerate(request.test_cases):
        result = execute_code(request.code, tc.get("input", ""))
        actual = result["output"]
        expected = tc.get("expected_output", "").strip()

        passed, match_type = smart_compare(actual, expected)
        if not passed:
            match_type, diff_diag = diagnose_output_diff(expected, actual, q_profile.expected_operation)
        else:
            diff_diag = ""

        test_diffs.append(TestDiff(
            test_index=i,
            input_val=tc.get("input", ""),
            expected=expected, actual=actual,
            passed=passed, match_type=match_type,
            diff_diagnosis=diff_diag,
            runtime_error=result.get("error", "")
        ))

    # Stage 4: detect logical errors
    logical_errors = detect_logical_errors(q_profile, c_profile, test_diffs, code_lines)

    # Sort: critical first, then by confidence
    order = {"critical": 0, "warning": 1, "info": 2}
    logical_errors.sort(key=lambda e: (order.get(e.severity, 3), -e.confidence))

    passed_count = sum(1 for d in test_diffs if d.passed)

    return {
        "studentId": request.studentId,
        "questionId": request.questionId,

        # What the question expects
        "question_analysis": {
            "detected_operation": q_profile.expected_operation,
            "expected_concepts": q_profile.expected_concepts,
            "expected_return_type": q_profile.expected_return_type,
            "input_structure": q_profile.input_structure,
            "edge_cases_in_problem": q_profile.edge_cases,
        },

        # What the student code actually does
        "code_analysis": {
            "has_loop": c_profile.has_loop,
            "has_recursion": c_profile.has_recursion,
            "has_accumulator": c_profile.has_accumulator,
            "has_comparison": c_profile.has_comparison,
            "has_return": c_profile.has_return,
            "loop_count": c_profile.loop_count,
            "max_nesting_depth": c_profile.max_nesting_depth,
            "accumulator_vars": c_profile.accumulator_vars,
        },

        # Test results with per-test diagnosis
        "test_summary": {
            "passed": passed_count,
            "total": len(test_diffs),
            "score": f"{passed_count}/{len(test_diffs)}",
            "all_passed": passed_count == len(test_diffs),
        },
        "test_results": [
            {
                "test_case": d.test_index + 1,
                "input": d.input_val,
                "expected": d.expected,
                "actual": d.actual,
                "passed": d.passed,
                "diagnosis": d.diff_diagnosis,
                "runtime_error": d.runtime_error or None,
            }
            for d in test_diffs
        ],

        # The core output: specific logical errors with what/where/why/hint
        "logical_errors": [
            {
                "error_id": e.error_id,
                "severity": e.severity,
                "category": e.category,
                "what": e.what,
                "where": e.where,
                "why": e.why,
                "hint": e.hint,
                "line": e.line,
                "code_snippet": e.code_snippet,
                "confidence": e.confidence,
                "related_test_cases": e.related_test_cases,
            }
            for e in logical_errors
        ],
        "error_count": len(logical_errors),
        "has_logical_errors": len(logical_errors) > 0,
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}