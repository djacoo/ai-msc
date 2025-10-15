#!/usr/bin/env python3
"""
Modern Visual Quiz Interface
AI-powered quiz with beautiful animations and modern design
"""

import os
import sys

# Silence tkinter deprecation warnings
os.environ['TK_SILENCE_DEPRECATION'] = '1'

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, font
except ImportError as e:
    print(f"Error: tkinter not available: {e}")
    print("Please make sure tkinter is installed: brew install python-tk@3.11")
    sys.exit(1)

import threading
from pathlib import Path
from quiz import CourseQuiz

class ModernQuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Quiz")
        self.root.geometry("1000x750")
        
        # Modern color scheme
        self.colors = {
            'bg': '#0f172a',           # Dark navy background
            'surface': '#1e293b',       # Lighter surface
            'card': '#334155',          # Card background
            'primary': '#3b82f6',       # Blue
            'secondary': '#8b5cf6',     # Purple
            'success': '#10b981',       # Green
            'warning': '#f59e0b',       # Orange
            'danger': '#ef4444',        # Red
            'text': '#f1f5f9',          # Light text
            'text_secondary': '#94a3b8', # Secondary text
            'accent': '#06b6d4',        # Cyan accent
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Bring window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # Initialize quiz
        repo_root = Path(__file__).parent.parent.absolute()
        self.quiz = CourseQuiz(repo_root)
        
        self.current_question_idx = 0
        self.quiz_chunks = []
        self.course_dir = None
        
        # Animation state
        self.fade_alpha = 0
        self.animation_running = False
        
        # Create UI
        self.create_widgets()
        self.show_course_selection()
    
    def create_widgets(self):
        """Create the main UI widgets with modern design."""
        # Header with gradient-like effect
        header_frame = tk.Frame(self.root, bg=self.colors['surface'], height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title with modern font and animation
        title_label = tk.Label(
            header_frame,
            text="🎓 AI Quiz",
            font=('SF Pro Display', 32, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 32, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['surface']
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Master your knowledge with AI-powered evaluation",
            font=('SF Pro Text', 11) if sys.platform == 'darwin' else ('Segoe UI', 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['surface']
        )
        subtitle_label.pack()
        
        # Fade in the title on startup
        self.fade_in_widget(title_label, duration=500)
        self.fade_in_widget(subtitle_label, duration=500, delay=100)
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Footer with stats
        footer_frame = tk.Frame(self.root, bg=self.colors['surface'], height=60)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            footer_frame,
            text="Ready to start",
            font=('SF Pro Text', 12, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 12, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['surface']
        )
        self.stats_label.pack(pady=20)
    
    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def fade_in_widget(self, widget, duration=300, delay=0):
        """Fade in animation for a widget."""
        if delay > 0:
            self.root.after(delay, lambda: self.fade_in_widget(widget, duration, 0))
            return
        
        steps = 20
        step_duration = duration // steps
        
        def animate_step(step):
            if step <= steps and widget.winfo_exists():
                # Can't change actual opacity in tkinter, so use position animation instead
                widget.pack_configure()
                self.root.after(step_duration, lambda: animate_step(step + 1))
        
        animate_step(0)
    
    def slide_in_widget(self, widget, from_y=-50, duration=400, delay=0):
        """Slide in animation from top."""
        if delay > 0:
            self.root.after(delay, lambda: self.slide_in_widget(widget, from_y, duration, 0))
            return
        
        widget.place(relx=0.5, rely=0.5, anchor='center', y=from_y)
        
        steps = 25
        step_duration = duration // steps
        distance_per_step = -from_y / steps
        
        def animate_step(step, current_y):
            if step <= steps and widget.winfo_exists():
                new_y = current_y + distance_per_step
                widget.place_configure(y=new_y)
                if step == steps:
                    # Final position - switch back to pack
                    widget.place_forget()
                    widget.pack()
                else:
                    self.root.after(step_duration, lambda: animate_step(step + 1, new_y))
        
        animate_step(0, from_y)
    
    def scale_in_widget(self, widget, duration=400, delay=0):
        """Scale in animation - widget grows from small to normal size."""
        if delay > 0:
            self.root.after(delay, lambda: self.scale_in_widget(widget, duration, 0))
            return
        
        # Note: tkinter doesn't support scaling directly, so we'll use a workaround
        # Just make it visible with a slide effect from the center
        original_pack = widget.pack_info()
        widget.pack_forget()
        
        self.root.after(50, lambda: widget.pack(**original_pack))
    
    def bounce_widget(self, widget):
        """Create a bounce effect by animating font size."""
        try:
            current_font = widget.cget('font')
            if isinstance(current_font, str):
                # Parse font string
                parts = current_font.split()
                family = parts[0] if parts else 'Arial'
                size = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 20
                weight = parts[2] if len(parts) > 2 else 'normal'
            else:
                # Font tuple
                family, size, weight = current_font[0], current_font[1], current_font[2] if len(current_font) > 2 else 'normal'
            
            # Bounce animation: grow then shrink to normal
            sizes = [int(size * 0.5), int(size * 0.7), int(size * 0.9), int(size * 1.1), int(size * 1.05), size]
            
            def animate_size(index):
                if index < len(sizes) and widget.winfo_exists():
                    widget.config(font=(family, sizes[index], weight))
                    self.root.after(50, lambda: animate_size(index + 1))
            
            animate_size(0)
        except Exception:
            pass  # If animation fails, widget still displays normally
    
    def create_card(self, parent, **kwargs):
        """Create a modern card widget."""
        card = tk.Frame(
            parent,
            bg=kwargs.get('bg', self.colors['card']),
            relief=tk.FLAT,
            bd=0
        )
        return card
    
    def create_button(self, parent, text, command, style='primary'):
        """Create a modern button with proper contrast."""
        colors = {
            'primary': ('#e0e7ff', '#c7d2fe', '#1e40af'),  # Light bg, hover, dark text
            'success': ('#d1fae5', '#a7f3d0', '#065f46'),
            'secondary': ('#ede9fe', '#ddd6fe', '#5b21b6'),
            'warning': ('#fef3c7', '#fde68a', '#92400e'),
            'danger': ('#fee2e2', '#fecaca', '#991b1b'),
        }
        
        bg_color, hover_color, text_color = colors.get(style, colors['primary'])
        
        btn = tk.Button(
            parent,
            text=text,
            font=('SF Pro Text', 13, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 13, 'bold'),
            bg=bg_color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2',
            command=command
        )
        
        # Smooth hover effects with animation
        def on_enter(e):
            btn.config(bg=hover_color)
            # Slight lift effect
            btn.config(pady=13)
            
        def on_leave(e):
            btn.config(bg=bg_color)
            btn.config(pady=12)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def show_course_selection(self):
        """Display course selection with modern cards."""
        self.clear_content()
        
        # Title with animation
        title = tk.Label(
            self.content_frame,
            text="📚 Choose Your Course",
            font=('SF Pro Display', 24, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 24, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        title.pack(pady=(20, 10))
        self.fade_in_widget(title, duration=300)
        
        subtitle = tk.Label(
            self.content_frame,
            text="Select a course to begin your AI-powered quiz session",
            font=('SF Pro Text', 12) if sys.platform == 'darwin' else ('Segoe UI', 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg']
        )
        subtitle.pack(pady=(0, 30))
        self.fade_in_widget(subtitle, duration=300, delay=100)
        
        # Get courses
        courses = self.quiz.get_courses()
        
        # Course cards container
        cards_container = tk.Frame(self.content_frame, bg=self.colors['bg'])
        cards_container.pack(fill=tk.BOTH, expand=True)
        
        # Create course cards with different colors
        course_colors = [
            self.colors['primary'],
            self.colors['secondary'],
            self.colors['accent'],
            self.colors['success'],
            self.colors['warning'],
        ]
        
        for i, course in enumerate(courses):
            course_name = course.name.replace('-', ' ').title()
            color = course_colors[i % len(course_colors)]
            
            # Card frame
            card = self.create_card(cards_container)
            card.pack(pady=8, fill=tk.X, padx=60)
            
            # Button inside card with light background and dark text
            lighter_color = self.lighten_color(color)
            hover_lighter = self.lighten_color(color, 0.9)
            darker_text = self.darken_color(color, 0.3)
            
            btn = tk.Button(
                card,
                text=f"  {course_name}",
                font=('SF Pro Text', 14, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 14, 'bold'),
                bg=lighter_color,
                fg=darker_text,
                activebackground=hover_lighter,
                activeforeground=darker_text,
                relief=tk.FLAT,
                bd=0,
                padx=25,
                pady=18,
                cursor='hand2',
                anchor='w',
                command=lambda c=course: self.start_quiz(c)
            )
            btn.pack(fill=tk.BOTH, expand=True)
            
            # Smooth hover effect
            def make_hover_handlers(button, normal_color, hover_color, text_col):
                def on_enter(e):
                    button.config(bg=hover_color, pady=19)
                def on_leave(e):
                    button.config(bg=normal_color, pady=18)
                return on_enter, on_leave
            
            on_enter, on_leave = make_hover_handlers(btn, lighter_color, hover_lighter, darker_text)
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            # Staggered animation - cards slide in one by one
            self.animate_card_in(card, delay=i * 80)
    
    def darken_color(self, color, factor=0.85):
        """Darken a hex color by given factor."""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def lighten_color(self, color, factor=0.85):
        """Lighten a hex color - blend with white."""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        # Blend with white (255, 255, 255)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def animate_card_in(self, widget, delay=0):
        """Animate card sliding in from left with fade effect."""
        def start_animation():
            if not widget.winfo_exists():
                return
            
            # Store original pack info
            pack_info = widget.pack_info()
            
            # Start from left (-200 pixels)
            widget.place(x=-200, rely=0, anchor='w')
            
            steps = 20
            step_duration = 15  # ms per step
            start_x = -200
            end_x = 0
            distance_per_step = (end_x - start_x) / steps
            
            def animate_step(step, current_x):
                if step <= steps and widget.winfo_exists():
                    new_x = current_x + distance_per_step
                    widget.place_configure(x=new_x)
                    
                    if step == steps:
                        # Animation complete - switch back to pack
                        widget.place_forget()
                        widget.pack(**pack_info)
                    else:
                        self.root.after(step_duration, lambda: animate_step(step + 1, new_x))
            
            animate_step(0, start_x)
        
        if delay > 0:
            self.root.after(delay, start_animation)
        else:
            start_animation()
    
    def start_quiz(self, course_dir):
        """Start the quiz for selected course."""
        self.course_dir = course_dir
        
        # Show loading screen with animation
        self.show_loading()
        
        # Load quiz data in background
        thread = threading.Thread(target=self.load_quiz_data)
        thread.start()
    
    def show_loading(self):
        """Show animated loading screen."""
        self.clear_content()
        
        loading_card = self.create_card(self.content_frame)
        loading_card.pack(expand=True)
        
        loading_label = tk.Label(
            loading_card,
            text="⚡ Analyzing Course Content",
            font=('SF Pro Display', 20, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 20, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card']
        )
        loading_label.pack(pady=(40, 10))
        
        # Animated dots
        self.loading_dots = 0
        self.loading_text = tk.Label(
            loading_card,
            text="Loading",
            font=('SF Pro Text', 14) if sys.platform == 'darwin' else ('Segoe UI', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['card']
        )
        self.loading_text.pack(pady=10)
        
        self.animate_loading()
    
    def animate_loading(self):
        """Animate loading dots."""
        if hasattr(self, 'loading_text') and self.loading_text.winfo_exists():
            self.loading_dots = (self.loading_dots + 1) % 4
            dots = '.' * self.loading_dots
            self.loading_text.config(text=f"Loading{dots}")
            self.root.after(500, self.animate_loading)
    
    def load_quiz_data(self):
        """Load quiz data in background thread."""
        import random
        
        # Find tex files
        tex_files = self.quiz.find_tex_files(self.course_dir)
        
        # Extract chunks
        all_chunks = []
        for tex_file in tex_files:
            chunks = self.quiz.extract_content_chunks(tex_file)
            all_chunks.extend(chunks)
        
        # Shuffle and limit
        random.shuffle(all_chunks)
        self.quiz_chunks = all_chunks[:min(15, len(all_chunks))]
        
        # Show first question
        self.root.after(0, self.show_question)
    
    def show_question(self):
        """Display current question with modern design."""
        if self.current_question_idx >= len(self.quiz_chunks):
            self.show_completion()
            return
        
        self.clear_content()
        
        chunk_type, title, content = self.quiz_chunks[self.current_question_idx]
        
        # Progress indicator with animation
        progress_text = f"Question {self.current_question_idx + 1} of {len(self.quiz_chunks)}"
        progress_label = tk.Label(
            self.content_frame,
            text=progress_text,
            font=('SF Pro Text', 11, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 11, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg']
        )
        progress_label.pack(anchor=tk.W, pady=(0, 10))
        self.fade_in_widget(progress_label, duration=200)
        
        # Question card
        question_card = self.create_card(self.content_frame)
        question_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Question label (will be updated)
        self.question_label = tk.Label(
            question_card,
            text="⚡ Generating question..." if not self.quiz.use_local_ai else "⚡ Generating question...",
            font=('SF Pro Text', 15) if sys.platform == 'darwin' else ('Segoe UI', 15),
            fg=self.colors['text'],
            bg=self.colors['card'],
            wraplength=900,
            justify=tk.LEFT,
            padx=25,
            pady=20
        )
        self.question_label.pack(fill=tk.X)
        
        # Answer section
        answer_label = tk.Label(
            self.content_frame,
            text="Your Answer:",
            font=('SF Pro Text', 13, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 13, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        answer_label.pack(anchor=tk.W, pady=(20, 5))
        
        # Answer text box with modern styling
        self.answer_text = scrolledtext.ScrolledText(
            self.content_frame,
            font=('SF Mono', 12) if sys.platform == 'darwin' else ('Consolas', 12),
            height=8,
            wrap=tk.WORD,
            bg=self.colors['surface'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.answer_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Submit button
        button_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X)
        
        self.submit_btn = self.create_button(
            button_frame,
            "Submit Answer →",
            lambda: self.evaluate_answer(chunk_type, title, content),
            'primary'
        )
        self.submit_btn.pack(side=tk.RIGHT)
        self.submit_btn.config(state=tk.DISABLED)
        
        # Generate question in background
        thread = threading.Thread(target=self.generate_question_async, args=(chunk_type, title, content))
        thread.start()
    
    def generate_question_async(self, chunk_type, title, content):
        """Generate question in background."""
        question = self.quiz.generate_question_from_chunk(chunk_type, title, content)
        
        # Update UI in main thread
        self.root.after(0, lambda: self.update_question_display(question))
    
    def update_question_display(self, question):
        """Update question display and enable answer input."""
        self.question_label.config(text=f"💡 {question}")
        self.answer_text.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.answer_text.focus()
    
    def evaluate_answer(self, chunk_type, title, content):
        """Evaluate the user's answer."""
        user_answer = self.answer_text.get("1.0", tk.END).strip()
        
        if not user_answer:
            messagebox.showwarning("Empty Answer", "Please enter an answer before submitting.")
            return
        
        # Disable controls
        self.answer_text.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED, text="Evaluating...")
        
        # Evaluate in background
        thread = threading.Thread(target=self.evaluate_async, args=(user_answer, content, title, chunk_type))
        thread.start()
    
    def evaluate_async(self, user_answer, content, title, chunk_type):
        """Evaluate answer in background."""
        level, explanation = self.quiz.evaluate_answer_5_level(user_answer, content, title, chunk_type)
        formatted_ref = self.quiz.format_reference(content, None)
        
        # Show result in main thread
        self.root.after(0, lambda: self.show_result(level, explanation, formatted_ref))
    
    def show_result(self, level, explanation, reference):
        """Display evaluation result with modern design."""
        self.clear_content()
        
        # Result card
        result_card = self.create_card(self.content_frame)
        result_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Level indicator with color
        level_colors = {
            "PERFECT": (self.colors['success'], "⭐⭐⭐⭐⭐ PERFECT"),
            "GOOD": (self.colors['primary'], "⭐⭐⭐⭐ GOOD"),
            "PARTIAL": (self.colors['warning'], "⭐⭐⭐ PARTIAL"),
            "WEAK": (self.colors['danger'], "⭐⭐ WEAK"),
            "WRONG": (self.colors['danger'], "⭐ WRONG")
        }
        
        color, text = level_colors.get(level, (self.colors['text_secondary'], level))
        
        level_label = tk.Label(
            result_card,
            text=text,
            font=('SF Pro Display', 26, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 26, 'bold'),
            fg=color,
            bg=self.colors['card']
        )
        level_label.pack(pady=25)
        
        # Animate the level label with a bounce effect
        self.bounce_widget(level_label)
        
        # Explanation section
        exp_title = tk.Label(
            result_card,
            text="📊 Detailed Evaluation",
            font=('SF Pro Text', 14, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 14, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card']
        )
        exp_title.pack(anchor=tk.W, padx=25, pady=(10, 5))
        
        exp_text = scrolledtext.ScrolledText(
            result_card,
            font=('SF Pro Text', 12) if sys.platform == 'darwin' else ('Segoe UI', 12),
            height=6,
            wrap=tk.WORD,
            bg=self.colors['surface'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=15
        )
        exp_text.pack(fill=tk.X, padx=25, pady=10)
        exp_text.insert("1.0", explanation)
        exp_text.config(state=tk.DISABLED)
        
        # Reference section for non-perfect answers
        if level not in ["PERFECT", "GOOD"]:
            ref_title = tk.Label(
                result_card,
                text="📖 Reference Material",
                font=('SF Pro Text', 14, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 14, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['card']
            )
            ref_title.pack(anchor=tk.W, padx=25, pady=(20, 5))
            
            ref_text = scrolledtext.ScrolledText(
                result_card,
                font=('SF Mono', 11) if sys.platform == 'darwin' else ('Consolas', 11),
                height=8,
                wrap=tk.WORD,
                bg='#422006',
                fg='#fef3c7',
                relief=tk.FLAT,
                bd=0,
                padx=15,
                pady=15
            )
            ref_text.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)
            ref_text.insert("1.0", reference)
            ref_text.config(state=tk.DISABLED)
        
        # Update stats
        if level == "PERFECT":
            self.quiz.streak += 1
            self.quiz.perfect_count += 1
            self.update_stats()
            
            # Next button
            next_btn = self.create_button(
                self.content_frame,
                "Continue →",
                self.next_question,
                'success'
            )
            next_btn.pack(pady=20)
            
        elif level == "GOOD":
            self.quiz.streak += 1
            self.quiz.good_count += 1
            self.update_stats()
            
            # Next button
            next_btn = self.create_button(
                self.content_frame,
                "Continue →",
                self.next_question,
                'primary'
            )
            next_btn.pack(pady=20)
        else:
            # End button
            end_btn = self.create_button(
                self.content_frame,
                "View Results",
                self.show_final_stats,
                'danger'
            )
            end_btn.pack(pady=20)
    
    def next_question(self):
        """Move to next question."""
        if not self.quiz.use_local_ai:
            # Show waiting screen for OpenAI
            self.clear_content()
            
            wait_label = tk.Label(
                self.content_frame,
                text="⏳ Please wait...",
                font=('SF Pro Display', 18, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 18, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['bg']
            )
            wait_label.pack(expand=True)
            
            self.root.after(6000, self._continue_to_next_question)
        else:
            self._continue_to_next_question()
    
    def _continue_to_next_question(self):
        """Continue to next question."""
        self.current_question_idx += 1
        self.show_question()
    
    def update_stats(self):
        """Update stats in footer."""
        self.stats_label.config(
            text=f"🔥 Streak: {self.quiz.streak} | ⭐ Perfect: {self.quiz.perfect_count} | ⭐ Good: {self.quiz.good_count}"
        )
    
    def show_completion(self):
        """Show quiz completion screen."""
        self.clear_content()
        
        # Completion card
        complete_card = self.create_card(self.content_frame)
        complete_card.pack(expand=True)
        
        title_label = tk.Label(
            complete_card,
            text="🎉 Quiz Completed!",
            font=('SF Pro Display', 32, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 32, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['card']
        )
        title_label.pack(pady=30)
        
        stats_label = tk.Label(
            complete_card,
            text=f"Perfect Answers: {self.quiz.perfect_count}\nGood Answers: {self.quiz.good_count}\nFinal Streak: {self.quiz.streak}",
            font=('SF Pro Text', 16) if sys.platform == 'darwin' else ('Segoe UI', 16),
            fg=self.colors['text'],
            bg=self.colors['card'],
            justify=tk.CENTER
        )
        stats_label.pack(pady=20)
    
    def show_final_stats(self):
        """Show final statistics."""
        self.clear_content()
        
        stats_card = self.create_card(self.content_frame)
        stats_card.pack(expand=True, padx=50)
        
        tk.Label(
            stats_card,
            text="📊 Final Results",
            font=('SF Pro Display', 28, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 28, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card']
        ).pack(pady=30)
        
        stats_text = f"""
        🔥 Final Streak: {self.quiz.streak}
        
        ⭐⭐⭐⭐⭐ Perfect Answers: {self.quiz.perfect_count}
        ⭐⭐⭐⭐ Good Answers: {self.quiz.good_count}
        
        Total Excellent: {self.quiz.perfect_count + self.quiz.good_count}
        """
        
        tk.Label(
            stats_card,
            text=stats_text,
            font=('SF Pro Text', 16) if sys.platform == 'darwin' else ('Segoe UI', 16),
            fg=self.colors['text'],
            bg=self.colors['card'],
            justify=tk.LEFT
        ).pack(pady=20, padx=40)
        
        restart_btn = self.create_button(
            stats_card,
            "Start New Quiz",
            lambda: self.root.after(0, self.show_course_selection),
            'primary'
        )
        restart_btn.pack(pady=20)


def main():
    root = tk.Tk()
    app = ModernQuizGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
