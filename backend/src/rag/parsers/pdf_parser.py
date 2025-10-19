"""
PDF document parser using pdfplumber
"""
import logging
from pathlib import Path
from typing import Dict, Any

import pdfplumber

from .base_parser import BaseParser


logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Parser for PDF documents"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    async def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse PDF document and extract text and metadata
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with text and metadata
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                full_text = "\n\n".join(text_parts)
                
                # Extract metadata
                metadata = {
                    "title": pdf.metadata.get("Title", file_path.stem) if pdf.metadata else file_path.stem,
                    "author": pdf.metadata.get("Author", "Unknown") if pdf.metadata else "Unknown",
                    "pages": len(pdf.pages),
                    "file_type": "pdf",
                    "file_name": file_path.name,
                }
                
                return {
                    "text": full_text,
                    "metadata": metadata
                }
        
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def supports_file_type(self, file_extension: str) -> bool:
        """Check if parser supports given file type"""
        return file_extension.lower() in self.supported_extensions

