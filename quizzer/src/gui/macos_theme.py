#!/usr/bin/env python3
"""
macOS Native Theme
Provides native macOS styling for Tkinter applications
"""

import tkinter as tk
from tkinter import ttk
import platform


class MacOSTheme:
    """Native macOS theme constants and styling utilities."""
    
    # Native macOS color palette (Light mode - like Apple TV+)
    COLORS = {
        # Background colors - LIGHT for readability
        "window_bg": "#F5F5F7",  # Light gray window background (Apple style)
        "content_bg": "#FFFFFF",  # Pure white for content
        "card_bg": "#FFFFFF",  # White cards
        "elevated_bg": "#FAFAFA",  # Slightly off-white for elevation
        
        # Text colors - DARK for high contrast
        "text_primary": "#1D1D1F",  # Almost black for primary text
        "text_secondary": "#6E6E73",  # Gray for secondary text
        "text_tertiary": "#86868B",  # Light gray for tertiary
        "text_placeholder": "#C7C7CC",  # Placeholder text
        
        # Accent colors (system blue) - adjusted for light mode
        "accent": "#007AFF",  # macOS system blue (light mode)
        "accent_hover": "#0051D5",  # Darker hover
        "accent_pressed": "#004EBF",  # Even darker pressed
        
        # Semantic colors - light mode versions
        "success": "#34C759",  # Green
        "warning": "#FF9500",  # Orange
        "error": "#FF3B30",  # Red
        "info": "#5AC8FA",  # Light blue
        
        # Control colors - light mode
        "control_bg": "#F2F2F7",  # Light gray button background
        "control_hover": "#E5E5EA",  # Slightly darker hover
        "control_pressed": "#D1D1D6",  # Darker pressed
        
        # Border/separator colors
        "separator": "#D2D2D7",  # Light gray separator
        "border": "#D1D1D6",  # Border color
        
        # Special colors
        "selection": "#007AFF",  # Selection highlight
        "focus": "#007AFF",  # Focus ring
        "list_hover": "#F0F0F5",  # Very subtle hover for lists
    }
    
    # Light mode variant (optional)
    COLORS_LIGHT = {
        "window_bg": "#F5F5F7",
        "content_bg": "#FFFFFF",
        "card_bg": "#FEFEFE",
        "elevated_bg": "#FFFFFF",
        "text_primary": "#000000",
        "text_secondary": "#6E6E73",
        "text_tertiary": "#8E8E93",
        "text_placeholder": "#AEAEB2",
        "accent": "#007AFF",
        "accent_hover": "#0051D5",
        "accent_pressed": "#004EBF",
        "success": "#34C759",
        "warning": "#FF9500",
        "error": "#FF3B30",
        "info": "#5AC8FA",
        "control_bg": "#EBEBF0",
        "control_hover": "#D1D1D6",
        "control_pressed": "#C7C7CC",
        "separator": "#D1D1D6",
        "border": "#C6C6C8",
        "selection": "#007AFF",
        "focus": "#007AFF",
    }
    
    # Typography (SF Pro is already used, these are fallbacks)
    FONTS = {
        "display_large": ("SF Pro Display", 32, "bold"),
        "display": ("SF Pro Display", 28, "bold"),
        "title_large": ("SF Pro", 24, "bold"),
        "title": ("SF Pro", 20, "bold"),
        "headline": ("SF Pro", 17, "bold"),
        "body": ("SF Pro", 15, "normal"),
        "body_emphasized": ("SF Pro", 15, "bold"),
        "callout": ("SF Pro", 13, "normal"),
        "subheadline": ("SF Pro", 11, "normal"),
        "footnote": ("SF Pro", 10, "normal"),
        "caption": ("SF Pro", 9, "normal"),
    }
    
    # Spacing (following macOS HIG)
    SPACING = {
        "xs": 4,
        "sm": 8,
        "md": 12,
        "lg": 16,
        "xl": 20,
        "xxl": 24,
        "xxxl": 32,
    }
    
    # Corner radius (macOS standard) - increased for more rounded look
    RADIUS = {
        "sm": 6,
        "md": 8,
        "lg": 10,
        "xl": 12,
        "xxl": 16,
        "xxxl": 20,
        "pill": 999,  # Fully rounded (pill shape)
    }
    
    # Button sizes (following macOS HIG)
    BUTTON_SIZES = {
        "small": {"padx": 12, "pady": 4, "font_size": 11},
        "regular": {"padx": 16, "pady": 6, "font_size": 13},
        "large": {"padx": 20, "pady": 10, "font_size": 15},
    }
    
    @staticmethod
    def is_macos():
        """Check if running on macOS."""
        return platform.system() == "Darwin"
    
    @staticmethod
    def configure_window(window, title=""):
        """Configure window with native macOS styling."""
        if MacOSTheme.is_macos():
            # macOS-specific window configuration
            window.configure(bg=MacOSTheme.COLORS["window_bg"])
            
            # Try to use native window appearance
            try:
                # These attributes are macOS-specific
                window.tk.call("::tk::unsupported::MacWindowStyle", "style", window._w, "document", "closeBox collapseBox resizable")
            except:
                pass
        else:
            window.configure(bg=MacOSTheme.COLORS["window_bg"])
    
    @staticmethod
    def create_rounded_frame(parent, bg_color, corner_radius=10, **kwargs):
        """Create a frame with rounded corners using Canvas.
        
        Args:
            parent: Parent widget
            bg_color: Background color
            corner_radius: Radius for rounded corners
            **kwargs: Additional Frame arguments
        """
        canvas = tk.Canvas(
            parent,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else MacOSTheme.COLORS["window_bg"],
            highlightthickness=0,
            **kwargs
        )
        
        # Store corner radius for later use
        canvas.corner_radius = corner_radius
        canvas.bg_color = bg_color
        
        return canvas
    
    @staticmethod
    def create_canvas_button(parent, text, command=None, style="default", size="regular", **kwargs):
        """Create a button using Canvas for better color control on macOS.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Callback function
            style: Button style
            size: Button size
        """
        # Get size configuration
        size_config = MacOSTheme.BUTTON_SIZES.get(size, MacOSTheme.BUTTON_SIZES["regular"])
        
        if style == "primary":
            bg = MacOSTheme.COLORS["accent"]
            fg = "#FFFFFF"
            active_bg = MacOSTheme.COLORS["accent_hover"]
        elif style == "destructive":
            bg = MacOSTheme.COLORS["error"]
            fg = "#FFFFFF"
            active_bg = "#E03A30"
        else:  # secondary or default
            bg = MacOSTheme.COLORS["control_bg"]
            fg = "#000000"
            active_bg = MacOSTheme.COLORS["control_hover"]
        
        # Create frame-based button
        btn_frame = tk.Frame(
            parent,
            bg=bg,
            cursor="hand2",
            highlightbackground=MacOSTheme.COLORS["border"],
            highlightthickness=0
        )
        
        default_font = ("SF Pro", size_config["font_size"], "bold" if style == "primary" else "normal")
        
        label = tk.Label(
            btn_frame,
            text=text,
            bg=bg,
            fg=fg,
            font=default_font,
            cursor="hand2",
            padx=size_config["padx"],
            pady=size_config["pady"]
        )
        label.pack()
        
        # Hover effects
        def on_enter(e):
            btn_frame.configure(bg=active_bg)
            label.configure(bg=active_bg)
        
        def on_leave(e):
            btn_frame.configure(bg=bg)
            label.configure(bg=bg)
        
        def on_click(e):
            if command:
                command()
        
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        btn_frame.bind("<Button-1>", on_click)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        label.bind("<Button-1>", on_click)
        
        return btn_frame
    
    @staticmethod
    def create_button(parent, text, command=None, style="default", size="regular", use_frame=True, **kwargs):
        """Create a native macOS-style button with rounded corners.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Callback function
            style: Button style ('default', 'primary', 'secondary', 'destructive')
            size: Button size ('small', 'regular', 'large')
            use_frame: Use frame-based button for better color control (default True)
            **kwargs: Additional arguments
        """
        # On macOS or when use_frame=True, use frame-based button for reliable colors
        if use_frame or MacOSTheme.is_macos():
            return MacOSTheme.create_canvas_button(parent, text, command, style, size, **kwargs)
        
        # Get size configuration
        size_config = MacOSTheme.BUTTON_SIZES.get(size, MacOSTheme.BUTTON_SIZES["regular"])
        
        if style == "primary":
            bg = MacOSTheme.COLORS["accent"]
            fg = "#FFFFFF"  # White text on blue for high contrast
            active_bg = MacOSTheme.COLORS["accent_hover"]
            active_fg = "#FFFFFF"
        elif style == "destructive":
            bg = MacOSTheme.COLORS["error"]
            fg = "#FFFFFF"  # White text on red
            active_bg = "#E03A30"
            active_fg = "#FFFFFF"
        elif style == "secondary":
            bg = MacOSTheme.COLORS["control_bg"]
            fg = "#000000"  # Black text on light gray for maximum readability
            active_bg = MacOSTheme.COLORS["control_hover"]
            active_fg = "#000000"  # Keep black on hover
        else:  # default
            bg = MacOSTheme.COLORS["control_bg"]
            fg = "#000000"  # Black text for readability
            active_bg = MacOSTheme.COLORS["control_hover"]
            active_fg = "#000000"
        
        # Use size config for padding and font
        default_font = ("SF Pro", size_config["font_size"], "bold" if style == "primary" else "normal")
        
        # Create button with explicit color configuration
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=active_fg,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            highlightbackground=bg,
            highlightcolor=bg,
            cursor="hand2" if MacOSTheme.is_macos() else "arrow",
            font=kwargs.get("font", default_font),
            padx=kwargs.get("padx", size_config["padx"]),
            pady=kwargs.get("pady", size_config["pady"]),
            disabledforeground=fg,
        )
        
        # Force update to ensure colors are applied (macOS fix)
        try:
            btn.configure(bg=bg, fg=fg)
        except:
            pass
        
        # Add hover effects with smooth transition feel
        def on_enter(e):
            btn.configure(bg=active_bg)
        
        def on_leave(e):
            btn.configure(bg=bg)
        
        def on_press(e):
            pressed_bg = MacOSTheme.COLORS["accent_pressed"] if style == "primary" else MacOSTheme.COLORS["control_pressed"]
            btn.configure(bg=pressed_bg)
        
        def on_release(e):
            if btn.winfo_containing(e.x_root, e.y_root) == btn:
                btn.configure(bg=active_bg)
            else:
                btn.configure(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        
        return btn
    
    @staticmethod
    def create_card(parent, elevated=True, **kwargs):
        """Create a card/panel with native macOS styling and optional elevation.
        
        Args:
            parent: Parent widget
            elevated: Whether to show as elevated (with border)
            **kwargs: Additional Frame arguments
        """
        if elevated:
            return tk.Frame(
                parent,
                bg=MacOSTheme.COLORS["card_bg"],
                highlightbackground=MacOSTheme.COLORS["border"],
                highlightthickness=1,
                **kwargs
            )
        else:
            return tk.Frame(
                parent,
                bg=MacOSTheme.COLORS["card_bg"],
                **kwargs
            )
    
    @staticmethod
    def create_header(parent, height=70):
        """Create a header frame with native macOS styling."""
        return tk.Frame(
            parent,
            bg=MacOSTheme.COLORS["elevated_bg"],
            height=height
        )
    
    @staticmethod
    def create_separator(parent):
        """Create a separator line."""
        return tk.Frame(
            parent,
            bg=MacOSTheme.COLORS["separator"],
            height=1
        )
    
    @staticmethod
    def configure_text_widget(widget, readonly=False):
        """Apply native macOS styling to text widgets."""
        if readonly:
            bg = MacOSTheme.COLORS["card_bg"]
            fg = MacOSTheme.COLORS["text_primary"]
        else:
            bg = MacOSTheme.COLORS["content_bg"]
            fg = MacOSTheme.COLORS["text_primary"]
        
        widget.configure(
            bg=bg,
            fg=fg,
            insertbackground=MacOSTheme.COLORS["accent"],  # Cursor color
            selectbackground=MacOSTheme.COLORS["selection"],
            selectforeground="#FFFFFF",
            relief="solid",
            borderwidth=1,
            highlightthickness=0
        )
    
    @staticmethod
    def configure_scrollbar():
        """Configure scrollbar styling (limited in Tkinter)."""
        # Note: True native scrollbars require platform-specific code
        # This provides a basic improvement
        style = ttk.Style()
        if MacOSTheme.is_macos():
            # Use native macOS scrollbars
            try:
                style.theme_use("aqua")
            except:
                style.theme_use("default")
    
    @staticmethod
    def create_label(parent, text, style="body", **kwargs):
        """Create a label with proper macOS typography.
        
        Args:
            parent: Parent widget
            text: Label text
            style: Typography style key
            **kwargs: Additional Label arguments
        """
        return tk.Label(
            parent,
            text=text,
            font=MacOSTheme.FONTS.get(style, MacOSTheme.FONTS["body"]),
            bg=kwargs.get("bg", MacOSTheme.COLORS["window_bg"]),
            fg=kwargs.get("fg", MacOSTheme.COLORS["text_primary"]),
            **{k: v for k, v in kwargs.items() if k not in ["bg", "fg", "font"]}
        )
    
    @staticmethod
    def apply_hover_effect(widget, hover_bg=None, children=True):
        """Apply hover effect to a widget and optionally its children.
        
        Args:
            widget: Widget to apply effect to
            hover_bg: Optional hover background color
            children: Whether to also update children backgrounds
        """
        original_bg = widget.cget("bg")
        hover_bg = hover_bg or MacOSTheme.COLORS["control_hover"]
        
        def on_enter(e):
            widget.configure(bg=hover_bg)
            if children:
                for child in widget.winfo_children():
                    try:
                        child.configure(bg=hover_bg)
                    except:
                        pass
        
        def on_leave(e):
            widget.configure(bg=original_bg)
            if children:
                for child in widget.winfo_children():
                    try:
                        child.configure(bg=original_bg)
                    except:
                        pass
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    @staticmethod
    def create_list_item(parent, text, icon="", callback=None, **kwargs):
        """Create a native macOS list item with hover effect.
        
        Args:
            parent: Parent widget
            text: Item text
            icon: Optional icon emoji
            callback: Optional click callback
            **kwargs: Additional arguments
        """
        item_frame = tk.Frame(
            parent,
            bg=MacOSTheme.COLORS["card_bg"],
            cursor="hand2" if callback else "arrow"
        )
        
        # Content container
        content = tk.Frame(item_frame, bg=MacOSTheme.COLORS["card_bg"])
        content.pack(fill="x", padx=MacOSTheme.SPACING["md"], pady=MacOSTheme.SPACING["sm"])
        
        # Icon and text
        if icon:
            icon_label = MacOSTheme.create_label(
                content,
                text=icon,
                style="body",
                bg=MacOSTheme.COLORS["card_bg"]
            )
            icon_label.pack(side="left", padx=(0, MacOSTheme.SPACING["sm"]))
        
        text_label = MacOSTheme.create_label(
            content,
            text=text,
            style="body",
            bg=MacOSTheme.COLORS["card_bg"],
            **kwargs
        )
        text_label.pack(side="left", fill="x", expand=True)
        
        # Apply hover effect to all elements
        if callback:
            MacOSTheme.apply_hover_effect(item_frame, children=True)
            MacOSTheme.apply_hover_effect(content, children=True)
            item_frame.bind("<Button-1>", lambda e: callback())
            content.bind("<Button-1>", lambda e: callback())
            text_label.bind("<Button-1>", lambda e: callback())
            if icon:
                icon_label.bind("<Button-1>", lambda e: callback())
        
        return item_frame
    
    @staticmethod
    def create_rounded_text(parent, corner_radius=8, **kwargs):
        """Create a text widget with rounded corners effect.
        
        Args:
            parent: Parent widget
            corner_radius: Radius for rounded corners
            **kwargs: Text widget arguments
        """
        # Create container frame for rounded effect
        container = tk.Frame(
            parent,
            bg=kwargs.get('bg', MacOSTheme.COLORS["content_bg"]),
            highlightbackground=MacOSTheme.COLORS["border"],
            highlightthickness=1
        )
        
        # Create text widget with padding for rounded appearance
        text_widget = tk.Text(
            container,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            **kwargs
        )
        text_widget.pack(padx=2, pady=2, fill="both", expand=True)
        
        return container, text_widget
    
    @staticmethod
    def create_rounded_entry(parent, corner_radius=8, **kwargs):
        """Create an entry widget with rounded corners.
        
        Args:
            parent: Parent widget
            corner_radius: Radius for rounded corners
            **kwargs: Entry widget arguments
        """
        # Create container frame for rounded effect
        container = tk.Frame(
            parent,
            bg=MacOSTheme.COLORS["content_bg"],
            highlightbackground=MacOSTheme.COLORS["border"],
            highlightthickness=1
        )
        
        # Create entry widget
        entry_widget = tk.Entry(
            container,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            bg=kwargs.get('bg', MacOSTheme.COLORS["content_bg"]),
            fg=kwargs.get('fg', MacOSTheme.COLORS["text_primary"]),
            insertbackground=MacOSTheme.COLORS["accent"],
            **{k: v for k, v in kwargs.items() if k not in ['bg', 'fg']}
        )
        entry_widget.pack(padx=4, pady=4, fill="both", expand=True)
        
        return container, entry_widget
