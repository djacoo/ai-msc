#!/usr/bin/env python3
"""
Profile GUI
User profile page with statistics and account management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.animations import ProgressBar


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
        
        # Show loading screen first
        self.show_loading_screen()
    
    def center_window(self):
        """Center the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_loading_screen(self):
        """Show loading screen with progress bar."""
        loading_frame = tk.Frame(self.window, bg=self.COLORS["bg"])
        loading_frame.pack(expand=True, fill="both")
        
        # Profile icon
        icon = tk.Label(
            loading_frame,
            text="👤",
            font=("SF Pro", 60),
            bg=self.COLORS["bg"],
            fg=self.COLORS["accent"]
        )
        icon.pack(pady=(200, 20))
        
        # Title
        title = tk.Label(
            loading_frame,
            text=f"Loading {self.username}'s Profile",
            font=("SF Pro", 18, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        title.pack(pady=10)
        
        # Progress bar
        self.profile_progress = ProgressBar(
            loading_frame,
            width=350,
            height=6,
            color="#2563eb",
            bg="#374151"
        )
        self.profile_progress.pack(pady=30)
        
        # Loading text
        self.profile_load_label = tk.Label(
            loading_frame,
            text="Fetching user statistics...",
            font=("SF Pro", 11),
            bg=self.COLORS["bg"],
            fg="#9ca3af"
        )
        self.profile_load_label.pack(pady=10)
        
        # Start animation
        self._animate_profile_loading(0, loading_frame)
    
    def _animate_profile_loading(self, progress, loading_frame):
        """Animate profile loading progress.
        
        Args:
            progress: Current progress (0-100)
            loading_frame: Frame to destroy when done
        """
        if progress <= 100:
            self.profile_progress.set_progress(progress, animated=True)
            
            # Update text
            if progress < 40:
                text = "Fetching user statistics..."
            elif progress < 70:
                text = "Calculating rating..."
            else:
                text = "Loading profile..."
            
            self.profile_load_label.config(text=text)
            
            # Continue animation (5 seconds total: 100ms * 50 steps = 5000ms)
            self.window.after(100, lambda: self._animate_profile_loading(progress + 2, loading_frame))
        else:
            # Loading complete
            loading_frame.destroy()
            self.load_profile()
    
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
        # Main container - no scrollbar, everything fits in view
        content = tk.Frame(self.window, bg=self.COLORS["bg"])
        content.pack(padx=25, pady=15, fill="both", expand=True)
        
        # Header - more compact
        header_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=15, pady=12)
        header_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            header_frame,
            text=f"👤 {stats['username']}",
            font=("SF Pro", 20, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w")
        
        tk.Label(
            header_frame,
            text=f"Member since {stats['member_since'][:10]}",
            font=("SF Pro", 9),
            fg=self.COLORS["stat_label"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w", pady=(3, 0))
        
        # Rating Card - more compact
        rating_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=15, pady=12)
        rating_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            rating_frame,
            text=rating['title'],
            font=("SF Pro", 18, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w")
        
        # Show condensed description
        desc_text = rating['description'][:120] + "..." if len(rating['description']) > 120 else rating['description']
        tk.Label(
            rating_frame,
            text=desc_text,
            font=("SF Pro", 10),
            fg=self.COLORS["fg"],
            bg=self.COLORS["card_bg"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(5, 0))
        
        # Statistics Grid - compact
        stats_frame = tk.Frame(content, bg=self.COLORS["bg"])
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Row 1
        row1 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        row1.pack(fill="x", pady=(0, 8))
        
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
        row2.pack(fill="x", pady=(0, 8))
        
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
        row3.pack(fill="x", pady=(0, 8))
        
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
        
        # Action Buttons - compact
        actions_frame = tk.Frame(content, bg=self.COLORS["bg"])
        actions_frame.pack(fill="x", pady=(10, 0))
        
        # Close button - more compact
        close_btn = tk.Button(
            actions_frame,
            text="Close",
            font=("SF Pro", 11, "bold"),
            bg="#e5e7eb",  # Light gray
            fg="#000000",  # Black text
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2",
            borderwidth=0,
            command=self.close_profile
        )
        close_btn.pack(side="left", padx=(0, 8))
        
        # Change Password button - more compact
        password_btn = tk.Button(
            actions_frame,
            text="🔑 Change Password",
            font=("SF Pro", 11, "bold"),
            bg="#e5e7eb",  # Light gray
            fg="#000000",  # Black text
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2",
            borderwidth=0,
            command=self.show_change_password_dialog
        )
        password_btn.pack(side="left", padx=(0, 8))
        
        # Delete account button - more compact
        delete_btn = tk.Button(
            actions_frame,
            text="Delete Account",
            font=("SF Pro", 11, "bold"),
            bg="#e5e7eb",  # Light gray
            fg="#000000",  # Black text
            activebackground="#d1d5db",
            activeforeground="#000000",
            relief="flat",
            padx=25,
            pady=10,
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
        card = tk.Frame(parent, bg=self.COLORS["card_bg"], padx=12, pady=10)
        card.grid(row=row, column=col, sticky="ew", padx=(0, 10) if col == 0 else (0, 0))
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(
            card,
            text=label,
            font=("SF Pro", 9),
            fg=self.COLORS["stat_label"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w")
        
        tk.Label(
            card,
            text=value,
            font=("SF Pro", 18, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["card_bg"]
        ).pack(anchor="w", pady=(3, 0))
    
    def show_change_password_dialog(self):
        """Show dialog to change password."""
        # Create dialog window
        dialog = tk.Toplevel(self.window)
        dialog.title("Change Password")
        dialog.geometry("450x400")
        dialog.configure(bg=self.COLORS["bg"])
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - dialog.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = tk.Frame(dialog, bg=self.COLORS["bg"])
        content.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Title
        tk.Label(
            content,
            text="🔑 Change Password",
            font=("SF Pro", 22, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["bg"]
        ).pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(content, bg=self.COLORS["secondary"], padx=20, pady=20)
        form_frame.pack(fill="x")
        
        # Current password
        tk.Label(
            form_frame,
            text="Current Password",
            font=("SF Pro", 11, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        old_password_entry = tk.Entry(
            form_frame,
            font=("SF Pro", 12),
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["fg"],
            insertbackground=self.COLORS["fg"],
            relief="flat",
            show="●",
            bd=2
        )
        old_password_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # New password
        tk.Label(
            form_frame,
            text="New Password",
            font=("SF Pro", 11, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            form_frame,
            text="At least 6 characters, can include symbols",
            font=("SF Pro", 9),
            fg="#888",
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        new_password_entry = tk.Entry(
            form_frame,
            font=("SF Pro", 12),
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["fg"],
            insertbackground=self.COLORS["fg"],
            relief="flat",
            show="●",
            bd=2
        )
        new_password_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Confirm new password
        tk.Label(
            form_frame,
            text="Confirm New Password",
            font=("SF Pro", 11, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        confirm_password_entry = tk.Entry(
            form_frame,
            font=("SF Pro", 12),
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["fg"],
            insertbackground=self.COLORS["fg"],
            relief="flat",
            show="●",
            bd=2
        )
        confirm_password_entry.pack(fill="x", ipady=8, pady=(0, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(content, bg=self.COLORS["bg"])
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        def handle_change_password():
            """Handle password change submission."""
            old_password = old_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()
            
            if not old_password or not new_password or not confirm_password:
                messagebox.showerror("Error", "Please fill in all fields", parent=dialog)
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match", parent=dialog)
                new_password_entry.delete(0, tk.END)
                confirm_password_entry.delete(0, tk.END)
                new_password_entry.focus()
                return
            
            # Attempt to change password
            success, message = self.engine.change_password(old_password, new_password)
            
            if success:
                messagebox.showinfo("Success", message, parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Error", message, parent=dialog)
                old_password_entry.delete(0, tk.END)
                old_password_entry.focus()
        
        # Change button
        change_btn = tk.Button(
            buttons_frame,
            text="Change Password",
            font=("SF Pro", 12, "bold"),
            bg=self.COLORS["accent"],
            fg="white",
            activebackground="#d63851",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=12,
            cursor="hand2",
            borderwidth=0,
            command=handle_change_password
        )
        change_btn.pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            font=("SF Pro", 12, "bold"),
            bg="#4b5563",
            fg="white",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=12,
            cursor="hand2",
            borderwidth=0,
            command=dialog.destroy
        )
        cancel_btn.pack(side="left")
        
        # Focus first field
        old_password_entry.focus()
        
        # Bind Enter key
        confirm_password_entry.bind("<Return>", lambda e: handle_change_password())
    
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
