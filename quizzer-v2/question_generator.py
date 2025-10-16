#!/usr/bin/env python3
"""
Question Generator
Generates grounded exam-quality questions from PDF notes
"""

import json
import random
from typing import List, Dict, Optional
from pathlib import Path
from pdf_grounding import PDFGroundingEngine


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
                        section = sections[j % len(sections)]
                        
                        # Choose question type
                        qtype = random.choice(question_types)
                        
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
                        
                        if question:
                            questions.append(question)
                        
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
                
                if question:
                    questions.append(question)
        
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
        """Generate a single question with grounding.
        
        Args:
            qtype: Question type
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
        # Build prompt based on question type
        if qtype == "mcq_single":
            prompt = self._build_mcq_prompt(topic, content, difficulty, single=True)
        elif qtype == "mcq_multi":
            prompt = self._build_mcq_prompt(topic, content, difficulty, single=False)
        elif qtype == "short_answer":
            prompt = self._build_short_answer_prompt(topic, content, difficulty)
        elif qtype == "derivation":
            prompt = self._build_derivation_prompt(topic, content, difficulty)
        elif qtype == "proof":
            prompt = self._build_proof_prompt(topic, content, difficulty)
        elif qtype == "code":
            prompt = self._build_code_prompt(topic, content, difficulty)
        else:
            prompt = self._build_short_answer_prompt(topic, content, difficulty)
        
        # Generate question using AI
        try:
            response = self.ai.generate_json(
                prompt,
                "You are an expert professor creating exam questions. Generate ONLY from the provided content. Respond with valid JSON only.",
                temperature=0.8,  # Higher for faster generation
                max_tokens=600  # Reduced for speed
            )
            
            if not response or "error" in response:
                return None
            
            # Build question object
            question = {
                "id": question_id,
                "type": qtype,
                "prompt": response.get("prompt", response.get("question", "")),
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
            if qtype in ["mcq_single", "mcq_multi"]:
                question["options"] = response.get("options", [])
                question["answer_key"] = {
                    "correct": response.get("correct", []),
                    "concepts_required": response.get("concepts", [topic]),
                    "max_points": max_points
                }
            else:
                concepts = response.get("concepts", [topic])
                question["answer_key"] = {
                    "canonical_answer": response.get("answer", ""),
                    "concepts_required": concepts,
                    "point_breakdown": self._generate_rubric(topic, max_points, concepts),
                    "max_points": max_points
                }
            
            return question
            
        except Exception as e:
            print(f"Error generating question: {e}")
            return None
    
    def _build_mcq_prompt(self, topic: str, content: str, difficulty: str,
                          single: bool = True) -> str:
        """Build prompt for MCQ generation following specification."""
        num_correct = "exactly 1" if single else "2 or more"
        
        difficulty_guide = {
            "intro": "recall and comprehension (definitions, basic facts)",
            "standard": "concept application (use ideas in new context)",
            "advanced": "integration of multiple concepts",
            "exam": "rigorous, multi-step reasoning required"
        }.get(difficulty, "standard level")
        
        return f"""You are an expert professor creating exam questions. Generate ONLY from the provided content.

KNOWLEDGE CONSTRAINT:
- The ONLY valid source is the content below
- Every part of the question and all options must be traceable to this content
- No external knowledge or invented facts

CONTENT FROM COURSE NOTES (Topic: {topic}):
{content[:800]}

TASK: Create a multiple choice question

REQUIREMENTS:
1. Question Clarity:
   - Self-contained (understandable without external context)
   - Clear, academic phrasing
   - No ambiguity or opinion-based wording

2. Options:
   - {num_correct} correct answer(s)
   - 3-4 total options (A, B, C, D)
   - Distractors must be plausible but clearly incorrect based on the content
   - Each option must relate to concepts in the content

3. Difficulty: {difficulty_guide}

4. Grounding:
   - Must be answerable using ONLY the content above
   - Extract key concepts that the question tests

Respond with JSON:
{{
    "prompt": "<question text>",
    "options": ["A: option 1", "B: option 2", "C: option 3", "D: option 4"],
    "correct": ["A"],
    "concepts": ["<concept 1 from content>", "<concept 2 from content>"]
}}"""
    
    def _build_short_answer_prompt(self, topic: str, content: str,
                                    difficulty: str) -> str:
        """Build prompt for short answer generation following specification."""
        difficulty_guide = {
            "intro": "recall and comprehension",
            "standard": "concept application and explanation",
            "advanced": "integration and analysis",
            "exam": "rigorous reasoning with multiple concepts"
        }.get(difficulty, "standard")
        
        return f"""You are an expert professor creating exam questions. Generate ONLY from the provided content.

KNOWLEDGE CONSTRAINT:
- The ONLY valid source is the content below
- Question and answer must be traceable to this content
- No external knowledge allowed

CONTENT FROM COURSE NOTES (Topic: {topic}):
{content[:800]}

TASK: Create a short answer question

REQUIREMENTS:
1. Question Clarity:
   - Self-contained and unambiguous
   - Test understanding, not just memorization
   - Answerable in 2-4 sentences using the content

2. Difficulty: {difficulty_guide}

3. Grounding:
   - Must be answerable using ONLY the content above
   - Identify all key concepts tested
   - Provide canonical answer derived from content

Respond with JSON:
{{
    "prompt": "<question text>",
    "answer": "<canonical answer from content, 2-4 sentences>",
    "concepts": ["<concept 1 tested>", "<concept 2 tested>"]
}}"""
    
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
