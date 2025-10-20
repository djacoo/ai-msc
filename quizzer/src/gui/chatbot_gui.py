#!/usr/bin/env python3
"""
Chatbot GUI
Modern chat interface for course Q&A
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ..utils.animations import ProgressBar, AnimationEngine
import time
from pathlib import Path
from typing import Optional
from .macos_theme import MacOSTheme


class ChatbotGUI:
    """Modern chat interface for asking questions about course notes."""
    
    # Use native macOS color scheme
    COLORS = MacOSTheme.COLORS
    
    # Chat-specific colors (light mode)
    CHAT_COLORS = {
        "user_bubble": MacOSTheme.COLORS["accent"],  # Blue bubble like iMessage
        "ai_bubble": "#E9E9EB",  # Light gray bubble for AI (like iMessage received)
    }
    
    def __init__(self, parent, chatbot_engine, course_code: str, course_name: str, on_close=None):
        """Initialize chatbot GUI.
        
        Args:
            parent: Parent window
            chatbot_engine: ChatbotEngine instance
            course_code: Course code (nlp, ml-dl, etc.)
            course_name: Full course name
            on_close: Callback when window is closed
        """
        self.parent = parent
        self.chatbot = chatbot_engine
        self.course_code = course_code
        self.course_name = course_name
        self.on_close = on_close
        self.is_generating = False
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Course Assistant")
        self.window.geometry("700x650")  # More compact, native size
        self.window.minsize(500, 400)
        
        # Apply native macOS styling
        MacOSTheme.configure_window(self.window)
        if MacOSTheme.is_macos():
            try:
                # Unified toolbar appearance like Messages.app
                self.window.tk.call("::tk::unsupported::MacWindowStyle", "style", 
                                   self.window._w, "unified", "closeBox collapseBox resizable zoomBox")
            except:
                pass
        
        # Handle close
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # Build UI
        self.build_ui()
        
        # Show welcome message
        self.show_welcome_message()
    
    def build_ui(self):
        """Build the chat interface with native macOS toolbar."""
        # Toolbar - native macOS unified toolbar
        toolbar_frame = tk.Frame(self.window, bg=self.COLORS["window_bg"], height=52)
        toolbar_frame.pack(fill="x", side="top", padx=MacOSTheme.SPACING["xl"], pady=(MacOSTheme.SPACING["md"], 0))
        toolbar_frame.pack_propagate(False)
        
        # Left side - course title
        left_frame = tk.Frame(toolbar_frame, bg=self.COLORS["window_bg"])
        left_frame.pack(side="left", fill="y")
        
        title = MacOSTheme.create_label(
            left_frame,
            text=f"📚 {self.course_name}",
            style="title",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_primary"]
        )
        title.pack(side="left", anchor="w", pady=8)
        
        # Right side - clear button
        right_frame = tk.Frame(toolbar_frame, bg=self.COLORS["window_bg"])
        right_frame.pack(side="right", fill="y")
        
        clear_btn = MacOSTheme.create_button(
            right_frame,
            text="Clear",
            command=self.clear_chat,
            style="secondary",
            size="small"
        )
        clear_btn.pack(side="right")
        
        # Chat display area
        chat_container = tk.Frame(self.window, bg=self.COLORS["window_bg"])
        chat_container.pack(fill="both", expand=True, padx=MacOSTheme.SPACING["md"], pady=MacOSTheme.SPACING["md"])
        
        # Create canvas for scrollable chat
        self.canvas = tk.Canvas(chat_container, bg=self.COLORS["window_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.canvas.yview)
        
        self.chat_frame = tk.Frame(self.canvas, bg=self.COLORS["window_bg"])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        
        # Bind canvas resize
        self.chat_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel scrolling to multiple widgets for better coverage
        # This ensures scrolling works regardless of where the mouse is
        self._bind_mousewheel(self.window)
        self._bind_mousewheel(chat_container)
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.chat_frame)
        
        # Show loading screen before displaying welcome message
        self.show_chatbot_loading()
        
        # Input area - native macOS style
        input_frame = tk.Frame(self.window, bg=self.COLORS["window_bg"], height=80)
        input_frame.pack(fill="x", side="bottom", padx=MacOSTheme.SPACING["xl"], pady=MacOSTheme.SPACING["md"])
        input_frame.pack_propagate(False)
        
        # Input field with rounded corners and proper styling
        input_container = tk.Frame(
            input_frame,
            bg=self.COLORS["window_bg"],
            highlightbackground=self.COLORS["border"],
            highlightthickness=2
        )
        input_container.pack(side="left", fill="both", expand=True, padx=(0, MacOSTheme.SPACING["sm"]))
        
        self.input_text = tk.Text(
            input_container,
            font=("SF Pro", 14),
            bg="#FFFFFF",  # White background for input
            fg=self.COLORS["text_primary"],  # Dark text
            insertbackground=self.COLORS["accent"],  # Blue cursor
            selectbackground=self.COLORS["selection"],  # Blue selection
            selectforeground="#FFFFFF",  # White selected text
            height=2,
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=MacOSTheme.SPACING["md"],
            pady=MacOSTheme.SPACING["sm"]
        )
        self.input_text.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Add focus effects
        def on_focus_in(e):
            input_container.configure(highlightbackground=self.COLORS["accent"], highlightthickness=2)
        
        def on_focus_out(e):
            input_container.configure(highlightbackground=self.COLORS["border"], highlightthickness=2)
        
        self.input_text.bind("<FocusIn>", on_focus_in)
        self.input_text.bind("<FocusOut>", on_focus_out)
        
        # Bind Enter key
        self.input_text.bind("<Return>", self.on_enter_key)
        self.input_text.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for new line
        
        # Send button - circular like Messages.app
        send_btn = MacOSTheme.create_button(
            input_frame,
            text="↑",  # Up arrow like Messages
            command=self.send_message,
            style="primary",
            size="regular"
        )
        send_btn.pack(side="right")
        
        # Focus input
        self.input_text.focus()
    
    def _bind_mousewheel(self, widget):
        """Bind mousewheel events to a widget for scrolling.
        
        Args:
            widget: The widget to bind scroll events to
        """
        # Bind all scroll event types
        widget.bind("<MouseWheel>", self.on_mousewheel, add="+")
        widget.bind("<Button-4>", self.on_mousewheel, add="+")  # Linux scroll up
        widget.bind("<Button-5>", self.on_mousewheel, add="+")  # Linux scroll down
    
    def on_frame_configure(self, event=None):
        """Update canvas scroll region when frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        """Update chat frame width when canvas is resized."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def on_mousewheel(self, event):
        """Handle mousewheel/trackpad scrolling with smooth support for macOS."""
        # Linux scroll wheel
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:
            # macOS and Windows
            delta = event.delta
            
            # Reduce sensitivity to 40% of original (divide by 2.5x more)
            # Detect platform and handle appropriately
            if abs(delta) > 100:  
                # Windows: delta is typically ±120 per notch
                scroll_amount = int(-1 * (delta / 300))  # 40% of original (120 * 2.5)
            else:  
                # macOS: delta is typically small values for trackpad
                # Reduce trackpad sensitivity to 40%
                if abs(delta) <= 3:
                    # Very small movements - ignore to reduce sensitivity
                    scroll_amount = 0
                elif abs(delta) <= 12:
                    # Medium trackpad scrolling - every 4 delta units = 1 scroll
                    scroll_amount = int(-1 * delta / 4) if abs(delta) > 3 else 0
                else:
                    # Mouse wheel on macOS
                    scroll_amount = int(-1 * delta / 25)  # 40% of original (10 * 2.5)
            
            if scroll_amount != 0:
                self.canvas.yview_scroll(scroll_amount, "units")
    
    def show_chatbot_loading(self):
        """Show loading screen for chatbot initialization."""
        # Create temporary loading overlay
        loading_overlay = tk.Frame(self.chat_frame, bg=self.COLORS["window_bg"])
        loading_overlay.pack(expand=True, fill="both", pady=100)
        
        # Chatbot icon
        icon = MacOSTheme.create_label(
            loading_overlay,
            text="💬",
            style="display_large",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["accent"]
        )
        icon.pack(pady=20)
        
        # Loading title
        title = MacOSTheme.create_label(
            loading_overlay,
            text="Initializing AI Assistant",
            style="headline",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_primary"]
        )
        title.pack(pady=MacOSTheme.SPACING["md"])
        
        # Progress bar
        self.chatbot_progress = ProgressBar(
            loading_overlay,
            width=300,
            height=5,
            color=self.COLORS["accent"],
            bg=self.COLORS["control_bg"]
        )
        self.chatbot_progress.pack(pady=20)
        
        # Loading text
        self.chatbot_load_label = MacOSTheme.create_label(
            loading_overlay,
            text="Loading course notes...",
            style="footnote",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_tertiary"]
        )
        self.chatbot_load_label.pack(pady=MacOSTheme.SPACING["sm"])
        
        # Animate loading
        self._animate_chatbot_loading(0, loading_overlay)
    
    def _animate_chatbot_loading(self, progress, overlay):
        """Animate chatbot loading progress.
        
        Args:
            progress: Current progress (0-100)
            overlay: Overlay frame to destroy when done
        """
        # Check if overlay still exists
        if not overlay.winfo_exists():
            return
            
        if progress <= 100:
            try:
                self.chatbot_progress.set_progress(progress, animated=False)  # Changed to False to avoid nested animations
            except:
                return
            
            # Update text
            if progress < 33:
                text = "Loading course notes..."
            elif progress < 66:
                text = "Initializing AI engine..."
            else:
                text = "Preparing chat interface..."
            
            try:
                self.chatbot_load_label.config(text=text)
            except:
                return
            
            # Continue animation (2 seconds total: 100ms * 20 steps = 2000ms)
            self.window.after(100, lambda: self._animate_chatbot_loading(progress + 5, overlay))
        else:
            # Loading complete
            try:
                overlay.destroy()
                self.show_welcome_message()
            except:
                pass
    
    def show_welcome_message(self):
        """Display welcome message."""
        overview = self.chatbot.get_course_overview()
        
        welcome_bubble = tk.Frame(self.chat_frame, bg=self.COLORS["window_bg"])
        welcome_bubble.pack(fill="x", padx=MacOSTheme.SPACING["md"], pady=MacOSTheme.SPACING["md"], anchor="w")
        
        # Rounded bubble with border
        bubble = tk.Frame(
            welcome_bubble, 
            bg=self.CHAT_COLORS["ai_bubble"],
            highlightbackground=self.COLORS["separator"],
            highlightthickness=1
        )
        bubble.pack(anchor="w", padx=MacOSTheme.SPACING["xl"])
        
        msg_label = MacOSTheme.create_label(
            bubble,
            text=f"Hello! 👋\n\n{overview}",
            style="body",
            bg=self.CHAT_COLORS["ai_bubble"],
            fg=self.COLORS["text_primary"],  # Dark text on light gray
            wraplength=500,
            justify="left",
            padx=15,
            pady=12
        )
        msg_label.pack()
        
        # Animate welcome message
        AnimationEngine.fade_in(welcome_bubble, duration=500)
        
        # Bind scrolling to new widgets
        self._bind_mousewheel(welcome_bubble)
        self._bind_mousewheel(bubble)
        self._bind_mousewheel(msg_label)
        
        self.scroll_to_bottom()
    
    def on_enter_key(self, event):
        """Handle Enter key press."""
        # If Shift is not held, send message
        if not (event.state & 0x1):  # Check if Shift is not pressed
            self.send_message()
            return "break"  # Prevent default newline behavior
        return None
    
    def send_message(self):
        """Send user message and get AI response."""
        question = self.input_text.get("1.0", "end-1c").strip()
        
        if not question:
            return
        
        # Clear input
        self.input_text.delete("1.0", "end")
        
        # Show user message with animation
        self.add_user_message(question)
        
        # Brief pause before showing typing indicator for better UX
        self.window.after(200, lambda: self._show_typing_and_get_answer(question))
    
    def _show_typing_and_get_answer(self, question):
        """Show typing indicator and get AI answer."""
        # Show typing indicator
        typing_indicator = self.add_typing_indicator()
        
        # Get answer in background thread
        def get_answer():
            time.sleep(0.5)  # Slightly longer delay for better perception
            result = self.chatbot.answer_question(question)
            
            # Update UI on main thread
            self.window.after(0, lambda: self.show_ai_response(result, typing_indicator))
        
        self.is_generating = True
        thread = threading.Thread(target=get_answer, daemon=True)
        thread.start()
    
    def add_user_message(self, message: str):
        """Add user message bubble with animation."""
        msg_frame = tk.Frame(self.chat_frame, bg=self.COLORS["window_bg"])
        msg_frame.pack(fill="x", padx=MacOSTheme.SPACING["md"], pady=MacOSTheme.SPACING["sm"], anchor="e")
        
        # Rounded bubble with subtle shadow effect
        bubble = tk.Frame(
            msg_frame, 
            bg=self.CHAT_COLORS["user_bubble"],
            highlightbackground=self.COLORS["accent_pressed"],
            highlightthickness=1
        )
        bubble.pack(anchor="e", padx=MacOSTheme.SPACING["xl"])
        
        msg_label = MacOSTheme.create_label(
            bubble,
            text=message,
            style="body",
            bg=self.CHAT_COLORS["user_bubble"],
            fg="#FFFFFF",  # White text on blue (like iMessage)
            wraplength=450,
            justify="left",
            padx=15,
            pady=10
        )
        msg_label.pack()
        
        # Animate bubble entrance
        AnimationEngine.fade_in(msg_frame, duration=300)
        
        # Bind scrolling to new widgets
        self._bind_mousewheel(msg_frame)
        self._bind_mousewheel(bubble)
        self._bind_mousewheel(msg_label)
        
        self.scroll_to_bottom()
    
    def add_typing_indicator(self) -> tk.Frame:
        """Add typing indicator animation with smooth appearance."""
        typing_frame = tk.Frame(self.chat_frame, bg=self.COLORS["window_bg"])
        typing_frame.pack(fill="x", padx=MacOSTheme.SPACING["md"], pady=MacOSTheme.SPACING["sm"], anchor="w")
        
        bubble = tk.Frame(
            typing_frame, 
            bg=self.CHAT_COLORS["ai_bubble"],
            highlightbackground=self.COLORS["separator"],
            highlightthickness=1
        )
        bubble.pack(anchor="w", padx=MacOSTheme.SPACING["xl"])
        
        typing_label = tk.Label(
            bubble,
            text="typing",
            font=("SF Pro", 13, "italic"),
            bg=self.CHAT_COLORS["ai_bubble"],
            fg=self.COLORS["text_secondary"],  # Gray text on light gray bubble
            padx=15,
            pady=10
        )
        typing_label.pack()
        
        # Animate typing indicator entrance
        AnimationEngine.fade_in(typing_frame, duration=200)
        
        # Animate typing dots
        self._animate_typing_dots(typing_label, 0)
        
        self.scroll_to_bottom()
        return typing_frame
    
    def _animate_typing_dots(self, label, dot_count):
        """Animate typing indicator dots.
        
        Args:
            label: Label widget to animate
            dot_count: Current number of dots
        """
        if label.winfo_exists():
            dots = "." * (dot_count % 4)
            label.config(text=f"typing{dots}")
            label.after(400, lambda: self._animate_typing_dots(label, dot_count + 1))
    
    def show_ai_response(self, result: dict, typing_indicator: tk.Frame):
        """Show AI response with sources and smooth animation."""
        self.is_generating = False
        
        # Remove typing indicator with fade out
        typing_indicator.destroy()
        
        # Add AI message bubble
        msg_frame = tk.Frame(self.chat_frame, bg=self.COLORS["window_bg"])
        msg_frame.pack(fill="x", padx=MacOSTheme.SPACING["md"], pady=MacOSTheme.SPACING["sm"], anchor="w")
        
        bubble = tk.Frame(
            msg_frame, 
            bg=self.CHAT_COLORS["ai_bubble"],
            highlightbackground=self.COLORS["separator"],
            highlightthickness=1
        )
        bubble.pack(anchor="w", padx=MacOSTheme.SPACING["xl"])
        
        # Animate bubble entrance
        AnimationEngine.fade_in(msg_frame, duration=400)
        
        # AI answer
        answer_label = MacOSTheme.create_label(
            bubble,
            text=result["answer"],
            style="body",
            bg=self.CHAT_COLORS["ai_bubble"],
            fg=self.COLORS["text_primary"],  # Dark text on light gray
            wraplength=450,
            justify="left",
            padx=15,
            pady=10
        )
        answer_label.pack()
        
        # Bind scrolling to main widgets
        self._bind_mousewheel(msg_frame)
        self._bind_mousewheel(bubble)
        self._bind_mousewheel(answer_label)
        
        # Sources (if any)
        if result.get("sources"):
            # Rounded sources container
            sources_container = tk.Frame(
                bubble,
                bg="#F5F5F7",  # Slightly different background
                highlightbackground=self.COLORS["separator"],
                highlightthickness=1
            )
            sources_container.pack(fill="x", padx=10, pady=(5, 10))
            
            sources_frame = tk.Frame(sources_container, bg="#F5F5F7")
            sources_frame.pack(fill="x", padx=8, pady=6)
            
            sources_title = MacOSTheme.create_label(
                sources_frame,
                text="📚 Sources:",
                style="caption",
                bg="#F5F5F7",
                fg=self.COLORS["accent"],
                anchor="w",
                font=("SF Pro", 9, "bold")
            )
            sources_title.pack(anchor="w", pady=(0, 2))
            
            # Bind scrolling to sources
            self._bind_mousewheel(sources_frame)
            self._bind_mousewheel(sources_title)
            
            for source in result["sources"]:
                # Handle both old format (page) and new format (location)
                if 'location' in source:
                    source_text = f"• {source['path']}, {source['location']}"
                elif 'page' in source:
                    source_text = f"• {source['path']}, page {source['page']}"
                else:
                    source_text = f"• {source['path']}"
                
                source_label = MacOSTheme.create_label(
                    sources_frame,
                    text=source_text,
                    style="caption",
                    bg="#F5F5F7",
                    fg=self.COLORS["text_tertiary"],
                    anchor="w",
                    font=("SF Pro", 9, "normal")
                )
                source_label.pack(anchor="w", pady=1)
                self._bind_mousewheel(source_label)
                self._bind_mousewheel(sources_container)
        
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom."""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def clear_chat(self):
        """Clear chat history with smooth animation."""
        # Fade out all messages
        children = self.chat_frame.winfo_children()
        for i, widget in enumerate(children):
            # Stagger the fade out
            self.window.after(i * 30, lambda w=widget: w.destroy())
        
        # Clear chatbot history
        self.chatbot.clear_history()
        
        # Show welcome again after clearing
        self.window.after(len(children) * 30 + 100, self.show_welcome_message)
    
    def close_window(self):
        """Close the chatbot window."""
        if self.on_close:
            self.on_close()
        self.window.destroy()


def main():
    """Test chatbot GUI."""
    import sys
    from pathlib import Path
    
    # Find repo root
    repo_root = Path(__file__).parent.parent
    
    # Initialize AI and chatbot
    from local_ai import LocalAI
    from pdf_grounding import PDFGroundingEngine
    from chatbot_engine import ChatbotEngine
    
    ai = LocalAI("llama3.2:3b")
    grounding = PDFGroundingEngine(str(repo_root))
    chatbot = ChatbotEngine(str(repo_root), ai, grounding)
    
    # Set course
    chatbot.set_course("nlp", ["courses/natural-language-processing/notes/NLP Appunti.pdf"])
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide root
    
    # Launch chatbot
    app = ChatbotGUI(root, chatbot, "nlp", "Natural Language Processing")
    root.mainloop()


if __name__ == "__main__":
    main()
