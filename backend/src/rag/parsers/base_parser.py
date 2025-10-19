"""
Base parser interface for document parsing
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class BaseParser(ABC):
    """Abstract base class for document parsers"""
    
    @abstractmethod
    async def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse document and extract text and metadata
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with:
                - text: Extracted text content
                - metadata: Document metadata (title, author, pages, etc.)
        """
        pass
    
    @abstractmethod
    def supports_file_type(self, file_extension: str) -> bool:
        """
        Check if parser supports given file type
        
        Args:
            file_extension: File extension (e.g., '.pdf', '.docx')
            
        Returns:
            True if supported, False otherwise
        """
        pass

