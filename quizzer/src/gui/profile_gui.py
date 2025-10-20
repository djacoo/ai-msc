#!/usr/bin/env python3
"""
Profile GUI
User profile page with statistics and account management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.animations import ProgressBar
from .macos_theme import MacOSTheme


class ProfileGUI:
    """User profile interface."""
    
    # Use native macOS color scheme
    COLORS = MacOSTheme.COLORS
    
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
        self.window.configure(bg=self.COLORS["window_bg"])
        self.window.resizable(False, False)
        
        # Apply macOS window styling
        MacOSTheme.configure_window(self.window)
        
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
        loading_frame = tk.Frame(self.window, bg=self.COLORS["window_bg"])
        loading_frame.pack(expand=True, fill="both")
        
        # Profile icon
        icon = tk.Label(
            loading_frame,
            text="👤",
            font=("SF Pro", 60),
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["accent"]
        )
        icon.pack(pady=(200, 20))
        
        # Title
        title = MacOSTheme.create_label(
            loading_frame,
            text=f"Loading {self.username}'s Profile",
            style="title_large",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_primary"]
        )
        title.pack(pady=10)
        
        # Progress bar
        self.profile_progress = ProgressBar(
            loading_frame,
            width=350,
            height=6,
            color=self.COLORS["accent"],
            bg=self.COLORS["control_bg"]
        )
        self.profile_progress.pack(pady=30)
        
        # Loading text
        self.profile_load_label = MacOSTheme.create_label(
            loading_frame,
            text="Fetching user statistics...",
            style="callout",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["text_secondary"]
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
        content = tk.Frame(self.window, bg=self.COLORS["window_bg"])
        content.pack(padx=25, pady=15, fill="both", expand=True)
        
        # Header - more compact
        header_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=15, pady=12)
        header_frame.pack(fill="x", pady=(0, 10))
        
        MacOSTheme.create_label(
            header_frame,
            text=f"👤 {stats['username']}",
            style="title",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_primary"]
        ).pack(anchor="w")
        
        MacOSTheme.create_label(
            header_frame,
            text=f"Member since {stats['member_since'][:10]}",
            style="footnote",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_tertiary"]
        ).pack(anchor="w", pady=(3, 0))
        
        # Rating Card - more compact
        rating_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=15, pady=12)
        rating_frame.pack(fill="x", pady=(0, 10))
        
        MacOSTheme.create_label(
            rating_frame,
            text=rating['title'],
            style="headline",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["accent"]
        ).pack(anchor="w")
        
        # Show condensed description
        desc_text = rating['description'][:120] + "..." if len(rating['description']) > 120 else rating['description']
        MacOSTheme.create_label(
            rating_frame,
            text=desc_text,
            style="footnote",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_secondary"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(5, 0))
        
        # Statistics Grid - compact
        stats_frame = tk.Frame(content, bg=self.COLORS["window_bg"])
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Row 1
        row1 = tk.Frame(stats_frame, bg=self.COLORS["window_bg"])
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
        row2 = tk.Frame(stats_frame, bg=self.COLORS["window_bg"])
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
        row3 = tk.Frame(stats_frame, bg=self.COLORS["window_bg"])
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
        row4 = tk.Frame(stats_frame, bg=self.COLORS["window_bg"])
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
        actions_frame = tk.Frame(content, bg=self.COLORS["window_bg"])
        actions_frame.pack(fill="x", pady=(10, 0))
        
        # Close button
        close_btn = MacOSTheme.create_button(
            actions_frame,
            text="Close",
            command=self.close_profile,
            style="secondary",
            size="regular"
        )
        close_btn.pack(side="left", padx=(0, 8))
        
        # Change Password button
        password_btn = MacOSTheme.create_button(
            actions_frame,
            text="🔑 Change Password",
            command=self.show_change_password_dialog,
            style="primary",
            size="regular"
        )
        password_btn.pack(side="left", padx=(0, 8))
        
        # Delete account button
        delete_btn = MacOSTheme.create_button(
            actions_frame,
            text="Delete Account",
            command=self.confirm_delete_account,
            style="destructive",
            size="regular"
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
        
        MacOSTheme.create_label(
            card,
            text=label,
            style="footnote",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_tertiary"]
        ).pack(anchor="w")
        
        MacOSTheme.create_label(
            card,
            text=value,
            style="headline",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_primary"]
        ).pack(anchor="w", pady=(3, 0))
    
    def show_change_password_dialog(self):
        """Show dialog to change password."""
        # Create dialog window
        dialog = tk.Toplevel(self.window)
        dialog.title("Change Password")
        dialog.geometry("450x400")
        dialog.configure(bg=self.COLORS["window_bg"])
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - dialog.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = tk.Frame(dialog, bg=self.COLORS["window_bg"])
        content.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Title
        MacOSTheme.create_label(
            content,
            text="🔑 Change Password",
            style="title_large",
            bg=self.COLORS["window_bg"],
            fg=self.COLORS["accent"]
        ).pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(content, bg=self.COLORS["card_bg"], padx=20, pady=20)
        form_frame.pack(fill="x")
        
        # Current password
        MacOSTheme.create_label(
            form_frame,
            text="Current Password",
            style="callout",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 5))
        
        old_password_entry = tk.Entry(
            form_frame,
            font=("SF Pro", 12),
            bg=self.COLORS["content_bg"],
            fg=self.COLORS["text_primary"],
            insertbackground=self.COLORS["accent"],
            relief="flat",
            show="●",
            bd=2
        )
        old_password_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # New password
        MacOSTheme.create_label(
            form_frame,
            text="New Password",
            style="callout",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 5))
        
        MacOSTheme.create_label(
            form_frame,
            text="At least 6 characters, can include symbols",
            style="footnote",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_tertiary"]
        ).pack(anchor="w", pady=(0, 5))
        
        new_password_entry = tk.Entry(
            form_frame,
            font=("SF Pro", 12),
            bg=self.COLORS["content_bg"],
            fg=self.COLORS["text_primary"],
            insertbackground=self.COLORS["accent"],
            relief="flat",
            show="●",
            bd=2
        )
        new_password_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Confirm new password
        MacOSTheme.create_label(
            form_frame,
            text="Confirm New Password",
            style="callout",
            bg=self.COLORS["card_bg"],
            fg=self.COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 5))
        
        confirm_password_entry = tk.Entry(
            form_frame,
            font=("SF Pro", 12),
            bg=self.COLORS["content_bg"],
            fg=self.COLORS["text_primary"],
            insertbackground=self.COLORS["accent"],
            relief="flat",
            show="●",
            bd=2
        )
        confirm_password_entry.pack(fill="x", ipady=8, pady=(0, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(content, bg=self.COLORS["window_bg"])
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
        change_btn = MacOSTheme.create_button(
            buttons_frame,
            text="Change Password",
            command=handle_change_password,
            style="primary",
            size="regular"
        )
        change_btn.pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_btn = MacOSTheme.create_button(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy,
            style="secondary",
            size="regular"
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
