#!/usr/bin/env python3
"""
Quizzer V2 Engine
Main engine coordinating question generation and grading
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from ..utils.pdf_grounding import PDFGroundingEngine
from .question_generator import QuestionGenerator
from .grading_engine import GradingEngine
from ..utils.user_manager import UserManager
from .rating_generator import RatingGenerator
from .chatbot_engine import ChatbotEngine


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
        self.user_manager = UserManager(str(Path(repo_root) / "user_data" / "users.db"))
        self.rating_gen = RatingGenerator(ai_engine)
        self.chatbot = ChatbotEngine(repo_root, ai_engine, self.grounding)
        
        # Session state
        self.current_quiz = None
        self.current_question_idx = 0
        self.quiz_request = None  # Store original request for lazy generation
        self.generated_questions = []  # Questions generated so far
        self.current_user_id = None  # Currently logged in user
        self.current_session_id = None  # Current quiz session
        self.session_total_points = 0  # Total points earned in session
        self.session_max_points = 0  # Maximum possible points in session
        self.current_course_code = None  # Currently selected course
    
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
        
        # Store request for lazy generation
        self.quiz_request = request
        self.generated_questions = []
        self.current_question_idx = 0
        
        # Store current course and configure chatbot
        self.current_course_code = course
        self.chatbot.set_course(course, request["note_files"])
        
        # Reset session tracking
        self.session_total_points = 0
        self.session_max_points = 0
        
        # Start quiz session if user is logged in
        if self.current_user_id:
            self.current_session_id = self.user_manager.record_quiz_session(
                self.current_user_id,
                request["course"],
                request["difficulty"],
                request["num_questions"]
            )
        
        # Generate first question immediately
        first_question = self._generate_next_question()
        
        if first_question:
            self.generated_questions.append(first_question)
            
            # Build quiz structure
            self.current_quiz = {
                "meta": {
                    "course": request["course"],
                    "notes_used": [],
                    "question_count": request["num_questions"],
                    "lazy_generation": True
                },
                "questions": [first_question]
            }
            
            return self.current_quiz
        else:
            return {
                "error": {
                    "type": "generation_failed",
                    "message": "Failed to generate first question"
                }
            }
    
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
        
        # Record attempt if user is logged in
        if self.current_user_id and self.current_session_id and "grading" in result:
            grading = result["grading"]
            points_awarded = grading.get("points_awarded", 0)
            points_possible = grading.get("points_possible", 10)
            
            # Track session scores
            self.session_total_points += points_awarded
            self.session_max_points += points_possible
            
            self.user_manager.record_question_attempt(
                self.current_session_id,
                self.current_user_id,
                question.get("type", "unknown"),
                points_awarded,
                points_possible,
                grading.get("decision") == "correct"
            )
        
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
        """Move to next question. Generates on-demand if needed.
        
        Returns:
            Next question or None if quiz complete
        """
        if not self.current_quiz or not self.quiz_request:
            return None
        
        self.current_question_idx += 1
        
        # Check if we need to generate more questions
        total_requested = self.quiz_request.get("num_questions", 10)
        
        if self.current_question_idx >= len(self.generated_questions):
            # Generate next question if we haven't reached the limit
            if len(self.generated_questions) < total_requested:
                print(f"\n📝 Generating question {len(self.generated_questions) + 1}/{total_requested}...")
                next_q = self._generate_next_question()
                
                if next_q:
                    self.generated_questions.append(next_q)
                    self.current_quiz["questions"].append(next_q)
                    self.current_quiz["meta"]["question_count"] = len(self.generated_questions)
                    return next_q
                else:
                    # Failed to generate, mark quiz as complete
                    return None
            else:
                # Reached the requested limit
                return None
        
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
        
        # Use requested total, not generated count (for lazy generation)
        total = self.quiz_request.get("num_questions", 10) if self.quiz_request else len(self.current_quiz.get("questions", []))
        
        return {
            "active": True,
            "current": self.current_question_idx + 1,
            "total": total,
            "completed": self.current_question_idx >= total,
            "generated_so_far": len(self.generated_questions)
        }
    
    def _generate_next_question(self) -> Optional[Dict]:
        """Generate the next question on-demand.
        
        Returns:
            Generated question or None if failed
        """
        if not self.quiz_request:
            return None
        
        # Create a single-question request
        single_request = self.quiz_request.copy()
        single_request["num_questions"] = 1
        
        # Generate one question
        result = self.question_gen.generate_questions(single_request)
        
        if "questions" in result and result["questions"]:
            question = result["questions"][0]
            # Update question ID to be sequential
            question["id"] = f"q{len(self.generated_questions) + 1}"
            return question
        
        return None
    
    def complete_quiz(self):
        """Complete the current quiz and calculate stars earned."""
        if not self.current_session_id or not self.current_user_id:
            return
        
        # Calculate stars based on actual performance
        percentage = 0.0  # Initialize percentage
        if self.session_max_points > 0:
            percentage = (self.session_total_points / self.session_max_points) * 100
            
            # Star calculation: 
            # 90-100% = 5 stars, 80-89% = 4 stars, 70-79% = 3 stars, 
            # 60-69% = 2 stars, <60% = 1 star
            if percentage >= 90:
                stars = 5
            elif percentage >= 80:
                stars = 4
            elif percentage >= 70:
                stars = 3
            elif percentage >= 60:
                stars = 2
            else:
                stars = 1
        else:
            stars = 1
        
        print(f"\n⭐ Quiz completed! Score: {self.session_total_points}/{self.session_max_points} ({percentage:.1f}%) - {stars} stars earned")
        self.user_manager.complete_quiz_session(self.current_session_id, stars)
    
    def reset_quiz(self):
        """Reset quiz state."""
        if self.current_session_id and self.current_user_id:
            # Complete the session if it wasn't already
            self.complete_quiz()
        
        self.current_quiz = None
        self.current_question_idx = 0
        self.quiz_request = None
        self.generated_questions = []
        self.current_session_id = None
        self.session_total_points = 0
        self.session_max_points = 0
        self.current_course_code = None
    
    # User management methods
    
    def login(self, username: str, password: str) -> tuple:
        """Log in a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message, user_id)
        """
        success, message, user_id = self.user_manager.login_user(username, password)
        if success:
            self.current_user_id = user_id
        return success, message, user_id
    
    def register(self, username: str, password: str) -> tuple:
        """Register a new user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message, user_id)
        """
        return self.user_manager.register_user(username, password)
    
    def logout(self):
        """Log out the current user."""
        if self.current_session_id:
            self.complete_quiz()
        self.current_user_id = None
        self.current_session_id = None
        self.reset_quiz()
    
    def delete_account(self) -> tuple:
        """Delete the current user's account.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.current_user_id:
            return False, "No user logged in"
        
        user_id = self.current_user_id
        self.logout()
        return self.user_manager.delete_user(user_id)
    
    def change_password(self, old_password: str, new_password: str) -> tuple:
        """Change the current user's password.
        
        Args:
            old_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_user_id:
            return False, "No user logged in"
        
        return self.user_manager.change_password(self.current_user_id, old_password, new_password)
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get current user's profile with stats and rating.
        
        Returns:
            User profile dictionary or None
        """
        if not self.current_user_id:
            return None
        
        stats = self.user_manager.get_user_stats(self.current_user_id)
        if not stats:
            return None
        
        # Generate AI rating
        rating = self.rating_gen.generate_rating(stats)
        
        return {
            'stats': stats,
            'rating': rating
        }
    
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
    
    def get_current_course_name(self) -> Optional[str]:
        """Get the name of the currently selected course.
        
        Returns:
            Course name or None if no course selected
        """
        if self.current_course_code and self.current_course_code in self.COURSES:
            return self.COURSES[self.current_course_code]["name"]
        return None


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
