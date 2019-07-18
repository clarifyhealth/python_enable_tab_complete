import os
import logging

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
    python_files = [f.replace('.py', '') for f in non_special_objects if f.endswith('.py')]

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

    with open(init_file_name, 'w+') as file:
        if path_contains_transformer and not path_contains_folder:
            logging.info(f"writing Code to {init_file_name}")
            file.write(transformer_string)
        elif path_contains_transformer and path_contains_folder:
            logging.info(f"writing Code and __all__ to {init_file_name}")
            file.write(transformer_string)
            file.write(init_contents)
        elif non_special_objects:
            logging.info(f"writing __all__ to {init_file_name}")
            file.write(init_contents)
    for folder in folders:
        enable_star_imports(os.path.join(path, folder))


if __name__ == "__main__":
    enable_star_imports(os.path.dirname(os.path.abspath(__file__)))
