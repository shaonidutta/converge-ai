"""
Fix import paths - Replace 'backend.src.' with 'src.' throughout the codebase
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace 'from backend.src.' with 'from src.'
        content = re.sub(r'from backend\.src\.', 'from src.', content)
        
        # Replace 'import backend.src.' with 'import src.'
        content = re.sub(r'import backend\.src\.', 'import src.', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in src directory"""
    src_dir = Path(__file__).parent / 'src'
    
    fixed_count = 0
    total_count = 0
    
    print("Fixing import paths...")
    print("=" * 60)
    
    for py_file in src_dir.rglob('*.py'):
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
            print(f"✅ Fixed: {py_file.relative_to(src_dir)}")
    
    print("=" * 60)
    print(f"Total files processed: {total_count}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files unchanged: {total_count - fixed_count}")
    print("=" * 60)
    print("✅ Import path fix complete!")

if __name__ == "__main__":
    main()

