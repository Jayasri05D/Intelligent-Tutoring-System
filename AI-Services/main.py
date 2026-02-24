from fastapi import FastAPI
from pydantic import BaseModel
from tree_sitter import Parser
from tree_sitter_languages import get_language

app = FastAPI()

# -------- Request Model -------
class CodeRequest(BaseModel):
    studentId: int
    language: str
    code: str


# -------- Tree-sitter Setup --------
PY_LANGUAGE = get_language("python")
parser = Parser()
parser.set_language(PY_LANGUAGE)

# -------- Builtins (avoid false positives) --------
BUILTINS = {"print", "range", "True", "False", "len", "int", "str"}

# =========================================================
# CONCEPT MAP (Separate from rules)
# =========================================================
CONCEPT_MAP = {
    "R-LOOP-BOUNDARY-01": "Loops → Boundary",
    "R-LOOP-INFINITE-01": "Loops → Termination",
    "R-REC-BASE-01": "Recursion → Base Case",
    "R-VAR-INIT-01": "Variables → Initialization"
}

# =========================================================
# FEEDBACK TEMPLATES (Pedagogical Layer)
# =========================================================
FEEDBACK_TEMPLATES = {
    "R-LOOP-BOUNDARY-01": {
        "violated_principle": "Incorrect termination condition",
        "explanation": "Loop uses n+1 which may cause an extra iteration.",
        "why_it_matters": "This can cause index out-of-bounds errors."
    },
    "R-LOOP-INFINITE-01": {
        "violated_principle": "Infinite loop without termination",
        "explanation": "The loop condition is always True and no break is found.",
        "why_it_matters": "This may cause the program to run indefinitely."
    },
    "R-REC-BASE-01": {
        "violated_principle": "Missing base condition",
        "explanation": "Recursive function does not define a base case.",
        "why_it_matters": "This may lead to infinite recursion."
    },
    "R-VAR-INIT-01": {
        "violated_principle": "Variable used before assignment",
        "explanation": "A variable is referenced before being assigned.",
        "why_it_matters": "Using uninitialized variables causes runtime errors."
    }
}

# =========================================================
# LOOP BOUNDARY DETECTION
# =========================================================
def detect_loop_boundary_issue(node, violations):

    if node.type == "for_statement":
        iterable = node.child_by_field_name("right")

        if iterable and iterable.type == "call":
            function_name = iterable.child_by_field_name("function")

            if function_name and function_name.text.decode() == "range":
                arguments = iterable.child_by_field_name("arguments")

                if arguments:
                    args = [child for child in arguments.children if child.type != ","]

                    for arg in args:
                        if arg.type == "binary_operator":
                            right = arg.child_by_field_name("right")
                            operator = arg.child_by_field_name("operator")

                            if (
                                operator
                                and operator.text.decode() == "+"
                                and right
                                and right.text.decode() == "1"
                            ):
                                violations.append({
                                    "rule_id": "R-LOOP-BOUNDARY-01",
                                    "line": node.start_point[0] + 1,
                                    "confidence": 0.92
                                })

    for child in node.children:
        detect_loop_boundary_issue(child, violations)


# =========================================================
# INFINITE LOOP DETECTION
# =========================================================
def contains_break(node):
    if node.type == "break_statement":
        return True
    for child in node.children:
        if contains_break(child):
            return True
    return False


def detect_infinite_while(node, violations):

    if node.type == "while_statement":
        condition = node.child_by_field_name("condition")
        body = node.child_by_field_name("body")

        if condition and condition.text.decode() == "True":
            if body and not contains_break(body):
                violations.append({
                    "rule_id": "R-LOOP-INFINITE-01",
                    "line": node.start_point[0] + 1,
                    "confidence": 0.96
                })

    for child in node.children:
        detect_infinite_while(child, violations)


# =========================================================
# RECURSION WITHOUT BASE CASE
# =========================================================
def detect_missing_base_case(node, violations):

    if node.type == "function_definition":
        function_name_node = node.child_by_field_name("name")
        body = node.child_by_field_name("body")

        if function_name_node and body:
            function_name = function_name_node.text.decode()

            has_recursive_call = False
            has_if_condition = False

            for child in body.children:
                if child.type == "if_statement":
                    has_if_condition = True

                if function_name in child.text.decode():
                    has_recursive_call = True

            if has_recursive_call and not has_if_condition:
                violations.append({
                    "rule_id": "R-REC-BASE-01",
                    "line": node.start_point[0] + 1,
                    "confidence": 0.88
                })

    for child in node.children:
        detect_missing_base_case(child, violations)


# =========================================================
# VARIABLE USED BEFORE ASSIGNMENT
# =========================================================
def detect_uninitialized_variable(node, violations, assigned_vars=None):

    if assigned_vars is None:
        assigned_vars = set()

    if node.type == "assignment":
        left = node.child_by_field_name("left")
        if left:
            assigned_vars.add(left.text.decode())

    if node.type == "identifier":
        var_name = node.text.decode()

        if var_name not in assigned_vars and var_name not in BUILTINS:
            violations.append({
                "rule_id": "R-VAR-INIT-01",
                "line": node.start_point[0] + 1,
                "confidence": 0.85
            })

    for child in node.children:
        detect_uninitialized_variable(child, violations, assigned_vars)


# =========================================================
# CONCEPT MAPPER
# =========================================================
def map_concepts(violations):
    for v in violations:
        v["concept"] = CONCEPT_MAP.get(v["rule_id"], "Unknown Concept")
    return violations


# =========================================================
# FEEDBACK GENERATOR
# =========================================================
def generate_feedback(violations):
    for v in violations:
        template = FEEDBACK_TEMPLATES.get(v["rule_id"])
        if template:
            v.update(template)
    return violations


# =========================================================
# REMOVE DUPLICATES
# =========================================================
def remove_duplicate_violations(violations):
    unique = []
    seen = set()

    for v in violations:
        key = (v["rule_id"], v["line"])
        if key not in seen:
            seen.add(key)
            unique.append(v)

    return unique


# =========================================================
# ANALYZE ENDPOINT
# =========================================================
@app.post("/analyze")
def analyze_code(request: CodeRequest):

    tree = parser.parse(bytes(request.code, "utf8"))
    root = tree.root_node

    violations = []

    detect_loop_boundary_issue(root, violations)
    detect_infinite_while(root, violations)
    detect_missing_base_case(root, violations)
    detect_uninitialized_variable(root, violations)

    violations = remove_duplicate_violations(violations)
    violations = map_concepts(violations)
    violations = generate_feedback(violations)

    return {
        "studentId": request.studentId,
        "has_syntax_error": root.has_error,
        "violations": violations
    }