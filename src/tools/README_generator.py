# src/tools/readme_generator.py

import os
import re

# Adjusted paths using absolute paths for reliability
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
README_PATH = os.path.join(BASE_DIR, 'README.md')

def get_python_files(root_dir):
    """Recursively collect all Python files in the project."""
    python_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                relative_path = os.path.relpath(os.path.join(root, file), root_dir)
                python_files.append(relative_path)
    return set(python_files)

def parse_readme_sections(readme_path):
    """Parse README.md and extract categorized and TODO files."""
    with open(readme_path, 'r') as f:
        content = f.read()
    
    categorized_files = set(re.findall(r'- ([\w./]+\.py)', content))
    
    todo_match = re.search(r'## TODO\n(.*?)(\n## |\Z)', content, re.S)
    todo_section = todo_match.group(1).strip() if todo_match else ''
    todo_files = set(re.findall(r'- ([\w./]+\.py)', todo_section))
    
    return categorized_files, todo_files, content

def update_todo_section(content, new_files):
    """Update the TODO section with new Python files."""
    if not new_files:
        print("No new files to add to TODO.")
        return content
    
    todo_section = '## TODO\n'
    for file in new_files:
        todo_section += f'- {file}: # TODO: Add description\n'
    
    if '## TODO' in content:
        # Use a callable in re.sub to handle dynamic insertion
        def replace_todo_section(match):
            return f"{match.group(1)}{todo_section}{match.group(3)}"
        
        content = re.sub(r'(## TODO\n)(.*?)(\n## |\Z)', replace_todo_section, content, flags=re.S)
    else:
        content += f'\n{todo_section}'
    
    return content

def main():
    python_files = get_python_files(BASE_DIR)
    categorized_files, todo_files, content = parse_readme_sections(README_PATH)
    
    new_files = python_files - categorized_files - todo_files
    if not new_files:
        print("README.md is up-to-date. No new files detected.")
        return
    
    print(f"Adding {len(new_files)} new file(s) to TODO section.")
    content = update_todo_section(content, new_files)
    
    with open(README_PATH, 'w') as f:
        f.write(content)
    
    print("README.md has been updated successfully.")

if __name__ == '__main__':
    main()
