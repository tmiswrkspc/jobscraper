"""Script to build comprehensive test_quick_wins.py from existing test files."""

# Read the existing test files
with open('test_categorization_unit.py', 'r') as f:
    categorization_tests = f.read()

with open('test_category_exports_unit.py', 'r') as f:
    export_tests = f.read()

# Extract just the test functions (skip imports and main)
def extract_functions(content, start_marker="def test_"):
    lines = content.split('\n')
    functions = []
    current_func = []
    in_function = False
    
    for line in lines:
        if line.startswith('def test_'):
            if current_func:
                functions.append('\n'.join(current_func))
            current_func = [line]
            in_function = True
        elif in_function:
            if line and not line[0].isspace() and not line.startswith('def'):
                # End of function
                functions.append('\n'.join(current_func))
                current_func = []
                in_function = False
            else:
                current_func.append(line)
    
    if current_func:
        functions.append('\n'.join(current_func))
    
    return functions

print("Building comprehensive test file...")
print(f"Categorization tests: {len(extract_functions(categorization_tests))} functions")
print(f"Export tests: {len(extract_functions(export_tests))} functions")
print("Done!")
