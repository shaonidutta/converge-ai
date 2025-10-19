"""
DOCX document parser using python-docx
"""
import logging
from pathlib import Path
from typing import Dict, Any

from docx import Document

from .base_parser import BaseParser


logger = logging.getLogger(__name__)


class DOCXParser(BaseParser):
    """Parser for DOCX documents"""
    
    def __init__(self):
        self.supported_extensions = ['.docx', '.doc']
    
    async def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse DOCX document and extract text and metadata
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Dictionary with text and metadata
        """
        try:
            doc = Document(file_path)
            
            # Extract text from paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            full_text = "\n\n".join(paragraphs)
            
            # Extract metadata
            core_properties = doc.core_properties
            metadata = {
                "title": core_properties.title or file_path.stem,
                "author": core_properties.author or "Unknown",
                "pages": len(doc.sections),  # Approximate
                "file_type": "docx",
                "file_name": file_path.name,
            }
            
            return {
                "text": full_text,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {e}")
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
    
    def supports_file_type(self, file_extension: str) -> bool:
        """Check if parser supports given file type"""
        return file_extension.lower() in self.supported_extensions

