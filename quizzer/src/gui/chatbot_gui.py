#!/usr/bin/env python3
"""
Chatbot GUI
Modern chat interface for course Q&A
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ..utils.animations import ProgressBar
import time
from pathlib import Path
from typing import Optional


class ChatbotGUI:
    """Modern chat interface for asking questions about course notes."""
    
    # Color scheme (matching main app)
    COLORS = {
        "bg": "#1a1a2e",
        "fg": "#eee",
        "primary": "#0f3460",
        "secondary": "#16213e",
        "accent": "#e94560",
        "user_bubble": "#2563eb",
        "ai_bubble": "#374151",
        "success": "#2ecc71",
        "info": "#3498db"
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
        self.window.title(f"💬 Course Assistant - {course_name}")
        self.window.geometry("800x700")
        self.window.configure(bg=self.COLORS["bg"])
        
        # Handle close
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # Build UI
        self.build_ui()
        
        # Show welcome message
        self.show_welcome_message()
    
    def build_ui(self):
        """Build the chat interface."""
        # Header
        header_frame = tk.Frame(self.window, bg=self.COLORS["primary"], height=70)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text=f"💬 Course Assistant",
            font=("SF Pro", 20, "bold"),
            bg=self.COLORS["primary"],
            fg="white"
        )
        title.pack(side="left", padx=20, pady=15)
        
        course_label = tk.Label(
            header_frame,
            text=f"📚 {self.course_name}",
            font=("SF Pro", 12),
            bg=self.COLORS["primary"],
            fg="#a0a0a0"
        )
        course_label.pack(side="left", padx=10, pady=15)
        
        # Clear chat button
        clear_btn = tk.Button(
            header_frame,
            text="🗑️ Clear",
            font=("SF Pro", 11),
            bg="#e5e7eb",
            fg="#000000",
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.clear_chat,
            borderwidth=0
        )
        clear_btn.pack(side="right", padx=20, pady=15)
        
        # Chat display area
        chat_container = tk.Frame(self.window, bg=self.COLORS["bg"])
        chat_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas for scrollable chat
        self.canvas = tk.Canvas(chat_container, bg=self.COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.canvas.yview)
        
        self.chat_frame = tk.Frame(self.canvas, bg=self.COLORS["bg"])
        
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
        
        # Input area
        input_frame = tk.Frame(self.window, bg=self.COLORS["secondary"], height=100)
        input_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        input_frame.pack_propagate(False)
        
        # Input field
        self.input_text = tk.Text(
            input_frame,
            font=("SF Pro", 12),
            bg="white",
            fg="black",
            insertbackground="black",
            height=3,
            wrap="word",
            bd=2,
            relief="solid",
            padx=10,
            pady=10
        )
        self.input_text.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        # Bind Enter key
        self.input_text.bind("<Return>", self.on_enter_key)
        self.input_text.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for new line
        
        # Send button
        send_btn = tk.Button(
            input_frame,
            text="Send\n➤",
            font=("SF Pro", 11, "bold"),
            bg="#e5e7eb",
            fg="#000000",
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=15,
            cursor="hand2",
            command=self.send_message,
            borderwidth=0
        )
        send_btn.pack(side="right", padx=(5, 10), pady=10, fill="y")
        
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
        loading_overlay = tk.Frame(self.chat_frame, bg=self.COLORS["bg"])
        loading_overlay.pack(expand=True, fill="both", pady=100)
        
        # Chatbot icon
        icon = tk.Label(
            loading_overlay,
            text="💬",
            font=("SF Pro", 50),
            bg=self.COLORS["bg"],
            fg="#3498db"
        )
        icon.pack(pady=20)
        
        # Loading title
        title = tk.Label(
            loading_overlay,
            text="Initializing AI Assistant",
            font=("SF Pro", 16, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        title.pack(pady=10)
        
        # Progress bar
        self.chatbot_progress = ProgressBar(
            loading_overlay,
            width=300,
            height=5,
            color="#3498db",
            bg="#374151"
        )
        self.chatbot_progress.pack(pady=20)
        
        # Loading text
        self.chatbot_load_label = tk.Label(
            loading_overlay,
            text="Loading course notes...",
            font=("SF Pro", 10),
            bg=self.COLORS["bg"],
            fg="#9ca3af"
        )
        self.chatbot_load_label.pack(pady=5)
        
        # Animate loading
        self._animate_chatbot_loading(0, loading_overlay)
    
    def _animate_chatbot_loading(self, progress, overlay):
        """Animate chatbot loading progress.
        
        Args:
            progress: Current progress (0-100)
            overlay: Overlay frame to destroy when done
        """
        if progress <= 100:
            self.chatbot_progress.set_progress(progress, animated=True)
            
            # Update text
            if progress < 33:
                text = "Loading course notes..."
            elif progress < 66:
                text = "Initializing AI engine..."
            else:
                text = "Preparing chat interface..."
            
            self.chatbot_load_label.config(text=text)
            
            # Continue animation (5 seconds total: 100ms * 50 steps = 5000ms)
            self.window.after(100, lambda: self._animate_chatbot_loading(progress + 2, overlay))
        else:
            # Loading complete
            overlay.destroy()
            self.show_welcome_message()
    
    def show_welcome_message(self):
        """Display welcome message."""
        overview = self.chatbot.get_course_overview()
        
        welcome_bubble = tk.Frame(self.chat_frame, bg=self.COLORS["bg"])
        welcome_bubble.pack(fill="x", padx=10, pady=10, anchor="w")
        
        bubble = tk.Frame(welcome_bubble, bg=self.COLORS["ai_bubble"], bd=0)
        bubble.pack(anchor="w", padx=20)
        
        msg_label = tk.Label(
            bubble,
            text=f"Hello! 👋\n\n{overview}",
            font=("SF Pro", 11),
            bg=self.COLORS["ai_bubble"],
            fg="white",
            wraplength=500,
            justify="left",
            padx=15,
            pady=12
        )
        msg_label.pack()
        
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
        
        # Show user message
        self.add_user_message(question)
        
        # Show typing indicator
        typing_indicator = self.add_typing_indicator()
        
        # Get answer in background thread
        def get_answer():
            time.sleep(0.3)  # Brief delay for UX
            result = self.chatbot.answer_question(question)
            
            # Update UI on main thread
            self.window.after(0, lambda: self.show_ai_response(result, typing_indicator))
        
        self.is_generating = True
        thread = threading.Thread(target=get_answer, daemon=True)
        thread.start()
    
    def add_user_message(self, message: str):
        """Add user message bubble."""
        msg_frame = tk.Frame(self.chat_frame, bg=self.COLORS["bg"])
        msg_frame.pack(fill="x", padx=10, pady=5, anchor="e")
        
        bubble = tk.Frame(msg_frame, bg=self.COLORS["user_bubble"], bd=0)
        bubble.pack(anchor="e", padx=20)
        
        msg_label = tk.Label(
            bubble,
            text=message,
            font=("SF Pro", 11),
            bg=self.COLORS["user_bubble"],
            fg="white",
            wraplength=450,
            justify="left",
            padx=15,
            pady=10
        )
        msg_label.pack()
        
        # Bind scrolling to new widgets
        self._bind_mousewheel(msg_frame)
        self._bind_mousewheel(bubble)
        self._bind_mousewheel(msg_label)
        
        self.scroll_to_bottom()
    
    def add_typing_indicator(self) -> tk.Frame:
        """Add typing indicator animation."""
        typing_frame = tk.Frame(self.chat_frame, bg=self.COLORS["bg"])
        typing_frame.pack(fill="x", padx=10, pady=5, anchor="w")
        
        bubble = tk.Frame(typing_frame, bg=self.COLORS["ai_bubble"], bd=0)
        bubble.pack(anchor="w", padx=20)
        
        typing_label = tk.Label(
            bubble,
            text="typing",
            font=("SF Pro", 11, "italic"),
            bg=self.COLORS["ai_bubble"],
            fg="#9ca3af",
            padx=15,
            pady=10
        )
        typing_label.pack()
        
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
        """Show AI response with sources."""
        self.is_generating = False
        
        # Remove typing indicator
        typing_indicator.destroy()
        
        # Add AI message bubble
        msg_frame = tk.Frame(self.chat_frame, bg=self.COLORS["bg"])
        msg_frame.pack(fill="x", padx=10, pady=5, anchor="w")
        
        bubble = tk.Frame(msg_frame, bg=self.COLORS["ai_bubble"], bd=0)
        bubble.pack(anchor="w", padx=20)
        
        # AI answer
        answer_label = tk.Label(
            bubble,
            text=result["answer"],
            font=("SF Pro", 11),
            bg=self.COLORS["ai_bubble"],
            fg="white",
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
            sources_frame = tk.Frame(bubble, bg=self.COLORS["ai_bubble"])
            sources_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            sources_title = tk.Label(
                sources_frame,
                text="📚 Sources:",
                font=("SF Pro", 9, "bold"),
                bg=self.COLORS["ai_bubble"],
                fg="#60a5fa",
                anchor="w"
            )
            sources_title.pack(anchor="w", pady=(5, 2))
            
            # Bind scrolling to sources
            self._bind_mousewheel(sources_frame)
            self._bind_mousewheel(sources_title)
            
            for source in result["sources"]:
                source_text = f"• {source['path']}, page {source['page']}"
                source_label = tk.Label(
                    sources_frame,
                    text=source_text,
                    font=("SF Pro", 8),
                    bg=self.COLORS["ai_bubble"],
                    fg="#9ca3af",
                    anchor="w"
                )
                source_label.pack(anchor="w", pady=1)
                self._bind_mousewheel(source_label)
        
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom."""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def clear_chat(self):
        """Clear chat history."""
        # Clear all messages except welcome
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Clear chatbot history
        self.chatbot.clear_history()
        
        # Show welcome again
        self.show_welcome_message()
    
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
