# ==========================================
# AI LEARNSPHERE - PYTHON STATIC ANALYZER
# ==========================================
import ast
import re

def analyze_code_submission(challenge, submitted_code):
    """
    Perform basic static analysis without executing submitted code.

    Checks Python syntax and selected challenge-specific patterns.
    This is not a complete correctness verifier.
    """

    if not isinstance(challenge, dict):
        raise ValueError("Invalid coding challenge.")

    if not isinstance(submitted_code, str) or not submitted_code.strip():
        raise ValueError("Please submit your Python code.")

    result = {
        "syntax_valid": False,
        "issues": [],
        "warnings": [],
        "analysis_notes": []
    }

    # Step 1: Check Python syntax using AST parsing.
    try:
        syntax_tree = ast.parse(submitted_code)

        result["syntax_valid"] = True
        result["analysis_notes"].append(
            "Python syntax is valid."
        )

    except SyntaxError as error:
        result["issues"].append(
            f"Syntax error on line {error.lineno}: {error.msg}"
        )

        return result

    # Step 2: Identify the expected function name
    # from the challenge example, when available.
    example_input = challenge.get("example_input", "")

    function_match = re.match(
        r"\s*([A-Za-z_]\w*)\s*\(",
        example_input
    )

    if not function_match:
        result["analysis_notes"].append(
            "Could not identify an expected function name."
        )
        return result

    expected_function = function_match.group(1)

    function_node = None

    for node in ast.walk(syntax_tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == expected_function
        ):
            function_node = node
            break

    if function_node is None:
        result["issues"].append(
            f"Expected function '{expected_function}' was not found."
        )
        return result

    result["analysis_notes"].append(
        f"Found expected function '{expected_function}'."
    )

    # Step 3: Challenge-specific check for addition.
    # This check is intentionally limited to the
    # Sum of Two Numbers challenge.
    challenge_title = challenge.get("title", "").strip().lower()

    if challenge_title == "sum of two numbers":

        returned_expressions = [
            node.value
            for node in ast.walk(function_node)
            if isinstance(node, ast.Return) and node.value is not None
        ]

        uses_addition = any(
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Add)
            for expression in returned_expressions
            for node in ast.walk(expression)
        )

        uses_sum_function = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "sum"
            for expression in returned_expressions
            for node in ast.walk(expression)
        )

        uses_subtraction = any(
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Sub)
            for expression in returned_expressions
            for node in ast.walk(expression)
        )

        if uses_subtraction and not uses_addition and not uses_sum_function:
            result["issues"].append(
                "The returned expression uses subtraction instead "
                "of addition for the Sum of Two Numbers challenge."
            )

        elif uses_addition or uses_sum_function:
            result["analysis_notes"].append(
                "An addition operation was found in a return expression."
            )

        else:
            result["warnings"].append(
                "Could not confirm the expected addition operation "
                "using this basic static check. Manual review is needed."
            )

    return result
