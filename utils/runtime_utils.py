import ast
import os

def extract_functions_and_variables(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)

    functions = {}
    variables = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[f"{node.name}"] = node
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append(target)

    return functions, variables

def recursive_folder_search(root, callback):
    try:
        for path in os.listdir(root):
            if os.path.isdir(f"{root}/{path}"):
                recursive_folder_search(f"{root}/{path}", callback)
            else:
                callback(f"{root}/{path}")
    except(FileNotFoundError):
        print(FileNotFoundError.strerror)
