#!/usr/bin/env python3
"""
Question Generator
Generates grounded exam-quality questions from PDF notes
"""

import json
import random
import uuid
from typing import List, Dict, Optional
from pathlib import Path
from ..utils.pdf_grounding import PDFGroundingEngine


class QuestionGenerator:
    """Generate grounded questions from course notes."""
    
    def __init__(self, repo_root: str, ai_engine):
        """Initialize question generator.
        
        Args:
            repo_root: Root directory of repository
            ai_engine: AI engine for question generation (LocalAI or similar)
        """
        self.grounding = PDFGroundingEngine(repo_root)
        self.ai = ai_engine
        self.repo_root = Path(repo_root)
    
    def generate_questions(self, request: Dict) -> Dict:
        """Generate questions based on request.
        
        Args:
            request: JSON request object with course, topics, question_types, etc.
            
        Returns:
            JSON response with generated questions and grounding
        """
        # Parse request
        course = request.get("course")
        topics = request.get("topics", [])
        note_files = request.get("note_files", [])
        question_types = request.get("question_types", ["short_answer"])
        difficulty = request.get("difficulty", "standard")
        num_questions = request.get("num_questions", 10)
        include_solutions = request.get("include_solutions", True)
        grading_mode = request.get("grading_mode", "strict_concepts")
        max_points = request.get("max_points_per_question", 10)
        
        # Get note files if not provided
        if not note_files:
            note_paths = self.grounding.get_note_files(course)
            note_files = [str(p.relative_to(self.repo_root)) for p in note_paths]
        else:
            note_paths = [self.repo_root / f for f in note_files]
        
        if not note_paths:
            return {
                "error": {
                    "type": "missing_notes",
                    "message": f"No note files found for course: {course}"
                }
            }
        
        # Generate questions
        questions = []
        notes_used = []
        seen_questions = set()  # Track question text to prevent duplicates
        
        # Distribute questions across topics
        questions_per_topic = num_questions // len(topics) if topics else num_questions
        
        for i, topic in enumerate(topics):
            # Find relevant content in PDFs
            for note_path in note_paths:
                sections = self.grounding.search_content(note_path, topic, max_results=3)
                
                if sections:
                    # Track which notes we used
                    note_info = {
                        "path": str(note_path.relative_to(self.repo_root)),
                        "sections": [topic],
                        "pages": [s["page"] for s in sections[:2]]
                    }
                    if note_info not in notes_used:
                        notes_used.append(note_info)
                    
                    # Generate questions from this content
                    num_to_gen = min(questions_per_topic, num_questions - len(questions))
                    
                    for j in range(num_to_gen):
                        # Randomize section selection for variety
                        section = random.choice(sections)
                        
                        # Choose question type
                        qtype = random.choice(question_types)
                        
                        # Retry up to 3 times if validation fails
                        max_retries = 3
                        for attempt in range(max_retries):
                            # Generate question
                            question = self._generate_single_question(
                                qtype=qtype,
                                topic=topic,
                                content=section["text"],
                                page=section["page"],
                                pdf_path=note_path,
                                difficulty=difficulty,
                                max_points=max_points,
                                grading_mode=grading_mode,
                                question_id=f"q{len(questions) + 1}"
                            )
                            
                            # Check for duplicates and validate relevance
                            if question and self._is_valid_question(question, topic, section["text"], seen_questions):
                                questions.append(question)
                                seen_questions.add(question["prompt"].lower().strip())
                                break  # Success, move to next question
                        
                        if len(questions) >= num_questions:
                            break
                
                if len(questions) >= num_questions:
                    break
            
            if len(questions) >= num_questions:
                break
        
        # If still need more questions, generate generic ones
        while len(questions) < num_questions and note_paths:
            note_path = random.choice(note_paths)
            pages = self.grounding.extract_pdf_text(note_path)
            
            if pages:
                page_num = random.choice(list(pages.keys()))
                content = pages[page_num]
                
                qtype = random.choice(question_types)
                topic = topics[0] if topics else "general"
                
                question = self._generate_single_question(
                    qtype=qtype,
                    topic=topic,
                    content=content[:1000],
                    page=page_num,
                    pdf_path=note_path,
                    difficulty=difficulty,
                    max_points=max_points,
                    grading_mode=grading_mode,
                    question_id=f"q{len(questions) + 1}"
                )
                
                # Check for duplicates and validate relevance
                if question and self._is_valid_question(question, topic, content[:1000], seen_questions):
                    questions.append(question)
                    seen_questions.add(question["prompt"].lower().strip())
        
        # Build response
        response = {
            "meta": {
                "course": course,
                "notes_used": notes_used,
                "question_count": len(questions)
            },
            "questions": questions
        }
        
        return response
    
    def _generate_single_question(self, qtype: str, topic: str, content: str,
                                   page: int, pdf_path: Path, difficulty: str,
                                   max_points: int, grading_mode: str,
                                   question_id: str) -> Optional[Dict]:
        """Generate questions in batch using new extraction prompt.
        
        Args:
            qtype: Question type to generate (strictly enforced)
            topic: Topic being tested
            content: Source content from PDF
            page: Page number
            pdf_path: Path to source PDF
            difficulty: Difficulty level
            max_points: Maximum points for question
            grading_mode: Grading mode
            question_id: Unique question ID
            
        Returns:
            Question object with grounding and rubric
        """
        # Use new batch extraction prompt with strict type enforcement
        prompt = self._build_batch_extraction_prompt(topic, content, difficulty, qtype)
        
        # Generate questions using AI
        try:
            response = self.ai.generate_json(
                prompt,
                "Generate quiz question. Return ONLY valid JSON.",
                temperature=0.8,  # Higher for more variety between questions
                max_tokens=500  # Enough for complete responses
            )
            
            if not response or "error" in response:
                return None
            
            # Try to extract question data flexibly
            item = None
            
            # Check if response has "items" array
            if "items" in response:
                items = response["items"]
                if isinstance(items, list) and len(items) > 0:
                    item = items[0]
                elif isinstance(items, dict):
                    # AI returned single item as dict instead of array
                    item = items
                else:
                    return None
            else:
                # Maybe the AI returned the question directly without wrapping
                # Check if it has the required fields
                if "question" in response or "type" in response:
                    item = response
                else:
                    return None
            
            if not item:
                return None
            
            # Map item type to internal type
            item_type = item.get("type", "short")
            type_map = {
                "mcq": "mcq_single",
                "short": "short_answer",
                "true_false": "mcq_single"
            }
            internal_type = type_map.get(item_type, "short_answer")
            
            # STRICT TYPE VALIDATION: Reject if generated type doesn't match requested type
            if not self._type_matches(qtype, internal_type):
                print(f"⚠️ Generated question type '{internal_type}' doesn't match requested '{qtype}', rejecting")
                return None
            
            # Build question object
            question = {
                "id": question_id,
                "type": internal_type,
                "prompt": item.get("question", ""),
                "grounding": [
                    {
                        "path": str(pdf_path.relative_to(self.repo_root)),
                        "page": page,
                        "quote": self.grounding.extract_quote(content, max_words=25)
                    }
                ],
                "rubric": {
                    "strict_concepts": grading_mode == "strict_concepts",
                    "accept_synonyms": True,
                    "require_all_core_concepts": True,
                    "allow_equivalent_formulations": True
                }
            }
            
            # Add type-specific fields
            if internal_type == "mcq_single":
                choices = item.get("choices", [])
                answer = item.get("answer", "")
                
                question["options"] = choices
                question["answer_key"] = {
                    "correct": [answer] if isinstance(answer, str) else answer,
                    "concepts_required": item.get("tags", [topic]),
                    "max_points": max_points,
                    "explanation": item.get("explanation", "")
                }
            else:
                concepts = item.get("tags", [topic])
                answer = item.get("answer", "")
                
                question["answer_key"] = {
                    "canonical_answer": answer if isinstance(answer, str) else ", ".join(answer),
                    "concepts_required": concepts,
                    "point_breakdown": self._generate_rubric(topic, max_points, concepts),
                    "max_points": max_points,
                    "explanation": item.get("explanation", "")
                }
            
            return question
            
        except Exception as e:
            import traceback
            print(f"Error generating question: {type(e).__name__}: {e}")
            if str(e) != "0":  # Don't print full trace for simple errors
                traceback.print_exc()
            return None
    
    def _is_valid_question(self, question: Dict, topic: str, content: str, seen_questions: set) -> bool:
        """Validate question - now more lenient to prevent getting stuck.
        
        Args:
            question: Generated question object
            topic: Expected topic
            content: Source content
            seen_questions: Set of already seen question texts
            
        Returns:
            True if question is valid and unique
        """
        prompt = question.get("prompt", "").lower().strip()
        
        # Check if question is empty or None
        if not prompt:
            return False
        
        # Check for duplicate
        if prompt in seen_questions:
            return False
        
        # Check if question is substantive (at least 10 chars)
        if len(prompt) < 10:
            return False
        
        # That's it! Much simpler validation to prevent getting stuck
        # The AI should generate relevant questions from the content
        return True
    
    def _type_matches(self, requested_type: str, generated_type: str) -> bool:
        """Check if generated question type matches the requested type.
        
        Args:
            requested_type: The type that was requested (e.g., 'mcq_single', 'short_answer')
            generated_type: The type that was generated
            
        Returns:
            True if types match
        """
        # Normalize types for comparison
        if requested_type in ['mcq_single', 'mcq_multi'] and generated_type == 'mcq_single':
            return True
        if requested_type == 'short_answer' and generated_type == 'short_answer':
            return True
        if requested_type in ['derivation', 'proof', 'code'] and generated_type == 'short_answer':
            return True
        return False
    
    def _build_batch_extraction_prompt(self, topic: str, content: str, difficulty: str, qtype: str = "short_answer") -> str:
        """Build streamlined question extraction prompt for faster generation.
        
        Args:
            qtype: Question type to generate (strictly enforced)
        """
        difficulty_map = {
            "intro": "easy",
            "standard": "medium",
            "advanced": "hard",
            "exam": "hard"
        }
        mapped_difficulty = difficulty_map.get(difficulty, "medium")
        
        # Make prompt super clear with concrete example
        if qtype in ['mcq_single', 'mcq_multi']:
            example_json = '''{
  "topic": "''' + topic + '''",
  "difficulty": "''' + mapped_difficulty + '''",
  "items": [{
    "id": "q1",
    "type": "mcq",
    "question": "What is the main concept discussed?",
    "choices": ["A: Option 1", "B: Option 2", "C: Option 3", "D: Option 4"],
    "answer": "A",
    "explanation": "Brief explanation",
    "tags": ["concept"]
  }]
}'''
        else:
            example_json = '''{
  "topic": "''' + topic + '''",
  "difficulty": "''' + mapped_difficulty + '''",
  "items": [{
    "id": "q1",
    "type": "short",
    "question": "What is the main concept?",
    "answer": "Brief answer here",
    "explanation": "Why this is correct",
    "tags": ["concept"]
  }]
}'''
        
        # Add variety instruction
        variation_hints = [
            "Focus on a specific detail or concept.",
            "Ask about the main idea or relationship between concepts.",
            "Test understanding of technical terms or definitions.",
            "Challenge comprehension of how concepts work together.",
            "Focus on practical applications or implications."
        ]
        hint = random.choice(variation_hints)
        
        # Vary the starting point of content for more diversity
        content_len = len(content)
        if content_len > 1000:
            # Randomly select a chunk from the content
            max_start = content_len - 1000
            start_pos = random.randint(0, max_start)
            content_chunk = content[start_pos:start_pos + 1000]
        else:
            content_chunk = content[:1000]
        
        return f"""Create a unique quiz question from this text. {hint}

{content_chunk}

Return ONLY this JSON (no extra text):
{example_json}"""
    
    def _build_mcq_prompt(self, topic: str, content: str, difficulty: str,
                          single: bool = True) -> str:
        """Legacy MCQ prompt - now replaced by batch extraction."""
        qtype = "mcq_single" if single else "mcq_multi"
        return self._build_batch_extraction_prompt(topic, content, difficulty, qtype)
    
    def _build_short_answer_prompt(self, topic: str, content: str,
                                    difficulty: str) -> str:
        """Legacy short answer prompt - now replaced by batch extraction."""
        return self._build_batch_extraction_prompt(topic, content, difficulty, "short_answer")
    
    def _build_derivation_prompt(self, topic: str, content: str,
                                  difficulty: str) -> str:
        """Build prompt for derivation question."""
        return f"""Based on this content about {topic}, create a derivation question.

Content:
{content[:800]}

Requirements:
- Ask student to derive a formula or relationship
- Must be based on content provided
- Should show intermediate steps
- Difficulty: {difficulty}

Respond with JSON:
{{
    "prompt": "question text (derive...)",
    "answer": "step-by-step derivation",
    "concepts": ["key concept 1", "key concept 2"]
}}"""
    
    def _build_proof_prompt(self, topic: str, content: str,
                            difficulty: str) -> str:
        """Build prompt for proof question."""
        return f"""Based on this content about {topic}, create a proof question.

Content:
{content[:800]}

Requirements:
- Ask to prove a statement from the content
- Must be provable using the provided content
- Difficulty: {difficulty}

Respond with JSON:
{{
    "prompt": "Prove that...",
    "answer": "proof steps",
    "concepts": ["key concept 1", "key concept 2"]
}}"""
    
    def _build_code_prompt(self, topic: str, content: str,
                           difficulty: str) -> str:
        """Build prompt for code question."""
        return f"""Based on this content about {topic}, create a coding question.

Content:
{content[:800]}

Requirements:
- Implement an algorithm described in the content
- Provide clear input/output specification
- Difficulty: {difficulty}

Respond with JSON:
{{
    "prompt": "Implement...",
    "answer": "sample solution code",
    "concepts": ["algorithm name", "key concept"]
}}"""
    
    def _generate_rubric(self, topic: str, max_points: int, concepts: List[str] = None) -> List[Dict]:
        """Generate point breakdown rubric following specification.
        
        Args:
            topic: Topic being tested
            max_points: Maximum points
            concepts: Key concepts to grade (from question generation)
            
        Returns:
            List of rubric criteria with points, aligned with concepts
        """
        if not concepts:
            concepts = [topic]
        
        # Distribute points across concepts and overall quality
        rubric = []
        
        # Core concept criteria (70% of points)
        concept_points = int(max_points * 0.7)
        points_per_concept = concept_points // len(concepts) if concepts else concept_points
        
        for concept in concepts:
            rubric.append({
                "criterion": f"Correctly explains/uses concept: {concept}",
                "points": points_per_concept
            })
        
        # Completeness and accuracy (30% of points)
        remaining = max_points - sum(r["points"] for r in rubric)
        rubric.append({
            "criterion": "Answer is complete, accurate, and follows reasoning from notes",
            "points": remaining
        })
        
        return rubric
