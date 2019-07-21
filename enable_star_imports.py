import os
import sys
from difflib import Differ
from pprint import pprint
from shutil import rmtree

transformer_string = """
from clarify.enable_star_imports import CodeFactory
from clarify.library.progress_logger import ProgressLogger
import os

class Code(CodeFactory):
    def __init__(self, parameters, progress_logger: ProgressLogger = None, verify_count_remains_same=False):
        self.location = os.path.dirname(os.path.abspath(__file__))
        super().__init__(parameters, progress_logger, verify_count_remains_same)

"""


def delete_empty_dirs(path):

    def is_path_empty(directory):
        for dir_tuple in os.walk(directory):
            if [file for file in dir_tuple[2] if not (file.startswith(('__', '.')) or file.endswith('.pyc'))]:
                return False
        return True

    for path_tuple in os.walk(path):
        if path_tuple[0].endswith('__pycache__'):
            pass
        else:
            current_path = os.path.join(path, path_tuple[0])
            if is_path_empty(current_path):
                try:
                    print(f"removing {current_path}")
                    rmtree(current_path)
                except FileNotFoundError:
                    # The os.walk will generate keys under a dir, but by the time it reaches them,
                    # they may have been deleted by a previous call of the program. Hence,
                    # this will try to delete some files twice, which results in an error that
                    # i am ignoring here.
                    pass


def enable_star_imports(path):
    all_objects_in_path = os.listdir(path)
    non_special_objects = [d for d in all_objects_in_path if not d.startswith(('_', '.')) and not d.startswith('drgpy')]
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
        with open(init_file_name, 'w+') as write_file:
            if path_contains_transformer and not path_contains_folder:
                write_file.write(transformer_string)
            elif path_contains_transformer and path_contains_folder:
                write_file.write(transformer_string + init_contents)
            elif non_special_objects:
                write_file.write(init_contents)

    for folder in folders:
        enable_star_imports(os.path.join(path, folder))


def main():
    delete_empty_dirs(os.path.join(os.getcwd(), 'clarify'))
    enable_star_imports(os.path.join(os.getcwd(), 'clarify'))


if __name__ == "__main__":
    sys.exit(main())
