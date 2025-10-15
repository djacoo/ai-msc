#!/usr/bin/env python3
"""
Quizzer V2 GUI
Modern interface for grounded quiz system
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from typing import Dict, Optional


class QuizzerV2GUI:
    """Modern GUI for Quizzer V2."""
    
    # Color scheme
    COLORS = {
        "bg": "#1a1a2e",
        "fg": "#eee",
        "primary": "#0f3460",
        "secondary": "#16213e",
        "accent": "#e94560",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "error": "#e74c3c",
        "info": "#3498db"
    }
    
    def __init__(self, engine, ai_engine):
        """Initialize GUI.
        
        Args:
            engine: QuizzerV2 engine instance
            ai_engine: AI engine for display info
        """
        self.engine = engine
        self.ai = ai_engine
        
        # Session state
        self.current_question = None
        self.score = 0
        self.questions_answered = 0
        self.streak = 0
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Quizzer V2 - Grounded Exam Q&A")
        self.root.geometry("1000x800")
        self.root.configure(bg=self.COLORS["bg"])
        
        # Configure styles
        self.setup_styles()
        
        # Build UI
        self.build_ui()
        
        # Show start screen
        self.show_start_screen()
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Button style
        style.configure(
            "Accent.TButton",
            background=self.COLORS["accent"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 12, "bold")
        )
        
        # Label style
        style.configure(
            "Title.TLabel",
            background=self.COLORS["bg"],
            foreground=self.COLORS["fg"],
            font=("SF Pro", 24, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            background=self.COLORS["bg"],
            foreground=self.COLORS["fg"],
            font=("SF Pro", 14)
        )
    
    def build_ui(self):
        """Build main UI components."""
        # Header
        self.header_frame = tk.Frame(self.root, bg=self.COLORS["primary"], height=80)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.header_frame,
            text="🎓 Quizzer V2",
            font=("SF Pro", 28, "bold"),
            bg=self.COLORS["primary"],
            fg="white"
        )
        self.title_label.pack(pady=20)
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Footer (stats)
        self.footer_frame = tk.Frame(self.root, bg=self.COLORS["secondary"], height=50)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            self.footer_frame,
            text="Ready to start",
            font=("SF Pro", 11),
            bg=self.COLORS["secondary"],
            fg=self.COLORS["fg"]
        )
        self.stats_label.pack(pady=15)
    
    def show_start_screen(self):
        """Show course selection screen."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Welcome message
        welcome = tk.Label(
            self.content_frame,
            text="Select a Course to Begin",
            font=("SF Pro", 20, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        welcome.pack(pady=30)
        
        # Get available courses
        courses = self.engine.get_available_courses()
        
        # Course buttons
        button_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg"])
        button_frame.pack(pady=20)
        
        for course in courses:
            if course["notes_available"] > 0:
                btn = tk.Button(
                    button_frame,
                    text=f"📚 {course['name']}\n({course['notes_available']} notes available)",
                    font=("SF Pro", 14),
                    bg="white",
                    fg="black",
                    activebackground="#f0f0f0",
                    activeforeground="black",
                    bd=2,
                    relief="solid",
                    padx=30,
                    pady=15,
                    cursor="hand2",
                    command=lambda c=course: self.start_quiz(c["code"])
                )
                btn.pack(pady=10, fill="x")
        
        # Info
        info = tk.Label(
            self.content_frame,
            text="✨ Grounded in your course PDFs\n🎯 Teacher-grade evaluation\n📊 Detailed feedback with citations",
            font=("SF Pro", 11),
            bg=self.COLORS["bg"],
            fg=self.COLORS["info"],
            justify="left"
        )
        info.pack(pady=30)
    
    def start_quiz(self, course_code: str):
        """Start a quiz for the selected course.
        
        Args:
            course_code: Course identifier
        """
        # Show loading
        self.show_loading("Generating questions from course notes...")
        
        # Generate quiz
        request = {
            "course": course_code,
            "topics": ["general"],
            "question_types": ["short_answer"],
            "difficulty": "standard",
            "num_questions": 10,
            "include_solutions": True,
            "grading_mode": "strict_concepts",
            "max_points_per_question": 10
        }
        
        try:
            result = self.engine.generate_quiz(request)
            
            if "error" in result:
                messagebox.showerror("Error", result["error"]["message"])
                self.show_start_screen()
            else:
                # Reset stats
                self.score = 0
                self.questions_answered = 0
                self.streak = 0
                
                # Show first question
                self.show_question()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate quiz: {e}")
            self.show_start_screen()
    
    def show_loading(self, message: str):
        """Show loading screen.
        
        Args:
            message: Loading message
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        loading = tk.Label(
            self.content_frame,
            text=f"⏳ {message}",
            font=("SF Pro", 16),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        loading.pack(expand=True)
        
        self.root.update()
    
    def show_question(self):
        """Display current question."""
        question = self.engine.get_current_question()
        
        if not question:
            self.show_results()
            return
        
        self.current_question = question
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Progress
        progress = self.engine.get_quiz_progress()
        progress_text = f"Question {progress['current']} of {progress['total']}"
        
        progress_label = tk.Label(
            self.content_frame,
            text=progress_text,
            font=("SF Pro", 12),
            bg=self.COLORS["bg"],
            fg=self.COLORS["info"]
        )
        progress_label.pack(anchor="w", pady=(0, 10))
        
        # Question card
        card = tk.Frame(self.content_frame, bg=self.COLORS["secondary"], bd=0)
        card.pack(fill="both", expand=True, pady=10)
        
        # Question type badge
        qtype_badge = tk.Label(
            card,
            text=f"📝 {question['type'].replace('_', ' ').title()}",
            font=("SF Pro", 10),
            bg=self.COLORS["primary"],
            fg="white",
            padx=10,
            pady=5
        )
        qtype_badge.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Question text
        q_text = tk.Label(
            card,
            text=question["prompt"],
            font=("SF Pro", 16),
            bg=self.COLORS["secondary"],
            fg=self.COLORS["fg"],
            wraplength=900,
            justify="left"
        )
        q_text.pack(anchor="w", padx=20, pady=10)
        
        # Grounding info
        if question.get("grounding"):
            g = question["grounding"][0]
            grounding_text = f"📚 Source: {Path(g['path']).name}, page {g['page']}"
            
            grounding_label = tk.Label(
                card,
                text=grounding_text,
                font=("SF Pro", 9),
                bg=self.COLORS["secondary"],
                fg=self.COLORS["info"],
                justify="left"
            )
            grounding_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Answer input
        if question["type"] in ["mcq_single", "mcq_multi"]:
            self.show_mcq_options(card, question)
        else:
            self.show_text_answer(card, question)
        
        # Update stats
        self.update_stats()
    
    def show_mcq_options(self, parent, question):
        """Show MCQ options.
        
        Args:
            parent: Parent widget
            question: Question object
        """
        options = question.get("options", [])
        
        self.selected_option = tk.StringVar()
        
        options_frame = tk.Frame(parent, bg=self.COLORS["secondary"])
        options_frame.pack(fill="x", padx=20, pady=10)
        
        for option in options:
            rb = tk.Radiobutton(
                options_frame,
                text=option,
                variable=self.selected_option,
                value=option[0],  # A, B, C, D
                font=("SF Pro", 13),
                bg=self.COLORS["secondary"],
                fg=self.COLORS["fg"],
                selectcolor=self.COLORS["primary"],
                activebackground=self.COLORS["secondary"],
                activeforeground=self.COLORS["fg"],
                bd=0,
                cursor="hand2"
            )
            rb.pack(anchor="w", pady=5)
        
        # Submit button
        submit_btn = tk.Button(
            parent,
            text="Submit Answer",
            font=("SF Pro", 14, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            bd=0,
            padx=40,
            pady=12,
            cursor="hand2",
            command=lambda: self.submit_answer(self.selected_option.get())
        )
        submit_btn.pack(pady=20)
    
    def show_text_answer(self, parent, question):
        """Show text answer input.
        
        Args:
            parent: Parent widget
            question: Question object
        """
        # Answer text area
        self.answer_text = scrolledtext.ScrolledText(
            parent,
            font=("SF Pro", 12),
            bg="white",
            fg="black",
            insertbackground="black",
            height=8,
            wrap="word",
            bd=2,
            relief="solid",
            padx=10,
            pady=10
        )
        self.answer_text.pack(fill="both", padx=20, pady=10)
        
        # Submit button
        submit_btn = tk.Button(
            parent,
            text="Submit Answer",
            font=("SF Pro", 14, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            bd=0,
            padx=40,
            pady=12,
            cursor="hand2",
            command=lambda: self.submit_answer(self.answer_text.get("1.0", "end-1c"))
        )
        submit_btn.pack(pady=20)
    
    def submit_answer(self, answer: str):
        """Submit and grade answer.
        
        Args:
            answer: User's answer
        """
        if not answer or not answer.strip():
            messagebox.showwarning("Empty Answer", "Please provide an answer.")
            return
        
        # Show grading
        self.show_loading("Grading your answer...")
        
        try:
            # Grade answer
            submission = {
                "question_id": self.current_question["id"],
                "answer": answer
            }
            
            result = self.engine.grade_answer(submission)
            
            if "error" in result:
                messagebox.showerror("Error", result["error"]["message"])
                return
            
            # Show grading result
            self.show_grading_result(result["grading"])
        
        except Exception as e:
            messagebox.showerror("Error", f"Grading failed: {e}")
            self.show_question()
    
    def show_grading_result(self, grading: Dict):
        """Show grading result.
        
        Args:
            grading: Grading object
        """
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update stats
        self.questions_answered += 1
        points = grading["points_awarded"]
        max_points = grading["points_possible"]
        self.score += points
        
        # Update streak
        if grading["decision"] == "correct":
            self.streak += 1
        else:
            self.streak = 0
        
        # Result card
        card = tk.Frame(self.content_frame, bg=self.COLORS["secondary"])
        card.pack(fill="both", expand=True, pady=10)
        
        # Decision header
        decision = grading["decision"]
        
        if decision == "correct":
            color = self.COLORS["success"]
            icon = "✓"
            message = "Correct!"
        elif decision == "partially_correct":
            color = self.COLORS["warning"]
            icon = "~"
            message = "Partially Correct"
        else:
            color = self.COLORS["error"]
            icon = "✗"
            message = "Incorrect"
        
        header = tk.Label(
            card,
            text=f"{icon} {message}",
            font=("SF Pro", 24, "bold"),
            bg=color,
            fg="white",
            pady=15
        )
        header.pack(fill="x")
        
        # Score
        score_label = tk.Label(
            card,
            text=f"Score: {points}/{max_points} points",
            font=("SF Pro", 16),
            bg=self.COLORS["secondary"],
            fg=self.COLORS["fg"]
        )
        score_label.pack(pady=10)
        
        # Explanation
        explanation_frame = tk.Frame(card, bg="white")
        explanation_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        explanation = tk.Label(
            explanation_frame,
            text=grading.get("explanation_to_student", ""),
            font=("SF Pro", 12),
            bg="white",
            fg="black",
            wraplength=850,
            justify="left"
        )
        explanation.pack(pady=10)
        
        # Rubric checks
        checks = grading.get("checks", [])
        if checks:
            checks_label = tk.Label(
                explanation_frame,
                text="📋 Rubric Breakdown:",
                font=("SF Pro", 11, "bold"),
                bg="white",
                fg="#2563eb"
            )
            checks_label.pack(anchor="w", pady=(10, 5))
            
            for check in checks:
                status = "✓" if check.get("met") else "✗"
                check_color = self.COLORS["success"] if check.get("met") else self.COLORS["error"]
                
                check_text = tk.Label(
                    explanation_frame,
                    text=f"{status} {check['criterion']}: {check.get('evidence', '')}",
                    font=("SF Pro", 10),
                    bg="white",
                    fg=check_color,
                    wraplength=800,
                    justify="left"
                )
                check_text.pack(anchor="w", pady=2)
        
        # Citations
        citations = grading.get("citations", [])
        if citations:
            cite_label = tk.Label(
                explanation_frame,
                text="📚 Citations:",
                font=("SF Pro", 11, "bold"),
                bg="white",
                fg="#2563eb"
            )
            cite_label.pack(anchor="w", pady=(10, 5))
            
            for cite in citations:
                cite_text = f"• {Path(cite['path']).name}, page {cite['page']}"
                if "quote" in cite:
                    cite_text += f'\n  "{cite["quote"]}"'
                
                cite_label = tk.Label(
                    explanation_frame,
                    text=cite_text,
                    font=("SF Pro", 9),
                    bg="white",
                    fg="black",
                    wraplength=800,
                    justify="left"
                )
                cite_label.pack(anchor="w", pady=2)
        
        # Next button
        next_btn = tk.Button(
            card,
            text="Next Question →",
            font=("SF Pro", 14, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            bd=0,
            padx=40,
            pady=12,
            cursor="hand2",
            command=self.next_question
        )
        next_btn.pack(pady=20)
        
        # Update stats
        self.update_stats()
    
    def next_question(self):
        """Move to next question."""
        self.engine.next_question()
        self.show_question()
    
    def show_results(self):
        """Show final quiz results."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Results card
        card = tk.Frame(self.content_frame, bg=self.COLORS["secondary"])
        card.pack(fill="both", expand=True, pady=10)
        
        # Header
        header = tk.Label(
            card,
            text="🎉 Quiz Complete!",
            font=("SF Pro", 28, "bold"),
            bg=self.COLORS["primary"],
            fg="white",
            pady=20
        )
        header.pack(fill="x")
        
        # Stats
        stats_frame = tk.Frame(card, bg=self.COLORS["secondary"])
        stats_frame.pack(pady=30)
        
        # Score
        score_label = tk.Label(
            stats_frame,
            text=f"Total Score: {self.score} points",
            font=("SF Pro", 20, "bold"),
            bg=self.COLORS["secondary"],
            fg=self.COLORS["success"]
        )
        score_label.pack(pady=10)
        
        # Questions answered
        answered_label = tk.Label(
            stats_frame,
            text=f"Questions Answered: {self.questions_answered}",
            font=("SF Pro", 14),
            bg=self.COLORS["secondary"],
            fg=self.COLORS["fg"]
        )
        answered_label.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(card, bg=self.COLORS["secondary"])
        btn_frame.pack(pady=20)
        
        new_quiz_btn = tk.Button(
            btn_frame,
            text="New Quiz",
            font=("SF Pro", 14, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.show_start_screen
        )
        new_quiz_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(
            btn_frame,
            text="Exit",
            font=("SF Pro", 14),
            bg="#6b7280",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.root.quit
        )
        exit_btn.pack(side="left", padx=10)
    
    def update_stats(self):
        """Update footer stats."""
        progress = self.engine.get_quiz_progress()
        
        stats_text = (
            f"Score: {self.score} pts  |  "
            f"Question: {progress['current']}/{progress['total']}  |  "
            f"Streak: {self.streak} 🔥"
        )
        
        self.stats_label.config(text=stats_text)
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Launch Quizzer V2 GUI."""
    import sys
    from pathlib import Path
    
    # Find repo root
    repo_root = Path(__file__).parent.parent
    
    # Initialize AI
    try:
        from local_ai import LocalAI
        ai = LocalAI("llama3.2:3b")
        print("✓ Local AI initialized")
    except Exception as e:
        messagebox.showerror("AI Error", f"Failed to initialize AI: {e}")
        sys.exit(1)
    
    # Initialize engine
    from quizzer_v2_engine import QuizzerV2
    engine = QuizzerV2(str(repo_root), ai)
    
    # Launch GUI
    app = QuizzerV2GUI(engine, ai)
    app.run()


if __name__ == "__main__":
    main()
