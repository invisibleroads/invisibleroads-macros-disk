from os.path import dirname, join


TESTS_FOLDER = dirname(__file__)
EXAMPLES_FOLDER = join(TESTS_FOLDER, 'examples')
A_FOLDER = join(EXAMPLES_FOLDER, 'a')
B_FOLDER = join(EXAMPLES_FOLDER, 'b')
FILE_NAME = 'file.txt'
FILE_CONTENT = open(join(A_FOLDER, FILE_NAME)).read()
