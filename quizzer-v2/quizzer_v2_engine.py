#!/usr/bin/env python3
"""
Quizzer V2 Engine
Main engine coordinating question generation and grading
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from pdf_grounding import PDFGroundingEngine
from question_generator import QuestionGenerator
from grading_engine import GradingEngine


class QuizzerV2:
    """Grounded Q&A engine for exam-quality questions."""
    
    # Course configurations
    COURSES = {
        "nlp": {
            "name": "Natural Language Processing",
            "default_notes": ["courses/natural-language-processing/notes/NLP Appunti.pdf"]
        },
        "ml-dl": {
            "name": "Machine Learning & Deep Learning",
            "default_notes": ["courses/machine-learning-and-deep-learning/notes/ML&DL Appunti.pdf"]
        },
        "ar": {
            "name": "Automated Reasoning",
            "default_notes": ["courses/automated-reasoning/notes/AR Appunti.pdf"]
        },
        "planning": {
            "name": "Planning",
            "default_notes": ["courses/planning-and-reinforcement-learning/notes/Planning appunti.pdf"]
        },
        "hci": {
            "name": "Human-Computer Interaction",
            "default_notes": [
                "courses/human-computer-interaction/notes/HCI Theory 1 Appunti.pdf",
                "courses/human-computer-interaction/notes/HCI Theory 2 Appunti.pdf"
            ]
        }
    }
    
    def __init__(self, repo_root: str, ai_engine):
        """Initialize Quizzer V2.
        
        Args:
            repo_root: Root directory of ai-masters-notes repository
            ai_engine: AI engine for generation and grading
        """
        self.repo_root = Path(repo_root)
        self.ai = ai_engine
        
        # Initialize components
        self.grounding = PDFGroundingEngine(repo_root)
        self.question_gen = QuestionGenerator(repo_root, ai_engine)
        self.grader = GradingEngine(repo_root, ai_engine)
        
        # Session state
        self.current_quiz = None
        self.current_question_idx = 0
    
    def generate_quiz(self, request: Dict) -> Dict:
        """Generate a quiz from JSON request.
        
        Args:
            request: JSON request with course, topics, question types, etc.
            
        Returns:
            JSON response with questions and metadata
        """
        # Validate request
        course = request.get("course")
        if not course or course not in self.COURSES:
            return {
                "error": {
                    "type": "invalid_course",
                    "message": f"Course must be one of: {list(self.COURSES.keys())}",
                    "available_courses": list(self.COURSES.keys())
                }
            }
        
        # Set default note files if not provided
        if "note_files" not in request or not request["note_files"]:
            request["note_files"] = self.COURSES[course]["default_notes"]
        
        # Validate note files exist
        missing_files = []
        for note_file in request["note_files"]:
            if not self.grounding.validate_note_file(note_file):
                missing_files.append(note_file)
        
        if missing_files:
            return {
                "error": {
                    "type": "missing_notes",
                    "message": f"Note files not found: {missing_files}",
                    "requested_files": missing_files
                }
            }
        
        # Set defaults for optional fields
        request.setdefault("topics", ["general"])
        request.setdefault("question_types", ["short_answer"])
        request.setdefault("difficulty", "standard")
        request.setdefault("num_questions", 10)
        request.setdefault("include_solutions", True)
        request.setdefault("grading_mode", "strict_concepts")
        request.setdefault("max_points_per_question", 10)
        
        # Generate questions
        result = self.question_gen.generate_questions(request)
        
        # Store current quiz
        self.current_quiz = result
        self.current_question_idx = 0
        
        return result
    
    def grade_answer(self, submission: Dict) -> Dict:
        """Grade a user's answer.
        
        Args:
            submission: JSON with question_id and answer
            
        Returns:
            JSON grading result
        """
        question_id = submission.get("question_id")
        user_answer = submission.get("answer", "")
        
        if not self.current_quiz:
            return {
                "error": {
                    "type": "no_active_quiz",
                    "message": "No active quiz. Generate questions first."
                }
            }
        
        # Find question
        question = None
        for q in self.current_quiz.get("questions", []):
            if q.get("id") == question_id:
                question = q
                break
        
        if not question:
            return {
                "error": {
                    "type": "question_not_found",
                    "message": f"Question ID not found: {question_id}"
                }
            }
        
        # Grade answer
        result = self.grader.grade_answer(question, user_answer)
        
        return result
    
    def get_current_question(self) -> Optional[Dict]:
        """Get current question in quiz.
        
        Returns:
            Current question or None
        """
        if not self.current_quiz:
            return None
        
        questions = self.current_quiz.get("questions", [])
        
        if self.current_question_idx < len(questions):
            return questions[self.current_question_idx]
        
        return None
    
    def next_question(self) -> Optional[Dict]:
        """Move to next question.
        
        Returns:
            Next question or None if quiz complete
        """
        if not self.current_quiz:
            return None
        
        self.current_question_idx += 1
        return self.get_current_question()
    
    def get_quiz_progress(self) -> Dict:
        """Get current quiz progress.
        
        Returns:
            Progress information
        """
        if not self.current_quiz:
            return {
                "active": False,
                "current": 0,
                "total": 0,
                "completed": False
            }
        
        total = len(self.current_quiz.get("questions", []))
        
        return {
            "active": True,
            "current": self.current_question_idx + 1,
            "total": total,
            "completed": self.current_question_idx >= total
        }
    
    def reset_quiz(self):
        """Reset quiz state."""
        self.current_quiz = None
        self.current_question_idx = 0
    
    def validate_topics_in_notes(self, course: str, topics: List[str]) -> Dict:
        """Check which topics are covered in the notes.
        
        Args:
            course: Course identifier
            topics: List of topics to check
            
        Returns:
            Dictionary with found/not_found topics
        """
        if course not in self.COURSES:
            return {"error": "Invalid course"}
        
        note_files = self.COURSES[course]["default_notes"]
        
        found_topics = []
        not_found = []
        
        for topic in topics:
            topic_found = False
            
            for note_file in note_files:
                pdf_path = self.repo_root / note_file
                
                if pdf_path.exists():
                    results = self.grounding.search_content(pdf_path, topic, max_results=1)
                    
                    if results and results[0]["score"] > 0:
                        found_topics.append({
                            "topic": topic,
                            "file": note_file,
                            "page": results[0]["page"]
                        })
                        topic_found = True
                        break
            
            if not topic_found:
                not_found.append(topic)
        
        # Suggest nearby topics for not found ones
        suggestions = {}
        if not_found:
            # Get all available content (sample pages from notes)
            for topic in not_found:
                # Simple suggestion: use course name + general topics
                suggestions[topic] = [
                    f"Check {self.COURSES[course]['name']} course materials",
                    "Try more general topic keywords"
                ]
        
        return {
            "found": found_topics,
            "not_found": not_found,
            "suggestions": suggestions
        }
    
    def get_available_courses(self) -> List[Dict]:
        """Get list of available courses.
        
        Returns:
            List of course information
        """
        courses = []
        
        for code, info in self.COURSES.items():
            # Check if notes exist
            notes_exist = []
            for note_file in info["default_notes"]:
                path = self.repo_root / note_file
                if path.exists():
                    notes_exist.append(note_file)
            
            courses.append({
                "code": code,
                "name": info["name"],
                "notes_available": len(notes_exist),
                "note_files": notes_exist
            })
        
        return courses


def main():
    """Test the Quizzer V2 engine."""
    import sys
    from pathlib import Path
    
    # Find repo root
    repo_root = Path(__file__).parent.parent
    
    # Check if local AI is available
    try:
        from local_ai import LocalAI
        ai = LocalAI("llama3.2:3b")
        print("✓ Using Local AI (Ollama)")
    except Exception as e:
        print(f"✗ Local AI not available: {e}")
        print("Please install Ollama and pull llama3.2:3b model")
        sys.exit(1)
    
    # Initialize engine
    engine = QuizzerV2(str(repo_root), ai)
    
    print("\n" + "="*60)
    print("QUIZZER V2 - Grounded Q&A Engine")
    print("="*60)
    
    # Show available courses
    print("\n📚 Available Courses:")
    courses = engine.get_available_courses()
    for course in courses:
        print(f"  - {course['code']}: {course['name']} ({course['notes_available']} notes)")
    
    # Example: Generate NLP quiz
    print("\n🎯 Generating sample quiz...")
    
    request = {
        "course": "nlp",
        "topics": ["tokenization", "edit distance"],
        "question_types": ["short_answer", "mcq_single"],
        "difficulty": "standard",
        "num_questions": 3,
        "include_solutions": True,
        "grading_mode": "strict_concepts",
        "max_points_per_question": 10
    }
    
    result = engine.generate_quiz(request)
    
    if "error" in result:
        print(f"\n✗ Error: {result['error']}")
    else:
        print(f"\n✓ Generated {result['meta']['question_count']} questions")
        print(f"\nNotes used:")
        for note in result['meta']['notes_used']:
            print(f"  - {note['path']} (pages: {note['pages']})")
        
        # Show first question
        if result['questions']:
            q = result['questions'][0]
            print(f"\n📝 Sample Question ({q['type']}):")
            print(f"   {q['prompt']}")
            print(f"\n   Grounding: {q['grounding'][0]['path']}, p.{q['grounding'][0]['page']}")


if __name__ == "__main__":
    main()
