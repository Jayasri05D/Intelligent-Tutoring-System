
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

        # Get iterable part
        iterable = None
        for child in node.children:
            if child.type == "call":
                iterable = child
                break

        if iterable:
            # Check if function is range()
            function_name = iterable.child_by_field_name("function")

            if function_name and function_name.text.decode() == "range":

                arguments = iterable.child_by_field_name("arguments")

                if arguments:
                    # Look for binary operator inside arguments
                    for arg in arguments.children:
                        if arg.type == "binary_operator":

                            # Check operator
                            operator_node = None
                            left = None
                            right = None

                            for child in arg.children:
                                if child.type == "+":
                                    operator_node = child
                                if left is None:
                                    left = child
                                else:
                                    right = child

                            if right and right.text.decode() == "1":
                                violations.append({
                                    "rule_id": "R-LOOP-BOUNDARY-01",
                                    "concept": "Loops → Boundary",
                                    "line": node.start_point[0] + 1,
                                    "confidence": 0.9
                                })

    # Recursively check children
    for child in node.children:
        detect_loop_boundary_issue(child, violations)


# -------- Analyze Endpoint --------
@app.post("/analyze")
def analyze_code(request: CodeRequest):

    tree = parser.parse(bytes(request.code, "utf8"))
    root = tree.root_node

    violations = []

    detect_loop_boundary_issue(root, violations)

    return {
        "studentId": request.studentId,
        "has_syntax_error": root.has_error,
        "violations": violations
    }