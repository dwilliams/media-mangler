import os
import sys
from radon.complexity import cc_rank, cc_visit
from radon.visitors import Function, Class

# Get a list of all python files in the project
print('Compiling list of modules...')
MODULES = []
for i in os.walk(os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))):
    path, folders, files = i
    for file in files:
        if file.endswith('.py'):
            MODULES.append(os.path.join(path, file))

# Analyze each module with Radon
print('Analyzing modules with Radon...')
RESULTS = {}
for mod in MODULES:
    with open(mod, 'r') as py_file:
        RESULTS[mod] = cc_visit(py_file.read())

# Generate a report and save it to a file
print('Generating report...')
TEMPLATE = "{0:8} {1:9} {2:6} {3:20}"  # column widths: 7, 10, 12, 20
SCORES = []

def add_to_report(scores, chunk):
    lines = "{}-{}".format(chunk.lineno, chunk.endline)
    scores.append(chunk.complexity)
    complexity = cc_rank(chunk.complexity)
    if isinstance(chunk, Function):
        if chunk.is_method is False:
            print(TEMPLATE.format(lines, 'Function', complexity, chunk.name))
        else:
            print(TEMPLATE.format(lines, 'Method', complexity, '{}.{}'.format(chunk.classname, chunk.name)))
    elif isinstance(chunk, Class):
        print(TEMPLATE.format(lines, 'Class', complexity, chunk.name))
        for method in chunk.methods:
            add_to_report(scores, method)

for mod in RESULTS:
    if not RESULTS[mod]:
        continue
    print(mod + '\n' + TEMPLATE.format('Lines', 'Type', 'Score', 'Name'))
    for chonk in RESULTS[mod]:
        if isinstance(chonk, Function) and chonk.is_method:
            continue
        add_to_report(SCORES, chonk)

# Create a summary of the analysis
print('\nFiles analyzed: {}\nAverage score: {}\n\n'.format(str(len(SCORES)), str(sum(SCORES)/len(SCORES))))

# If the complexity of a module is above 10 (a 'c' grade), return a non-zero exit code
if max(SCORES) > 10:
    print('Analysis score too low, exiting with error code 1')
    sys.exit(1)
sys.exit(0)
