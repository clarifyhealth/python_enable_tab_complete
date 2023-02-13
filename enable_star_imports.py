import os
import sys
from shutil import rmtree
import re


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
    non_special_objects = [d for d in all_objects_in_path if not d.startswith(('_', '.')) and not d.startswith('drgpy') and not d.startswith('Dockerfile')]
    folders = [f for f in non_special_objects if '.' not in f and len(os.listdir(os.path.join(path, f))) != 0]
    files = [f for f in all_objects_in_path if '.' in f and not f.startswith('_')]
    transformer_file_indicators = ('.sql', '.json', '.csv', 'calculate.py')
    path_contains_transformer = len([file for file in files if file.endswith(transformer_file_indicators)]) > 0

    init_file = '__init__.py'
    if init_file in all_objects_in_path:
        init_file = os.path.join(path, init_file)
        with open(init_file, 'r') as readfile:
            if readfile.readlines():
                with open(init_file, 'w+') as writefile:
                    writefile.write("")

    def write_transformer(file_name):
        transformer_reader_class_name = ''.join([s.title() for s in file_name.split('_')])
        transformer_reader_string = f"""
from clarify.common.enable_star_imports import CodeFactory
from clarify.library.progress_logger import ProgressLogger
import os


class {transformer_reader_class_name}(CodeFactory):
    def __init__(self, parameters, progress_logger: ProgressLogger = None, verify_count_remains_same=False):
        self.location = os.path.dirname(os.path.abspath(__file__))
        super().__init__(parameters, progress_logger, verify_count_remains_same)
"""
        if path_contains_transformer:
            with open(os.path.join(path, file_name + '.py'), 'w+') as file:
                file.write(transformer_reader_string)

    supported_library = ['features/', 'data_sources/', 'ccgs/', 'filters/']
    if any(s in path for s in supported_library):
        if 'features/' in path:
            transformer_reader_file_name = path[re.search(r'/clarify/library/features/', path).end():].replace('/', '_')
            write_transformer(transformer_reader_file_name)
        elif 'filters/' in path:
            transformer_reader_file_name = path[re.search(r'/clarify/library/filters/', path).end():].replace('/', '_')
            write_transformer(transformer_reader_file_name)
        elif 'ccgs/' in path:
            transformer_reader_file_name = path[re.search(r'/clarify/library/ccgs/', path).end():].replace('/', '_')
            write_transformer(transformer_reader_file_name)
        elif re.search(r'/clarify/library/data_sources/[a-z_0-9]+/[a-z_0-9]+/', path):
            transformer_reader_file_name = path[re.search(r'/clarify/library/data_sources/[a-z_]+/', path).end():]\
                .replace('/', '_')
            write_transformer(transformer_reader_file_name)

    for folder in folders:
        enable_star_imports(os.path.join(path, folder))


def main():
    delete_empty_dirs(os.path.join(os.getcwd(), 'clarify'))
    enable_star_imports(os.path.join(os.getcwd(), 'clarify'))


if __name__ == "__main__":
    sys.exit(main())
