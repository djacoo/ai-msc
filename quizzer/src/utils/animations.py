#!/usr/bin/env python3
"""
Animation Utilities
Provides smooth, fluid animations for the UI
"""

import tkinter as tk
import math
from typing import Callable, Optional


class AnimationEngine:
    """Handles smooth animations for UI elements."""
    
    # Easing functions for smooth animations
    @staticmethod
    def ease_out_cubic(t):
        """Ease out cubic easing function."""
        return 1 - math.pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t):
        """Ease in-out cubic easing function."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - math.pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_out_bounce(t):
        """Ease out bounce easing function."""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def fade_in(widget, duration=400, callback=None, easing=None):
        """Fade in a widget smoothly by animating its position.
        
        Args:
            widget: Widget to fade in
            duration: Duration in milliseconds
            callback: Optional callback when animation completes
            easing: Easing function (defaults to ease_out_cubic)
        """
        if easing is None:
            easing = AnimationEngine.ease_out_cubic
        
        steps = 40  # More steps for smoother animation
        step_duration = duration // steps
        
        # Store original position
        widget.update_idletasks()
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                alpha = easing(progress)
                
                # Simulate fade by sliding up slightly
                try:
                    # Small upward movement for fade effect
                    offset = int((1 - alpha) * 10)
                    if hasattr(widget, '_original_y'):
                        widget.place(y=widget._original_y - offset)
                except:
                    pass
                
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            elif callback:
                callback()
        
        # Store original position
        if hasattr(widget, 'winfo_y'):
            widget._original_y = widget.winfo_y()
        
        animate()
    
    @staticmethod
    def slide_in(widget, direction='left', duration=500, distance=100, callback=None, easing=None):
        """Slide in a widget from a direction with smooth easing.
        
        Args:
            widget: Widget to slide in
            direction: Direction to slide from ('left', 'right', 'top', 'bottom')
            duration: Duration in milliseconds
            distance: Distance to slide in pixels
            callback: Optional callback when animation completes
            easing: Easing function (defaults to ease_out_cubic)
        """
        if easing is None:
            easing = AnimationEngine.ease_out_cubic
        
        steps = 40  # Smoother with more steps
        step_duration = duration // steps
        
        # Store original position
        widget.update_idletasks()
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                eased = easing(progress)
                
                # Calculate offset based on direction
                offset = int(distance * (1 - eased))
                
                try:
                    if direction == 'left':
                        widget.place(x=-offset if step == 0 else widget.winfo_x() + (widget.winfo_x() + offset) // (steps - step + 1))
                    elif direction == 'right':
                        widget.place(x=offset if step == 0 else widget.winfo_x() - offset // (steps - step + 1))
                    # Similar for top/bottom
                except:
                    pass
                
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            elif callback:
                callback()
        
        animate()
    
    @staticmethod
    def pulse(widget, duration=800, count=2, scale_factor=0.08, callback=None):
        """Smooth pulse animation for a widget.
        
        Args:
            widget: Widget to pulse
            duration: Duration of one pulse in milliseconds
            count: Number of pulses
            scale_factor: How much to scale (0.1 = 10% larger)
            callback: Optional callback when animation completes
        """
        steps = 30  # Smoother with more steps
        step_duration = duration // steps
        current_pulse = [0]
        
        original_font = None
        if hasattr(widget, 'cget'):
            try:
                font_info = widget.cget('font')
                if font_info:
                    original_font = font_info
            except:
                pass
        
        def animate(step=0):
            if current_pulse[0] >= count:
                # Reset to original
                if original_font and hasattr(widget, 'config'):
                    try:
                        widget.config(font=original_font)
                    except:
                        pass
                if callback:
                    callback()
                return
            
            if step <= steps:
                # Create smooth pulse effect using sine wave
                progress = step / steps
                scale = 1 + scale_factor * math.sin(progress * math.pi)
                
                # Apply scale to font size if it's a label/button
                if original_font and hasattr(widget, 'config'):
                    try:
                        if isinstance(original_font, tuple) and len(original_font) >= 2:
                            font_family, font_size = original_font[0], original_font[1]
                            new_size = int(font_size * scale)
                            weight = original_font[2] if len(original_font) > 2 else 'normal'
                            widget.config(font=(font_family, new_size, weight))
                    except:
                        pass
                
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            else:
                current_pulse[0] += 1
                animate(0)
        
        animate()
    
    @staticmethod
    def scale_in(widget, duration=400, callback=None, easing=None):
        """Scale in animation (grow from small to normal size).
        
        Args:
            widget: Widget to animate
            duration: Duration in milliseconds
            callback: Optional callback when animation completes
            easing: Easing function
        """
        if easing is None:
            easing = AnimationEngine.ease_out_cubic
        
        steps = 30
        step_duration = duration // steps
        
        original_font = None
        if hasattr(widget, 'cget'):
            try:
                font_info = widget.cget('font')
                if font_info:
                    original_font = font_info
            except:
                pass
        
        def animate(step=0):
            if step <= steps:
                progress = step / steps
                scale = easing(progress)
                
                # Apply scale to font size
                if original_font and hasattr(widget, 'config'):
                    try:
                        if isinstance(original_font, tuple) and len(original_font) >= 2:
                            font_family, font_size = original_font[0], original_font[1]
                            new_size = max(1, int(font_size * scale))
                            weight = original_font[2] if len(original_font) > 2 else 'normal'
                            widget.config(font=(font_family, new_size, weight))
                    except:
                        pass
                
                widget.update_idletasks()
                widget.after(step_duration, lambda: animate(step + 1))
            else:
                # Ensure final size is correct
                if original_font and hasattr(widget, 'config'):
                    try:
                        widget.config(font=original_font)
                    except:
                        pass
                if callback:
                    callback()
        
        animate()
    
    @staticmethod
    def shake(widget, duration=400, intensity=5, callback=None):
        """Shake animation for errors or attention.
        
        Args:
            widget: Widget to shake
            duration: Duration in milliseconds
            intensity: How far to shake in pixels
            callback: Optional callback when complete
        """
        steps = 20
        step_duration = duration // steps
        
        widget.update_idletasks()
        original_x = widget.winfo_x()
        
        def animate(step=0):
            if step <= steps:
                # Shake using sine wave
                offset = int(intensity * math.sin(step * math.pi / 2.5))
                try:
                    widget.place(x=original_x + offset)
                except:
                    pass
                
                widget.after(step_duration, lambda: animate(step + 1))
            else:
                # Reset position
                try:
                    widget.place(x=original_x)
                except:
                    pass
                if callback:
                    callback()
        
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
        
        # Continue animation with smooth 60fps (16ms per frame)
        self.canvas.after(16, self._animate)


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
