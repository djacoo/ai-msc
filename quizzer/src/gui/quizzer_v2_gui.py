#!/usr/bin/env python3
"""
Quizzer V2 GUI
Modern interface for grounded quiz system
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import time
from pathlib import Path
from typing import Dict, Optional
from ..utils.animations import LoadingSpinner, AnimationEngine, ProgressBar


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
    
    def __init__(self, engine, ai_engine, username=None):
        """Initialize GUI.
        
        Args:
            engine: QuizzerV2 engine instance
            ai_engine: AI engine for display info
            username: Optional username of logged in user
        """
        self.engine = engine
        self.ai = ai_engine
        self.username = username
        
        # Session state
        self.current_question = None
        self.score = 0
        self.questions_answered = 0
        self.streak = 0
        self.is_loading = False
        self.loading_dots = 0
        
        # Animation state
        self.animation_running = False
        self.fade_alpha = 0.0
        
        # Create window
        self.root = tk.Tk()
        title = f"Quizzer V2 - {username}" if username else "Quizzer V2 - Grounded Exam Q&A"
        self.root.title(title)
        self.root.geometry("1000x800")
        self.root.configure(bg=self.COLORS["bg"])
        
        # Bring window to front (above all other windows)
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure styles
        self.setup_styles()
        
        # Build UI
        self.build_ui()
        
        # Show initial loading screen
        self.show_initial_loading()
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Accent button style
        style.configure(
            "Accent.TButton",
            background=self.COLORS["accent"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 12, "bold")
        )
        
        # Primary blue button style
        style.configure(
            "Primary.TButton",
            background="#2563eb",
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 14, "bold"),
            padding=(40, 12)
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
            foreground=[("active", "white"), ("pressed", "white")]
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
        
        # Profile button (if logged in)
        if self.username:
            profile_btn = tk.Button(
                self.header_frame,
                text=f"👤 {self.username}",
                font=("SF Pro", 13, "bold"),
                bg="#e5e7eb",  # Light gray background
                fg="#000000",  # Black text
                activebackground="#d1d5db",
                activeforeground="#000000",
                relief="flat",
                padx=20,
                pady=10,
                cursor="hand2",
                command=self.show_profile,
                borderwidth=0
            )
            profile_btn.pack(side="right", padx=20, pady=20)
        
        # Chatbot button (hidden by default, shown when course is selected)
        self.chatbot_btn = tk.Button(
            self.header_frame,
            text="💬 Ask AI",
            font=("SF Pro", 13, "bold"),
            bg="#10b981",  # Green background
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.open_chatbot,
            borderwidth=0
        )
        # Don't pack yet - will show when course is selected
        
        self.title_label = tk.Label(
            self.header_frame,
            text="🎓 Quizzer V2",
            font=("SF Pro", 28, "bold"),
            bg=self.COLORS["primary"],
            fg="white"
        )
        self.title_label.pack(side="left", padx=20, pady=20)
        
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
    
    def fade_in_content(self, widgets, index=0, steps=10):
        """Animate fade-in effect for widgets."""
        if index >= steps:
            return
        
        # Gradually lighten the widgets (simulate fade-in)
        for widget in widgets:
            if widget.winfo_exists():
                try:
                    # For frames and labels, we can't do true alpha, but we can animate position
                    current_y = widget.winfo_y()
                    if index == 0:
                        widget.place_forget()
                        widget.pack()
                except:
                    pass
        
        self.root.after(20, lambda: self.fade_in_content(widgets, index + 1, steps))
    
    def show_initial_loading(self):
        """Show initial loading screen with progress bar."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        loading_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg"])
        loading_frame.pack(expand=True)
        
        # Welcome message
        welcome = tk.Label(
            loading_frame,
            text=f"Welcome{', ' + self.username if self.username else ''}!",
            font=("SF Pro", 28, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["accent"]
        )
        welcome.pack(pady=(100, 20))
        
        # Progress bar
        self.init_progress_bar = ProgressBar(
            loading_frame,
            width=400,
            height=6,
            color="#2563eb",
            bg="#374151"
        )
        self.init_progress_bar.pack(pady=30)
        
        # Loading message
        self.init_loading_label = tk.Label(
            loading_frame,
            text="Loading application...",
            font=("SF Pro", 13),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        self.init_loading_label.pack(pady=10)
        
        # Start animation
        self._animate_initial_loading(0, loading_frame)
    
    def _animate_initial_loading(self, progress, loading_frame):
        """Animate initial loading progress.
        
        Args:
            progress: Current progress (0-100)
            loading_frame: Frame to destroy when done
        """
        if progress <= 100:
            self.init_progress_bar.set_progress(progress, animated=True)
            
            # Update text based on progress
            if progress < 25:
                text = "Loading application..."
            elif progress < 50:
                text = "Initializing quiz engine..."
            elif progress < 75:
                text = "Loading user data..."
            else:
                text = "Preparing interface..."
            
            self.init_loading_label.config(text=text)
            
            # Continue animation (5 seconds total: 100ms * 50 steps = 5000ms)
            self.root.after(100, lambda: self._animate_initial_loading(progress + 2, loading_frame))
        else:
            # Loading complete
            loading_frame.destroy()
            self.show_start_screen()
    
    def show_start_screen(self):
        """Show course selection screen."""
        # Hide chatbot button when returning to main menu
        if hasattr(self, 'chatbot_btn'):
            self.chatbot_btn.pack_forget()
        
        # Clear content with fade effect
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # User stats banner (if logged in) - compact version
        if self.username:
            profile = self.engine.get_user_profile()
            if profile:
                stats = profile['stats']
                rating = profile['rating']
                
                stats_banner = tk.Frame(
                    self.content_frame, 
                    bg="#1a1a2e",
                    padx=15, 
                    pady=8,
                    highlightbackground="#0f3460",
                    highlightthickness=1
                )
                stats_banner.pack(fill="x", pady=(0, 10))
                
                tk.Label(
                    stats_banner,
                    text=f"{rating['emoji']} {rating['tier']} • {stats['total_quizzes']} quizzes • {stats['accuracy']:.0f}% • {stats['total_stars']} ⭐",
                    font=("SF Pro", 12),
                    fg="#00d4ff",
                    bg="#1a1a2e"
                ).pack(anchor="w")
        
        # Welcome message - more compact
        welcome = tk.Label(
            self.content_frame,
            text="Select a Course",
            font=("SF Pro", 16, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        welcome.pack(pady=(10, 8))
        
        # Get available courses
        courses = self.engine.get_available_courses()
        
        # Course cards container - very compact grid layout
        courses_container = tk.Frame(self.content_frame, bg=self.COLORS["bg"])
        courses_container.pack(pady=5, fill="both", expand=True)
        
        # Configure grid to center content
        courses_container.grid_columnconfigure(0, weight=1)
        courses_container.grid_columnconfigure(1, weight=1)
        
        row = 0
        col = 0
        max_cols = 2  # Two columns for compact layout
        
        for course in courses:
            if course["notes_available"] > 0:
                # Course card container - very compact
                card = tk.Frame(
                    courses_container,
                    bg=self.COLORS["secondary"],
                    highlightbackground="#0f3460",
                    highlightthickness=1
                )
                card.grid(row=row, column=col, pady=5, padx=10, sticky="ew")
                
                # Inner padding frame - reduced padding
                inner = tk.Frame(card, bg=self.COLORS["secondary"])
                inner.pack(padx=10, pady=8, fill="both", expand=True)
                
                # Course title - compact
                title_label = tk.Label(
                    inner,
                    text=f"📚 {course['name']}",
                    font=("SF Pro", 12, "bold"),
                    bg=self.COLORS["secondary"],
                    fg=self.COLORS["fg"]
                )
                title_label.pack(anchor="w")
                
                # Course info - smaller, inline with less spacing
                info_label = tk.Label(
                    inner,
                    text=f"{course['notes_available']} notes",
                    font=("SF Pro", 8),
                    bg=self.COLORS["secondary"],
                    fg="#888"
                )
                info_label.pack(anchor="w", pady=(1, 6))
                
                # Action buttons frame
                actions_frame = tk.Frame(inner, bg=self.COLORS["secondary"])
                actions_frame.pack(fill="x")
                
                # Chat button - styled like "Back" button, more compact
                chat_btn = tk.Button(
                    actions_frame,
                    text="💬 Chat",
                    font=("SF Pro", 10, "bold"),
                    bg="#d1d5db",  # Light gray like Back button
                    fg="#1f2937",  # Dark text
                    activebackground="#9ca3af",
                    activeforeground="#1f2937",
                    relief="flat",
                    padx=12,
                    pady=6,
                    cursor="hand2",
                    command=lambda c=course: self.open_chatbot_from_home(c["code"], c["name"], c["note_files"]),
                    borderwidth=0,
                    highlightthickness=0
                )
                chat_btn.pack(side="left", padx=(0, 6))
                
                # Quiz button - styled like "Start Quiz" button, more compact
                quiz_btn = tk.Button(
                    actions_frame,
                    text="Start Quiz →",
                    font=("SF Pro", 10, "bold"),
                    bg="#e5e7eb",  # Light gray background
                    fg="#000000",  # Black text
                    activebackground="#d1d5db",
                    activeforeground="#000000",
                    relief="flat",
                    padx=12,
                    pady=6,
                    cursor="hand2",
                    command=lambda c=course: self.show_quiz_config(c["code"]),
                    borderwidth=0,
                    highlightthickness=0
                )
                quiz_btn.pack(side="left")
                
                # Move to next grid position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
    
    def show_quiz_config(self, course_code: str):
        """Show quiz configuration screen for question type selection."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(
            self.content_frame,
            text="⚙️ Quiz Configuration",
            font=("SF Pro", 24, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        title.pack(pady=(20, 10))
        
        # Subtitle
        subtitle = tk.Label(
            self.content_frame,
            text="Choose your preferred question types",
            font=("SF Pro", 13),
            bg=self.COLORS["bg"],
            fg="#a0a0a0"
        )
        subtitle.pack(pady=(0, 30))
        
        # Config card
        config_card = tk.Frame(self.content_frame, bg="white", bd=2, relief="solid")
        config_card.pack(padx=100, pady=20, fill="both", expand=True)
        
        # Question type selection
        type_label = tk.Label(
            config_card,
            text="Question Types:",
            font=("SF Pro", 16, "bold"),
            bg="white",
            fg="black"
        )
        type_label.pack(pady=(30, 15), anchor="w", padx=30)
        
        # Radio buttons for question type
        self.question_type_var = tk.StringVar(value="mixed")
        
        type_options = [
            ("mcq", "📋 Multiple Choice Only", "Fast-paced quiz with checkboxes"),
            ("short", "✍️ Short Answers Only", "Concise explanations (2-4 sentences)"),
            ("long", "📝 Long Answers Only", "Detailed explanations and derivations"),
            ("mixed_open", "📊 Mixed Answers (Short + Long)", "Variety of open-ended questions"),
            ("mixed", "🎯 Everything Mixed", "MCQ + Short + Long answers")
        ]
        
        for value, label, description in type_options:
            frame = tk.Frame(config_card, bg="white", padx=10, pady=5)
            frame.pack(anchor="w", padx=50, pady=8, fill="x")
            
            rb = tk.Radiobutton(
                frame,
                text=label,
                variable=self.question_type_var,
                value=value,
                font=("SF Pro", 13, "bold"),
                bg="white",
                fg="black",
                selectcolor="white",
                activebackground="white",
                activeforeground="black",
                cursor="hand2"
            )
            rb.pack(anchor="w")
            
            desc = tk.Label(
                frame,
                text=f"  {description}",
                font=("SF Pro", 10),
                bg="white",
                fg="#666",
                justify="left"
            )
            desc.pack(anchor="w", padx=(25, 0))
            
            # Add hover effect to entire frame
            frame.bind("<Enter>", lambda e, f=frame: f.config(bg="#f8f9fa"))
            frame.bind("<Leave>", lambda e, f=frame: f.config(bg="white"))
            rb.bind("<Enter>", lambda e, f=frame: f.config(bg="#f8f9fa"))
            rb.bind("<Leave>", lambda e, f=frame: f.config(bg="white"))
            desc.bind("<Enter>", lambda e, f=frame: f.config(bg="#f8f9fa"))
            desc.bind("<Leave>", lambda e, f=frame: f.config(bg="white"))
        
        # Buttons
        btn_frame = tk.Frame(config_card, bg="white")
        btn_frame.pack(pady=30)
        
        # Back button - styled to match homepage
        back_btn = tk.Button(
            btn_frame,
            text="← Back",
            font=("SF Pro", 13, "bold"),
            bg="#d1d5db",  # Light gray
            fg="#1f2937",  # Dark text
            activebackground="#9ca3af",
            activeforeground="#1f2937",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.show_start_screen,
            borderwidth=0
        )
        back_btn.pack(side="left", padx=10)
        
        # Start button - styled to match homepage
        start_btn = tk.Button(
            btn_frame,
            text="Start Quiz →",
            font=("SF Pro", 13, "bold"),
            bg="#e5e7eb",  # Light gray background
            fg="#000000",  # Black text
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=lambda: self.start_quiz(course_code),
            borderwidth=0
        )
        start_btn.pack(side="left", padx=10)
    
    def start_quiz(self, course_code: str):
        """Start quiz with selected parameters (async with loading)."""
        # Show loading screen
        self.show_loading_screen("🔄 Generating questions from course notes...")
        
        # Run generation in background thread
        def generate_async():
            start_time = time.time()
            
            # Map user selection to question types
            type_selection = self.question_type_var.get() if hasattr(self, 'question_type_var') else "mixed"
            
            type_mapping = {
                "mcq": ["mcq_single", "mcq_multi"],
                "short": ["short_answer"],
                "long": ["derivation", "proof"],
                "mixed_open": ["short_answer", "derivation"],
                "mixed": ["mcq_single", "short_answer", "derivation"]
            }
            
            question_types = type_mapping.get(type_selection, ["mcq_single", "short_answer"])
            
            # Generate quiz with user preferences
            request = {
                "course": course_code,
                "topics": ["general"],
                "question_types": question_types,
                "difficulty": "standard",
                "num_questions": 5,  # Reduced from 10 for faster generation
                "include_solutions": True,
                "grading_mode": "strict_concepts",
                "max_points_per_question": 10
            }
            result = self.engine.generate_quiz(request)
            
            # Store quiz
            if "questions" in result:
                self.engine.current_quiz = result
                self.engine.current_question_idx = 0
            
            # Ensure minimum animation time (1 second) for UX
            elapsed = time.time() - start_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            
            # Switch to first question on main thread
            self.root.after(0, self.finish_loading)
        
        thread = threading.Thread(target=generate_async, daemon=True)
        thread.start()
    
    def finish_loading(self):
        """Finish loading and show first question."""
        self.is_loading = False
        if hasattr(self, 'loading_spinner'):
            self.loading_spinner.stop()
        # Show chatbot button now that course is loaded
        if hasattr(self, 'chatbot_btn'):
            self.chatbot_btn.pack(side="right", padx=(0, 10), pady=20)
        self.show_question()
    
    def show_loading_screen(self, message="Generating questions..."):
        """Show loading animation."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        loading_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg"])
        loading_frame.pack(expand=True)
        
        # Loading spinner with smooth animation
        self.loading_spinner = LoadingSpinner(loading_frame, size=60, color="#3498db")
        self.loading_spinner.pack(pady=30)
        self.loading_spinner.start()
        
        # Loading message with animated dots
        self.loading_message = tk.Label(
            loading_frame,
            text=message,
            font=("SF Pro", 16),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        self.loading_message.pack(pady=10)
        
        self.is_loading = True
        self._animate_loading_dots(0)
    
    def _animate_loading_dots(self, count):
        """Animate loading message dots.
        
        Args:
            count: Current dot count
        """
        if not self.is_loading:
            return
        
        if hasattr(self, 'loading_message') and self.loading_message.winfo_exists():
            base_text = self.loading_message.cget("text").rstrip(".")
            dots = "." * (count % 4)
            self.loading_message.config(text=f"{base_text}{dots}")
            self.root.after(400, lambda: self._animate_loading_dots(count + 1))
    
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
        
        # Progress with animated bar
        progress = self.engine.get_quiz_progress()
        progress_text = f"Question {progress['current']} of {progress['total']}"
        
        progress_label = tk.Label(
            self.content_frame,
            text=progress_text,
            font=("SF Pro", 12),
            bg=self.COLORS["bg"],
            fg=self.COLORS["info"]
        )
        progress_label.pack(anchor="w", pady=(0, 5))
        
        # Animated progress bar
        progress_frame = tk.Frame(self.content_frame, bg="#2a2a3e", height=8)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        percentage = (progress['current'] / progress['total']) if progress['total'] > 0 else 0
        progress_bar = tk.Frame(progress_frame, bg="#2563eb", height=8)
        progress_bar.place(x=0, y=0, relwidth=0, relheight=1)
        
        # Animate progress bar fill
        self.animate_progress_bar(progress_bar, percentage)
        
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
        
        # Submit button (macOS-compatible with ttk)
        submit_btn = ttk.Button(
            parent,
            text="Submit Answer",
            style="Primary.TButton",
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
        
        # Submit button (macOS-compatible with ttk)
        submit_btn = ttk.Button(
            parent,
            text="Submit Answer",
            style="Primary.TButton",
            cursor="hand2",
            command=lambda: self.submit_answer(self.answer_text.get("1.0", "end-1c"))
        )
        submit_btn.pack(pady=20)
    
    def submit_answer(self, answer: str):
        """Submit and grade answer (async with loading).
        
        Args:
            answer: User's answer
        """
        if not answer or not answer.strip():
            messagebox.showwarning("Empty Answer", "Please provide an answer.")
            return
        
        # Check for minimal/invalid answers ONLY for open-ended questions (not MCQ)
        question_type = self.current_question.get("type", "")
        if question_type not in ["mcq_single", "mcq_multi"]:
            answer_stripped = answer.strip()
            if len(answer_stripped) < 3 or answer_stripped.replace(".", "").replace(",", "").replace("!", "").replace("?", "").strip() == "":
                messagebox.showwarning("Invalid Answer", "Please provide a meaningful answer (at least a few words).")
                return
        
        # Show grading animation
        self.show_loading_screen("🤖 AI Teacher grading your answer...")
        
        # Grade in background thread
        def grade_async():
            start_time = time.time()
            
            # Grade the answer
            # The engine expects: {"question_id": id, "answer": text}
            question_id = self.current_question.get("id")
            
            # Fallback: if question has no ID, assign one based on current index
            if not question_id:
                question_id = f"q{self.engine.current_question_idx + 1}"
                self.current_question["id"] = question_id
                print(f"⚠️ Question had no ID, assigned: {question_id}")
            
            submission = {
                "question_id": question_id,
                "answer": answer
            }
            result = self.engine.grade_answer(submission)
            
            # Debug: Print full result
            print("\n" + "="*60)
            print("GRADE_ANSWER RETURNED:")
            print(f"Result type: {type(result)}")
            print(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
            if isinstance(result, dict):
                if "grading" in result:
                    print(f"Grading keys: {result['grading'].keys()}")
                elif "error" in result:
                    print(f"ERROR DETECTED: {result['error']}")
                    print(f"Full error: {result}")
            print("="*60 + "\n")
            
            # Ensure minimum animation time (0.8 seconds) for UX
            elapsed = time.time() - start_time
            if elapsed < 0.8:
                time.sleep(0.8 - elapsed)
            
            # Show result on main thread
            self.root.after(0, lambda: self.finish_grading(result))
        
        thread = threading.Thread(target=grade_async, daemon=True)
        thread.start()
    
    def finish_grading(self, result):
        """Finish grading and show result with animation."""
        self.is_loading = False
        if hasattr(self, 'loading_spinner'):
            self.loading_spinner.stop()
        self.show_result(result)
    
    def show_result(self, result: Dict):
        """Show grading result with animation.
        
        Args:
            result: Grading result dictionary
        """
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Check for errors
        if "error" in result and "grading" not in result:
            # Grading failed, create fallback grading
            error_msg = result.get("error", "Unknown error")
            print(f"⚠️ Grading error, using fallback: {error_msg}")
            
            grading = {
                "decision": "incorrect",
                "points_awarded": 0,
                "points_possible": 10,
                "explanation_to_student": f"⚠️ Grading system error: {error_msg}\n\nPlease try again or contact support if the issue persists.",
                "checks": [],
                "citations": self.current_question.get("grounding", [])
            }
            result = {"grading": grading}
        
        grading = result.get("grading", {})
        decision = grading.get("decision", "unknown")
        points_awarded = grading.get("points_awarded", 0)
        points_possible = grading.get("points_possible", 10)
        
        # Debug: Print grading result to console
        print("\n" + "="*50)
        print("GRADING RESULT:")
        print(f"Decision: {decision}")
        print(f"Points: {points_awarded}/{points_possible}")
        print(f"Explanation: {grading.get('explanation_to_student', 'MISSING')[:100]}")
        print(f"Checks: {len(grading.get('checks', []))} items")
        print(f"Citations: {len(grading.get('citations', []))} items")
        print("="*50 + "\n")
        
        # Determine colors and emoji based on score
        percentage = points_awarded / points_possible if points_possible > 0 else 0
        if percentage >= 0.9:
            result_color = "#10b981"  # Green
            result_emoji = "🎉"
            result_title = "Excellent!"
        elif percentage >= 0.4:
            result_color = "#f59e0b"  # Yellow/Orange
            result_emoji = "👍"
            result_title = "Good Effort!"
        else:
            result_color = "#ef4444"  # Red
            result_emoji = "📚"
            result_title = "Keep Studying!"
        
        # Result card with animated entrance
        card = tk.Frame(
            self.content_frame,
            bg="white",
            bd=2,
            relief="raised"
        )
        card.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Animated result header
        result_header = tk.Label(
            card,
            text=f"{result_emoji} {result_title}",
            font=("SF Pro", 28, "bold"),
            bg="white",
            fg=result_color
        )
        result_header.pack(pady=(30, 10))
        
        # Animate the header (pulse effect)
        self.animate_result_header(result_header, result_color, 0)
        
        # Update session stats
        self.score += points_awarded
        self.questions_answered += 1
        if decision == "correct":
            self.streak += 1
        else:
            self.streak = 0
        
        # Score (with counting animation)
        score_label = tk.Label(
            card,
            text=f"Score: 0/{points_possible} points",
            font=("SF Pro", 16),
            bg="white",
            fg=self.COLORS["fg"]
        )
        score_label.pack(pady=10)
        
        # Animate score counting up
        self.animate_score_count(score_label, points_awarded)
        
        # Explanation
        explanation_frame = tk.Frame(card, bg="white")
        explanation_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get explanation text with fallback
        explanation_text = grading.get("explanation_to_student", "")
        if not explanation_text or explanation_text.strip() == "":
            # Fallback explanation
            if decision == "correct":
                explanation_text = "Your answer is correct!"
            elif decision == "partially_correct":
                explanation_text = "Your answer is partially correct. Review the feedback below."
            else:
                explanation_text = "Your answer needs improvement. See the rubric breakdown for details."
        
        explanation = tk.Label(
            explanation_frame,
            text=explanation_text,
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
        else:
            # No checks available - show basic feedback
            no_checks_label = tk.Label(
                explanation_frame,
                text="ℹ️ Detailed rubric breakdown not available for this question type.",
                font=("SF Pro", 10, "italic"),
                bg="white",
                fg="#6b7280",
                wraplength=800,
                justify="left"
            )
            no_checks_label.pack(anchor="w", pady=(10, 5))
        
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
        
        # Next button (macOS-compatible with ttk)
        next_btn = ttk.Button(
            card,
            text="Next Question →",
            style="Primary.TButton",
            cursor="hand2",
            command=self.next_question
        )
        next_btn.pack(pady=20)
        
        # Update stats
        self.update_stats()
    
    def animate_result_header(self, label, color, step):
        """Animate result header with pulse effect."""
        if not label.winfo_exists() or step > 10:
            return
        
        # Pulse: grow then shrink
        if step < 5:
            size = 28 + step * 2
        else:
            size = 28 + (10 - step) * 2
        
        label.config(font=("SF Pro", size, "bold"))
        self.root.after(50, lambda: self.animate_result_header(label, color, step + 1))
    
    def animate_score_count(self, label, target_score, current=0, step=1):
        """Animate counting up to target score."""
        if not label.winfo_exists() or current >= target_score:
            if label.winfo_exists():
                label.config(text=f"Score: {target_score}/10 points")
            return
        
        current += step
        if current > target_score:
            current = target_score
        
        label.config(text=f"Score: {current}/10 points")
        self.root.after(30, lambda: self.animate_score_count(label, target_score, current, step))
    
    def animate_progress_bar(self, bar, target_width, current_width=0.0):
        """Animate progress bar fill."""
        if not bar.winfo_exists() or current_width >= target_width:
            if bar.winfo_exists():
                bar.place(relwidth=target_width)
            return
        
        # Smooth easing function
        current_width += (target_width - current_width) * 0.15
        if abs(target_width - current_width) < 0.01:
            current_width = target_width
        
        bar.place(relwidth=current_width)
        self.root.after(20, lambda: self.animate_progress_bar(bar, target_width, current_width))  # Smoother: 60ms
    
    def next_question(self):
        """Move to next question."""
        self.engine.next_question()
        self.show_question()
    
    def show_results(self):
        """Show final quiz results."""
        # Complete the quiz session for user tracking
        self.engine.complete_quiz()
        
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
        
        # Calculate total possible score
        total_possible = self.questions_answered * 10
        percentage = (self.score / total_possible * 100) if total_possible > 0 else 0
        
        # Score
        score_label = tk.Label(
            stats_frame,
            text=f"Total Score: {self.score}/{total_possible} points ({percentage:.1f}%)",
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
        
        # Buttons - styled to match homepage
        btn_frame = tk.Frame(card, bg=self.COLORS["secondary"])
        btn_frame.pack(pady=20)
        
        # Back to Menu button
        menu_btn = tk.Button(
            btn_frame,
            text="← Back to Menu",
            font=("SF Pro", 13, "bold"),
            bg="#d1d5db",  # Light gray
            fg="#1f2937",  # Dark text
            activebackground="#9ca3af",
            activeforeground="#1f2937",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.show_start_screen,
            borderwidth=0
        )
        menu_btn.pack(side="left", padx=10)
        
        # New Quiz button
        new_quiz_btn = tk.Button(
            btn_frame,
            text="New Quiz →",
            font=("SF Pro", 13, "bold"),
            bg="#e5e7eb",  # Light gray background
            fg="#000000",  # Black text
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.reset_and_start,
            borderwidth=0
        )
        new_quiz_btn.pack(side="left", padx=10)
        
        # Exit button style
        style = ttk.Style()
        style.configure(
            "Exit.TButton",
            background="#6b7280",
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 14),
            padding=(30, 12)
        )
        style.map(
            "Exit.TButton",
            background=[("active", "#4b5563")],
            foreground=[("active", "white")]
        )
        
        exit_btn = ttk.Button(
            btn_frame,
            text="Exit",
            style="Exit.TButton",
            cursor="hand2",
            command=self.root.quit
        )
        exit_btn.pack(side="left", padx=10)
    
    def reset_and_start(self):
        """Reset session and show start screen."""
        self.score = 0
        self.questions_answered = 0
        self.streak = 0
        self.engine.reset_quiz()  # Clear course selection
        self.show_start_screen()
    
    def update_stats(self):
        """Update footer stats."""
        progress = self.engine.get_quiz_progress()
        
        stats_text = (
            f"Score: {self.score} pts  |  "
            f"Question: {progress['current']}/{progress['total']}  |  "
            f"Streak: {self.streak} 🔥"
        )
        
        self.stats_label.config(text=stats_text)
    
    def show_profile(self):
        """Show user profile window."""
        if not self.username:
            return
        
        from .profile_gui import ProfileGUI
        
        def on_profile_close(logout=False):
            """Handle profile window close."""
            if logout:
                # User deleted account, close app
                self.root.quit()
                self.root.destroy()
        
        ProfileGUI(self.root, self.engine, self.username, on_profile_close)
    
    def open_chatbot(self):
        """Open chatbot window for current course."""
        # Check if a course is selected
        if not self.engine.current_course_code:
            from tkinter import messagebox
            messagebox.showinfo("No Course Selected", "Please start a quiz first to use the chatbot.")
            return
        
        # Get course info
        course_code = self.engine.current_course_code
        course_name = self.engine.get_current_course_name()
        
        if not course_name:
            from tkinter import messagebox
            messagebox.showerror("Error", "Could not load course information.")
            return
        
        # Launch chatbot
        from .chatbot_gui import ChatbotGUI
        ChatbotGUI(self.root, self.engine.chatbot, course_code, course_name)
    
    def open_chatbot_from_home(self, course_code: str, course_name: str, note_files: list):
        """Open chatbot window directly from homepage.
        
        Args:
            course_code: Course code (nlp, ml-dl, etc.)
            course_name: Full course name
            note_files: List of note file paths
        """
        # Configure chatbot for this course
        self.engine.chatbot.set_course(course_code, note_files)
        
        # Launch chatbot
        from .chatbot_gui import ChatbotGUI
        ChatbotGUI(self.root, self.engine.chatbot, course_code, course_name)
    
    def on_closing(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit Quizzer V2?"):
            # Logout user if logged in
            if self.username and self.engine.current_user_id:
                self.engine.logout()
            self.root.quit()
            self.root.destroy()
    
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
