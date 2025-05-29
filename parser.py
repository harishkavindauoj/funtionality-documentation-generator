import ast

def extract_functions_and_docs(filepath):
    with open(filepath, "r") as file:
        tree = ast.parse(file.read(), filename=filepath)

    function_data = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            function_code = ast.get_source_segment(open(filepath).read(), node)
            function_data.append({
                "name": node.name,
                "docstring": docstring or "",
                "code": function_code,
            })

    return function_data
