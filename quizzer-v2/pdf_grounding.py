#!/usr/bin/env python3
"""
PDF Grounding Engine
Extracts and indexes content from course PDF notes for grounded question generation
"""

import re
import warnings
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import PyPDF2

# Suppress PyPDF2 warnings about malformed PDFs (duplicate dictionary entries)
warnings.filterwarnings("ignore", message=".*Multiple definitions in dictionary.*")


class PDFGroundingEngine:
    """Engine for extracting and grounding content from PDF course notes."""
    
    def __init__(self, repo_root: str):
        """Initialize the PDF grounding engine.
        
        Args:
            repo_root: Root directory of the ai-masters-notes repository
        """
        self.repo_root = Path(repo_root)
        self.courses_dir = self.repo_root / "courses"
        self.pdf_cache = {}  # Cache parsed PDFs
        
        # Course name mappings
        self.course_map = {
            "nlp": "natural-language-processing",
            "ml-dl": "machine-learning-and-deep-learning",
            "ar": "automated-reasoning",
            "planning": "planning-and-reinforcement-learning",
            "hci": "human-computer-interaction"
        }
    
    def get_note_files(self, course: str) -> List[Path]:
        """Get all PDF note files for a course.
        
        Args:
            course: Course identifier (nlp, ml-dl, ar, planning, hci)
            
        Returns:
            List of paths to PDF files
        """
        course_dir_name = self.course_map.get(course, course)
        notes_dir = self.courses_dir / course_dir_name / "notes"
        
        if not notes_dir.exists():
            return []
        
        return list(notes_dir.glob("*.pdf"))
    
    def extract_pdf_text(self, pdf_path: Path) -> Dict[int, str]:
        """Extract text from PDF with page numbers.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary mapping page number to text content
        """
        if str(pdf_path) in self.pdf_cache:
            return self.pdf_cache[str(pdf_path)]
        
        pages = {}
        
        try:
            # Suppress stderr output from PyPDF2 during PDF parsing
            import sys
            import os
            
            # Save original stderr
            original_stderr = sys.stderr
            
            try:
                # Redirect stderr to devnull to suppress PyPDF2 warnings
                sys.stderr = open(os.devnull, 'w')
                
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(reader.pages, start=1):
                        text = page.extract_text()
                        if text:
                            pages[page_num] = text
            finally:
                # Always restore stderr
                sys.stderr.close()
                sys.stderr = original_stderr
            
            self.pdf_cache[str(pdf_path)] = pages
            
        except Exception as e:
            print(f"Warning: Could not read PDF {pdf_path}: {e}")
            return {}
        
        return pages
    
    def search_content(self, pdf_path: Path, query: str, max_results: int = 5) -> List[Dict]:
        """Search for content in PDF matching query.
        
        Args:
            pdf_path: Path to PDF file
            query: Search query (topic/keyword)
            max_results: Maximum number of results to return
            
        Returns:
            List of matches with page numbers and excerpts
        """
        pages = self.extract_pdf_text(pdf_path)
        results = []
        
        # Tokenize query
        query_terms = query.lower().split()
        
        for page_num, text in pages.items():
            text_lower = text.lower()
            
            # Simple relevance scoring
            score = sum(1 for term in query_terms if term in text_lower)
            
            if score > 0:
                # Find best excerpt (context around first match)
                for term in query_terms:
                    if term in text_lower:
                        # Get context around the term
                        idx = text_lower.find(term)
                        start = max(0, idx - 150)
                        end = min(len(text), idx + 150)
                        excerpt = text[start:end].strip()
                        
                        results.append({
                            "page": page_num,
                            "text": text,
                            "excerpt": excerpt,
                            "score": score,
                            "path": str(pdf_path)
                        })
                        break
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def get_page_content(self, pdf_path: Path, page_num: int) -> Optional[str]:
        """Get content of a specific page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-indexed)
            
        Returns:
            Page text or None if not found
        """
        pages = self.extract_pdf_text(pdf_path)
        return pages.get(page_num)
    
    def extract_quote(self, text: str, max_words: int = 25) -> str:
        """Extract a representative quote from text.
        
        Args:
            text: Source text
            max_words: Maximum number of words in quote
            
        Returns:
            Extracted quote (≤ max_words)
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        # Find shortest complete sentence under word limit
        for sentence in sentences:
            words = sentence.split()
            if 5 <= len(words) <= max_words:
                return sentence.strip()
        
        # If no suitable sentence, truncate to word limit
        words = text.split()[:max_words]
        return ' '.join(words) + "..."
    
    def find_grounding(self, pdf_path: Path, topic: str, concept: str) -> List[Dict]:
        """Find grounding evidence for a specific topic/concept.
        
        Args:
            pdf_path: Path to PDF file
            topic: Topic name
            concept: Specific concept to ground
            
        Returns:
            List of grounding citations with page numbers and quotes
        """
        # Search for topic and concept
        results = self.search_content(pdf_path, f"{topic} {concept}", max_results=3)
        
        groundings = []
        for result in results:
            # Extract a short quote
            quote = self.extract_quote(result["excerpt"], max_words=25)
            
            groundings.append({
                "path": result["path"],
                "page": result["page"],
                "quote": quote
            })
        
        return groundings
    
    def validate_note_file(self, note_file: str) -> bool:
        """Check if a note file exists.
        
        Args:
            note_file: Relative path to note file
            
        Returns:
            True if file exists, False otherwise
        """
        path = self.repo_root / note_file
        return path.exists() and path.suffix == '.pdf'
    
    def extract_topic_sections(self, pdf_path: Path, topics: List[str]) -> Dict[str, List[Dict]]:
        """Extract sections related to specific topics.
        
        Args:
            pdf_path: Path to PDF file
            topics: List of topics to extract
            
        Returns:
            Dictionary mapping topics to relevant page sections
        """
        topic_sections = {topic: [] for topic in topics}
        
        for topic in topics:
            results = self.search_content(pdf_path, topic, max_results=5)
            topic_sections[topic] = results
        
        return topic_sections
