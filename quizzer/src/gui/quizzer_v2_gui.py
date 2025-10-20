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
from .macos_theme import MacOSTheme
import random


class QuizzerV2GUI:
    """Modern GUI for Quizzer V2."""
    
    # Use native macOS color scheme
    COLORS = MacOSTheme.COLORS
    
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
        title = f"Quizzer V2" if not username else f"Quizzer V2"
        self.root.title(title)
        self.root.geometry("900x900")  # Taller to fit all courses comfortably
        self.root.minsize(700, 600)
        
        # Apply native macOS window configuration
        MacOSTheme.configure_window(self.root)
        
        # macOS-specific window styling - unified toolbar look
        if MacOSTheme.is_macos():
            try:
                # Unified title/toolbar appearance
                self.root.tk.call("::tk::unsupported::MacWindowStyle", "style", 
                                 self.root._w, "unified", "closeBox collapseBox resizable zoomBox")
            except:
                pass
        
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
        
        # Use aqua theme on macOS for native look
        if MacOSTheme.is_macos():
            try:
                style.theme_use("aqua")
            except:
                style.theme_use("clam")
        else:
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
        
        # Primary button style with native macOS accent color
        style.configure(
            "Primary.TButton",
            background=self.COLORS["accent"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 14, "bold"),
            padding=(40, 12)
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.COLORS["accent_hover"]), ("pressed", self.COLORS["accent_pressed"])],
            foreground=[("active", "white"), ("pressed", "white")]
        )
        
        # Label style
        style.configure(
            "Title.TLabel",
            background=self.COLORS["window_bg"],
            foreground=self.COLORS["text_primary"],
            font=("SF Pro", 24, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            background=self.COLORS["window_bg"],
            foreground=self.COLORS["text_primary"],
            font=("SF Pro", 14)
        )
    
    def build_ui(self):
        """Build main UI components with native macOS toolbar layout."""
        # Toolbar - native macOS unified toolbar
        toolbar_container = tk.Frame(self.root, bg=self.COLORS["window_bg"])
        toolbar_container.pack(fill="x", side="top")
        
        self.toolbar_frame = tk.Frame(toolbar_container, bg=self.COLORS["window_bg"], height=52)
        self.toolbar_frame.pack(fill="x", padx=MacOSTheme.SPACING["xl"], pady=(MacOSTheme.SPACING["md"], 0))
        self.toolbar_frame.pack_propagate(False)
        
        # Left side - title
        left_frame = tk.Frame(self.toolbar_frame, bg=self.COLORS["window_bg"])
        left_frame.pack(side="left", fill="y")
        
        # Title with native macOS style
        if self.username:
            title_text = "Courses"
            self.title_label = MacOSTheme.create_label(
                left_frame,
                text=title_text,
                style="title_large",
                bg=self.COLORS["window_bg"],
                fg=self.COLORS["text_primary"]
            )
            self.title_label.pack(side="left", anchor="w", pady=8)
        
        # Right side - toolbar buttons
        right_frame = tk.Frame(self.toolbar_frame, bg=self.COLORS["window_bg"])
        right_frame.pack(side="right", fill="y")
        
        # Profile button (if logged in)
        if self.username:
            profile_btn = MacOSTheme.create_button(
                right_frame,
                text=f"👤 {self.username}",
                command=self.show_profile,
                style="secondary",
                size="small"
            )
            profile_btn.pack(side="right", padx=(MacOSTheme.SPACING["sm"], 0))
        
        # Chatbot button (hidden by default)
        self.chatbot_btn = MacOSTheme.create_button(
            right_frame,
            text="💬 Ask AI",
            command=self.open_chatbot,
            style="primary",
            size="small"
        )
        # Don't pack yet
        
        # Main content area with native insets
        self.content_frame = tk.Frame(self.root, bg=self.COLORS["window_bg"])
        self.content_frame.pack(fill="both", expand=True, 
                               padx=MacOSTheme.SPACING["xl"], 
                               pady=(MacOSTheme.SPACING["md"], MacOSTheme.SPACING["xl"]))
        
        # Status bar (macOS style)
        status_sep = MacOSTheme.create_separator(self.root)
        status_sep.pack(fill="x", side="bottom")
        
        self.status_frame = tk.Frame(self.root, bg=self.COLORS["window_bg"], height=28)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        self.stats_label = MacOSTheme.create_label(
            self.status_frame,
            text="Ready",
            style="footnote",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_tertiary"]
        )
        self.stats_label.pack(side="left", padx=MacOSTheme.SPACING["md"], pady=6)
    
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
        
        loading_frame = tk.Frame(self.content_frame, bg=self.COLORS["window_bg"])
        loading_frame.pack(expand=True)
        
        # Welcome message
        welcome = MacOSTheme.create_label(
            loading_frame,
            text=f"Welcome{', ' + self.username if self.username else ''}!",
            style="display",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["accent"]
        )
        welcome.pack(pady=(100, 20))
        
        # Progress bar with native accent color
        self.init_progress_bar = ProgressBar(
            loading_frame,
            width=400,
            height=6,
            color=self.COLORS["accent"],
            bg=self.COLORS["control_bg"]
        )
        self.init_progress_bar.pack(pady=30)
        
        # Loading message
        self.init_loading_label = MacOSTheme.create_label(
            loading_frame,
            text="Loading application...",
            style="callout",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_secondary"]
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
        """Show course selection screen with native macOS list view."""
        # Update toolbar title
        if hasattr(self, 'title_label'):
            self.title_label.config(text="Courses")
        
        # Hide chatbot button when returning to main menu
        if hasattr(self, 'chatbot_btn'):
            self.chatbot_btn.pack_forget()
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # User stats (if logged in) - inline, macOS style
        if self.username:
            profile = self.engine.get_user_profile()
            if profile:
                stats = profile['stats']
                rating = profile['rating']
                
                stats_frame = tk.Frame(self.content_frame, bg=self.COLORS["window_bg"])
                stats_frame.pack(fill="x", pady=(0, MacOSTheme.SPACING["lg"]))
                
                MacOSTheme.create_label(
                    stats_frame,
                    text=f"{rating['emoji']} {rating['tier']}  ·  {stats['total_quizzes']} quizzes  ·  {stats['accuracy']:.0f}%  ·  {stats['total_stars']} ⭐",
                    style="callout",
                    bg=self.COLORS["window_bg"],
                    fg=self.COLORS["text_secondary"]
                ).pack(anchor="w")
        
        # Get available courses
        courses = self.engine.get_available_courses()
        
        # Simple list container - no scrolling, all items visible
        list_container = tk.Frame(
            self.content_frame,
            bg=self.COLORS["window_bg"]
        )
        list_container.pack(fill="x", expand=False, pady=(0, 20))
        
        # List items - simple clean style
        for i, course in enumerate(courses):
            # Check if course has notes
            has_notes = course["notes_available"] > 0
            
            # Course card with border
            card = tk.Frame(
                list_container,
                bg=self.COLORS["card_bg"],
                highlightbackground=self.COLORS["border"],
                highlightthickness=1
            )
            card.pack(fill="x", padx=0, pady=(0, 12))
            
            # Content container with proper padding
            content = tk.Frame(card, bg=self.COLORS["card_bg"])
            content.pack(fill="x", padx=20, pady=16)
            
            # Left side - course info
            left_side = tk.Frame(content, bg=self.COLORS["card_bg"])
            left_side.pack(side="left", fill="both", expand=True)
            
            # Course icon and title
            title_row = tk.Frame(left_side, bg=self.COLORS["card_bg"])
            title_row.pack(fill="x", anchor="w")
            
            MacOSTheme.create_label(
                title_row,
                text="📚",
                style="title",  # Larger icon
                bg=self.COLORS["card_bg"]
            ).pack(side="left", padx=(0, MacOSTheme.SPACING["md"]))
            
            MacOSTheme.create_label(
                title_row,
                text=course['name'],
                style="headline",  # Larger title
                bg=self.COLORS["card_bg"],
                fg=self.COLORS["text_primary"]
            ).pack(side="left")
            
            # Course info subtitle
            if has_notes:
                subtitle_text = f"{course['notes_available']} document{'s' if course['notes_available'] > 1 else ''} available"
                subtitle_color = self.COLORS["text_tertiary"]
            else:
                subtitle_text = "No documents available"
                subtitle_color = self.COLORS["error"]
            
            MacOSTheme.create_label(
                left_side,
                text=subtitle_text,
                style="callout",  # Slightly larger subtitle
                bg=self.COLORS["card_bg"],
                fg=subtitle_color
            ).pack(anchor="w", pady=(MacOSTheme.SPACING["xs"], 0), padx=(30, 0))
            
            # Right side - action buttons
            right_side = tk.Frame(content, bg=self.COLORS["card_bg"])
            right_side.pack(side="right", padx=(MacOSTheme.SPACING["lg"], 0))
            
            # Only show buttons if course has notes
            if has_notes:
                # Chat button
                chat_btn = MacOSTheme.create_button(
                    right_side,
                    text="💬",
                    command=lambda c=course: self.open_chatbot_from_home(c["code"], c["name"], c["note_files"]),
                    style="secondary",
                    size="small"
                )
                chat_btn.pack(side="left", padx=(0, MacOSTheme.SPACING["xs"]))
                
                # Quiz button
                quiz_btn = MacOSTheme.create_button(
                    right_side,
                    text="Start Quiz",
                    command=lambda c=course: self.show_quiz_config(c["code"]),
                    style="primary",
                    size="small"
                )
                quiz_btn.pack(side="left")
            else:
                # Show "Add Notes" button for courses without notes
                add_notes_label = MacOSTheme.create_label(
                    right_side,
                    text="📁 Add notes to enable",
                    style="footnote",
                    bg=self.COLORS["card_bg"],
                    fg=self.COLORS["text_tertiary"]
                )
                add_notes_label.pack(side="left")
            
            # Apply hover effect only if course has notes
            if has_notes:
                MacOSTheme.apply_hover_effect(content, self.COLORS["list_hover"], children=True)
    
    def show_quiz_config(self, course_code: str):
        """Show quiz configuration screen for question type selection."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = MacOSTheme.create_label(
            self.content_frame,
            text="⚙️ Quiz Configuration",
            style="title_large",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_primary"]
        )
        title.pack(pady=(20, 10))
        
        # Subtitle
        subtitle = MacOSTheme.create_label(
            self.content_frame,
            text="Choose your preferred question types",
            style="callout",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_secondary"]
        )
        subtitle.pack(pady=(0, 20))
        
        # Simple options container
        options_container = tk.Frame(
            self.content_frame,
            bg=self.COLORS["window_bg"]
        )
        options_container.pack(fill="x", expand=False, pady=(0, 20))
        
        # Radio buttons for question type
        self.question_type_var = tk.StringVar(value="mixed")
        
        type_options = [
            ("mcq", "📋 Multiple Choice Only", "Fast-paced quiz with checkboxes"),
            ("short", "✍️ Short Answers Only", "Concise explanations (2-4 sentences)"),
            ("long", "📝 Long Answers Only", "Detailed explanations and derivations"),
            ("mixed_open", "📊 Mixed Answers (Short + Long)", "Variety of open-ended questions"),
            ("mixed", "🎯 Everything Mixed", "MCQ + Short + Long answers")
        ]
        
        for i, (value, label, description) in enumerate(type_options):
            # Option card
            frame_container = tk.Frame(
                options_container,
                bg=self.COLORS["card_bg"],
                highlightbackground=self.COLORS["border"],
                highlightthickness=1
            )
            frame_container.pack(fill="x", padx=0, pady=(0, 10))
            
            frame = tk.Frame(frame_container, bg=self.COLORS["card_bg"], padx=16, pady=12)
            frame.pack(fill="x")
            
            rb = tk.Radiobutton(
                frame,
                text=label,
                variable=self.question_type_var,
                value=value,
                font=("SF Pro", 13, "bold"),
                bg=self.COLORS["card_bg"],
                fg=self.COLORS["text_primary"],
                selectcolor="#FFFFFF",
                activebackground=self.COLORS["list_hover"],
                activeforeground=self.COLORS["text_primary"],
                cursor="hand2"
            )
            rb.pack(anchor="w")
            
            desc = MacOSTheme.create_label(
                frame,
                text=f"  {description}",
                style="footnote",
                bg=self.COLORS["card_bg"],
                fg=self.COLORS["text_secondary"],
                justify="left"
            )
            desc.pack(anchor="w", padx=(25, 0))
            
            # Add hover effect
            MacOSTheme.apply_hover_effect(frame_container, self.COLORS["list_hover"], children=True)
        
        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg=self.COLORS["window_bg"])
        btn_frame.pack(pady=30)
        
        # Back button using MacOSTheme
        back_btn = MacOSTheme.create_button(
            btn_frame,
            text="← Back",
            command=self.show_start_screen,
            style="secondary",
            size="large"
        )
        back_btn.pack(side="left", padx=10)
        
        # Start button using MacOSTheme
        start_btn = MacOSTheme.create_button(
            btn_frame,
            text="Start Quiz →",
            command=lambda: self.start_quiz(course_code),
            style="primary",
            size="large"
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
            self.chatbot_btn.pack(side="right", padx=(MacOSTheme.SPACING["sm"], MacOSTheme.SPACING["sm"]))
        self.show_question()
    
    def show_loading_screen(self, message="Generating questions..."):
        """Show loading animation."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        loading_frame = tk.Frame(self.content_frame, bg=self.COLORS["window_bg"])
        loading_frame.pack(expand=True)
        
        # Loading spinner with native accent color
        self.loading_spinner = LoadingSpinner(loading_frame, size=60, color=self.COLORS["accent"])
        self.loading_spinner.pack(pady=30)
        self.loading_spinner.start()
        
        # Loading message with animated dots
        self.loading_message = MacOSTheme.create_label(
            loading_frame,
            text=message,
            style="body",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_secondary"]
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
        
        progress_label = MacOSTheme.create_label(
            self.content_frame,
            text=progress_text,
            style="callout",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_secondary"]
        )
        progress_label.pack(anchor="w", pady=(0, 5))
        
        # Animated progress bar
        progress_frame = tk.Frame(self.content_frame, bg=self.COLORS["control_bg"], height=8)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        percentage = (progress['current'] / progress['total']) if progress['total'] > 0 else 0
        progress_bar = tk.Frame(progress_frame, bg=self.COLORS["accent"], height=8)
        progress_bar.place(x=0, y=0, relwidth=0, relheight=1)
        
        # Animate progress bar fill
        self.animate_progress_bar(progress_bar, percentage)
        
        # Question card with rounded corners and light background
        card_container = tk.Frame(self.content_frame, bg=self.COLORS["window_bg"])
        card_container.pack(fill="both", expand=True, pady=10)
        
        card = tk.Frame(
            card_container, 
            bg=self.COLORS["card_bg"],
            highlightbackground=self.COLORS["border"],
            highlightthickness=1
        )
        card.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Question type badge
        badge_frame = tk.Frame(card, bg=self.COLORS["card_bg"])
        badge_frame.pack(anchor="w", padx=20, pady=(20, 10))
        
        qtype_badge = tk.Label(
            badge_frame,
            text=f"📝 {question['type'].replace('_', ' ').title()}",
            font=("SF Pro", 11, "bold"),
            bg=self.COLORS["accent"],
            fg="#FFFFFF",
            padx=12,
            pady=6,
            relief="flat"
        )
        qtype_badge.pack()
        
        # Question text
        q_text = MacOSTheme.create_label(
            card,
            text=question["prompt"],
            style="body",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_primary"],
            wraplength=800,
            justify="left"
        )
        q_text.pack(anchor="w", padx=20, pady=10)
        
        # Grounding info
        if question.get("grounding"):
            g = question["grounding"][0]
            grounding_text = f"📚 Source: {Path(g['path']).name}, page {g['page']}"
            
            grounding_label = MacOSTheme.create_label(
                card,
                text=grounding_text,
                style="footnote",
                bg=self.COLORS["card_bg"],
                fg=self.COLORS["accent"]
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
        
        options_frame = tk.Frame(parent, bg=self.COLORS["card_bg"])
        options_frame.pack(fill="x", padx=20, pady=10)
        
        for i, option in enumerate(options):
            # Simple option card
            option_container = tk.Frame(
                options_frame,
                bg=self.COLORS["card_bg"],
                highlightbackground=self.COLORS["border"],
                highlightthickness=1
            )
            option_container.pack(fill="x", pady=(0, 8))
            
            rb = tk.Radiobutton(
                option_container,
                text=option,
                variable=self.selected_option,
                value=option[0],  # A, B, C, D
                font=("SF Pro", 13),
                bg=self.COLORS["card_bg"],
                fg=self.COLORS["text_primary"],
                selectcolor="#FFFFFF",
                activebackground=self.COLORS["list_hover"],
                activeforeground=self.COLORS["text_primary"],
                bd=0,
                cursor="hand2",
                padx=16,
                pady=12
            )
            rb.pack(fill="x")
            
            # Add hover effect
            MacOSTheme.apply_hover_effect(option_container, self.COLORS["list_hover"], children=True)
        
        # Submit button
        submit_btn = MacOSTheme.create_button(
            parent,
            text="Submit Answer",
            command=lambda: self.submit_answer(self.selected_option.get()),
            style="primary",
            size="large"
        )
        submit_btn.pack(pady=20)
    
    def show_text_answer(self, parent, question):
        """Show text answer input.
        
        Args:
            parent: Parent widget
            question: Question object
        """
        # Answer text area with simple styling
        text_container = tk.Frame(
            parent,
            bg=self.COLORS["card_bg"],
            highlightbackground=self.COLORS["border"],
            highlightthickness=1
        )
        text_container.pack(fill="both", padx=20, pady=10)
        
        self.answer_text = scrolledtext.ScrolledText(
            text_container,
            font=("SF Pro", 13),
            bg=self.COLORS["content_bg"],
            fg=self.COLORS["text_primary"],
            insertbackground=self.COLORS["accent"],
            selectbackground=self.COLORS["selection"],
            selectforeground="#FFFFFF",
            height=8,
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.answer_text.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Submit button
        submit_btn = MacOSTheme.create_button(
            parent,
            text="Submit Answer",
            command=lambda: self.submit_answer(self.answer_text.get("1.0", "end-1c")),
            style="primary",
            size="large"
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
        
        # Result card with rounded corners and animated entrance
        card = tk.Frame(
            self.content_frame,
            bg="#FFFFFF",
            highlightbackground=self.COLORS["border"],
            highlightthickness=2,
            relief="flat"
        )
        card.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Animate card entrance with bounce
        AnimationEngine.scale_in(card, duration=500, easing=AnimationEngine.ease_out_bounce)
        
        # Animated result header
        result_header = tk.Label(
            card,
            text=f"{result_emoji} {result_title}",
            font=("SF Pro", 28, "bold"),
            bg="#FFFFFF",
            fg=result_color
        )
        result_header.pack(pady=(30, 10))
        
        # Animate the header with smooth pulse
        AnimationEngine.pulse(result_header, duration=800, count=2, scale_factor=0.12)
        
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
            bg="#FFFFFF",
            fg=self.COLORS["text_primary"]
        )
        score_label.pack(pady=10)
        
        # Animate score counting up with smooth transition
        self.animate_score_count(score_label, points_awarded, points_possible)
        
        # Explanation with rounded container
        explanation_frame = tk.Frame(card, bg="#FFFFFF")
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
            font=("SF Pro", 13),
            bg="#FFFFFF",
            fg=self.COLORS["text_primary"],
            wraplength=850,
            justify="left"
        )
        explanation.pack(pady=10)
        
        # Animate explanation entrance
        AnimationEngine.fade_in(explanation, duration=400)
        
        # Rubric checks
        checks = grading.get("checks", [])
        if checks:
            checks_label = tk.Label(
                explanation_frame,
                text="📋 Rubric Breakdown:",
                font=("SF Pro", 12, "bold"),
                bg="#FFFFFF",
                fg=self.COLORS["accent"]
            )
            checks_label.pack(anchor="w", pady=(10, 5))
            
            for check in checks:
                status = "✓" if check.get("met") else "✗"
                check_color = self.COLORS["success"] if check.get("met") else self.COLORS["error"]
                
                check_container = tk.Frame(
                    explanation_frame,
                    bg=self.COLORS["control_bg"] if check.get("met") else "#FEE2E2",
                    highlightbackground=self.COLORS["border"],
                    highlightthickness=1
                )
                check_container.pack(fill="x", pady=4)
                
                check_text = tk.Label(
                    check_container,
                    text=f"{status} {check['criterion']}: {check.get('evidence', '')}",
                    font=("SF Pro", 11),
                    bg=self.COLORS["control_bg"] if check.get("met") else "#FEE2E2",
                    fg=check_color,
                    wraplength=780,
                    justify="left",
                    padx=10,
                    pady=6
                )
                check_text.pack(fill="x")
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
        """Animate result header with smooth pulse effect."""
        # This method is now replaced by AnimationEngine.pulse
        # Kept for backward compatibility
        pass
    
    def animate_score_count(self, label, target_score, points_possible=10, current=0):
        """Animate counting up to target score with smooth easing."""
        if not label.winfo_exists():
            return
        
        steps = 40
        step_duration = 30  # 30ms per step for smooth 1.2 second animation
        
        def count_step(step=0):
            if not label.winfo_exists() or step > steps:
                if label.winfo_exists():
                    label.config(text=f"Score: {target_score}/{points_possible} points")
                return
            
            # Use easing for smooth count
            progress = AnimationEngine.ease_out_cubic(step / steps)
            current_value = int(target_score * progress)
            
            label.config(text=f"Score: {current_value}/{points_possible} points")
            self.root.after(step_duration, lambda: count_step(step + 1))
        
        count_step()
    
    def animate_progress_bar(self, bar, target_width, current_width=0.0):
        """Animate progress bar fill with smooth easing."""
        if not bar.winfo_exists() or current_width >= target_width:
            if bar.winfo_exists():
                bar.place(relwidth=target_width)
            return
        
        # Smooth easing with faster acceleration
        current_width += (target_width - current_width) * 0.2
        if abs(target_width - current_width) < 0.005:
            current_width = target_width
        
        bar.place(relwidth=current_width)
        self.root.after(16, lambda: self.animate_progress_bar(bar, target_width, current_width))  # 60fps
    
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
        
        # Results card with rounded corners
        card = tk.Frame(
            self.content_frame, 
            bg="#FFFFFF",
            highlightbackground=self.COLORS["border"],
            highlightthickness=2
        )
        card.pack(fill="both", expand=True, pady=10)
        
        # Animate card entrance
        AnimationEngine.scale_in(card, duration=500, easing=AnimationEngine.ease_out_bounce)
        
        # Header with gradient-like effect
        header_frame = tk.Frame(card, bg=self.COLORS["accent"])
        header_frame.pack(fill="x")
        
        header = tk.Label(
            header_frame,
            text="🎉 Quiz Complete!",
            font=("SF Pro", 28, "bold"),
            bg=self.COLORS["accent"],
            fg="#FFFFFF",
            pady=20
        )
        header.pack()
        
        # Animate header
        AnimationEngine.pulse(header, duration=800, count=2, scale_factor=0.1)
        
        # Stats
        stats_frame = tk.Frame(card, bg="#FFFFFF")
        stats_frame.pack(pady=30)
        
        # Calculate total possible score
        total_possible = self.questions_answered * 10
        percentage = (self.score / total_possible * 100) if total_possible > 0 else 0
        
        # Determine color based on percentage
        if percentage >= 80:
            score_color = self.COLORS["success"]
        elif percentage >= 60:
            score_color = "#F59E0B"
        else:
            score_color = self.COLORS["error"]
        
        # Score with animation
        score_label = tk.Label(
            stats_frame,
            text=f"Total Score: 0/{total_possible} points (0.0%)",
            font=("SF Pro", 20, "bold"),
            bg="#FFFFFF",
            fg=score_color
        )
        score_label.pack(pady=10)
        
        # Animate score counting
        self._animate_final_score(score_label, self.score, total_possible, percentage)
        
        # Questions answered
        answered_label = tk.Label(
            stats_frame,
            text=f"Questions Answered: {self.questions_answered}",
            font=("SF Pro", 14),
            bg="#FFFFFF",
            fg=self.COLORS["text_primary"]
        )
        answered_label.pack(pady=5)
        
        # Buttons with MacOSTheme
        btn_frame = tk.Frame(card, bg="#FFFFFF")
        btn_frame.pack(pady=20)
        
        # Back to Menu button
        menu_btn = MacOSTheme.create_button(
            btn_frame,
            text="← Back to Menu",
            command=self.show_start_screen,
            style="secondary",
            size="large"
        )
        menu_btn.pack(side="left", padx=10)
        
        # New Quiz button
        new_quiz_btn = MacOSTheme.create_button(
            btn_frame,
            text="New Quiz →",
            command=self.reset_and_start,
            style="primary",
            size="large"
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
    
    def _animate_final_score(self, label, score, total, percentage):
        """Animate final score counting."""
        steps = 50
        step_duration = 25
        
        def count_step(step=0):
            if not label.winfo_exists() or step > steps:
                if label.winfo_exists():
                    label.config(text=f"Total Score: {score}/{total} points ({percentage:.1f}%)")
                return
            
            progress = AnimationEngine.ease_out_cubic(step / steps)
            current_score = int(score * progress)
            current_percentage = percentage * progress
            
            label.config(text=f"Total Score: {current_score}/{total} points ({current_percentage:.1f}%)")
            self.root.after(step_duration, lambda: count_step(step + 1))
        
        count_step()
    
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
