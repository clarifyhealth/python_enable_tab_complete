import os
import logging
import sys
from difflib import Differ
from pprint import pprint

transformer_string = """
from clarify.enable_star_imports import CodeFactory
from clarify.library.progress_logger import ProgressLogger
import os

class Code(CodeFactory):
    def __init__(self, parameters, progress_logger: ProgressLogger = None, verify_count_remains_same=False):
        self.location = os.path.dirname(os.path.abspath(__file__))
        super().__init__(parameters, progress_logger, verify_count_remains_same)

"""


def enable_star_imports(path):
    all_objects_in_path = os.listdir(path)
    non_special_objects = [d for d in all_objects_in_path if not d.startswith(('_', '.'))]
    folders = [f for f in non_special_objects if '.' not in f and len(os.listdir(os.path.join(path, f))) != 0]
    folders.sort()
    python_files = [f.replace('.py', '') for f in non_special_objects if f.endswith('.py')]
    python_files.sort()

    init_file_name = os.path.join(path, '__init__.py')
    init_contents = f"""
__all__ = {folders + python_files}
for item in __all__:
    try:
        exec("from . import " + item)
    except ImportError:
        print("WARNING - trying to import non existent module" + item)

"""

    files = [f for f in all_objects_in_path if '.' in f and not f.startswith('_')]
    transformer_file_indicators = ('.sql', '.json', '.csv', 'calculate.py')
    path_contains_transformer = len([file for file in files if file.endswith(transformer_file_indicators)]) > 0
    path_contains_folder = len(folders) > 0

    differ = Differ()
    try:
        with open(init_file_name, 'r') as read_file:

            def compare_overwrite(write_contents):
                current_text = read_file.read()
                if current_text != write_contents:
                    print(f"writing to {init_file_name}")
                    pprint(list(differ.compare(current_text.splitlines(keepends=True),
                                               write_contents.splitlines(keepends=True))))
                    with open(init_file_name, 'w+') as write_file:
                        write_file.write(write_contents)

            if path_contains_transformer and not path_contains_folder:
                compare_overwrite(transformer_string)
            elif path_contains_transformer and path_contains_folder:
                compare_overwrite(transformer_string + init_contents)
            elif non_special_objects:
                compare_overwrite(init_contents)
    except FileNotFoundError:
        raise Exception(f"You probably have an empty dir or set of empty dirs at {path}. Delete them.")

    for folder in folders:
        enable_star_imports(os.path.join(path, folder))

def main():
    enable_star_imports(os.path.join(os.getcwd(), 'clarify'))

if __name__ == "__main__":
    sys.exit(main())
