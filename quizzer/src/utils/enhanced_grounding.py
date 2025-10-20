#!/usr/bin/env python3
"""
Enhanced Grounding Engine
Extracts and indexes content from both PDF and TeX course notes for improved grounding
"""

import re
import warnings
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
import PyPDF2
from collections import defaultdict
import hashlib

# Suppress PyPDF2 warnings about malformed PDFs
warnings.filterwarnings("ignore", message=".*Multiple definitions in dictionary.*")


class EnhancedGroundingEngine:
    """Advanced engine for extracting and grounding content from PDF and TeX course notes."""
    
    def __init__(self, repo_root: str):
        """Initialize the enhanced grounding engine.
        
        Args:
            repo_root: Root directory of the ai-masters-notes repository
        """
        self.repo_root = Path(repo_root)
        self.courses_dir = self.repo_root / "courses"
        self.pdf_cache = {}  # Cache parsed PDFs
        self.tex_cache = {}  # Cache parsed TeX files
        self.semantic_index = {}  # Semantic index for better search
        
        # Course name mappings
        self.course_map = {
            "nlp": "natural-language-processing",
            "ml-dl": "machine-learning-and-deep-learning",
            "ar": "automated-reasoning",
            "planning": "planning-and-reinforcement-learning",
            "hci": "human-computer-interaction"
        }
    
    def get_all_note_files(self, course: str) -> Dict[str, List[Path]]:
        """Get all note files (PDF and TeX) for a course.
        
        Args:
            course: Course identifier
            
        Returns:
            Dictionary with 'pdf' and 'tex' keys containing file paths
        """
        course_dir_name = self.course_map.get(course, course)
        notes_dir = self.courses_dir / course_dir_name / "notes"
        
        files = {"pdf": [], "tex": []}
        
        if notes_dir.exists():
            files["pdf"] = list(notes_dir.glob("*.pdf"))
            files["tex"] = list(notes_dir.glob("*.tex"))
        
        return files
    
    def get_note_files(self, course: str) -> List[Path]:
        """Get all PDF note files for a course (compatibility method).
        
        Args:
            course: Course identifier
            
        Returns:
            List of paths to PDF files
        """
        all_files = self.get_all_note_files(course)
        return all_files["pdf"]
    
    def extract_tex_content(self, tex_path: Path) -> Dict[str, any]:
        """Extract structured content from TeX file.
        
        Args:
            tex_path: Path to TeX file
            
        Returns:
            Dictionary with sections, theorems, definitions, etc.
        """
        if str(tex_path) in self.tex_cache:
            return self.tex_cache[str(tex_path)]
        
        content = {
            "sections": {},
            "definitions": [],
            "theorems": [],
            "examples": [],
            "equations": [],
            "raw_text": "",
            "concepts": set()
        }
        
        try:
            with open(tex_path, 'r', encoding='utf-8', errors='ignore') as f:
                tex_content = f.read()
                content["raw_text"] = tex_content
                
                # Extract sections
                sections = re.findall(r'\\section\{([^}]+)\}(.*?)(?=\\section|\\end\{document\}|$)', 
                                     tex_content, re.DOTALL)
                for i, (title, text) in enumerate(sections, 1):
                    content["sections"][f"Section {i}: {title}"] = self._clean_tex(text[:3000])
                
                # Extract subsections
                subsections = re.findall(r'\\subsection\{([^}]+)\}(.*?)(?=\\subsection|\\section|\\end\{document\}|$)', 
                                        tex_content, re.DOTALL)
                for title, text in subsections:
                    content["sections"][f"Subsection: {title}"] = self._clean_tex(text[:2000])
                
                # Extract definitions
                definitions = re.findall(r'\\begin\{definition\}(.*?)\\end\{definition\}', 
                                        tex_content, re.DOTALL)
                for defn in definitions:
                    cleaned = self._clean_tex(defn)
                    if cleaned:
                        content["definitions"].append(cleaned)
                        # Extract concept from definition
                        concept_match = re.search(r'\\textbf\{([^}]+)\}', defn)
                        if concept_match:
                            content["concepts"].add(concept_match.group(1))
                
                # Extract theorems
                theorems = re.findall(r'\\begin\{theorem\}(.*?)\\end\{theorem\}', 
                                     tex_content, re.DOTALL)
                for thm in theorems:
                    cleaned = self._clean_tex(thm)
                    if cleaned:
                        content["theorems"].append(cleaned)
                
                # Extract examples
                examples = re.findall(r'\\begin\{example\}(.*?)\\end\{example\}', 
                                     tex_content, re.DOTALL)
                for ex in examples:
                    cleaned = self._clean_tex(ex)
                    if cleaned:
                        content["examples"].append(cleaned)
                
                # Extract important equations
                equations = re.findall(r'\$\$(.*?)\$\$', tex_content, re.DOTALL)
                for eq in equations[:20]:  # Limit to 20 most important equations
                    if len(eq) > 10:  # Skip trivial equations
                        content["equations"].append(eq.strip())
                
                # Extract key concepts from bold and emphasized text
                bold_concepts = re.findall(r'\\textbf\{([^}]+)\}', tex_content)
                emph_concepts = re.findall(r'\\emph\{([^}]+)\}', tex_content)
                content["concepts"].update(bold_concepts)
                content["concepts"].update(emph_concepts)
                
                self.tex_cache[str(tex_path)] = content
                
        except Exception as e:
            print(f"Warning: Could not read TeX file {tex_path}: {e}")
            return content
        
        return content
    
    def _clean_tex(self, text: str) -> str:
        """Clean TeX markup to get readable text.
        
        Args:
            text: Raw TeX text
            
        Returns:
            Cleaned text
        """
        # Remove comments
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
        
        # Replace common TeX commands with readable equivalents
        replacements = {
            r'\\textbf\{([^}]+)\}': r'\1',
            r'\\emph\{([^}]+)\}': r'\1',
            r'\\textit\{([^}]+)\}': r'\1',
            r'\\item': '• ',
            r'\\ldots': '...',
            r'\\rightarrow': '→',
            r'\\leftarrow': '←',
            r'\\Rightarrow': '⇒',
            r'\\Leftarrow': '⇐',
            r'\\forall': '∀',
            r'\\exists': '∃',
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\delta': 'δ',
            r'\\epsilon': 'ε',
            r'\\lambda': 'λ',
            r'\\mu': 'μ',
            r'\\sigma': 'σ',
            r'\\theta': 'θ',
            r'\\phi': 'φ',
            r'\\psi': 'ψ',
            r'\\omega': 'ω',
            r'\\sum': 'Σ',
            r'\\prod': 'Π',
            r'\\int': '∫',
            r'\\partial': '∂',
            r'\\nabla': '∇',
            r'\\infty': '∞',
            r'\\cdot': '·',
            r'\\times': '×',
            r'\\subset': '⊂',
            r'\\subseteq': '⊆',
            r'\\in': '∈',
            r'\\notin': '∉',
            r'\\cap': '∩',
            r'\\cup': '∪',
            r'\\approx': '≈',
            r'\\neq': '≠',
            r'\\leq': '≤',
            r'\\geq': '≥',
            r'\\\\': ' ',
            r'\$': '',
            r'\\begin\{[^}]+\}': '',
            r'\\end\{[^}]+\}': '',
            r'\\[a-zA-Z]+': ' '
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_pdf_text(self, pdf_path: Path) -> Dict[int, Dict]:
        """Compatibility method - calls extract_pdf_text_enhanced.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary mapping page numbers to content
        """
        return self.extract_pdf_text_enhanced(pdf_path)
    
    def extract_pdf_text_enhanced(self, pdf_path: Path) -> Dict[int, Dict]:
        """Enhanced PDF text extraction with structure detection.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary mapping page numbers to structured content
        """
        if str(pdf_path) in self.pdf_cache:
            return self.pdf_cache[str(pdf_path)]
        
        pages = {}
        
        try:
            import sys
            import os
            
            # Suppress stderr for PyPDF2 warnings
            original_stderr = sys.stderr
            
            try:
                sys.stderr = open(os.devnull, 'w')
                
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(reader.pages, start=1):
                        text = page.extract_text()
                        if text:
                            # Enhanced content extraction
                            pages[page_num] = {
                                "text": text,
                                "paragraphs": self._extract_paragraphs(text),
                                "bullet_points": self._extract_bullet_points(text),
                                "headings": self._extract_headings(text),
                                "key_terms": self._extract_key_terms(text)
                            }
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr
            
            self.pdf_cache[str(pdf_path)] = pages
            
        except Exception as e:
            print(f"Warning: Could not read PDF {pdf_path}: {e}")
            return {}
        
        return pages
    
    def _extract_paragraphs(self, text: str) -> List[str]:
        """Extract paragraphs from text."""
        # Split by double newlines or period followed by newline
        paragraphs = re.split(r'\n\n+|\.\n', text)
        return [p.strip() for p in paragraphs if len(p.strip()) > 50]
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text."""
        patterns = [
            r'[•·▪▫◦‣⁃]\s*([^\n]+)',
            r'^\s*[-*]\s+([^\n]+)',
            r'^\s*\d+[\.)]\s+([^\n]+)'
        ]
        
        points = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            points.extend(matches)
        
        return [p.strip() for p in points if p.strip()]
    
    def _extract_headings(self, text: str) -> List[str]:
        """Extract potential headings from text."""
        lines = text.split('\n')
        headings = []
        
        for line in lines:
            line = line.strip()
            # Heuristics for headings
            if (len(line) > 5 and len(line) < 100 and 
                (line.isupper() or 
                 re.match(r'^\d+\.?\s+[A-Z]', line) or
                 re.match(r'^[A-Z][^.!?]*$', line) and len(line.split()) < 10)):
                headings.append(line)
        
        return headings
    
    def _extract_key_terms(self, text: str) -> Set[str]:
        """Extract key terms and concepts from text."""
        # Look for emphasized terms (capitalized multi-word phrases, technical terms)
        terms = set()
        
        # Capitalized phrases
        cap_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        terms.update(cap_phrases)
        
        # Terms in parentheses (often abbreviations/definitions)
        paren_terms = re.findall(r'\(([A-Z]{2,})\)', text)
        terms.update(paren_terms)
        
        # Common technical patterns
        tech_patterns = [
            r'\b(?:algorithm|method|technique|approach|model|framework|system|architecture|component|module)\s+\w+',
            r'\b\w+(?:ization|isation|ment|tion|sion|ance|ence)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.update([m.lower() for m in matches if len(m) > 5])
        
        return terms
    
    def semantic_search(self, query: str, course: str, max_results: int = 5,
                       include_tex: bool = True) -> List[Dict]:
        """Advanced semantic search across all course materials.
        
        Args:
            query: Search query
            course: Course identifier
            max_results: Maximum results to return
            include_tex: Whether to include TeX files in search
            
        Returns:
            List of relevant content with metadata and scores
        """
        results = []
        query_terms = set(query.lower().split())
        
        # Get all note files
        files = self.get_all_note_files(course)
        
        # Search PDFs
        for pdf_path in files["pdf"]:
            pages = self.extract_pdf_text_enhanced(pdf_path)
            
            for page_num, content in pages.items():
                if not content:
                    continue
                    
                # Calculate relevance score
                text_lower = content["text"].lower()
                
                # Multi-factor scoring
                score = 0
                
                # Term frequency
                for term in query_terms:
                    score += text_lower.count(term) * 2
                
                # Check headings (higher weight)
                for heading in content.get("headings", []):
                    if any(term in heading.lower() for term in query_terms):
                        score += 10
                
                # Check key terms
                for key_term in content.get("key_terms", set()):
                    if any(term in key_term.lower() for term in query_terms):
                        score += 5
                
                # Check bullet points
                for bullet in content.get("bullet_points", []):
                    if any(term in bullet.lower() for term in query_terms):
                        score += 3
                
                if score > 0:
                    # Extract best excerpt
                    excerpt = self._get_best_excerpt(content["text"], query_terms)
                    
                    results.append({
                        "source_type": "pdf",
                        "path": str(pdf_path),
                        "page": page_num,
                        "score": score,
                        "text": content["text"],
                        "excerpt": excerpt,
                        "headings": content.get("headings", [])[:3],
                        "key_terms": list(content.get("key_terms", set()))[:10]
                    })
        
        # Search TeX files if enabled
        if include_tex:
            for tex_path in files["tex"]:
                tex_content = self.extract_tex_content(tex_path)
                
                # Search different TeX structures
                for section_title, section_text in tex_content["sections"].items():
                    score = self._calculate_relevance_score(section_text, query_terms)
                    
                    if any(term in section_title.lower() for term in query_terms):
                        score += 15
                    
                    if score > 0:
                        results.append({
                            "source_type": "tex",
                            "path": str(tex_path),
                            "section": section_title,
                            "score": score,
                            "text": section_text,
                            "excerpt": self._get_best_excerpt(section_text, query_terms),
                            "structure_type": "section"
                        })
                
                # Search definitions
                for i, definition in enumerate(tex_content["definitions"]):
                    score = self._calculate_relevance_score(definition, query_terms)
                    if score > 0:
                        results.append({
                            "source_type": "tex",
                            "path": str(tex_path),
                            "section": f"Definition {i+1}",
                            "score": score + 8,  # Boost definitions
                            "text": definition,
                            "excerpt": definition[:300],
                            "structure_type": "definition"
                        })
                
                # Search theorems
                for i, theorem in enumerate(tex_content["theorems"]):
                    score = self._calculate_relevance_score(theorem, query_terms)
                    if score > 0:
                        results.append({
                            "source_type": "tex",
                            "path": str(tex_path),
                            "section": f"Theorem {i+1}",
                            "score": score + 6,  # Boost theorems
                            "text": theorem,
                            "excerpt": theorem[:300],
                            "structure_type": "theorem"
                        })
                
                # Search examples
                for i, example in enumerate(tex_content["examples"]):
                    score = self._calculate_relevance_score(example, query_terms)
                    if score > 0:
                        results.append({
                            "source_type": "tex",
                            "path": str(tex_path),
                            "section": f"Example {i+1}",
                            "score": score + 4,  # Boost examples
                            "text": example,
                            "excerpt": example[:300],
                            "structure_type": "example"
                        })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Deduplicate similar results
        seen_hashes = set()
        unique_results = []
        
        for result in results:
            content_hash = hashlib.md5(result["excerpt"].encode()).hexdigest()[:8]
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_results.append(result)
        
        return unique_results[:max_results]
    
    def _calculate_relevance_score(self, text: str, query_terms: Set[str]) -> float:
        """Calculate relevance score for text against query terms."""
        text_lower = text.lower()
        score = 0
        
        # Term frequency
        for term in query_terms:
            count = text_lower.count(term)
            score += count * 2
        
        # Boost for exact phrase match
        query_phrase = ' '.join(query_terms)
        if query_phrase in text_lower:
            score += 20
        
        # Proximity bonus (terms appear close together)
        words = text_lower.split()
        for i, word in enumerate(words):
            if word in query_terms:
                # Check nearby words
                window = words[max(0, i-5):min(len(words), i+6)]
                nearby_matches = sum(1 for w in window if w in query_terms)
                if nearby_matches > 1:
                    score += nearby_matches * 3
        
        return score
    
    def _get_best_excerpt(self, text: str, query_terms: Set[str], max_length: int = 300) -> str:
        """Extract the most relevant excerpt from text."""
        text_lower = text.lower()
        best_score = 0
        best_excerpt = ""
        
        # Try different starting positions
        sentences = re.split(r'[.!?]\s+', text)
        
        for i, sentence in enumerate(sentences):
            if any(term in sentence.lower() for term in query_terms):
                # Build context around this sentence
                start_idx = max(0, i - 1)
                end_idx = min(len(sentences), i + 2)
                excerpt = '. '.join(sentences[start_idx:end_idx])
                
                if len(excerpt) > max_length:
                    excerpt = excerpt[:max_length] + "..."
                
                # Score this excerpt
                score = sum(excerpt.lower().count(term) for term in query_terms)
                
                if score > best_score:
                    best_score = score
                    best_excerpt = excerpt
        
        if not best_excerpt:
            # Fallback to first part of text
            best_excerpt = text[:max_length] + "..." if len(text) > max_length else text
        
        return best_excerpt.strip()
    
    def get_comprehensive_context(self, topic: str, course: str, max_sources: int = 5) -> Dict:
        """Get comprehensive context about a topic from all sources.
        
        Args:
            topic: Topic to search for
            course: Course identifier
            max_sources: Maximum number of sources to include
            
        Returns:
            Dictionary with structured context from multiple sources
        """
        results = self.semantic_search(topic, course, max_results=max_sources * 2, include_tex=True)
        
        context = {
            "definitions": [],
            "theorems": [],
            "examples": [],
            "key_points": [],
            "sources": [],
            "related_concepts": set()
        }
        
        for result in results[:max_sources]:
            source_info = {
                "type": result["source_type"],
                "path": Path(result["path"]).name,
                "location": result.get("page") or result.get("section", "Unknown")
            }
            context["sources"].append(source_info)
            
            # Extract structured information based on source type
            if result["source_type"] == "tex":
                structure_type = result.get("structure_type", "")
                
                if structure_type == "definition":
                    context["definitions"].append(result["text"])
                elif structure_type == "theorem":
                    context["theorems"].append(result["text"])
                elif structure_type == "example":
                    context["examples"].append(result["text"])
                else:
                    context["key_points"].append(result["excerpt"])
            else:
                # For PDFs, extract key points
                context["key_points"].append(result["excerpt"])
                
                # Add any detected key terms as related concepts
                if "key_terms" in result:
                    context["related_concepts"].update(result["key_terms"])
        
        # Convert set to list for JSON serialization
        context["related_concepts"] = list(context["related_concepts"])
        
        return context
    
    def validate_note_files(self, note_files: List[str]) -> Tuple[List[str], List[str]]:
        """Validate that note files exist and return valid/invalid lists.
        
        Args:
            note_files: List of file paths to validate
            
        Returns:
            Tuple of (valid_files, invalid_files)
        """
        valid = []
        invalid = []
        
        for file_path in note_files:
            full_path = self.repo_root / file_path
            if full_path.exists() and full_path.suffix in ['.pdf', '.tex']:
                valid.append(file_path)
            else:
                invalid.append(file_path)
        
        return valid, invalid
    
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
