#!/usr/bin/env python3
"""
Chatbot Engine
AI assistant that answers questions based strictly on course notes
"""

from pathlib import Path
from typing import Dict, List, Optional
from ..utils.pdf_grounding import PDFGroundingEngine


class ChatbotEngine:
    """Chatbot that answers questions based on course PDF notes."""
    
    def __init__(self, repo_root: str, ai_engine, grounding_engine: PDFGroundingEngine):
        """Initialize chatbot engine.
        
        Args:
            repo_root: Root directory of ai-masters-notes repository
            ai_engine: AI engine for generating responses
            grounding_engine: PDF grounding engine for searching notes
        """
        self.repo_root = Path(repo_root)
        self.ai = ai_engine
        self.grounding = grounding_engine
        self.current_course = None
        self.current_notes = []
        self.chat_history = []
        
    def set_course(self, course_code: str, note_files: List[str]):
        """Set the active course and notes for the chatbot.
        Also searches for ALL available files in the course directory.
        
        Args:
            course_code: Course identifier (nlp, ml-dl, etc.)
            note_files: List of note file paths for this course
        """
        self.current_course = course_code
        
        # Expand to include ALL PDF files in the course directory
        all_files = []
        for note_file in note_files:
            note_path = self.repo_root / note_file
            if note_path.exists():
                # Add the specified file
                all_files.append(note_file)
                
                # Also search for other PDFs in the same directory
                parent_dir = note_path.parent
                for pdf_file in parent_dir.glob("*.pdf"):
                    relative_path = pdf_file.relative_to(self.repo_root)
                    if str(relative_path) not in all_files:
                        all_files.append(str(relative_path))
        
        self.current_notes = all_files
        self.chat_history = []
        
        print(f"📚 Chatbot configured for {course_code}")
        print(f"   Loaded {len(self.current_notes)} files: {[Path(f).name for f in self.current_notes]}")
        
    def get_relevant_context(self, question: str, max_pages: int = 3) -> List[Dict]:
        """Search course notes for relevant content.
        
        Args:
            question: User's question
            max_pages: Maximum number of relevant pages to retrieve
            
        Returns:
            List of relevant page contents with metadata
        """
        if not self.current_notes:
            return []
        
        all_results = []
        
        # Search all note files for this course
        for note_file in self.current_notes:
            pdf_path = self.repo_root / note_file
            
            if not pdf_path.exists():
                continue
            
            # Search for relevant content
            results = self.grounding.search_content(pdf_path, question, max_results=max_pages)
            all_results.extend(results)
        
        # Sort by relevance score and take top results
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:max_pages]
    
    def _is_casual_message(self, question: str) -> bool:
        """Detect if message is casual/conversational rather than technical.
        
        Args:
            question: User's question
            
        Returns:
            True if casual, False if technical
        """
        question_lower = question.lower().strip()
        
        # Common greetings and casual phrases
        casual_patterns = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'whats up', "what's up", 'thanks', 'thank you', 'bye',
            'goodbye', 'see you', 'nice', 'cool', 'ok', 'okay', 'yes', 'no',
            'sure', 'please', 'help'
        ]
        
        # Check if it's a very short casual message
        if len(question.split()) <= 3 and any(pattern in question_lower for pattern in casual_patterns):
            return True
        
        # Check if it starts with a greeting
        starts_with_casual = any(question_lower.startswith(pattern) for pattern in casual_patterns)
        if starts_with_casual and len(question.split()) <= 5:
            return True
            
        return False
    
    def _generate_casual_response(self, question: str) -> str:
        """Generate a friendly conversational response.
        
        Args:
            question: User's casual message
            
        Returns:
            Friendly response
        """
        question_lower = question.lower().strip()
        
        # Specific responses for common patterns
        if any(greeting in question_lower for greeting in ['hello', 'hi', 'hey']):
            return "Hello! 👋 I'm your AI course assistant. I'm here to help you understand the course material. Feel free to ask me any questions about the topics we're covering!"
        
        if 'how are you' in question_lower:
            return "I'm doing great, thank you for asking! 😊 I'm here and ready to help you with any questions about the course material. What would you like to learn about?"
        
        if any(thanks in question_lower for thanks in ['thanks', 'thank you']):
            return "You're very welcome! 😊 Feel free to ask if you have any more questions. I'm here to help!"
        
        if any(bye in question_lower for bye in ['bye', 'goodbye', 'see you']):
            return "Goodbye! 👋 Good luck with your studies! Come back anytime you need help with the course material."
        
        if 'help' in question_lower and len(question.split()) <= 3:
            return "Of course! I'm here to help you understand the course material. You can ask me:\n\n• Conceptual questions (e.g., 'What is backpropagation?')\n• Definition questions (e.g., 'Define attention mechanism')\n• Clarification questions (e.g., 'Explain the difference between...')\n• Any topic covered in your course notes!\n\nJust type your question and I'll find the relevant information for you."
        
        # Generic friendly response
        return "I'm here to help you with the course material! Feel free to ask me any questions about the topics covered in your notes. 📚"
    
    def answer_question(self, question: str) -> Dict:
        """Answer a user question based on course notes.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        if not self.current_course:
            return {
                "answer": "⚠️ No course selected. Please select a course first.",
                "sources": [],
                "found_info": False
            }
        
        # Check if this is a casual/conversational message
        if self._is_casual_message(question):
            return {
                "answer": self._generate_casual_response(question),
                "sources": [],
                "found_info": True,
                "is_casual": True
            }
        
        # Get relevant context from notes (search more pages since we have all course files)
        relevant_pages = self.get_relevant_context(question, max_pages=5)
        
        if not relevant_pages:
            # Try to be helpful even when no direct match is found
            return {
                "answer": "❌ I couldn't find specific information about this topic in the course notes.\n\n"
                         "This might mean:\n"
                         "• The topic isn't covered in the loaded course materials\n"
                         "• The question might be phrased differently than the course content\n"
                         "• It might be a more general question not specific to this course\n\n"
                         "💡 Try rephrasing your question or asking about a core concept from the course!",
                "sources": [],
                "found_info": False
            }
        
        # Build context from relevant pages
        context_parts = []
        sources = []
        
        for idx, page in enumerate(relevant_pages, 1):
            # Add page content to context (increased limit for fuller context)
            context_parts.append(f"[Source {idx}] {page['text'][:2500]}")  # Increased to 2500 chars per page
            
            # Add to sources list
            sources.append({
                "page": page["page"],
                "path": Path(page["path"]).name,
                "excerpt": page["excerpt"]
            })
        
        context = "\n\n".join(context_parts)
        
        # Build prompt for AI
        system_prompt = """You are a knowledgeable teaching assistant helping students understand their course material. You have access to the full course notes and can provide detailed, educational responses.

IMPORTANT RULES:
1. Answer ONLY based on the provided course notes context
2. Be thorough and educational - explain concepts clearly with examples from the notes
3. Reference which source ([Source 1], [Source 2], etc.) you're using when appropriate
4. If the context doesn't fully answer the question, explain what information is available
5. Be conversational and helpful, like ChatGPT
6. Don't add information that isn't in the provided context"""

        prompt = f"""Question: {question}

Course Notes Context:
{context}

Please provide a comprehensive answer based on the context above. Explain the concepts clearly and thoroughly."""

        # Generate answer using AI
        answer_text = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,  # Slightly higher for more natural responses
            max_tokens=1200  # Increased for more comprehensive answers
        )
        
        if not answer_text:
            return {
                "answer": "⚠️ Sorry, I had trouble generating an answer. Please try again.",
                "sources": sources,
                "found_info": False
            }
        
        # Add to chat history
        self.chat_history.append({
            "question": question,
            "answer": answer_text,
            "sources": sources
        })
        
        return {
            "answer": answer_text,
            "sources": sources,
            "found_info": True
        }
    
    def get_chat_history(self) -> List[Dict]:
        """Get the current chat history.
        
        Returns:
            List of chat exchanges
        """
        return self.chat_history
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
    
    def get_course_overview(self) -> str:
        """Get a welcome message for the chatbot.
        
        Returns:
            Welcome message text
        """
        if not self.current_course or not self.current_notes:
            return "No course selected."
        
        # Count total pages across all notes
        total_pages = 0
        for note_file in self.current_notes:
            note_path = self.repo_root / note_file
            if note_path.exists():
                pages = self.grounding.extract_pdf_text(note_path)
                total_pages += len(pages)
        
        file_names = [Path(f).name for f in self.current_notes]
        
        message = f"""I'm your AI course assistant! 🤖📚

I have access to {len(self.current_notes)} course document(s) with {total_pages} pages of material:

{chr(10).join(f"• {name}" for name in file_names)}

**What I can help with:**
• Answer questions about course concepts and theories
• Explain definitions and technical terms  
• Clarify complex topics with examples from your notes
• Provide grounded answers with citations

**How to interact:**
• Ask technical questions about the course material
• Have casual conversations (I'm friendly! 😊)
• Request clarifications or deeper explanations

Feel free to say hi or jump straight into asking questions!"""
        
        return message
