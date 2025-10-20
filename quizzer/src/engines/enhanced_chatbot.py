#!/usr/bin/env python3
"""
Enhanced ChatGPT-like Chatbot Engine
Advanced AI assistant with conversation memory and comprehensive course knowledge
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import hashlib
from ..utils.enhanced_grounding import EnhancedGroundingEngine


class EnhancedChatbotEngine:
    """Advanced chatbot that provides ChatGPT-like interactions with course materials."""
    
    def __init__(self, repo_root: str, ai_engine, grounding_engine: EnhancedGroundingEngine = None):
        """Initialize enhanced chatbot engine.
        
        Args:
            repo_root: Root directory of ai-masters-notes repository
            ai_engine: AI engine for generating responses
            grounding_engine: Enhanced grounding engine for searching notes
        """
        self.repo_root = Path(repo_root)
        self.ai = ai_engine
        self.grounding = grounding_engine or EnhancedGroundingEngine(repo_root)
        
        # Course and note management
        self.current_course = None
        self.current_notes = []
        self.course_context = {}
        
        # Conversation memory management
        self.conversation_history = []
        self.conversation_memory = {}  # Key facts remembered from conversation
        self.max_history_length = 10  # Keep last N exchanges
        self.conversation_id = self._generate_conversation_id()
        
        # Context window management
        self.max_context_tokens = 3000  # Approximate token limit for context
        self.summarized_history = []  # Compressed older history
        
        # User preferences learned during conversation
        self.user_preferences = {
            "detail_level": "moderate",  # brief, moderate, detailed
            "learning_style": "balanced",  # visual, textual, examples, theoretical
            "expertise_level": "intermediate"  # beginner, intermediate, advanced
        }
        
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def set_course(self, course_code: str, note_files: List[str] = None):
        """Set the active course and intelligently load all available materials.
        
        Args:
            course_code: Course identifier (nlp, ml-dl, etc.)
            note_files: Optional specific note files (will auto-discover if not provided)
        """
        self.current_course = course_code
        
        # Get all available files for the course
        all_files = self.grounding.get_all_note_files(course_code)
        
        # Combine PDF and TeX files
        available_notes = []
        
        for pdf_path in all_files["pdf"]:
            available_notes.append(str(pdf_path.relative_to(self.repo_root)))
        
        for tex_path in all_files["tex"]:
            available_notes.append(str(tex_path.relative_to(self.repo_root)))
        
        # If specific files requested, validate them
        if note_files:
            valid_files, invalid_files = self.grounding.validate_note_files(note_files)
            if invalid_files:
                print(f"⚠️ Warning: Some files not found: {invalid_files}")
            self.current_notes = valid_files
        else:
            self.current_notes = available_notes
        
        # Pre-load course context for better responses
        self._initialize_course_context()
        
        # Reset conversation for new course
        self.conversation_history = []
        self.conversation_memory = {}
        
        print(f"🎓 Enhanced Chatbot ready for {course_code}")
        print(f"📚 Loaded {len(self.current_notes)} documents:")
        for note in self.current_notes[:5]:
            print(f"   • {Path(note).name}")
        if len(self.current_notes) > 5:
            print(f"   ... and {len(self.current_notes) - 5} more")
    
    def _initialize_course_context(self):
        """Pre-load important course context for faster responses."""
        if not self.current_course:
            return
        
        # Load key concepts, definitions, and theorems
        self.course_context = {
            "key_concepts": set(),
            "definitions": {},
            "theorems": [],
            "important_topics": []
        }
        
        # Extract from TeX files for structured content
        for note_file in self.current_notes:
            if note_file.endswith('.tex'):
                tex_path = self.repo_root / note_file
                content = self.grounding.extract_tex_content(tex_path)
                
                # Store key concepts
                self.course_context["key_concepts"].update(content.get("concepts", set()))
                
                # Store first few definitions and theorems
                for definition in content.get("definitions", [])[:3]:
                    # Extract concept name if possible
                    import re
                    concept_match = re.search(r'^([A-Za-z\s]+):', definition)
                    if concept_match:
                        concept_name = concept_match.group(1).strip()
                        self.course_context["definitions"][concept_name] = definition
                
                self.course_context["theorems"].extend(content.get("theorems", [])[:2])
    
    def _detect_user_intent(self, question: str) -> Dict[str, any]:
        """Detect the user's intent from their question.
        
        Returns:
            Dictionary with intent type and parameters
        """
        question_lower = question.lower().strip()
        
        # Casual/greeting detection
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in question_lower for greeting in greetings):
            return {"type": "greeting", "casual": True}
        
        # Thanks/appreciation
        if any(word in question_lower for word in ['thanks', 'thank you', 'appreciate']):
            return {"type": "thanks", "casual": True}
        
        # Goodbye
        if any(word in question_lower for word in ['bye', 'goodbye', 'see you']):
            return {"type": "goodbye", "casual": True}
        
        # Help request
        if 'help' in question_lower and len(question.split()) <= 5:
            return {"type": "help_request", "casual": False}
        
        # Definition request
        if any(phrase in question_lower for phrase in ['what is', 'define', 'definition of', 'what are']):
            return {"type": "definition", "casual": False}
        
        # Explanation request
        if any(phrase in question_lower for phrase in ['explain', 'how does', 'how do', 'why', 'describe']):
            return {"type": "explanation", "casual": False}
        
        # Comparison request
        if any(phrase in question_lower for phrase in ['difference between', 'compare', 'versus', 'vs']):
            return {"type": "comparison", "casual": False}
        
        # Example request
        if any(phrase in question_lower for phrase in ['example', 'instance', 'demonstrate', 'show me']):
            return {"type": "example_request", "casual": False}
        
        # List/enumeration request
        if any(phrase in question_lower for phrase in ['list', 'what are the', 'types of', 'kinds of']):
            return {"type": "enumeration", "casual": False}
        
        # Default: technical question
        return {"type": "technical_question", "casual": False}
    
    def _update_conversation_memory(self, question: str, answer: str, sources: List[Dict]):
        """Update conversation memory with key facts from the exchange."""
        # Extract key facts from the answer
        import re
        
        # Look for definitions
        definition_patterns = [
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+is\s+([^.]+\.)',
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+refers to\s+([^.]+\.)'
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, answer)
            for concept, definition in matches:
                if len(concept) > 2 and len(definition) > 10:
                    self.conversation_memory[concept] = {
                        "type": "definition",
                        "content": definition,
                        "timestamp": datetime.now().isoformat()
                    }
        
        # Remember topics discussed
        if "topics_discussed" not in self.conversation_memory:
            self.conversation_memory["topics_discussed"] = []
        
        # Extract main topic from question
        topics = self._extract_topics(question)
        for topic in topics:
            if topic not in self.conversation_memory["topics_discussed"]:
                self.conversation_memory["topics_discussed"].append(topic)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        topics = []
        text_lower = text.lower()
        
        # Check against known course concepts
        for concept in self.course_context.get("key_concepts", set()):
            if concept.lower() in text_lower:
                topics.append(concept)
        
        return topics[:3]  # Limit to top 3 topics
    
    def _build_context_aware_prompt(self, question: str, relevant_content: List[Dict], 
                                   intent: Dict) -> Tuple[str, str]:
        """Build a context-aware prompt based on conversation history and intent.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Adjust system prompt based on intent and user preferences
        base_system = """You are an expert AI teaching assistant with deep knowledge of university-level computer science courses. 
You provide clear, accurate, and pedagogically sound explanations based on course materials."""
        
        # Add personality based on intent
        if intent["type"] == "greeting":
            base_system += "\nBe warm and welcoming, showing enthusiasm for helping with the course."
        elif intent["type"] == "definition":
            base_system += "\nProvide clear, concise definitions followed by context and examples."
        elif intent["type"] == "explanation":
            base_system += "\nExplain concepts step-by-step with clarity, using examples where helpful."
        elif intent["type"] == "comparison":
            base_system += "\nClearly distinguish between concepts, highlighting key differences and similarities."
        
        # Add detail level preference
        detail_instructions = {
            "brief": "\nKeep responses concise and to the point.",
            "moderate": "\nProvide balanced responses with appropriate detail.",
            "detailed": "\nProvide comprehensive, in-depth explanations with multiple examples."
        }
        base_system += detail_instructions.get(self.user_preferences["detail_level"], "")
        
        # Build context from relevant content and history
        context_parts = []
        
        # Add relevant conversation history if it exists
        if self.conversation_history:
            recent_context = []
            for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                recent_context.append(f"Previous Q: {entry['question'][:100]}...")
                if len(entry['answer']) > 150:
                    recent_context.append(f"Previous A: {entry['answer'][:150]}...")
            
            if recent_context:
                context_parts.append("Recent conversation:\n" + "\n".join(recent_context))
        
        # Add course material context
        for idx, content in enumerate(relevant_content, 1):
            source_type = content.get("source_type", "unknown")
            
            if source_type == "tex" and content.get("structure_type") == "definition":
                context_parts.append(f"[Definition {idx}] {content['text'][:500]}")
            elif source_type == "tex" and content.get("structure_type") == "theorem":
                context_parts.append(f"[Theorem {idx}] {content['text'][:400]}")
            elif source_type == "tex" and content.get("structure_type") == "example":
                context_parts.append(f"[Example {idx}] {content['text'][:400]}")
            else:
                # Regular content
                context_parts.append(f"[Source {idx}] {content['text'][:600]}")
        
        context = "\n\n".join(context_parts)
        
        # Build user prompt with context
        user_prompt = f"""Question: {question}

Course Materials Context:
{context}

Instructions:
1. Answer based PRIMARILY on the provided course materials
2. Reference specific sources when applicable
3. If the materials don't fully cover the topic, indicate what IS available
4. Be conversational and helpful like ChatGPT
5. Use examples from the materials when possible
6. Maintain academic accuracy while being approachable"""
        
        return base_system, user_prompt
    
    def answer_question(self, question: str) -> Dict:
        """Answer a question with ChatGPT-like quality and context awareness.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        if not self.current_course:
            return {
                "answer": "📚 Please select a course first! I need to know which course materials to reference.",
                "sources": [],
                "found_info": False
            }
        
        # Detect user intent
        intent = self._detect_user_intent(question)
        
        # Handle casual conversation
        if intent.get("casual", False):
            response = self._handle_casual_interaction(question, intent)
            return {
                "answer": response,
                "sources": [],
                "found_info": True,
                "is_casual": True
            }
        
        # Perform comprehensive search across all materials
        relevant_content = self.grounding.semantic_search(
            question, 
            self.current_course, 
            max_results=8,  # Get more context
            include_tex=True
        )
        
        # Also get comprehensive context for key topics
        topics = self._extract_topics(question)
        comprehensive_context = {}
        for topic in topics[:2]:  # Get context for top 2 topics
            comprehensive_context[topic] = self.grounding.get_comprehensive_context(
                topic, 
                self.current_course, 
                max_sources=3
            )
        
        if not relevant_content and not comprehensive_context:
            return self._handle_no_content_found(question, intent)
        
        # Build enhanced context
        enhanced_content = relevant_content.copy()
        
        # Add definitions from comprehensive context
        for topic, context in comprehensive_context.items():
            for definition in context.get("definitions", [])[:2]:
                enhanced_content.append({
                    "source_type": "tex",
                    "structure_type": "definition",
                    "text": definition,
                    "topic": topic
                })
        
        # Build context-aware prompt
        system_prompt, user_prompt = self._build_context_aware_prompt(
            question, 
            enhanced_content[:6],  # Limit context size
            intent
        )
        
        # Generate response with higher quality settings
        try:
            answer_text = self.ai.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,  # Balanced creativity and accuracy
                max_tokens=1500  # Allow for comprehensive answers
            )
            
            if not answer_text:
                return self._handle_generation_failure(question)
            
            # Format answer with proper citations
            formatted_answer = self._format_answer_with_citations(
                answer_text, 
                enhanced_content,
                comprehensive_context
            )
            
            # Build source list
            sources = self._build_source_list(enhanced_content, comprehensive_context)
            
            # Update conversation history and memory
            self.conversation_history.append({
                "question": question,
                "answer": formatted_answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "intent": intent["type"]
            })
            
            # Trim history if too long
            if len(self.conversation_history) > self.max_history_length:
                # Summarize oldest entry before removing
                self._summarize_old_history()
                self.conversation_history.pop(0)
            
            # Update memory with key facts
            self._update_conversation_memory(question, formatted_answer, sources)
            
            return {
                "answer": formatted_answer,
                "sources": sources,
                "found_info": True,
                "intent": intent["type"],
                "confidence": self._calculate_confidence(enhanced_content, question)
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._handle_generation_failure(question)
    
    def _handle_casual_interaction(self, question: str, intent: Dict) -> str:
        """Handle casual/conversational interactions."""
        intent_type = intent["type"]
        
        responses = {
            "greeting": [
                "Hello! 👋 I'm your AI course assistant, ready to help you master the material. What would you like to learn about today?",
                "Hi there! 🎓 I have access to all your course materials and I'm here to help you understand any concept. What can I explain for you?",
                "Welcome! 📚 I'm here to make your learning journey easier. Ask me anything about the course content!"
            ],
            "thanks": [
                "You're very welcome! 😊 I'm glad I could help. Feel free to ask if you have more questions!",
                "Happy to help! 🌟 Learning is a journey, and I'm here to support you every step of the way.",
                "My pleasure! Keep those questions coming - that's how we learn best! 💪"
            ],
            "goodbye": [
                "Goodbye! 👋 Best of luck with your studies. Come back anytime you need help!",
                "See you later! 📖 Remember, consistent practice is key to mastering the material. You've got this!",
                "Take care! 🌟 Keep up the great work with your studies!"
            ],
            "help_request": [
                """I'm here to help you understand your course material! Here's what I can do:

📖 **Explain Concepts**: Ask me to explain any topic from your notes
🔍 **Define Terms**: Get clear definitions with examples
⚖️ **Compare Ideas**: Understand differences between related concepts
💡 **Provide Examples**: See practical applications of theories
📚 **Deep Dive**: Explore topics in detail with citations

Just ask your question naturally, like:
• "What is backpropagation?"
• "Explain the difference between supervised and unsupervised learning"
• "Give me an example of dynamic programming"

I'll search through all your course materials to give you accurate, comprehensive answers!"""
            ]
        }
        
        import random
        response_list = responses.get(intent_type, ["I'm here to help with your course material!"])
        return random.choice(response_list)
    
    def _handle_no_content_found(self, question: str, intent: Dict) -> Dict:
        """Handle cases where no relevant content is found."""
        suggestions = self._suggest_related_topics(question)
        
        response = f"""I couldn't find specific information about "{question}" in the loaded course materials. 

This could mean:
• The topic might not be covered in the current course
• The question might use different terminology than the course materials
• This might be a more advanced topic not yet covered

"""
        
        if suggestions:
            response += "📝 **Related topics I can help with:**\n"
            for suggestion in suggestions[:5]:
                response += f"• {suggestion}\n"
            response += "\nTry asking about one of these topics, or rephrase your question!"
        else:
            response += "💡 **Tip:** Try asking about core concepts from your course, or let me know which specific chapter or topic you're studying!"
        
        return {
            "answer": response,
            "sources": [],
            "found_info": False,
            "suggestions": suggestions
        }
    
    def _suggest_related_topics(self, question: str) -> List[str]:
        """Suggest related topics from the course."""
        suggestions = []
        question_lower = question.lower()
        
        # Check course concepts for partial matches
        for concept in list(self.course_context.get("key_concepts", set()))[:50]:
            concept_lower = concept.lower()
            # Check for partial word matches
            question_words = set(question_lower.split())
            concept_words = set(concept_lower.split())
            
            if question_words & concept_words:  # Intersection
                suggestions.append(concept)
        
        return suggestions[:5]
    
    def _format_answer_with_citations(self, answer: str, sources: List[Dict], 
                                     comprehensive_context: Dict) -> str:
        """Format answer with proper inline citations."""
        # Add citation markers if not present
        if "[Source" not in answer:
            # Add a citation footer
            answer += "\n\n📚 **Sources:**\n"
            
            seen_files = set()
            for idx, source in enumerate(sources[:3], 1):
                file_name = Path(source.get("path", "")).name
                if file_name not in seen_files:
                    seen_files.add(file_name)
                    
                    if source.get("source_type") == "tex":
                        location = source.get("section", "")
                    else:
                        location = f"Page {source.get('page', '?')}"
                    
                    answer += f"[{idx}] {file_name} - {location}\n"
        
        return answer
    
    def _build_source_list(self, enhanced_content: List[Dict], 
                          comprehensive_context: Dict) -> List[Dict]:
        """Build a clean source list for the response."""
        sources = []
        seen_sources = set()
        
        for content in enhanced_content[:5]:
            # Create unique source identifier
            source_id = f"{content.get('path', '')}_{content.get('page', '')}_{content.get('section', '')}"
            
            if source_id not in seen_sources:
                seen_sources.add(source_id)
                
                source = {
                    "type": content.get("source_type", "unknown"),
                    "path": Path(content.get("path", "")).name,
                    "excerpt": content.get("excerpt", "")[:200]
                }
                
                if content.get("source_type") == "tex":
                    source["location"] = content.get("section", "Unknown section")
                else:
                    source["location"] = f"Page {content.get('page', '?')}"
                
                sources.append(source)
        
        return sources
    
    def _calculate_confidence(self, sources: List[Dict], question: str) -> float:
        """Calculate confidence score for the answer."""
        if not sources:
            return 0.0
        
        # Base confidence on number and quality of sources
        confidence = min(0.3 + (len(sources) * 0.1), 0.8)
        
        # Boost for high-scoring sources
        max_score = max(s.get("score", 0) for s in sources)
        if max_score > 20:
            confidence = min(confidence + 0.2, 0.95)
        
        # Boost for structured content (definitions, theorems)
        structured_sources = sum(1 for s in sources if s.get("structure_type") in 
                               ["definition", "theorem", "example"])
        confidence += structured_sources * 0.05
        
        return min(confidence, 0.95)
    
    def _handle_generation_failure(self, question: str) -> Dict:
        """Handle AI generation failures gracefully."""
        return {
            "answer": """I encountered an issue generating a response. Let me try to help differently:

The question you asked was about: """ + question + """

Please try:
1. Rephrasing your question
2. Breaking it into smaller parts
3. Asking about specific concepts mentioned in your course

I'm still here to help! 🤝""",
            "sources": [],
            "found_info": False,
            "error": True
        }
    
    def _summarize_old_history(self):
        """Summarize old conversation history before removal."""
        if self.conversation_history:
            oldest = self.conversation_history[0]
            summary = {
                "question_summary": oldest["question"][:100],
                "key_topics": self._extract_topics(oldest["question"]),
                "timestamp": oldest.get("timestamp", ""),
                "intent": oldest.get("intent", "unknown")
            }
            self.summarized_history.append(summary)
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return {"message": "No conversation history yet."}
        
        summary = {
            "total_exchanges": len(self.conversation_history),
            "topics_discussed": self.conversation_memory.get("topics_discussed", []),
            "key_concepts_learned": list(self.conversation_memory.keys()),
            "conversation_id": self.conversation_id,
            "duration": self._calculate_conversation_duration()
        }
        
        # Add most recent questions
        summary["recent_questions"] = [
            entry["question"][:100] for entry in self.conversation_history[-3:]
        ]
        
        return summary
    
    def _calculate_conversation_duration(self) -> str:
        """Calculate conversation duration."""
        if not self.conversation_history:
            return "0 minutes"
        
        try:
            first_timestamp = self.conversation_history[0].get("timestamp", "")
            last_timestamp = self.conversation_history[-1].get("timestamp", "")
            
            if first_timestamp and last_timestamp:
                from datetime import datetime
                first = datetime.fromisoformat(first_timestamp)
                last = datetime.fromisoformat(last_timestamp)
                duration = last - first
                minutes = duration.total_seconds() / 60
                return f"{int(minutes)} minutes"
        except:
            pass
        
        return "Unknown duration"
    
    def clear_history(self):
        """Clear conversation history while preserving learned preferences."""
        self.conversation_history = []
        self.summarized_history = []
        self.conversation_memory = {}
        self.conversation_id = self._generate_conversation_id()
    
    def set_preference(self, preference: str, value: str):
        """Set user preference for response style.
        
        Args:
            preference: Preference type (detail_level, learning_style, expertise_level)
            value: Preference value
        """
        if preference in self.user_preferences:
            self.user_preferences[preference] = value
            print(f"✅ Updated {preference} to {value}")
    
    def get_course_overview(self) -> str:
        """Get an enhanced welcome message with course insights."""
        if not self.current_course or not self.current_notes:
            return "No course selected. Please select a course to begin!"
        
        # Count different types of materials
        pdf_count = sum(1 for note in self.current_notes if note.endswith('.pdf'))
        tex_count = sum(1 for note in self.current_notes if note.endswith('.tex'))
        
        # Get key concepts count
        concept_count = len(self.course_context.get("key_concepts", set()))
        
        message = f"""🎓 **Welcome to Your AI Course Assistant!**

I'm an advanced ChatGPT-like assistant specialized in your course materials. 

**📚 Loaded Resources:**
• {pdf_count} PDF documents
• {tex_count} TeX documents  
• {concept_count} key concepts identified
• {len(self.course_context.get('definitions', {}))} definitions indexed
• {len(self.course_context.get('theorems', []))} theorems available

**🚀 What makes me special:**
• **Comprehensive Understanding**: I analyze both PDF and TeX files for complete coverage
• **Smart Context**: I remember our conversation and learn your preferences
• **Academic Accuracy**: All answers are grounded in your actual course materials
• **Structured Learning**: I can provide definitions, theorems, examples, and explanations
• **Intelligent Search**: I use semantic search to find the most relevant information

**💬 How to interact:**
• Ask questions naturally, just like ChatGPT
• Request definitions, explanations, or examples
• Ask for comparisons between concepts
• Request step-by-step explanations
• Feel free to have casual conversations too!

**🎯 Current Preferences:**
• Detail Level: {self.user_preferences['detail_level']}
• Learning Style: {self.user_preferences['learning_style']}
• Expertise: {self.user_preferences['expertise_level']}

Ready to help you excel in your studies! What would you like to explore first? 🌟"""
        
        return message
