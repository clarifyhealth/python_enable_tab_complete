from setuptools import setup

setup(
    name='python_enable_tab_complete',
    version='1.1.1',
    py_modules=['enable_star_imports'],
    entry_points={
        'console_scripts': ['enable_star_imports = enable_star_imports:main']
    }
)
