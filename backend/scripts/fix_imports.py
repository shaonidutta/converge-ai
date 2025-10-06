"""
Fix imports from backend.src to src
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace backend.src with src
    new_content = content.replace('from backend.src.', 'from src.')
    new_content = new_content.replace('import backend.src.', 'import src.')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {file_path}")
        return True
    return False

def main():
    """Fix all imports in backend/src directory"""
    backend_dir = Path(__file__).parent.parent / 'src'
    
    fixed_count = 0
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()

