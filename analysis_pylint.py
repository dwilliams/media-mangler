import os
import sys
from pylint import epylint as lint

# Add directories to exclude to this list.
EXCLUDE_DIRS = ['venv']

def get_result_value(result_string):
    tmp_res_list = result_string.rstrip().split('\n')
    for item in tmp_res_list:
        if 'Your code has been rated at' in item:
            tmp_result = float(item.split()[6].split('/')[0])
            return tmp_result
    return None

# Get a list of all python files in the project
print('Compiling list of modules...')
MODULES = []
for i in os.walk(os.path.abspath(os.path.join(os.path.abspath(__file__), '..')), topdown = True):
    root, dirs, files = i
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        if file.endswith('.py'):
            MODULES.append(os.path.join(root, file))

# Run PyLint on all of the modules, keeping the output
RESULTS = {}
ERRORS = []
print("Analyzing modules with PyLint...")
for mod in MODULES:
    print(mod)
    (stdout, stderr) = lint.py_run(mod, return_std=True) # Need to update this to specify the pylintrc at the repo base.
    RESULTS[mod] = stdout
    ERRORS.append(stderr)

# Generate a report to save in the project, keeping track of scores
print('\n--- Generating report ---')
REPORT = ''
SCORES = []
for mod in RESULTS:
    res = RESULTS[mod].read()
    REPORT += '{}\n'.format(mod)
    REPORT += res.replace(' {}:'.format(mod), 'line ')
    REPORT += '\n\n'

    # Get the score of the result
    tmp_score = get_result_value(res)
    if tmp_score:
        SCORES.append(tmp_score)

# Create a summary of the analysis
ANALYSIS = 'Files analyzed: {}\nAverage score: {}\n\n'.format(str(len(SCORES)), str(sum(SCORES)/len(SCORES)))
REPORT = REPORT + ANALYSIS

# Dump report to console
print(REPORT)

# Exit with a non-zero code if a score was too low
if min(SCORES) < 6:
    print('Analysis score too low, exiting with error code 1')
    sys.exit(1)
sys.exit(0)
