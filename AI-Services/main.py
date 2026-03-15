

# """
# Question-Aware Logical Error Detection Engine  v3.0
# =====================================================
# Detects LOGICAL errors in student code by understanding:
#   - What the QUESTION is asking (parsed from problem statement)
#   - What the student's CODE is doing (AST analysis)
#   - How the OUTPUT differs from expected (test case diffing)

# 100% offline — no LLM API required.

# Flow:
#   Stage 1 — QuestionAnalyzer    : reads problem text → detects operation, expected concepts, edge cases
#   Stage 2 — CodeStructureAnalyzer: reads student code → detects loops, recursion, accumulators, comparisons
#   Stage 3 — OutputDiffer        : compares actual vs expected → diagnoses HOW it's wrong
#   Stage 4 — MismatchDetector    : question needs vs code does → produces specific LogicalErrors
#   Stage 5 — FeedbackEngine      : emits what/where/why/hint per error
# """

# import re
# import ast
# import math
# import subprocess
# import tempfile
# import os
# from dataclasses import dataclass, field
# from collections import defaultdict, Counter
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from tree_sitter import Parser
# from tree_sitter_languages import get_language

# app = FastAPI(title="Question-Aware Logical Error Detector", version="3.0.0")


# # =========================================================
# # REQUEST MODEL
# # =========================================================
# class EvaluationRequest(BaseModel):
#     studentId: int
#     questionId: str
#     problem_statement: str   # e.g. "Write a function to find the maximum element in a list"
#     code: str
#     test_cases: list[dict]   # [{"input": "5\n1 2 3 4 5", "expected_output": "5"}]
#     language: str = "python"


# # =========================================================
# # TREE-SITTER SETUP
# # =========================================================
# PY_LANGUAGE = get_language("python")
# _ts_parser = Parser()
# _ts_parser.set_language(PY_LANGUAGE)


# # =========================================================
# # DATA STRUCTURES
# # =========================================================

# @dataclass
# class QuestionProfile:
#     """What a question EXPECTS the solution to implement."""
#     raw_text: str
#     expected_operation: str = "unknown"
#     expected_concepts: list[str] = field(default_factory=list)
#     expected_return_type: str = "unknown"
#     input_structure: str = "unknown"
#     edge_cases: list[str] = field(default_factory=list)


# @dataclass
# class CodeProfile:
#     """What the student code actually does (extracted from AST)."""
#     has_loop: bool = False
#     has_nested_loop: bool = False
#     has_recursion: bool = False
#     has_return: bool = False
#     has_if: bool = False
#     has_accumulator: bool = False
#     has_comparison: bool = False
#     has_sort_call: bool = False
#     has_index_access: bool = False
#     loop_count: int = 0
#     function_count: int = 0
#     max_nesting_depth: int = 0
#     accumulator_vars: list[str] = field(default_factory=list)
#     comparison_operators: list[str] = field(default_factory=list)
#     called_builtins: list[str] = field(default_factory=list)
#     return_lines: list[int] = field(default_factory=list)


# @dataclass
# class TestDiff:
#     """Diagnosis of a single failed test case."""
#     test_index: int
#     input_val: str
#     expected: str
#     actual: str
#     passed: bool
#     match_type: str
#     diff_diagnosis: str = ""
#     runtime_error: str = ""


# @dataclass
# class LogicalError:
#     """A fully diagnosed logical error with what/where/why/hint."""
#     error_id: str
#     severity: str           # critical / warning / info
#     category: str           # algorithm / loop / condition / variable / output
#     line: object            # int or None
#     code_snippet: str
#     what: str
#     where: str
#     why: str
#     hint: str
#     confidence: float
#     related_test_cases: list[int] = field(default_factory=list)


# # =========================================================
# # STAGE 1: QUESTION ANALYZER
# # =========================================================

# OPERATION_KEYWORDS = {
#     "find_max":      ["maximum", "largest", "greatest", "max", "biggest", "highest"],
#     "find_min":      ["minimum", "smallest", "least", "min", "lowest"],
#     "sum":           ["sum", "total", "add all", "accumulate", "aggregate"],
#     "count":         ["count", "how many", "number of", "frequency", "occurrences"],
#     "search":        ["search", "find", "locate", "exists", "contains", "present"],
#     "sort":          ["sort", "order", "arrange", "ascending", "descending"],
#     "reverse":       ["reverse", "reversed", "backward", "flip"],
#     "palindrome":    ["palindrome", "reads same"],
#     "prime":         ["prime", "prime number"],
#     "factorial":     ["factorial"],
#     "fibonacci":     ["fibonacci", "fib"],
#     "average":       ["average", "mean", "arithmetic mean"],
#     "binary_search": ["binary search"],
#     "two_sum":       ["two sum", "pair that adds"],
#     "unique":        ["unique", "distinct", "duplicates"],
#     "matrix":        ["matrix", "2d array", "grid"],
#     "string_ops":    ["string", "substring", "character", "vowel", "consonant"],
#     "gcd_lcm":       ["gcd", "lcm", "greatest common", "least common multiple"],
#     "power":         ["power", "exponent", "raise to"],
# }

# OPERATION_TO_CONCEPTS = {
#     "find_max":      ["loop", "comparison", "variable_tracking"],
#     "find_min":      ["loop", "comparison", "variable_tracking"],
#     "sum":           ["loop", "accumulator"],
#     "count":         ["loop", "condition", "accumulator"],
#     "search":        ["loop", "condition"],
#     "sort":          ["nested_loop_or_builtin", "comparison"],
#     "reverse":       ["loop_or_slicing"],
#     "palindrome":    ["string_indexing_or_reverse", "comparison"],
#     "prime":         ["loop", "condition", "divisibility"],
#     "factorial":     ["loop_or_recursion", "accumulator"],
#     "fibonacci":     ["loop_or_recursion", "two_variables"],
#     "average":       ["loop", "accumulator", "division"],
#     "binary_search": ["loop_or_recursion", "mid_calculation", "comparison"],
#     "two_sum":       ["loop", "condition"],
#     "unique":        ["loop", "set_or_dict"],
#     "matrix":        ["nested_loop", "index_access"],
#     "string_ops":    ["loop_or_slicing", "string_methods"],
#     "gcd_lcm":       ["loop_or_recursion", "modulo"],
#     "power":         ["loop_or_recursion", "accumulator"],
# }

# OPERATION_TO_RETURN = {
#     "find_max":      "single_value",
#     "find_min":      "single_value",
#     "sum":           "single_value",
#     "count":         "single_value",
#     "search":        "boolean_or_index",
#     "sort":          "list",
#     "reverse":       "list_or_string",
#     "palindrome":    "boolean",
#     "prime":         "boolean",
#     "factorial":     "single_value",
#     "fibonacci":     "single_value_or_list",
#     "average":       "float",
#     "binary_search": "index_or_boolean",
#     "two_sum":       "pair_or_list",
#     "unique":        "list_or_count",
#     "matrix":        "varies",
#     "string_ops":    "string_or_value",
#     "gcd_lcm":       "single_value",
#     "power":         "single_value",
# }

# INPUT_STRUCTURE_KEYWORDS = {
#     "array":  ["list", "array", "elements", "sequence", "numbers"],
#     "string": ["string", "word", "sentence", "character"],
#     "matrix": ["matrix", "grid", "2d", "rows", "columns"],
#     "number": ["number", "integer", "digit", "value"],
# }

# EDGE_CASE_PATTERNS = {
#     "empty_list":     ["empty", "no elements"],
#     "single_element": ["single", "one element"],
#     "negative":       ["negative"],
#     "zero":           ["zero"],
#     "all_same":       ["all same", "identical", "duplicates"],
# }


# def analyze_question(problem_statement: str) -> QuestionProfile:
#     text = problem_statement.lower()
#     profile = QuestionProfile(raw_text=problem_statement)

#     for op, keywords in OPERATION_KEYWORDS.items():
#         if any(kw in text for kw in keywords):
#             profile.expected_operation = op
#             break

#     profile.expected_concepts = OPERATION_TO_CONCEPTS.get(
#         profile.expected_operation, ["loop", "condition"])
#     profile.expected_return_type = OPERATION_TO_RETURN.get(
#         profile.expected_operation, "unknown")

#     for structure, keywords in INPUT_STRUCTURE_KEYWORDS.items():
#         if any(kw in text for kw in keywords):
#             profile.input_structure = structure
#             break

#     for edge_case, patterns in EDGE_CASE_PATTERNS.items():
#         if any(p in text for p in patterns):
#             profile.edge_cases.append(edge_case)

#     return profile


# # =========================================================
# # STAGE 2: CODE STRUCTURE ANALYZER
# # =========================================================

# def analyze_code_structure(code: str) -> CodeProfile:
#     profile = CodeProfile()
#     try:
#         tree = ast.parse(code)
#     except SyntaxError:
#         return profile

#     max_depth = [0]

#     def walk(node, loop_depth=0):
#         if isinstance(node, (ast.For, ast.While)):
#             profile.loop_count += 1
#             profile.has_loop = True
#             loop_depth += 1
#             max_depth[0] = max(max_depth[0], loop_depth)
#             if loop_depth >= 2:
#                 profile.has_nested_loop = True

#         if isinstance(node, ast.FunctionDef):
#             profile.function_count += 1
#             fname = node.name
#             for n in ast.walk(node):
#                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == fname:
#                     profile.has_recursion = True

#         if isinstance(node, ast.Return):
#             profile.has_return = True
#             profile.return_lines.append(node.lineno)

#         if isinstance(node, ast.If):
#             profile.has_if = True

#         if isinstance(node, ast.AugAssign):
#             profile.has_accumulator = True
#             if isinstance(node.target, ast.Name):
#                 profile.accumulator_vars.append(node.target.id)

#         if isinstance(node, ast.Compare):
#             profile.has_comparison = True
#             for op in node.ops:
#                 profile.comparison_operators.append(type(op).__name__)

#         if isinstance(node, ast.Call):
#             if isinstance(node.func, ast.Attribute) and node.func.attr in ("sort", "sorted"):
#                 profile.has_sort_call = True
#             if isinstance(node.func, ast.Name):
#                 n = node.func.id
#                 profile.called_builtins.append(n)
#                 if n == "sorted":
#                     profile.has_sort_call = True

#         if isinstance(node, ast.Subscript):
#             profile.has_index_access = True

#         for child in ast.iter_child_nodes(node):
#             walk(child, loop_depth)

#     walk(tree)
#     profile.max_nesting_depth = max_depth[0]
#     return profile


# # =========================================================
# # STAGE 3: OUTPUT DIFFER
# # Diagnoses HOW the output is wrong, not just THAT it's wrong.
# # =========================================================

# def diagnose_output_diff(expected: str, actual: str, operation: str) -> tuple[str, str]:
#     """Returns (match_type, human_readable_diagnosis)."""
#     exp = expected.strip()
#     act = actual.strip()

#     if exp == act:
#         return "exact", ""

#     if not act:
#         return "empty", (
#             "Your code produced NO output. "
#             "This usually means a missing `print()`, a missing `return`, "
#             "or the function was defined but never called."
#         )

#     if any(kw in act.lower() for kw in ["error", "traceback", "exception"]):
#         return "runtime_error", (
#             "Your code crashed with a runtime error instead of producing output. "
#             "Fix the error first, then check your logic."
#         )

#     # Numeric comparison
#     try:
#         exp_num = float(exp)
#         act_num = float(act)
#         diff = act_num - exp_num

#         if abs(diff) == 1:
#             direction = "too high by 1" if diff > 0 else "too low by 1"
#             return "off_by_one", (
#                 f"Your answer is {direction}. "
#                 "This is a classic off-by-one error — check your loop range "
#                 "(`range(n)` vs `range(n+1)`) or your starting/ending index."
#             )

#         if exp_num != 0 and abs(act_num) == abs(exp_num) and act_num == -exp_num:
#             return "wrong_sign", (
#                 "Your answer has the correct magnitude but the wrong sign. "
#                 "Check if you are subtracting when you should add, "
#                 "or if a comparison operator (`>` / `<`) is reversed."
#             )

#         if act_num == 0 and exp_num != 0:
#             return "zero_output", (
#                 "Your answer is 0 but should be non-zero. "
#                 "The most common cause: your accumulator is reset to 0 inside "
#                 "the loop instead of before it, or it is never updated."
#             )

#         # Operation-specific
#         if op in ("find_max", "find_min"):
#             word = "maximum" if op == "find_max" else "minimum"
#             comp = ">" if op == "find_max" else "<"
#             wrong = "<" if op == "find_max" else ">"
#             if (op == "find_max" and act_num < exp_num) or (op == "find_min" and act_num > exp_num):
#                 return "wrong_comparison_direction", (
#                     f"You returned {act} but the {word} is {exp}. "
#                     f"Your comparison operator may be `{wrong}` when it should be `{comp}`, "
#                     f"or your initial tracker value is wrong (e.g. `= 0` instead of `= arr[0]`)."
#                 )

#         if op == "average" and exp_num != 0:
#             if math.isclose(act_num, exp_num * 2, rel_tol=0.05):
#                 return "forgot_division", (
#                     "Your result is about double the expected average. "
#                     "Did you multiply instead of divide, or divide by the wrong count?"
#                 )
#             # Check if they returned the sum instead of average
#             # (can't know exact n, but diagnose directionally)

#         return "wrong_value", (
#             f"Expected `{exp}` but got `{act}` (difference: {diff:+.4g}). "
#             "Trace through your logic manually with this input."
#         )

#     except (ValueError, TypeError):
#         pass

#     # String / list comparison
#     if act == exp[::-1]:
#         return "reversed", (
#             "Your output is the exact reverse of the expected output. "
#             "Check if you are iterating backward when you should go forward, "
#             "or if you're building the result in reverse."
#         )

#     common = os.path.commonprefix([exp, act])
#     if len(common) > max(len(exp), 1) * 0.5:
#         return "partial", (
#             f"Your output starts correctly (`{common[:30]}`) but ends differently. "
#             "Your loop may be stopping too early — check your termination condition."
#         )

#     if exp.lower() == act.lower():
#         return "case_mismatch", (
#             "Right content, wrong case (uppercase/lowercase). "
#             "Check any `.upper()` / `.lower()` calls."
#         )

#     return "failed", (
#         f"Expected `{exp}` but got `{act}`. "
#         "Your logic produces a completely different result. "
#         "Try tracing through the failing input step by step."
#     )


# # =========================================================
# # STAGE 4: MISMATCH DETECTOR
# # Compares question expectations vs code structure vs output diffs
# # =========================================================

# def detect_logical_errors(
#     question: QuestionProfile,
#     code_profile: CodeProfile,
#     test_diffs: list[TestDiff],
#     code_lines: list[str],
# ) -> list[LogicalError]:

#     errors: list[LogicalError] = []
#     failed = [d for d in test_diffs if not d.passed]
#     failed_idx = [d.test_index for d in failed]

#     if not failed:
#         return []  # All tests passed — no errors to report

#     op = question.expected_operation

#     # ── helpers ──────────────────────────────────────────────────

#     def snippet(line, ctx=1):
#         if line is None or line < 1:
#             return ""
#         start = max(0, line - 1 - ctx)
#         end = min(len(code_lines), line + ctx)
#         return "\n".join(f"  {start+i+1}: {l}" for i, l in enumerate(code_lines[start:end]))

#     def find_line(pattern):
#         for i, ln in enumerate(code_lines, 1):
#             if re.search(pattern, ln):
#                 return i
#         return None

#     def error(eid, sev, cat, what, where, why, hint, conf, line=None):
#         errors.append(LogicalError(
#             error_id=eid, severity=sev, category=cat,
#             line=line, code_snippet=snippet(line),
#             what=what, where=where, why=why, hint=hint,
#             confidence=conf, related_test_cases=failed_idx
#         ))

#     # ════════════════════════════════════════════════════════════
#     # GROUP A — Operation-specific mismatch rules
#     # ════════════════════════════════════════════════════════════

#     # ── find_max / find_min ──────────────────────────────────────
#     if op in ("find_max", "find_min"):
#         word = "maximum" if op == "find_max" else "minimum"
#         need_op  = "Gt" if op == "find_max" else "Lt"   # ast class name
#         wrong_op = "Lt" if op == "find_max" else "Gt"
#         need_sym  = ">"  if op == "find_max" else "<"
#         wrong_sym = "<"  if op == "find_max" else ">"

#         if not code_profile.has_comparison:
#             error("Q-MISSING-COMPARISON-01", "critical", "condition",
#                   f"No comparison found — finding the {word} requires comparing elements.",
#                   "Inside the loop body",
#                   f"Without comparing each element to the current best, you can't find the {word}.",
#                   f"Add: `if element {need_sym} current_best: current_best = element`",
#                   0.92)

#         elif wrong_op in code_profile.comparison_operators and need_op not in code_profile.comparison_operators:
#             line = find_line(re.escape(wrong_sym))
#             error("Q-WRONG-COMPARISON-01", "critical", "condition",
#                   f"Your comparison uses `{wrong_sym}` but for `{op}` you need `{need_sym}`.",
#                   f"Line {line}" if line else "Comparison condition",
#                   f"Using `{wrong_sym}` means you update your tracker when you find a "
#                   f"{'smaller' if op == 'find_max' else 'larger'} element — "
#                   f"so you end up with the {'minimum' if op == 'find_max' else 'maximum'} instead.",
#                   f"Change `{wrong_sym}` to `{need_sym}` in your `if` condition.",
#                   0.94, line)

#         # Check initialization: `max_val = 0` is wrong if list can have all negatives
#         init_line = find_line(r'(max_val|max_num|result|best|largest|smallest|min_val)\s*=\s*0\b')
#         if init_line:
#             error("Q-WRONG-INIT-01", "warning", "variable",
#                   f"You initialized your tracker to `0`, which is wrong if all elements are negative.",
#                   f"Line {init_line}",
#                   f"If every element in the list is negative, your tracker stays at 0 "
#                   f"and you return 0 instead of the actual {word}.",
#                   f"Initialize to the first element instead: `best = arr[0]`",
#                   0.80, init_line)

#     # ── sum / count / average ────────────────────────────────────
#     if op in ("sum", "count", "average"):
#         if not code_profile.has_accumulator:
#             error("Q-MISSING-ACCUMULATOR-01", "critical", "variable",
#                   f"No accumulator (`+=`) found — '{op}' requires building a running total.",
#                   "Loop body",
#                   "Without `total += element`, your loop iterates but discards every value.",
#                   "Add `total = 0` before the loop, then `total += element` inside it.",
#                   0.93)

#         else:
#             # Check if accumulator is reset inside the loop
#             for var in code_profile.accumulator_vars:
#                 reset_line = find_line(rf'\b{re.escape(var)}\s*=\s*(0|0\.0|\[\]|{{}})')
#                 if reset_line:
#                     ln_content = code_lines[reset_line - 1]
#                     indent = len(ln_content) - len(ln_content.lstrip())
#                     if indent >= 4:
#                         error("Q-ACCUMULATOR-RESET-01", "critical", "variable",
#                               f"Variable `{var}` is reset to 0 INSIDE the loop.",
#                               f"Line {reset_line}",
#                               "Every iteration resets the running total, so at the end "
#                               "you only have the last element's value, not the full sum.",
#                               f"Move `{var} = 0` to BEFORE the `for` loop.",
#                               0.95, reset_line)

#         if op == "average":
#             if not find_line(r'[/]'):
#                 error("Q-MISSING-DIVISION-01", "critical", "algorithm",
#                       "No division found — computing an average requires dividing by the count.",
#                       "After the loop",
#                       "Without dividing, you return the sum instead of the average.",
#                       "After the loop: `return total / len(numbers)` (or `/ n`).",
#                       0.90)

#         if op == "count":
#             if not code_profile.has_if:
#                 error("Q-MISSING-CONDITION-01", "critical", "condition",
#                       "No `if` condition found — counting requires checking each element.",
#                       "Inside the loop",
#                       "Without a condition, you count ALL elements rather than the matching ones.",
#                       "Add a condition: `if element == target: count += 1`",
#                       0.88)

#     # ── sort ─────────────────────────────────────────────────────
#     if op == "sort":
#         if not code_profile.has_sort_call and not code_profile.has_nested_loop:
#             error("Q-SORT-NO-LOGIC-01", "critical", "algorithm",
#                   "No sorting logic found (no `.sort()`, no `sorted()`, no nested loop).",
#                   "Function body",
#                   "Without sort logic, the output order is unchanged.",
#                   "Either use `return sorted(arr)` or implement a sort with nested loops.",
#                   0.88)

#     # ── factorial / fibonacci ─────────────────────────────────────
#     if op in ("factorial", "fibonacci"):
#         if code_profile.has_recursion and not code_profile.has_if:
#             error("Q-MISSING-BASE-CASE-01", "critical", "algorithm",
#                   f"Recursive `{op}` function has no base case (no `if` statement).",
#                   "Function definition",
#                   "Without a base case, the recursion never stops → RecursionError.",
#                   "Add: `if n == 0: return 1` (factorial) or `if n <= 1: return n` (fibonacci).",
#                   0.93)

#         if op == "fibonacci" and code_profile.has_loop:
#             # Check they have two variables (common mistake: only tracking one)
#             assign_lines = [ln for ln in code_lines if re.match(r'\s*\w+\s*=\s*\w+', ln)]
#             if len(assign_lines) < 2:
#                 error("Q-FIBONACCI-ONE-VAR-01", "warning", "variable",
#                       "Fibonacci requires tracking two previous values, but only one assignment found.",
#                       "Variable declarations",
#                       "You need both `a` and `b` (or `prev` and `curr`) to compute fibonacci.",
#                       "Start with `a, b = 0, 1` and update both: `a, b = b, a + b`.",
#                       0.72)

#     # ── search ────────────────────────────────────────────────────
#     if op == "search":
#         if not code_profile.has_return:
#             error("Q-SEARCH-NO-RETURN-01", "critical", "output",
#                   "Search function has no `return` statement.",
#                   "Function body",
#                   "Without returning `True`/`False` or an index, the caller gets `None`.",
#                   "Return `True` (or the index) when found inside the loop, `False` after it.",
#                   0.90)

#         if code_profile.has_loop and not code_profile.has_if:
#             error("Q-SEARCH-NO-CONDITION-01", "critical", "condition",
#                   "Loop found but no `if` condition — how are you checking for the target?",
#                   "Inside the loop",
#                   "Without `if element == target`, you loop but never actually compare.",
#                   "Add: `if element == target: return True` inside the loop.",
#                   0.88)

#     # ── prime ─────────────────────────────────────────────────────
#     if op == "prime":
#         mod_line = find_line(r'%')
#         if not mod_line:
#             error("Q-PRIME-NO-MODULO-01", "critical", "algorithm",
#                   "No modulo operator (`%`) found — prime checking requires divisibility test.",
#                   "Loop body",
#                   "Without `n % i == 0`, you can't check if a number divides evenly.",
#                   "Use: `if n % i == 0: return False` inside a loop from 2 to sqrt(n).",
#                   0.90)

#     # ── binary_search ─────────────────────────────────────────────
#     if op == "binary_search":
#         mid_line = find_line(r'(mid|middle)\s*=')
#         if not mid_line:
#             error("Q-BSEARCH-NO-MID-01", "critical", "algorithm",
#                   "No `mid` variable found — binary search requires computing a midpoint.",
#                   "Inside the loop",
#                   "Without a midpoint, you can't split the search space in half.",
#                   "Add: `mid = (left + right) // 2` inside your while loop.",
#                   0.88)

#         # Check for / instead of // in mid calculation
#         div_float = find_line(r'(left\s*\+\s*right|lo\s*\+\s*hi)\s*/[^/]')
#         if div_float:
#             error("Q-BSEARCH-FLOAT-MID-01", "warning", "arithmetic",
#                   "Midpoint uses `/` (float division) instead of `//` (integer division).",
#                   f"Line {div_float}",
#                   "A float index like `5.0` will raise a TypeError when used as a list index.",
#                   "Change `/` to `//`: `mid = (left + right) // 2`",
#                   0.90, div_float)

#     # ════════════════════════════════════════════════════════════
#     # GROUP B — Universal rules (apply to all question types)
#     # ════════════════════════════════════════════════════════════

#     # Missing return when question expects a value
#     if question.expected_return_type not in ("unknown",) and not code_profile.has_return:
#         error("Q-NO-RETURN-01", "critical", "output",
#               "Function never returns a value.",
#               "End of function",
#               f"This question expects a `{question.expected_return_type}`. "
#               "Without `return`, the caller receives `None`.",
#               "Add `return result` at the end of your function.",
#               0.85)

#     # Return inside loop (exits on first iteration)
#     early_return = _find_return_inside_loop(code_lines)
#     if early_return:
#         error("Q-EARLY-RETURN-01", "critical", "loop",
#               "Function returns inside the loop — exits after the FIRST iteration only.",
#               f"Line {early_return}",
#               "The loop body executes once then immediately exits. "
#               "The remaining elements are never processed.",
#               "Move `return` to AFTER the loop finishes.",
#               0.91, early_return)

#     # Diagnose specific output diff patterns
#     for diff_type, message, eid, sev in [
#         ("off_by_one",    "Output is off by exactly 1.", "Q-OFF-BY-ONE-01",   "warning"),
#         ("wrong_sign",    "Output has right magnitude but wrong sign.", "Q-WRONG-SIGN-01", "warning"),
#         ("empty",         "Code produced no output.", "Q-NO-OUTPUT-01",      "critical"),
#         ("zero_output",   "Output is 0 when it should not be.", "Q-ZERO-OUTPUT-01", "critical"),
#         ("reversed",      "Output is the reverse of expected.", "Q-REVERSED-OUTPUT-01", "warning"),
#         ("wrong_comparison_direction", "Comparison direction is wrong.", "Q-COMPARISON-DIR-01", "critical"),
#     ]:
#         matching = [d for d in failed if d.match_type == diff_type]
#         if matching:
#             diag = matching[0].diff_diagnosis
#             line = None
#             if diff_type == "off_by_one":
#                 line = find_line(r'range\s*\(')
#             elif diff_type in ("wrong_sign", "wrong_comparison_direction"):
#                 line = find_line(r'[><]')

#             errors.append(LogicalError(
#                 error_id=eid, severity=sev, category="output",
#                 line=line, code_snippet=snippet(line),
#                 what=message,
#                 where=f"Line {line}" if line else "Output logic",
#                 why=diag,
#                 hint="Trace through the failing input manually, checking each step.",
#                 confidence=0.88,
#                 related_test_cases=[d.test_index for d in matching]
#             ))

#     # Some tests pass, some fail → edge case
#     passed_set = {d.test_index for d in test_diffs if d.passed}
#     if passed_set and failed_idx:
#         failing_inputs = [test_diffs[i].input_val[:40] for i in failed_idx[:3]]
#         error("Q-EDGE-CASE-01", "warning", "algorithm",
#               "Code passes some tests but fails others — likely an edge case bug.",
#               "Condition or boundary handling",
#               "Your logic works for typical inputs but breaks on boundaries "
#               "(e.g. empty list, single element, all-same values, negatives).",
#               f"Test manually with: {failing_inputs}",
#               0.78)

#     return errors


# def _find_return_inside_loop(code_lines: list[str]) -> object:
#     """
#     Detect a bare `return` directly in a loop body (not inside an `if`).
#     Returns the line number or None.
#     """
#     in_loop = False
#     loop_indent = -1
#     for i, line in enumerate(code_lines, 1):
#         stripped = line.lstrip()
#         indent = len(line) - len(stripped)
#         if re.match(r'(for|while)\s', stripped):
#             in_loop = True
#             loop_indent = indent
#         if in_loop and indent <= loop_indent and i > 1 and not re.match(r'(for|while)\s', stripped):
#             in_loop = False
#             loop_indent = -1
#         if in_loop and re.match(r'return\s', stripped) and indent == loop_indent + 4:
#             return i
#     return None


# # =========================================================
# # SAFE EXECUTION
# # =========================================================

# DANGEROUS_IMPORTS = {
#     "os", "sys", "subprocess", "shutil", "socket", "requests",
#     "urllib", "ctypes", "multiprocessing", "threading", "importlib", "pickle"
# }


# def check_safety(code: str) -> list[str]:
#     issues = []
#     try:
#         tree = ast.parse(code)
#         for node in ast.walk(tree):
#             if isinstance(node, ast.Import):
#                 for a in node.names:
#                     if a.name.split(".")[0] in DANGEROUS_IMPORTS:
#                         issues.append(f"Dangerous import: `{a.name}`")
#             elif isinstance(node, ast.ImportFrom):
#                 if node.module and node.module.split(".")[0] in DANGEROUS_IMPORTS:
#                     issues.append(f"Dangerous import: `{node.module}`")
#     except SyntaxError:
#         pass
#     if len(code) > 10_000:
#         issues.append("Code exceeds 10,000 character limit.")
#     return issues


# def execute_code(code: str, stdin_input: str = "") -> dict:
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
#             f.write(code)
#             path = f.name
#         result = subprocess.run(
#             ["python", path], input=stdin_input,
#             capture_output=True, text=True, timeout=5
#         )
#         os.remove(path)
#         return {"output": result.stdout.strip(), "error": result.stderr.strip()}
#     except subprocess.TimeoutExpired:
#         return {"output": "", "error": "Execution timed out"}
#     except Exception as e:
#         return {"output": "", "error": str(e)}


# # =========================================================
# # SMART COMPARISON
# # =========================================================

# def smart_compare(actual: str, expected: str) -> tuple[bool, str]:
#     if actual.strip() == expected.strip():
#         return True, "exact"
#     if " ".join(actual.split()) == " ".join(expected.split()):
#         return True, "normalized_whitespace"
#     try:
#         if math.isclose(float(actual.strip()), float(expected.strip()), rel_tol=1e-6):
#             return True, "float_tolerance"
#     except (ValueError, TypeError):
#         pass
#     a_set = {l.strip() for l in actual.strip().splitlines() if l.strip()}
#     e_set = {l.strip() for l in expected.strip().splitlines() if l.strip()}
#     if a_set == e_set:
#         return True, "unordered_lines"
#     return False, "failed"


# # =========================================================
# # MAIN ENDPOINT
# # =========================================================

# @app.post("/analyze")
# def evaluate(request: EvaluationRequest):

#     safety_issues = check_safety(request.code)
#     if safety_issues:
#         raise HTTPException(status_code=400, detail={
#             "error": "Code blocked.", "issues": safety_issues
#         })

#     # Stage 1: understand the question
#     q_profile = analyze_question(request.problem_statement)

#     # Stage 2: understand the code
#     c_profile = analyze_code_structure(request.code)
#     code_lines = request.code.splitlines()

#     # Stage 3: run tests and collect diffs
#     test_diffs: list[TestDiff] = []
#     for i, tc in enumerate(request.test_cases):
#         result = execute_code(request.code, tc.get("input", ""))
#         actual = result["output"]
#         expected = tc.get("expected_output", "").strip()

#         passed, match_type = smart_compare(actual, expected)
#         if not passed:
#             match_type, diff_diag = diagnose_output_diff(expected, actual, q_profile.expected_operation)
#         else:
#             diff_diag = ""

#         test_diffs.append(TestDiff(
#             test_index=i,
#             input_val=tc.get("input", ""),
#             expected=expected, actual=actual,
#             passed=passed, match_type=match_type,
#             diff_diagnosis=diff_diag,
#             runtime_error=result.get("error", "")
#         ))

#     # Stage 4: detect logical errors
#     logical_errors = detect_logical_errors(q_profile, c_profile, test_diffs, code_lines)

#     # Sort: critical first, then by confidence
#     order = {"critical": 0, "warning": 1, "info": 2}
#     logical_errors.sort(key=lambda e: (order.get(e.severity, 3), -e.confidence))

#     passed_count = sum(1 for d in test_diffs if d.passed)

#     return {
#         "studentId": request.studentId,
#         "questionId": request.questionId,

#         # What the question expects
#         "question_analysis": {
#             "detected_operation": q_profile.expected_operation,
#             "expected_concepts": q_profile.expected_concepts,
#             "expected_return_type": q_profile.expected_return_type,
#             "input_structure": q_profile.input_structure,
#             "edge_cases_in_problem": q_profile.edge_cases,
#         },

#         # What the student code actually does
#         "code_analysis": {
#             "has_loop": c_profile.has_loop,
#             "has_recursion": c_profile.has_recursion,
#             "has_accumulator": c_profile.has_accumulator,
#             "has_comparison": c_profile.has_comparison,
#             "has_return": c_profile.has_return,
#             "loop_count": c_profile.loop_count,
#             "max_nesting_depth": c_profile.max_nesting_depth,
#             "accumulator_vars": c_profile.accumulator_vars,
#         },

#         # Test results with per-test diagnosis
#         "test_summary": {
#             "passed": passed_count,
#             "total": len(test_diffs),
#             "score": f"{passed_count}/{len(test_diffs)}",
#             "all_passed": passed_count == len(test_diffs),
#         },
#         "test_results": [
#             {
#                 "test_case": d.test_index + 1,
#                 "input": d.input_val,
#                 "expected": d.expected,
#                 "actual": d.actual,
#                 "passed": d.passed,
#                 "diagnosis": d.diff_diagnosis,
#                 "runtime_error": d.runtime_error or None,
#             }
#             for d in test_diffs
#         ],

#         # The core output: specific logical errors with what/where/why/hint
#         "logical_errors": [
#             {
#                 "error_id": e.error_id,
#                 "severity": e.severity,
#                 "category": e.category,
#                 "what": e.what,
#                 "where": e.where,
#                 "why": e.why,
#                 "hint": e.hint,
#                 "line": e.line,
#                 "code_snippet": e.code_snippet,
#                 "confidence": e.confidence,
#                 "related_test_cases": e.related_test_cases,
#             }
#             for e in logical_errors
#         ],
#         "error_count": len(logical_errors),
#         "has_logical_errors": len(logical_errors) > 0,
#     }


# @app.get("/health")
# def health():
#     return {"status": "ok", "version": "3.0.0"}


"""
Question-Aware Logical Error Detection Engine  v5.0
====================================================
KEY CHANGE from v4: Removed ALL hardcoded OPERATION_KEYWORDS.

Instead of keyword-matching questions to a fixed list of operations,
the LLM now reads the problem statement and derives:
  - What the algorithm MUST do
  - What code structures are REQUIRED
  - What the expected return type is
  - What edge cases exist
  - What a CORRECT solution would look like conceptually

This makes the system open-ended — admins can post ANY question
and the system understands it without any code changes.

Architecture:
  Stage 1 — LLMQuestionAnalyzer    : LLM reads problem → QuestionProfile (open-ended)
  Stage 2 — CodeStructureAnalyzer  : AST → what the student code actually does
  Stage 3 — TestRunner + Differ    : run tests → per-test diagnosis
  Stage 4 — LLMLogicAuditor        : LLM compares (question intent + code + test diffs) → LogicalErrors
  Stage 5 — RAGRetriever           : concept names → retrieved explanation docs
  Stage 6 — LLMExplainer           : (error + retrieved docs + student code) → rich explanation
  Stage 7 — PersonalizationEngine  : learner profile → adapt depth / flag repeats
  Stage 8 — XAI Assembler          : attach confidence, concept path, rule rationale

The LLM is used in TWO distinct roles:
  Role A (Stage 1 & 4) — REASONING: understands the question & detects logical mismatches
  Role B (Stage 6)     — EXPLAINING: takes a detected error and explains it pedagogically

Keeping roles separate prevents explanation hallucinations from contaminating detection.
"""

from __future__ import annotations

from dotenv import load_dotenv
import os

load_dotenv()   # ← This loads the .env file

import re
import ast
import math
import subprocess
import tempfile
import os
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="LLM-Powered Logical Error Detector", version="5.0.0")


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY      = os.environ.get("ANTHROPIC_API_KEY", "")
LLM_MODEL              = "claude-sonnet-4-20250514"
CHROMA_PATH            = "./chroma_store"
PROFILE_PATH           = "./student_profiles.json"
TOP_K_RETRIEVAL        = 3
MAX_ANALYSIS_TOKENS    = 1200   # Stage 1 & 4 — reasoning calls
MAX_EXPLANATION_TOKENS = 700    # Stage 6 — explanation call


# ─────────────────────────────────────────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────────────────────────────────────────

class EvaluationRequest(BaseModel):
    studentId:         int
    questionId:        str
    problem_statement: str          # Any question — no restrictions
    code:              str
    test_cases:        list[dict]   # [{"input": "...", "expected_output": "..."}]
    language:          str = "python"
    difficulty_level:  str = "intermediate"   # beginner / intermediate / advanced


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class QuestionProfile:
    """
    Fully LLM-derived — no keyword lists involved.
    The LLM reads the problem statement and fills every field.
    """
    raw_text:              str
    operation_summary:     str = ""          # e.g. "Find the second largest element in a list"
    required_concepts:     list[str] = field(default_factory=list)   # ["loop", "comparison", "tracking_two_values"]
    required_structures:   list[str] = field(default_factory=list)   # ["loop", "if_condition", "return_statement"]
    expected_return_type:  str = "unknown"   # "single_value" / "boolean" / "list" / "string" / etc.
    input_description:     str = ""          # "A list of integers and a target integer"
    edge_cases:            list[str] = field(default_factory=list)
    correct_approach:      str = ""          # Short English description of the ideal algorithm


@dataclass
class CodeProfile:
    """AST-extracted facts about what the student code actually does."""
    has_loop:             bool = False
    has_nested_loop:      bool = False
    has_recursion:        bool = False
    has_return:           bool = False
    has_if:               bool = False
    has_accumulator:      bool = False
    has_comparison:       bool = False
    has_sort_call:        bool = False
    has_index_access:     bool = False
    loop_count:           int  = 0
    function_count:       int  = 0
    max_nesting_depth:    int  = 0
    accumulator_vars:     list[str] = field(default_factory=list)
    comparison_operators: list[str] = field(default_factory=list)
    called_builtins:      list[str] = field(default_factory=list)
    return_lines:         list[int] = field(default_factory=list)
    defined_functions:    list[str] = field(default_factory=list)


@dataclass
class TestDiff:
    test_index:    int
    input_val:     str
    expected:      str
    actual:        str
    passed:        bool
    match_type:    str
    diff_summary:  str = ""    # Human-readable: "off by 1", "empty output", etc.
    runtime_error: str = ""


@dataclass
class LogicalError:
    """
    Detected by the LLM Logic Auditor (Stage 4).
    Enriched by RAG + LLM Explainer (Stages 5–6).
    """
    error_id:           str
    severity:           str           # critical / warning / info
    category:           str           # algorithm / loop / condition / variable / output / edge_case
    line:               object        # int or None
    code_snippet:       str
    what:               str           # One-line description
    where:              str           # "Line 5" or "Inside the loop"
    why:                str           # Rule-based or LLM reasoning
    hint:               str
    confidence:         float
    concept_path:       list[str] = field(default_factory=list)
    retrieved_docs:     list[str] = field(default_factory=list)
    llm_explanation:    str = ""
    analogy:            str = ""
    adapted_explanation: str = ""
    related_test_cases: list[int] = field(default_factory=list)


@dataclass
class LearnerProfile:
    student_id:       int
    concept_history:  dict[str, list[str]] = field(default_factory=dict)
    misconception_log: list[dict] = field(default_factory=list)
    session_count:    int = 0

    def concept_strength(self, concept: str) -> str:
        history = self.concept_history.get(concept, [])
        if not history:
            return "unknown"
        recent = history[-5:]
        weak_count = recent.count("weak")
        if weak_count >= 3:
            return "weak"
        if weak_count == 0:
            return "strong"
        return "moderate"

    def repeated_errors(self, concept: str) -> int:
        return self.concept_history.get(concept, []).count("weak")

    def record(self, concept: str, outcome: str):
        self.concept_history.setdefault(concept, []).append(outcome)


# ─────────────────────────────────────────────────────────────────────────────
# LLM CLIENT
# ─────────────────────────────────────────────────────────────────────────────

_client: Optional[anthropic.Anthropic] = None

def get_client() -> Optional[anthropic.Anthropic]:
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client

# def llm_call(prompt: str, max_tokens: int) -> str:
#     """Single-turn LLM call. Returns raw text or raises."""
#     client = get_client()
#     if not client:
#         raise RuntimeError("ANTHROPIC_API_KEY not set.")
#     response = client.messages.create(
#         model=LLM_MODEL,
#         max_tokens=max_tokens,
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response.content[0].text.strip()

# Free tier: 14,400 requests/day
# pip install groq
from groq import Groq

_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def llm_call(prompt: str, max_tokens: int) -> str:
    response = _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def parse_json_response(raw: str) -> dict | list:
    """Strip markdown fences and parse JSON."""
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw.strip())


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1 — LLM QUESTION ANALYZER
# Replaces all OPERATION_KEYWORDS, OPERATION_TO_CONCEPTS, etc.
# The LLM reads the raw problem statement and derives everything.
# ─────────────────────────────────────────────────────────────────────────────

QUESTION_ANALYSIS_PROMPT = """You are a CS education expert analyzing a programming problem statement.
Your job is to extract structured information about what a CORRECT solution must do.

=== PROBLEM STATEMENT ===
{problem}

=== YOUR TASK ===
Return a JSON object with exactly these keys:

{{
  "operation_summary": "One sentence: what must the function compute or do?",
  "required_concepts": ["list", "of", "concepts", "the", "solution", "must", "use"],
  "required_structures": ["loop", "if_condition", "return_statement", ...],
  "expected_return_type": "single_value | boolean | list | string | tuple | void",
  "input_description": "What is the input? (e.g. 'a list of integers and a target value')",
  "edge_cases": ["empty input", "single element", "all negatives", "duplicates", ...],
  "correct_approach": "2-3 sentence description of the correct algorithm (pseudocode-level)"
}}

For required_concepts, use programmer-readable names like:
  loop, nested_loop, recursion, accumulator, comparison, tracking_variable,
  two_pointer, hash_map, sorting, string_traversal, modulo, division,
  base_case, stack, queue, set, memoization, bit_manipulation, etc.

Return ONLY the JSON object. No markdown, no explanation."""


def analyze_question_with_llm(problem_statement: str) -> QuestionProfile:
    """
    Stage 1: Use LLM to understand ANY question — no keyword lists needed.
    Falls back to a minimal profile if LLM is unavailable.
    """
    profile = QuestionProfile(raw_text=problem_statement)

    try:
        raw = llm_call(
            QUESTION_ANALYSIS_PROMPT.format(problem=problem_statement),
            max_tokens=MAX_ANALYSIS_TOKENS
        )
        data = parse_json_response(raw)

        profile.operation_summary    = data.get("operation_summary", "")
        profile.required_concepts    = data.get("required_concepts", [])
        profile.required_structures  = data.get("required_structures", [])
        profile.expected_return_type = data.get("expected_return_type", "unknown")
        profile.input_description    = data.get("input_description", "")
        profile.edge_cases           = data.get("edge_cases", [])
        profile.correct_approach     = data.get("correct_approach", "")

    except Exception as e:
        print(f"[Stage1] LLM question analysis failed: {e}. Using minimal profile.")
        # Graceful fallback: populate what we can from the raw text
        profile.operation_summary   = problem_statement[:120]
        profile.required_concepts   = ["loop", "condition", "return"]
        profile.required_structures = ["loop", "if_condition", "return_statement"]

    return profile


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2 — CODE STRUCTURE ANALYZER (AST — unchanged, no keyword dependency)
# ─────────────────────────────────────────────────────────────────────────────

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
            profile.defined_functions.append(node.name)
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == node.name:
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


def code_structure_summary(profile: CodeProfile) -> str:
    """Convert CodeProfile to a readable string for LLM prompts."""
    parts = []
    if profile.has_loop:
        parts.append(f"{profile.loop_count} loop(s), max nesting depth {profile.max_nesting_depth}")
    else:
        parts.append("no loops")
    if profile.has_recursion:
        parts.append("uses recursion")
    if profile.has_accumulator:
        parts.append(f"accumulator variables: {profile.accumulator_vars}")
    else:
        parts.append("no accumulator (+=) found")
    if profile.has_comparison:
        parts.append(f"comparison operators used: {profile.comparison_operators}")
    else:
        parts.append("no comparisons found")
    parts.append("has return: " + str(profile.has_return))
    if profile.has_if:
        parts.append("has if-conditions")
    else:
        parts.append("no if-conditions")
    if profile.called_builtins:
        parts.append(f"builtins called: {list(set(profile.called_builtins))}")
    if profile.defined_functions:
        parts.append(f"functions defined: {profile.defined_functions}")
    return "; ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 3 — TEST RUNNER + OUTPUT DIFFER
# ─────────────────────────────────────────────────────────────────────────────

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
            ["python3", path], input=stdin_input,
            capture_output=True, text=True, timeout=5
        )
        os.remove(path)
        return {"output": result.stdout.strip(), "error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Execution timed out"}
    except Exception as e:
        return {"output": "", "error": str(e)}


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
    a_set = {ln.strip() for ln in actual.strip().splitlines() if ln.strip()}
    e_set = {ln.strip() for ln in expected.strip().splitlines() if ln.strip()}
    if a_set == e_set:
        return True, "unordered_lines"
    return False, "failed"


def classify_diff(expected: str, actual: str) -> str:
    """Return a short label describing HOW the output is wrong."""
    exp, act = expected.strip(), actual.strip()
    if not act:
        return "empty_output"
    if any(kw in act.lower() for kw in ["error", "traceback", "exception"]):
        return "runtime_error"
    try:
        e, a = float(exp), float(act)
        if abs(a - e) == 1:
            return "off_by_one"
        if e != 0 and a == -e:
            return "wrong_sign"
        if a == 0 and e != 0:
            return "zero_when_nonzero"
        if math.isclose(a, e * 2, rel_tol=0.05):
            return "double_expected"
        if math.isclose(a, e / 2, rel_tol=0.05):
            return "half_expected"
        return "wrong_numeric_value"
    except (ValueError, TypeError):
        pass
    if act == exp[::-1]:
        return "reversed_output"
    if exp.lower() == act.lower():
        return "case_mismatch"
    return "wrong_output"


def run_tests(code: str, test_cases: list[dict]) -> list[TestDiff]:
    diffs = []
    for i, tc in enumerate(test_cases):
        result   = execute_code(code, tc.get("input", ""))
        actual   = result["output"]
        expected = tc.get("expected_output", "").strip()
        passed, match_type = smart_compare(actual, expected)
        diff_summary = "" if passed else classify_diff(expected, actual)
        diffs.append(TestDiff(
            test_index=i, input_val=tc.get("input", ""),
            expected=expected, actual=actual,
            passed=passed, match_type=match_type,
            diff_summary=diff_summary,
            runtime_error=result.get("error", "")
        ))
    return diffs


def build_test_diff_summary(diffs: list[TestDiff]) -> str:
    """Compact text summary of test results for the LLM prompt."""
    lines = []
    for d in diffs:
        status = "PASS" if d.passed else "FAIL"
        line = f"  Test {d.test_index+1}: {status}"
        if not d.passed:
            line += (
                f" | input={repr(d.input_val[:60])}"
                f" | expected={repr(d.expected[:40])}"
                f" | got={repr(d.actual[:40])}"
                f" | pattern={d.diff_summary}"
            )
            if d.runtime_error:
                line += f" | runtime_error={d.runtime_error[:80]}"
        lines.append(line)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 4 — LLM LOGIC AUDITOR
# This is the core Phase 2 engine. The LLM:
#   - Knows what the question REQUIRES (from Stage 1)
#   - Knows what the code DOES (from Stage 2 AST)
#   - Knows HOW the outputs differ (from Stage 3)
#   - Reasons about the GAP between requirement and implementation
# ─────────────────────────────────────────────────────────────────────────────

LOGIC_AUDIT_PROMPT = """You are a CS education expert auditing a student's code for LOGICAL errors.

You have been given:
1. The problem statement (what the code must do)
2. An analysis of what the problem requires (from a CS expert)
3. An AST-based analysis of what the student code actually does
4. The student's raw code
5. Test results showing exactly where the code fails

Your job: identify every LOGICAL error — places where the student's understanding or
implementation is fundamentally wrong. Focus on WHY it fails, not just THAT it fails.

Do NOT report style issues, variable naming, or efficiency problems.
Only report errors that directly cause incorrect output.

=== PROBLEM STATEMENT ===
{problem}

=== WHAT THIS PROBLEM REQUIRES (Expert Analysis) ===
Operation: {operation_summary}
Required concepts: {required_concepts}
Required code structures: {required_structures}
Expected return type: {expected_return_type}
Input: {input_description}
Edge cases: {edge_cases}
Correct approach: {correct_approach}

=== WHAT THE STUDENT CODE ACTUALLY DOES (AST Analysis) ===
{code_structure}

=== STUDENT CODE ===
{code}

=== TEST RESULTS ===
{test_summary}

=== YOUR TASK ===
Return a JSON array. Each element is one logical error:

[
  {{
    "error_id": "LE-001",
    "severity": "critical | warning | info",
    "category": "algorithm | loop | condition | variable | output | edge_case",
    "line": <line number as integer, or null if not pinpointable>,
    "what": "One sentence: what is wrong?",
    "where": "e.g. 'Line 12 inside the for loop' or 'Return statement at end of function'",
    "why": "2-3 sentences: WHY this causes the observed failure. Reference the test results.",
    "hint": "One actionable sentence: how to fix it.",
    "confidence": <0.0 to 1.0>,
    "concept_path": ["primary_concept", "sub_concept"],
    "related_test_cases": [<0-indexed list of failing test indices>]
  }}
]

Rules:
- If ALL tests pass, return an empty array: []
- List errors from most critical to least critical
- Be specific about line numbers when you can see them in the code
- The "why" must connect to actual test failures — don't guess blindly
- concept_path should use programmer terms: loop, accumulator, comparison, recursion,
  base_case, return, condition, initialization, boundary, division, modulo, etc.

Return ONLY the JSON array. No markdown, no explanation outside the JSON."""


def detect_errors_with_llm(
    question:      QuestionProfile,
    code_profile:  CodeProfile,
    test_diffs:    list[TestDiff],
    code:          str,
) -> list[LogicalError]:
    """
    Stage 4: LLM-powered logical error detection.
    No hardcoded rules — works for any question.
    """
    failed = [d for d in test_diffs if not d.passed]
    if not failed:
        return []

    prompt = LOGIC_AUDIT_PROMPT.format(
        problem          = question.raw_text,
        operation_summary= question.operation_summary,
        required_concepts= ", ".join(question.required_concepts),
        required_structures= ", ".join(question.required_structures),
        expected_return_type= question.expected_return_type,
        input_description= question.input_description,
        edge_cases       = ", ".join(question.edge_cases) if question.edge_cases else "none specified",
        correct_approach = question.correct_approach,
        code_structure   = code_structure_summary(code_profile),
        code             = code,
        test_summary     = build_test_diff_summary(test_diffs),
    )

    code_lines = code.splitlines()

    def snippet(line, ctx=1):
        if not line or line < 1:
            return ""
        start = max(0, line - 1 - ctx)
        end   = min(len(code_lines), line + ctx)
        return "\n".join(f"  {start+i+1}: {ln}" for i, ln in enumerate(code_lines[start:end]))

    try:
        raw  = llm_call(prompt, max_tokens=MAX_ANALYSIS_TOKENS)
        data = parse_json_response(raw)

        errors = []
        failed_indices = [d.test_index for d in failed]

        for i, item in enumerate(data):
            line = item.get("line")
            if isinstance(line, float):
                line = int(line)

            errors.append(LogicalError(
                error_id       = item.get("error_id", f"LE-{i+1:03d}"),
                severity       = item.get("severity", "warning"),
                category       = item.get("category", "algorithm"),
                line           = line,
                code_snippet   = snippet(line),
                what           = item.get("what", ""),
                where          = item.get("where", ""),
                why            = item.get("why", ""),
                hint           = item.get("hint", ""),
                confidence     = float(item.get("confidence", 0.75)),
                concept_path   = item.get("concept_path", []),
                related_test_cases = item.get("related_test_cases", failed_indices),
            ))

        # Sort: critical first, then by confidence descending
        order = {"critical": 0, "warning": 1, "info": 2}
        errors.sort(key=lambda e: (order.get(e.severity, 3), -e.confidence))
        return errors

    except Exception as e:
        print(f"[Stage4] LLM error detection failed: {e}")
        # Return a minimal fallback error so the student gets some feedback
        return [LogicalError(
            error_id="LE-FALLBACK", severity="warning", category="algorithm",
            line=None, code_snippet="",
            what="Could not fully analyze — tests are failing.",
            where="Unknown",
            why=f"The automated analyzer encountered an issue ({type(e).__name__}). "
                f"Tests failed with: {[d.diff_summary for d in failed[:3]]}",
            hint="Review your code manually against each failing test case.",
            confidence=0.5,
            concept_path=["unknown"],
            related_test_cases=[d.test_index for d in failed],
        )]


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 5 — RAG RETRIEVER (concept knowledge base)
# ─────────────────────────────────────────────────────────────────────────────

CONCEPT_KB: list[dict] = [
    {
        "id": "loop_boundary",
        "concept": "Loop Boundary / Off-by-One",
        "explanation": (
            "A loop boundary error happens when a loop runs one iteration too many or too few. "
            "In Python, `range(n)` produces 0..n-1 (n items). Always ask: does my loop start "
            "at the right index? Does it include or exclude the last element?"
        ),
        "example": "for i in range(len(arr)):      # correct\nfor i in range(1, len(arr)):   # skips index 0!",
        "tags": "loop boundary off-by-one range index iteration",
    },
    {
        "id": "accumulator_reset",
        "concept": "Accumulator Reset Inside Loop",
        "explanation": (
            "An accumulator builds a result across iterations (total += x). "
            "If you reset it (total = 0) INSIDE the loop, each iteration wipes prior work. "
            "Always initialize the accumulator BEFORE the loop."
        ),
        "example": "# Wrong:\nfor x in arr:\n    total = 0\n    total += x\n\n# Correct:\ntotal = 0\nfor x in arr:\n    total += x",
        "tags": "accumulator sum loop variable reset initialization",
    },
    {
        "id": "wrong_comparison",
        "concept": "Wrong Comparison Operator",
        "explanation": (
            "Tracking a maximum requires > (update when element is greater). "
            "Tracking a minimum requires < (update when element is smaller). "
            "Flipping the operator tracks the opposite extreme. "
            "Also check initialization — using 0 instead of arr[0] breaks for all-negative inputs."
        ),
        "example": "# Finding max — WRONG:\nif element < current_max:\n    current_max = element\n# Correct:\nif element > current_max:\n    current_max = element",
        "tags": "comparison operator max min greater less tracker initialization",
    },
    {
        "id": "missing_base_case",
        "concept": "Missing Base Case in Recursion",
        "explanation": (
            "Every recursive function needs a base case — a condition that stops the recursion. "
            "Without it, the function calls itself forever until Python raises RecursionError. "
            "The base case handles the smallest possible input."
        ),
        "example": "def factorial(n):\n    if n == 0:  # base case\n        return 1\n    return n * factorial(n-1)",
        "tags": "recursion base case infinite stack overflow stopping condition",
    },
    {
        "id": "early_return",
        "concept": "Early Return Inside Loop",
        "explanation": (
            "A `return` directly in a loop body (not inside an `if`) exits after the first iteration. "
            "For aggregation operations (sum, max, count), the `return` must come AFTER the loop."
        ),
        "example": "# Wrong:\nfor x in arr:\n    total += x\n    return total  # exits after 1st element!\n\n# Correct:\nfor x in arr:\n    total += x\nreturn total",
        "tags": "return loop early exit iteration scope",
    },
    {
        "id": "missing_return",
        "concept": "Missing Return Statement",
        "explanation": (
            "A function without `return` implicitly returns None. "
            "The caller receives None instead of the expected value, causing silent bugs or crashes downstream."
        ),
        "example": "def find_max(arr):\n    best = arr[0]\n    for x in arr:\n        if x > best: best = x\n    return best  # required!",
        "tags": "return None function output missing result",
    },
    {
        "id": "missing_division",
        "concept": "Missing Division (e.g. for Average)",
        "explanation": (
            "The average is sum / count. A common mistake is returning the sum without dividing. "
            "Similarly, percentage, ratio, and rate calculations all require a division step."
        ),
        "example": "return total / len(arr)  # correct\nreturn total              # wrong — returns sum",
        "tags": "average mean division sum count arithmetic ratio percentage",
    },
    {
        "id": "modulo_check",
        "concept": "Divisibility Check with Modulo (%)",
        "explanation": (
            "Use `n % d == 0` to check if d divides n evenly. "
            "This is used in prime checking, even/odd detection, FizzBuzz, GCD, and cyclic patterns."
        ),
        "example": "if n % 2 == 0:      # even\nif n % i == 0:      # divisible by i → not prime",
        "tags": "modulo divisibility remainder prime even odd gcd",
    },
    {
        "id": "two_pointer_swap",
        "concept": "Two-Variable / Two-Pointer Pattern",
        "explanation": (
            "Many problems require tracking two values simultaneously — e.g. fibonacci (prev + curr), "
            "or two pointers for reversing a list. Python's simultaneous assignment `a, b = b, a+b` "
            "is the safest way to do this without temporary variables."
        ),
        "example": "a, b = 0, 1\nfor _ in range(n):\n    a, b = b, a + b",
        "tags": "two pointer fibonacci swap simultaneous update variables",
    },
    {
        "id": "integer_division",
        "concept": "Integer vs Float Division",
        "explanation": (
            "In Python 3, `/` always returns a float. `//` returns an integer (floor). "
            "Using `/` for an index (e.g. in binary search midpoint) causes a TypeError. "
            "Use `//` whenever the result will be used as a list index."
        ),
        "example": "mid = (left + right) // 2   # correct — int\nmid = (left + right) / 2    # wrong — float, crashes as index",
        "tags": "integer division float floor binary search index midpoint",
    },
    {
        "id": "missing_condition",
        "concept": "Missing Condition in Loop",
        "explanation": (
            "Counting, filtering, or searching requires an `if` condition inside the loop. "
            "Without it, every element is processed identically — e.g. every element is counted "
            "instead of only the matching ones."
        ),
        "example": "# Wrong — counts everything:\nfor x in arr:\n    count += 1\n\n# Correct:\nfor x in arr:\n    if x == target:\n        count += 1",
        "tags": "condition if loop filter count search match",
    },
    {
        "id": "wrong_initialization",
        "concept": "Wrong Variable Initialization",
        "explanation": (
            "The starting value of a tracking variable matters. Initializing a max-tracker to 0 "
            "fails when all inputs are negative. Initializing a product-accumulator to 0 (instead of 1) "
            "always returns 0. Match the identity element to the operation: 0 for sum, 1 for product, "
            "arr[0] for max/min."
        ),
        "example": "product = 1  # correct identity for multiplication\nproduct = 0  # wrong — result always 0",
        "tags": "initialization variable tracker identity element product sum max min",
    },
    {
        "id": "nested_loop_required",
        "concept": "Nested Loop Requirement",
        "explanation": (
            "Some algorithms inherently require nested loops: bubble sort, selection sort, "
            "matrix traversal, checking all pairs. A single loop only visits each element once "
            "and cannot compare or correlate pairs of elements."
        ),
        "example": "for i in range(len(arr)):\n    for j in range(i+1, len(arr)):\n        if arr[i] > arr[j]:\n            arr[i], arr[j] = arr[j], arr[i]",
        "tags": "nested loop pairs matrix comparison sort bubble selection",
    },
    {
        "id": "string_immutability",
        "concept": "String Immutability in Python",
        "explanation": (
            "Python strings are immutable — you cannot modify them in place (e.g. s[i] = 'x' raises TypeError). "
            "Build a new string by concatenation or join, or convert to a list first."
        ),
        "example": "# Wrong:\ns[0] = 'A'\n\n# Correct:\ns = list(s)\ns[0] = 'A'\ns = ''.join(s)",
        "tags": "string immutable modify index concatenation list join",
    },
    {
        "id": "index_out_of_bounds",
        "concept": "Index Out of Bounds",
        "explanation": (
            "Accessing arr[i] when i >= len(arr) raises IndexError. "
            "Common causes: off-by-one in loop range, not checking length before access, "
            "or assuming the list is non-empty without a guard."
        ),
        "example": "# Safe access:\nif i < len(arr):\n    val = arr[i]",
        "tags": "index out of bounds list array length guard range",
    },
]


class RAGRetriever:
    def __init__(self):
        self._available = False
        self._collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            ef = embedding_functions.DefaultEmbeddingFunction()
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            self._collection = client.get_or_create_collection(
                name="concepts",
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"}
            )
            if self._collection.count() == 0:
                self._seed()
            self._available = True
        except Exception as e:
            print(f"[RAG] ChromaDB init failed ({e}). Using keyword fallback.")

    def _seed(self):
        docs, ids, metas = [], [], []
        for entry in CONCEPT_KB:
            text = f"{entry['concept']}\n\n{entry['explanation']}\n\nExample:\n{entry['example']}"
            docs.append(text)
            ids.append(entry["id"])
            metas.append({"concept": entry["concept"], "tags": entry["tags"]})
        self._collection.add(documents=docs, ids=ids, metadatas=metas)

    def retrieve(self, query: str, k: int = TOP_K_RETRIEVAL) -> list[str]:
        if self._available and self._collection:
            try:
                n = min(k, self._collection.count())
                results = self._collection.query(query_texts=[query], n_results=n)
                return results["documents"][0] if results["documents"] else []
            except Exception as e:
                print(f"[RAG] Query failed ({e}). Falling back to keyword search.")

        # Keyword fallback
        query_tokens = set(query.lower().split())
        scored = []
        for entry in CONCEPT_KB:
            tags = set(entry["tags"].split())
            score = len(query_tokens & tags)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda x: -x[0])
        return [
            f"{e['concept']}\n\n{e['explanation']}\n\nExample:\n{e['example']}"
            for _, e in scored[:k]
        ]


_rag = RAGRetriever()


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 6 — LLM EXPLAINER (pedagogical, not detection)
# ─────────────────────────────────────────────────────────────────────────────

DIFFICULTY_INSTRUCTIONS = {
    "beginner": (
        "The student is a beginner. Use simple everyday language. "
        "Avoid jargon. Use a real-world analogy to make the concept memorable. "
        "Be patient and encouraging."
    ),
    "intermediate": (
        "The student has basic programming knowledge. "
        "Be clear and precise. A short analogy is helpful but not required."
    ),
    "advanced": (
        "The student is experienced. Be concise and technical. "
        "Skip analogies. Focus on edge cases and precise fix."
    ),
}

EXPLAIN_PROMPT = """You are an expert CS tutor. A student's code has a logical error that was
already detected by an automated system. Your ONLY job is to EXPLAIN it clearly.
Do NOT detect new errors. Do NOT rewrite the code.

=== DETECTED ERROR ===
What: {what}
Where: {where}
Category: {category}
Concept path: {concept_path}

=== STUDENT CODE SNIPPET ===
{snippet}

=== RETRIEVED KNOWLEDGE FROM CONCEPT DATABASE ===
{retrieved}

=== DIFFICULTY LEVEL ===
{difficulty_instruction}
{repeat_note}

=== YOUR TASK ===
Return a JSON object with exactly these keys:
{{
  "explanation": "2-4 sentences explaining WHY this error occurs and HOW to fix it. Ground it in the retrieved knowledge.",
  "analogy": "1 sentence real-world analogy (or empty string for advanced students)."
}}

Return ONLY the JSON. No markdown, no preamble."""


def explain_error_with_llm(
    error:          LogicalError,
    retrieved_docs: list[str],
    difficulty:     str = "intermediate",
    repeated_times: int = 0,
) -> tuple[str, str]:
    """Returns (explanation, analogy). Falls back to error.why on failure."""
    client = get_client()
    if not client:
        return error.why, ""

    repeat_note = ""
    if repeated_times >= 2:
        repeat_note = (
            f"\nIMPORTANT: The student has made this same type of error {repeated_times} times before. "
            "Provide extra detail, an additional worked example, and suggest a specific practice exercise."
        )

    retrieved_text = "\n\n---\n\n".join(retrieved_docs) if retrieved_docs else "No additional context."

    prompt = EXPLAIN_PROMPT.format(
        what                  = error.what,
        where                 = error.where,
        category              = error.category,
        concept_path          = " → ".join(error.concept_path),
        snippet               = error.code_snippet or "(no snippet available)",
        retrieved             = retrieved_text,
        difficulty_instruction= DIFFICULTY_INSTRUCTIONS.get(difficulty, DIFFICULTY_INSTRUCTIONS["intermediate"]),
        repeat_note           = repeat_note,
    )

    try:
        raw  = llm_call(prompt, max_tokens=MAX_EXPLANATION_TOKENS)
        data = parse_json_response(raw)
        return data.get("explanation", error.why), data.get("analogy", "")
    except Exception as e:
        print(f"[Stage6] LLM explanation failed ({e}). Using fallback.")
        return error.why, ""


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 7 — PERSONALIZATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class PersonalizationEngine:
    def __init__(self, profile_path: str = PROFILE_PATH):
        self.path = Path(profile_path)
        self._profiles: dict[int, LearnerProfile] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text())
                for sid, data in raw.items():
                    p = LearnerProfile(student_id=int(sid))
                    p.concept_history   = data.get("concept_history", {})
                    p.misconception_log = data.get("misconception_log", [])
                    p.session_count     = data.get("session_count", 0)
                    self._profiles[int(sid)] = p
            except Exception as e:
                print(f"[Personalization] Load failed: {e}")

    def _save(self):
        try:
            out = {
                str(sid): {
                    "concept_history":   p.concept_history,
                    "misconception_log": p.misconception_log,
                    "session_count":     p.session_count,
                }
                for sid, p in self._profiles.items()
            }
            self.path.write_text(json.dumps(out, indent=2))
        except Exception as e:
            print(f"[Personalization] Save failed: {e}")

    def get_profile(self, student_id: int) -> LearnerProfile:
        if student_id not in self._profiles:
            self._profiles[student_id] = LearnerProfile(student_id=student_id)
        return self._profiles[student_id]

    def record_session(self, student_id: int, errors: list[LogicalError]):
        profile = self.get_profile(student_id)
        profile.session_count += 1
        for err in errors:
            for concept in err.concept_path:
                profile.record(concept, "weak")
            profile.misconception_log.append({
                "timestamp":    int(time.time()),
                "error_id":     err.error_id,
                "concept_path": err.concept_path,
            })
        self._save()

    def record_pass(self, student_id: int, concepts: list[str]):
        profile = self.get_profile(student_id)
        for concept in concepts:
            profile.record(concept, "strong")
        self._save()

    def build_summary(self, student_id: int) -> dict:
        profile = self.get_profile(student_id)
        strengths  = [c for c in profile.concept_history if profile.concept_strength(c) == "strong"]
        weaknesses = [c for c in profile.concept_history if profile.concept_strength(c) == "weak"]
        moderate   = [c for c in profile.concept_history if profile.concept_strength(c) == "moderate"]
        return {
            "session_count": profile.session_count,
            "strengths":  strengths,
            "weaknesses": weaknesses,
            "moderate":   moderate,
            "repeated_misconceptions": [
                {"concept": c, "times": profile.repeated_errors(c)}
                for c in weaknesses if profile.repeated_errors(c) >= 2
            ],
        }


_personalization = PersonalizationEngine()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/analyze")
def evaluate(request: EvaluationRequest):

    # Safety gate
    safety_issues = check_safety(request.code)
    if safety_issues:
        raise HTTPException(status_code=400, detail={
            "error": "Code blocked.", "issues": safety_issues
        })

    # ── Stage 1: LLM understands the question ───────────────────────────────
    q_profile = analyze_question_with_llm(request.problem_statement)

    # ── Stage 2: AST understands the code ───────────────────────────────────
    c_profile  = analyze_code_structure(request.code)

    # ── Stage 3: Run tests, collect diffs ───────────────────────────────────
    test_diffs = run_tests(request.code, request.test_cases)

    # ── Stage 4: LLM detects logical errors ─────────────────────────────────
    errors = detect_errors_with_llm(q_profile, c_profile, test_diffs, request.code)

    # ── Stages 5–7: RAG + LLM Explain + Personalization per error ───────────
    learner = _personalization.get_profile(request.studentId)

    for err in errors:
        # Stage 5: retrieve relevant concept docs
        rag_query = " ".join(err.concept_path) + " " + err.category + " " + err.what
        docs = _rag.retrieve(rag_query, k=TOP_K_RETRIEVAL)
        err.retrieved_docs = docs

        # How many times has this student hit this concept before?
        repeated = max(
            (learner.repeated_errors(c) for c in err.concept_path),
            default=0
        )

        # Stage 6: LLM explains the error
        explanation, analogy = explain_error_with_llm(
            error=err,
            retrieved_docs=docs,
            difficulty=request.difficulty_level,
            repeated_times=repeated,
        )
        err.llm_explanation = explanation
        err.analogy         = analogy

        # Stage 7: personalization — flag repeated issues
        if repeated >= 2:
            err.adapted_explanation = (
                f"[Repeated Issue — seen {repeated}x] {explanation} "
                "Consider revisiting this concept with additional practice problems."
            )
        else:
            err.adapted_explanation = explanation

    # Record outcomes in learner profile
    if errors:
        _personalization.record_session(request.studentId, errors)
    else:
        _personalization.record_pass(request.studentId, q_profile.required_concepts)

    passed_count = sum(1 for d in test_diffs if d.passed)

    return {
        "studentId":  request.studentId,
        "questionId": request.questionId,

        # What the LLM understood about this question
        "question_analysis": {
            "operation_summary":    q_profile.operation_summary,
            "required_concepts":    q_profile.required_concepts,
            "required_structures":  q_profile.required_structures,
            "expected_return_type": q_profile.expected_return_type,
            "input_description":    q_profile.input_description,
            "edge_cases":           q_profile.edge_cases,
            "correct_approach":     q_profile.correct_approach,
        },

        # What the student code actually does (AST facts)
        "code_analysis": {
            "has_loop":           c_profile.has_loop,
            "has_recursion":      c_profile.has_recursion,
            "has_accumulator":    c_profile.has_accumulator,
            "has_comparison":     c_profile.has_comparison,
            "has_return":         c_profile.has_return,
            "loop_count":         c_profile.loop_count,
            "max_nesting_depth":  c_profile.max_nesting_depth,
            "accumulator_vars":   c_profile.accumulator_vars,
            "defined_functions":  c_profile.defined_functions,
        },

        # Test execution results
        "test_summary": {
            "passed":     passed_count,
            "total":      len(test_diffs),
            "score":      f"{passed_count}/{len(test_diffs)}",
            "all_passed": passed_count == len(test_diffs),
        },
        "test_results": [
            {
                "test_case":     d.test_index + 1,
                "input":         d.input_val,
                "expected":      d.expected,
                "actual":        d.actual,
                "passed":        d.passed,
                "diff_pattern":  d.diff_summary,
                "runtime_error": d.runtime_error or None,
            }
            for d in test_diffs
        ],

        # Core output — fully enriched logical errors
        "logical_errors": [
            {
                "error_id":  e.error_id,
                "severity":  e.severity,
                "category":  e.category,
                "line":      e.line,
                "code_snippet": e.code_snippet,
                "what":      e.what,
                "where":     e.where,
                "why":       e.why,
                "hint":      e.hint,
                "confidence": e.confidence,
                # XAI
                "xai": {
                    "concept_path":        e.concept_path,
                    "confidence":          e.confidence,
                    "retrieved_doc_count": len(e.retrieved_docs),
                },
                # LLM-enriched explanation
                "llm_explanation":    e.llm_explanation,
                "analogy":            e.analogy,
                "adapted_explanation": e.adapted_explanation,
                "related_test_cases": e.related_test_cases,
            }
            for e in errors
        ],
        "error_count":       len(errors),
        "has_logical_errors": len(errors) > 0,

        # Learner profile summary
        "learner_profile": _personalization.build_summary(request.studentId),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN / UTILITY ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/student/{student_id}/profile")
def get_student_profile(student_id: int):
    return _personalization.build_summary(student_id)


@app.post("/rag/seed")
def reseed_rag():
    """Force re-seed the concept vector DB."""
    try:
        _rag._seed()
        return {"status": "ok", "concepts_loaded": len(CONCEPT_KB)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {
        "status":          "ok",
        "version":         "5.0.0",
        "llm_available":   bool(ANTHROPIC_API_KEY),
        "rag_available":   _rag._available,
        "concepts_in_kb":  len(CONCEPT_KB),
    }