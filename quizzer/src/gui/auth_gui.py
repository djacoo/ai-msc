#!/usr/bin/env python3
"""
Authentication GUI
Login and registration screens for Quizzer V2
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from ..utils.animations import ProgressBar

class AuthGUI:
    """Authentication GUI for login and registration."""
    
    # Color scheme (matching main app)
    COLORS = {
        "bg": "#1a1a2e",
        "fg": "#eee",
        "primary": "#0f3460",
        "secondary": "#16213e",
        "accent": "#e94560",
        "success": "#2ecc71",
        "input_bg": "#2c2c44",
        "input_fg": "#ffffff"
    }
    
    def __init__(self, engine, on_success_callback):
        """Initialize authentication GUI.
        
        Args:
            engine: QuizzerV2 engine with user management
            on_success_callback: Callback function called when login succeeds
        """
        self.engine = engine
        self.on_success = on_success_callback
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Quizzer V2 - Login")
        self.root.geometry("500x650")
        self.root.configure(bg=self.COLORS["bg"])
        self.root.resizable(False, False)
        
        # Bring window to front (above all other windows)
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()
        
        # Center window
        self.center_window()
        
        # Show loading screen first
        self.show_loading_screen()
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_loading_screen(self):
        """Show loading screen with progress bar."""
        # Create loading frame
        loading_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        loading_frame.pack(expand=True, fill="both")
        
        # Logo/Title
        title = tk.Label(
            loading_frame,
            text="🎓 Quizzer V3",
            font=("SF Pro", 32, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["accent"]
        )
        title.pack(pady=(150, 30))
        
        # Subtitle
        subtitle = tk.Label(
            loading_frame,
            text="AI-Powered Quiz System",
            font=("SF Pro", 14),
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        subtitle.pack(pady=(0, 50))
        
        # Progress bar
        self.progress_bar = ProgressBar(
            loading_frame,
            width=350,
            height=6,
            color="#2563eb",
            bg="#374151"
        )
        self.progress_bar.pack(pady=20)
        
        # Loading text
        self.loading_label = tk.Label(
            loading_frame,
            text="Loading authentication system...",
            font=("SF Pro", 11),
            bg=self.COLORS["bg"],
            fg="#9ca3af"
        )
        self.loading_label.pack(pady=10)
        
        # Animate progress
        self._animate_loading(0, loading_frame)
    
    def _animate_loading(self, progress, loading_frame):
        """Animate loading progress bar.
        
        Args:
            progress: Current progress (0-100)
            loading_frame: Frame to remove when done
        """
        if progress <= 100:
            self.progress_bar.set_progress(progress, animated=True)
            
            # Update loading text
            if progress < 30:
                text = "Loading authentication system..."
            elif progress < 60:
                text = "Initializing security modules..."
            elif progress < 90:
                text = "Preparing user interface..."
            else:
                text = "Almost ready..."
            
            self.loading_label.config(text=text)
            
            # Continue animation (5 seconds total: 100ms * 50 steps = 5000ms)
            self.root.after(100, lambda: self._animate_loading(progress + 2, loading_frame))
        else:
            # Loading complete, show login screen
            loading_frame.destroy()
            self.setup_styles()
            self.show_login_screen()
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Primary button
        style.configure(
            "Auth.TButton",
            background=self.COLORS["accent"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 13, "bold"),
            padding=(20, 12)
        )
        style.map(
            "Auth.TButton",
            background=[("active", "#d63851"), ("pressed", "#c92a3f")]
        )
        
        # Secondary button
        style.configure(
            "Secondary.TButton",
            background=self.COLORS["primary"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("SF Pro", 11),
            padding=(15, 8)
        )
    
    def clear_window(self):
        """Clear all widgets from window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen."""
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg=self.COLORS["bg"])
        container.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title
        title = tk.Label(
            container,
            text="🎓 Quizzer V2",
            font=("SF Pro", 32, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["bg"]
        )
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(
            container,
            text="AI-Powered Quiz System",
            font=("SF Pro", 14),
            fg=self.COLORS["fg"],
            bg=self.COLORS["bg"]
        )
        subtitle.pack(pady=(0, 40))
        
        # Login form
        form_frame = tk.Frame(container, bg=self.COLORS["secondary"], padx=30, pady=30)
        form_frame.pack(fill="x")
        
        # Username
        tk.Label(
            form_frame,
            text="Username",
            font=("SF Pro", 12, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.login_username = tk.Entry(
            form_frame,
            font=("SF Pro", 13),
            bg=self.COLORS["input_bg"],
            fg=self.COLORS["input_fg"],
            insertbackground=self.COLORS["input_fg"],
            relief="flat",
            bd=2
        )
        self.login_username.pack(fill="x", ipady=10, pady=(0, 20))
        
        # Password
        tk.Label(
            form_frame,
            text="Password",
            font=("SF Pro", 12, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.login_password = tk.Entry(
            form_frame,
            font=("SF Pro", 13),
            bg=self.COLORS["input_bg"],
            fg=self.COLORS["input_fg"],
            insertbackground=self.COLORS["input_fg"],
            relief="flat",
            bd=2,
            show="●"
        )
        self.login_password.pack(fill="x", ipady=10, pady=(0, 25))
        
        # Bind Enter key
        self.login_password.bind("<Return>", lambda e: self.handle_login())
        
        # Login button
        ttk.Button(
            form_frame,
            text="Login",
            style="Auth.TButton",
            command=self.handle_login
        ).pack(fill="x", pady=(0, 15))
        
        # Switch to register
        switch_frame = tk.Frame(form_frame, bg=self.COLORS["secondary"])
        switch_frame.pack(fill="x")
        
        tk.Label(
            switch_frame,
            text="Don't have an account?",
            font=("SF Pro", 11),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(side="left")
        
        register_btn = tk.Label(
            switch_frame,
            text="Register",
            font=("SF Pro", 11, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["secondary"],
            cursor="hand2"
        )
        register_btn.pack(side="left", padx=(5, 0))
        register_btn.bind("<Button-1>", lambda e: self.show_register_screen())
        
        # Focus username
        self.login_username.focus()
    
    def show_register_screen(self):
        """Display registration screen."""
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg=self.COLORS["bg"])
        container.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title
        title = tk.Label(
            container,
            text="Create Account",
            font=("SF Pro", 28, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["bg"]
        )
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(
            container,
            text="Join Quizzer V2 and start learning!",
            font=("SF Pro", 12),
            fg=self.COLORS["fg"],
            bg=self.COLORS["bg"]
        )
        subtitle.pack(pady=(0, 30))
        
        # Registration form
        form_frame = tk.Frame(container, bg=self.COLORS["secondary"], padx=30, pady=30)
        form_frame.pack(fill="x")
        
        # Username
        tk.Label(
            form_frame,
            text="Username",
            font=("SF Pro", 12, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            form_frame,
            text="Letters and numbers only, no symbols",
            font=("SF Pro", 9),
            fg="#888",
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.register_username = tk.Entry(
            form_frame,
            font=("SF Pro", 13),
            bg=self.COLORS["input_bg"],
            fg=self.COLORS["input_fg"],
            insertbackground=self.COLORS["input_fg"],
            relief="flat",
            bd=2
        )
        self.register_username.pack(fill="x", ipady=10, pady=(0, 20))
        
        # Password
        tk.Label(
            form_frame,
            text="Password",
            font=("SF Pro", 12, "bold"),
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
        
        self.register_password = tk.Entry(
            form_frame,
            font=("SF Pro", 13),
            bg=self.COLORS["input_bg"],
            fg=self.COLORS["input_fg"],
            insertbackground=self.COLORS["input_fg"],
            relief="flat",
            bd=2,
            show="●"
        )
        self.register_password.pack(fill="x", ipady=10, pady=(0, 20))
        
        # Confirm password
        tk.Label(
            form_frame,
            text="Confirm Password",
            font=("SF Pro", 12, "bold"),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.register_password_confirm = tk.Entry(
            form_frame,
            font=("SF Pro", 13),
            bg=self.COLORS["input_bg"],
            fg=self.COLORS["input_fg"],
            insertbackground=self.COLORS["input_fg"],
            relief="flat",
            bd=2,
            show="●"
        )
        self.register_password_confirm.pack(fill="x", ipady=10, pady=(0, 25))
        
        # Bind Enter key
        self.register_password_confirm.bind("<Return>", lambda e: self.handle_register())
        
        # Register button
        ttk.Button(
            form_frame,
            text="Create Account",
            style="Auth.TButton",
            command=self.handle_register
        ).pack(fill="x", pady=(0, 15))
        
        # Switch to login
        switch_frame = tk.Frame(form_frame, bg=self.COLORS["secondary"])
        switch_frame.pack(fill="x")
        
        tk.Label(
            switch_frame,
            text="Already have an account?",
            font=("SF Pro", 11),
            fg=self.COLORS["fg"],
            bg=self.COLORS["secondary"]
        ).pack(side="left")
        
        login_btn = tk.Label(
            switch_frame,
            text="Login",
            font=("SF Pro", 11, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["secondary"],
            cursor="hand2"
        )
        login_btn.pack(side="left", padx=(5, 0))
        login_btn.bind("<Button-1>", lambda e: self.show_login_screen())
        
        # Focus username
        self.register_username.focus()
    
    def handle_login(self):
        """Handle login button click."""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Attempt login
        success, message, user_id = self.engine.login(username, password)
        
        if success:
            # Show success animation
            self.show_success_animation(f"Welcome back, {username}!", user_id, username)
        else:
            messagebox.showerror("Login Failed", message)
            self.login_password.delete(0, tk.END)
            self.login_password.focus()
    
    def handle_register(self):
        """Handle registration button click."""
        username = self.register_username.get().strip()
        password = self.register_password.get()
        password_confirm = self.register_password_confirm.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != password_confirm:
            messagebox.showerror("Error", "Passwords do not match")
            self.register_password.delete(0, tk.END)
            self.register_password_confirm.delete(0, tk.END)
            self.register_password.focus()
            return
        
        # Attempt registration
        success, message, user_id = self.engine.register(username, password)
        
        if success:
            # Auto-login after registration
            self.engine.login(username, password)
            # Show success animation
            self.show_success_animation(f"Account created! Welcome, {username}!", user_id, username)
        else:
            messagebox.showerror("Registration Failed", message)
    
    def show_success_animation(self, message, user_id, username):
        """Show success animation before closing.
        
        Args:
            message: Success message to display
            user_id: User ID
            username: Username
        """
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create success screen
        success_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        success_frame.pack(expand=True, fill="both")
        
        # Success icon with animation
        success_label = tk.Label(
            success_frame,
            text="✓",
            font=("SF Pro", 80, "bold"),
            fg="#2ecc71",
            bg=self.COLORS["bg"]
        )
        success_label.pack(pady=(100, 20))
        
        # Success message
        msg_label = tk.Label(
            success_frame,
            text=message,
            font=("SF Pro", 18),
            fg=self.COLORS["fg"],
            bg=self.COLORS["bg"]
        )
        msg_label.pack(pady=20)
        
        # Animate: fade in effect by scaling
        def animate_checkmark(scale=0.0):
            if scale < 1.0:
                # Simple scale animation
                self.root.update_idletasks()
                self.root.after(20, lambda: animate_checkmark(scale + 0.1))
            else:
                # After animation, wait then close
                self.root.after(800, lambda: self.finish_auth(user_id, username))
        
        animate_checkmark()
    
    def finish_auth(self, user_id, username):
        """Finish authentication and launch main app."""
        self.root.destroy()
        self.on_success(user_id, username)
    
    def run(self):
        """Start the authentication GUI."""
        self.root.mainloop()
