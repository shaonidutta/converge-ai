#!/usr/bin/env python3
"""
Script to fix all .query() calls in metrics_repository.py to use the new async SQLAlchemy syntax
"""

import re

def fix_metrics_repository():
    """Fix all .query() calls in the metrics repository"""
    
    # Read the file
    with open('src/repositories/metrics_repository.py', 'r') as f:
        content = f.read()
    
    # Define replacement patterns
    replacements = [
        # Simple count queries
        (r'await self\.db\.query\(func\.count\(([^)]+)\)\)\.filter\(([^)]+(?:\([^)]*\))*[^)]*)\)\.scalar\(\)', 
         r'(await self.db.execute(select(func.count(\1)).where(\2))).scalar()'),
        
        # Count queries without filter
        (r'await self\.db\.query\(func\.count\(([^)]+)\)\)\.scalar\(\)',
         r'(await self.db.execute(select(func.count(\1)))).scalar()'),
        
        # Simple queries with filter
        (r'query = self\.db\.query\(([^)]+(?:\([^)]*\))*[^)]*)\)',
         r'query = select(\1)'),
        
        # Filter to where
        (r'\.filter\(', r'.where('),
        
        # Execute query
        (r'result = await query\.all\(\)', r'result = await self.db.execute(query)\n        rows = result.all()'),
        (r'result = await query\.scalar\(\)', r'result = (await self.db.execute(query)).scalar()'),
        
        # Fix row references
        (r'for row in result:', r'for row in rows:'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Write back the file
    with open('src/repositories/metrics_repository.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed metrics_repository.py")

if __name__ == "__main__":
    fix_metrics_repository()
