#!/usr/bin/env python3
"""
Chatbot GUI
Modern chat interface for course Q&A
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
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
            bg="#4b5563",
            fg="white",
            activebackground="#374151",
            activeforeground="white",
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
        
        # Bind mousewheel scrolling (for touchpad and mouse wheel)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows/Linux
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down
        
        # macOS touchpad scrolling
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Enable scrolling when mouse enters the canvas
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        
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
            bg=self.COLORS["user_bubble"],
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=15,
            cursor="hand2",
            command=self.send_message,
            borderwidth=0
        )
        send_btn.pack(side="right", padx=(5, 10), pady=10, fill="y")
        
        # Focus input
        self.input_text.focus()
    
    def on_frame_configure(self, event=None):
        """Update canvas scroll region when frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        """Update chat frame width when canvas is resized."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def on_mousewheel(self, event):
        """Handle mousewheel/touchpad scrolling."""
        # macOS and Windows handle wheel events differently
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:
            # macOS and Windows
            # macOS uses event.delta directly, positive = scroll up
            # Windows uses event.delta / 120
            delta = event.delta
            if abs(delta) > 100:  # Windows
                delta = int(-1 * (delta / 120))
            else:  # macOS
                delta = int(-1 * delta)
            self.canvas.yview_scroll(delta, "units")
    
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
        
        self.scroll_to_bottom()
    
    def add_typing_indicator(self) -> tk.Frame:
        """Add typing indicator animation."""
        typing_frame = tk.Frame(self.chat_frame, bg=self.COLORS["bg"])
        typing_frame.pack(fill="x", padx=10, pady=5, anchor="w")
        
        bubble = tk.Frame(typing_frame, bg=self.COLORS["ai_bubble"], bd=0)
        bubble.pack(anchor="w", padx=20)
        
        typing_label = tk.Label(
            bubble,
            text="typing...",
            font=("SF Pro", 11, "italic"),
            bg=self.COLORS["ai_bubble"],
            fg="#9ca3af",
            padx=15,
            pady=10
        )
        typing_label.pack()
        
        self.scroll_to_bottom()
        return typing_frame
    
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
