#!/usr/bin/env python3
"""
Animation Utilities
Provides smooth, fluid animations for the UI
"""

import tkinter as tk
import math


class AnimationEngine:
    """Handles smooth animations for UI elements."""
    
    @staticmethod
    def fade_in(widget, duration=300, callback=None):
        """Fade in a widget smoothly.
        
        Args:
            widget: Widget to fade in
            duration: Duration in milliseconds
            callback: Optional callback when animation completes
        """
        steps = 30
        step_duration = duration // steps
        
        def animate(step=0):
            if step <= steps:
                alpha = step / steps
                # Can't change actual opacity in tkinter, but we can simulate with colors
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            elif callback:
                callback()
        
        animate()
    
    @staticmethod
    def slide_in(widget, direction='left', duration=300, callback=None):
        """Slide in a widget from a direction.
        
        Args:
            widget: Widget to slide in
            direction: Direction to slide from ('left', 'right', 'top', 'bottom')
            duration: Duration in milliseconds
            callback: Optional callback when animation completes
        """
        steps = 20
        step_duration = duration // steps
        
        # Store original position
        widget.update_idletasks()
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                # Ease out cubic
                eased = 1 - math.pow(1 - progress, 3)
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            elif callback:
                callback()
        
        animate()
    
    @staticmethod
    def pulse(widget, duration=1000, count=3, callback=None):
        """Pulse animation for a widget.
        
        Args:
            widget: Widget to pulse
            duration: Duration of one pulse in milliseconds
            count: Number of pulses
            callback: Optional callback when animation completes
        """
        steps = 20
        step_duration = duration // steps
        current_pulse = [0]
        
        def animate(step=0):
            if current_pulse[0] >= count:
                if callback:
                    callback()
                return
            
            if step <= steps:
                # Create pulse effect using sine wave
                scale = 1 + 0.1 * math.sin(step * math.pi / steps)
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            else:
                current_pulse[0] += 1
                animate(0)
        
        animate()


class LoadingSpinner:
    """Animated loading spinner widget."""
    
    def __init__(self, parent, size=50, color="#2563eb"):
        """Initialize loading spinner.
        
        Args:
            parent: Parent widget
            size: Size of the spinner
            color: Color of the spinner
        """
        self.parent = parent
        self.size = size
        self.color = color
        self.angle = 0
        self.running = False
        
        # Create canvas for spinner
        self.canvas = tk.Canvas(
            parent,
            width=size,
            height=size,
            bg=parent.cget('bg'),
            highlightthickness=0
        )
        
        # Draw spinner arc
        self.arc = self.canvas.create_arc(
            5, 5, size-5, size-5,
            start=0,
            extent=120,
            outline=color,
            width=4,
            style=tk.ARC
        )
    
    def pack(self, **kwargs):
        """Pack the spinner."""
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the spinner."""
        self.canvas.grid(**kwargs)
    
    def start(self):
        """Start the spinner animation."""
        self.running = True
        self._animate()
    
    def stop(self):
        """Stop the spinner animation."""
        self.running = False
    
    def destroy(self):
        """Destroy the spinner."""
        self.running = False
        self.canvas.destroy()
    
    def _animate(self):
        """Animate the spinner rotation."""
        if not self.running:
            return
        
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        
        # Continue animation
        self.canvas.after(30, self._animate)


class ProgressBar:
    """Animated progress bar."""
    
    def __init__(self, parent, width=300, height=6, color="#2563eb", bg="#e5e7eb"):
        """Initialize progress bar.
        
        Args:
            parent: Parent widget
            width: Width of progress bar
            height: Height of progress bar
            color: Color of progress fill
            bg: Background color
        """
        self.parent = parent
        self.width = width
        self.height = height
        self.color = color
        self.progress = 0
        
        # Create canvas
        self.canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0
        )
        
        # Create progress rectangle
        self.bar = self.canvas.create_rectangle(
            0, 0, 0, height,
            fill=color,
            outline=""
        )
    
    def pack(self, **kwargs):
        """Pack the progress bar."""
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the progress bar."""
        self.canvas.grid(**kwargs)
    
    def set_progress(self, value, animated=True):
        """Set progress value (0-100).
        
        Args:
            value: Progress value (0-100)
            animated: Whether to animate the change
        """
        value = max(0, min(100, value))
        target_width = (value / 100) * self.width
        
        if animated:
            self._animate_to(target_width)
        else:
            self.canvas.coords(self.bar, 0, 0, target_width, self.height)
            self.progress = value
    
    def _animate_to(self, target_width):
        """Animate progress to target width."""
        current_width = (self.progress / 100) * self.width
        diff = target_width - current_width
        steps = 15
        step_size = diff / steps
        
        def animate(step=0):
            if step < steps:
                new_width = current_width + (step_size * step)
                self.canvas.coords(self.bar, 0, 0, new_width, self.height)
                self.canvas.after(20, lambda: animate(step + 1))
            else:
                self.canvas.coords(self.bar, 0, 0, target_width, self.height)
                self.progress = (target_width / self.width) * 100
        
        animate()
    
    def destroy(self):
        """Destroy the progress bar."""
        self.canvas.destroy()


class DotsLoader:
    """Animated dots loader (...)."""
    
    def __init__(self, parent, text="Loading", font=("SF Pro", 14), color="#ffffff"):
        """Initialize dots loader.
        
        Args:
            parent: Parent widget
            text: Text to display
            font: Font tuple
            color: Text color
        """
        self.parent = parent
        self.base_text = text
        self.dots = 0
        self.running = False
        
        self.label = tk.Label(
            parent,
            text=text,
            font=font,
            fg=color,
            bg=parent.cget('bg')
        )
    
    def pack(self, **kwargs):
        """Pack the loader."""
        self.label.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the loader."""
        self.label.grid(**kwargs)
    
    def start(self):
        """Start the dots animation."""
        self.running = True
        self._animate()
    
    def stop(self):
        """Stop the dots animation."""
        self.running = False
    
    def destroy(self):
        """Destroy the loader."""
        self.running = False
        self.label.destroy()
    
    def _animate(self):
        """Animate the dots."""
        if not self.running:
            return
        
        self.dots = (self.dots + 1) % 4
        text = self.base_text + "." * self.dots
        self.label.config(text=text)
        
        # Continue animation
        self.label.after(500, self._animate)
