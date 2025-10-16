#!/usr/bin/env python3
"""
Profile GUI
User profile page with statistics and account management
"""

import tkinter as tk
from tkinter import ttk, messagebox


class ProfileGUI:
    """User profile interface."""
    
    # Color scheme
    COLORS = {
        "bg": "#1a1a2e",
        "fg": "#eee",
        "primary": "#0f3460",
        "secondary": "#16213e",
        "accent": "#e94560",
        "success": "#2ecc71",
        "card_bg": "#2c2c44",
        "stat_label": "#888"
    }
    
    def __init__(self, parent, engine, username, on_close_callback):
        """Initialize profile GUI.
        
        Args:
            parent: Parent window
            engine: QuizzerV2 engine
            username: Current username
            on_close_callback: Callback when profile is closed
        """
        self.parent = parent
        self.engine = engine
        self.username = username
        self.on_close = on_close_callback
        
        # Create toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Profile - {username}")
        self.window.geometry("700x800")
        self.window.configure(bg=self.COLORS["bg"])
        self.window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Load and display profile
        self.load_profile()
    
    def center_window(self):
        """Center the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_profile(self):
        """Load user profile data and display."""
        # Get profile from engine
        profile = self.engine.get_user_profile()
        
        if not profile:
            messagebox.showerror("Error", "Failed to load profile")
            self.window.destroy()
            return
        
        stats = profile['stats']
        rating = profile['rating']
        
        self.build_profile_ui(stats, rating)
    
    def build_profile_ui(self, stats, rating):
        """Build profile UI with stats and rating.
        
        Args:
            stats: User statistics dictionary
            rating: Rating information
        """
        # Main container with scrollbar
        canvas = tk.Canvas(self.window, bg=self.COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel scrolling (for touchpad and mouse wheel)
        def on_mousewheel(event):
            """Handle mousewheel/touchpad scrolling."""
            if event.num == 4:  # Linux scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux scroll down
                canvas.yview_scroll(1, "units")
            else:
                # macOS and Windows
                delta = event.delta
                if abs(delta) > 100:  # Windows
                    delta = int(-1 * (delta / 120))
                else:  # macOS
                    delta = int(-1 * delta)
                canvas.yview_scroll(delta, "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)  # Linux scroll up
        canvas.bind("<Button-5>", on_mousewheel)  # Linux scroll down
        canvas.bind("<Enter>", lambda e: canvas.focus_set())
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Content
        content = tk.Frame(scrollable_frame, bg=self.COLORS["bg"])
        content.pack(padx=40, pady=30, fill="both", expand=True)
        
        # Header
        header_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=30, pady=25)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            header_frame,
            text=f"👤 {stats['username']}",
            font=("SF Pro", 28, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w")
        
        tk.Label(
            header_frame,
            text=f"Member since {stats['member_since'][:10]}",
            font=("SF Pro", 11),
            fg=self.COLORS["stat_label"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w", pady=(5, 0))
        
        # Rating Card
        rating_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=30, pady=25)
        rating_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            rating_frame,
            text=rating['title'],
            font=("SF Pro", 24, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w")
        
        tk.Label(
            rating_frame,
            text=rating['description'],
            font=("SF Pro", 13),
            fg=self.COLORS["fg"],
            bg=self.COLORS["card_bg"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))
        
        # Statistics Grid
        stats_frame = tk.Frame(content, bg=self.COLORS["bg"])
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Row 1
        row1 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        row1.pack(fill="x", pady=(0, 15))
        
        self.create_stat_card(
            row1,
            "🎯 Quizzes Taken",
            str(stats['total_quizzes']),
            0, 0
        )
        
        self.create_stat_card(
            row1,
            "❓ Questions Answered",
            str(stats['total_questions']),
            0, 1
        )
        
        # Row 2
        row2 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        row2.pack(fill="x", pady=(0, 15))
        
        self.create_stat_card(
            row2,
            "✅ Correct Answers",
            str(stats['correct_answers']),
            0, 0
        )
        
        self.create_stat_card(
            row2,
            "❌ Incorrect Answers",
            str(stats['incorrect_answers']),
            0, 1
        )
        
        # Row 3
        row3 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        row3.pack(fill="x", pady=(0, 15))
        
        self.create_stat_card(
            row3,
            "📊 Accuracy",
            f"{stats['accuracy']:.1f}%",
            0, 0
        )
        
        self.create_stat_card(
            row3,
            "⭐ Total Stars",
            str(stats['total_stars']),
            0, 1
        )
        
        # Row 4
        row4 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        row4.pack(fill="x")
        
        self.create_stat_card(
            row4,
            "💯 Average Score",
            f"{stats['average_score']:.1f}%",
            0, 0
        )
        
        self.create_stat_card(
            row4,
            "📚 Favorite Course",
            stats['favorite_course'],
            0, 1
        )
        
        # Action Buttons
        actions_frame = tk.Frame(content, bg=self.COLORS["bg"])
        actions_frame.pack(fill="x", pady=(20, 0))
        
        # Close button
        close_btn = tk.Button(
            actions_frame,
            text="Close",
            font=("SF Pro", 13, "bold"),
            bg="#1e3a5f",  # Dark blue
            fg="#ffffff",  # White text
            activebackground="#2563eb",
            activeforeground="#ffffff",
            relief="flat",
            padx=35,
            pady=14,
            cursor="hand2",
            borderwidth=0,
            command=self.close_profile
        )
        close_btn.pack(side="left", padx=(0, 10))
        
        # Delete account button
        delete_btn = tk.Button(
            actions_frame,
            text="Delete Account",
            font=("SF Pro", 13, "bold"),
            bg="#dc2626",  # Red background
            fg="#ffffff",  # White text
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            relief="flat",
            padx=35,
            pady=14,
            cursor="hand2",
            borderwidth=0,
            command=self.confirm_delete_account
        )
        delete_btn.pack(side="left")
    
    def create_stat_card(self, parent, label, value, row, col):
        """Create a stat card.
        
        Args:
            parent: Parent frame
            label: Stat label
            value: Stat value
            row: Grid row
            col: Grid column
        """
        card = tk.Frame(parent, bg=self.COLORS["card_bg"], padx=20, pady=20)
        card.grid(row=row, column=col, sticky="ew", padx=(0, 15) if col == 0 else (0, 0))
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(
            card,
            text=label,
            font=("SF Pro", 11),
            fg=self.COLORS["stat_label"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w")
        
        tk.Label(
            card,
            text=value,
            font=("SF Pro", 24, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w", pady=(5, 0))
    
    def confirm_delete_account(self):
        """Confirm account deletion."""
        result = messagebox.askyesno(
            "Delete Account",
            f"Are you sure you want to delete your account '{self.username}'?\n\n"
            "This action cannot be undone and will delete:\n"
            "• All your quiz history\n"
            "• All your statistics\n"
            "• All your earned stars\n\n"
            "Do you want to continue?",
            icon="warning"
        )
        
        if result:
            # Double confirmation
            confirm = messagebox.askyesno(
                "Final Confirmation",
                "This is your last chance!\n\n"
                "Type YES in your mind and click Yes to permanently delete your account.",
                icon="warning"
            )
            
            if confirm:
                self.delete_account()
    
    def delete_account(self):
        """Delete user account."""
        success, message = self.engine.delete_account()
        
        if success:
            messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
            self.window.destroy()
            self.on_close(logout=True)
        else:
            messagebox.showerror("Error", f"Failed to delete account: {message}")
    
    def close_profile(self):
        """Close profile window."""
        self.window.destroy()
        self.on_close(logout=False)
