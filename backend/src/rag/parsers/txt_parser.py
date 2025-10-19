"""
Plain text document parser
"""
import logging
from pathlib import Path
from typing import Dict, Any

from .base_parser import BaseParser


logger = logging.getLogger(__name__)


class TXTParser(BaseParser):
    """Parser for plain text documents"""
    
    def __init__(self):
        self.supported_extensions = ['.txt']
    
    async def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse text document and extract content
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary with text and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            metadata = {
                "title": file_path.stem,
                "author": "Unknown",
                "file_type": "txt",
                "file_name": file_path.name,
            }
            
            return {
                "text": full_text,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path}: {e}")
            raise ValueError(f"Failed to parse TXT: {str(e)}")
    
    def supports_file_type(self, file_extension: str) -> bool:
        """Check if parser supports given file type"""
        return file_extension.lower() in self.supported_extensions

