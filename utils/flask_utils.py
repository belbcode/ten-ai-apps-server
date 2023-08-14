from .runtime_utils import extract_functions_and_variables
from flask import Flask, request
from flask_cors import CORS, cross_origin
import os
import importlib

def import_module_from_directory(directory, module_name):
    print(directory, module_name)
    module_spec = importlib.util.spec_from_file_location(module_name, f"{directory}/{module_name}.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def route_app(pythonFile: str):
    basename = os.path.basename(pythonFile)
    if basename != "index.py":
        return
    module = import_module_from_directory(pythonFile.split('/index.py')[0], 'index')
    

    # @app.route("/", methods=module.methods())
    # @cross_origin()
    # def route(): module.index

