
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


# -------- Helper: Extract For Loops --------
def detect_loop_boundary_issue(node, violations):

    if node.type == "for_statement":

        iterable = node.child_by_field_name("right")

        if iterable and iterable.type == "call":

            function_name = iterable.child_by_field_name("function")

            if function_name and function_name.text.decode() == "range":

                arguments = iterable.child_by_field_name("arguments")

                if arguments:

                    # Extract argument expressions
                    args = [child for child in arguments.children if child.type != ","]

                    for arg in args:
                        if arg.type == "binary_operator":

                            left = arg.child_by_field_name("left")
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
                                    "concept": "Loops → Boundary",
                                    "violated_principle": "Incorrect termination condition",
                                    "explanation": "Loop uses n+1 which may cause an extra iteration.",
                                    "why_it_matters": "This can cause index out-of-bounds errors.",
                                    "line": node.start_point[0] + 1,
                                    "confidence": 0.92
                                })

    for child in node.children:
        detect_loop_boundary_issue(child, violations)

#--- detect infinite while ---#
def detect_infinite_while(node, violations):

    if node.type == "while_statement":

        condition = node.child_by_field_name("condition")

        if condition and condition.text.decode() == "True":

            violations.append({
                "rule_id": "R-LOOP-INFINITE-01",
                "concept": "Loops → Termination",
                "violated_principle": "Infinite loop without termination",
                "explanation": "The loop condition is always True.",
                "why_it_matters": "This may cause the program to run indefinitely.",
                "line": node.start_point[0] + 1,
                "confidence": 0.95
            })

    for child in node.children:
        detect_infinite_while(child, violations)

 #--- Recursion without base case ---#
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

                if child.type == "expression_statement":
                    if function_name in child.text.decode():
                        has_recursive_call = True

            if has_recursive_call and not has_if_condition:
                violations.append({
                    "rule_id": "R-REC-BASE-01",
                    "concept": "Recursion → Base Case",
                    "violated_principle": "Missing base condition",
                    "explanation": "Recursive function does not define a base case.",
                    "why_it_matters": "This may lead to infinite recursion.",
                    "line": node.start_point[0] + 1,
                    "confidence": 0.88
                })

    for child in node.children:
        detect_missing_base_case(child, violations)            

# -------- Analyze Endpoint --------
@app.post("/analyze")
def analyze_code(request: CodeRequest):

    tree = parser.parse(bytes(request.code, "utf8"))
    root = tree.root_node

    violations = []

    detect_loop_boundary_issue(root, violations)
    detect_infinite_while(root, violations)
    detect_missing_base_case(root, violations)

    return {
        "studentId": request.studentId,
        "has_syntax_error": root.has_error,
        "violations": violations
    }