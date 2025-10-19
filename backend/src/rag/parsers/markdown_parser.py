"""
Markdown document parser
"""
import logging
from pathlib import Path
from typing import Dict, Any
import re

from .base_parser import BaseParser


logger = logging.getLogger(__name__)


class MarkdownParser(BaseParser):
    """Parser for Markdown documents"""
    
    def __init__(self):
        self.supported_extensions = ['.md', '.markdown']
    
    async def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse Markdown document and extract content
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Dictionary with text and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            # Extract title from first H1 heading
            title_match = re.search(r'^#\s+(.+)$', full_text, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            metadata = {
                "title": title,
                "author": "Unknown",
                "file_type": "markdown",
                "file_name": file_path.name,
            }
            
            return {
                "text": full_text,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error parsing Markdown {file_path}: {e}")
            raise ValueError(f"Failed to parse Markdown: {str(e)}")
    
    def supports_file_type(self, file_extension: str) -> bool:
        """Check if parser supports given file type"""
        return file_extension.lower() in self.supported_extensions

