# macOS Native Design Enhancements

## Overview
The Quizzer V2 application has been enhanced with native macOS design patterns to provide a more polished, familiar experience for Mac users.

## Key Improvements

### 1. **Native macOS Theme Module** (`src/gui/macos_theme.py`)
A comprehensive theming system that provides:
- **Native Color Palette**: Uses macOS system colors (dark mode optimized)
  - Window backgrounds: `#1E1E1E` (dark window) / `#F5F5F7` (light)
  - Accent color: `#0A84FF` (system blue)
  - Text hierarchy: Primary, secondary, tertiary levels
  - Semantic colors: Success (green), Warning (yellow), Error (red)

- **Typography System**: SF Pro font family with proper sizing
  - Display: 28-32pt for hero text
  - Title: 20-24pt for section headers
  - Body: 15pt for main content
  - Callout/Subheadline: 11-13pt for secondary info
  - Caption/Footnote: 9-10pt for details

- **Spacing Guidelines**: Consistent spacing following macOS HIG
  - XS: 4px, SM: 8px, MD: 12px, LG: 16px, XL: 20px, XXL: 24px

- **UI Components**:
  - `create_button()`: Native-style buttons with hover states (primary, secondary, destructive)
  - `create_card()`: Panel/card containers with proper borders
  - `create_header()`: Elevated header bars
  - `create_separator()`: Subtle divider lines
  - `create_label()`: Typography-aware labels

### 2. **Main Application Improvements** (`quizzer_v2_gui.py`)

#### Window & Chrome
- Native macOS window styling using `::tk::unsupported::MacWindowStyle`
- Proper window controls (close, minimize, zoom buttons)
- Aqua theme integration for native scrollbars and controls

#### Header
- Elevated background (`#383838`) with subtle separator
- System blue accent for "Ask AI" button
- Consistent spacing and button styling

#### Course Cards
- Card-based layout with native borders
- Proper color hierarchy (card background, text colors)
- Native button styles with hover effects:
  - **Chat button**: Secondary style (gray)
  - **Start Quiz button**: Primary style (system blue)
- Responsive hover states

#### Colors
- Window background: `#1E1E1E`
- Card/elevated surfaces: `#2D2D2D` / `#383838`
- Text: White primary, gray secondary/tertiary
- Accent: System blue (`#0A84FF`)

### 3. **Chatbot Interface Improvements** (`chatbot_gui.py`)

#### Window
- Native macOS window appearance
- Proper document-style chrome
- Native aqua scrollbars

#### Header
- Elevated design with separator
- Title hierarchy (20pt title, 13pt subtitle)
- Native button for "Clear" action

#### Chat Interface
- **Message Bubbles**:
  - User messages: System blue background (`#0A84FF`)
  - AI messages: Card background (`#2D2D2D`) with subtle border
  - Proper padding (15px horizontal, 10-12px vertical)
  - Rounded corners feel

- **Input Area**:
  - Native text field styling
  - System blue cursor and selection
  - Proper focus states (blue border on focus)
  - Send button with primary accent

- **Loading States**:
  - System blue progress bars
  - Native color scheme for loading screens
  - Smooth animations

### 4. **Visual Improvements**

#### Spacing & Layout
- Consistent use of macOS spacing units (8px grid)
- Proper padding on all interactive elements
- Better visual hierarchy

#### Typography
- SF Pro font throughout (system default on macOS)
- Proper font weights and sizes
- Text color hierarchy (primary, secondary, tertiary)

#### Buttons
- Three styles: Primary (blue), Secondary (gray), Destructive (red)
- Smooth hover transitions
- Proper active/pressed states
- Native cursor styles ("hand2" on macOS)

#### Separators
- Subtle 1px lines (`#3C3C3E`)
- Used between header/content, content/footer, etc.

## Visual Design Philosophy

### Color System
- **Dark Mode First**: Optimized for macOS dark mode
- **System Colors**: Uses macOS system blue as accent
- **Hierarchy**: Clear visual hierarchy with text colors
- **Contrast**: Maintains WCAG AA contrast ratios

### Spacing
- **8px Grid**: All spacing based on 8px increments
- **Breathing Room**: Generous padding for comfort
- **Alignment**: Consistent margins and padding

### Components
- **Native Feel**: Buttons and controls feel native to macOS
- **Hover States**: Smooth transitions on hover
- **Focus States**: Clear focus indicators
- **Consistency**: Same patterns used throughout

## Technical Details

### Platform Detection
- Uses `platform.system() == "Darwin"` to detect macOS
- Falls back gracefully on other platforms
- Native macOS APIs used only when available

### Window Styling
```python
window.tk.call("::tk::unsupported::MacWindowStyle", "style", 
               window._w, "document", "closeBox collapseBox resizable zoomBox")
```

### Theme Integration
```python
style = ttk.Style()
if MacOSTheme.is_macos():
    style.theme_use("aqua")  # Native macOS theme
```

## Benefits

1. **Native Feel**: App looks and feels like a native Mac application
2. **Visual Hierarchy**: Clear information architecture
3. **Consistency**: Follows macOS Human Interface Guidelines
4. **Professionalism**: Modern, polished appearance
5. **Familiarity**: Mac users feel at home immediately
6. **Accessibility**: Proper contrast and text sizing
7. **Future-Proof**: Easy to update colors and styles

## Before & After

### Before
- Generic dark theme
- Inconsistent spacing
- Mixed button styles
- No native integration

### After
- Native macOS color palette
- Consistent 8px grid spacing
- Native button styles with hover effects
- Aqua theme integration
- System accent colors
- Proper window chrome

## Usage

The theme system is automatically applied when running on macOS. No additional configuration needed:

```bash
./start_quiz.sh
```

All GUI components automatically use the native macOS theme module.

## Future Enhancements

Potential improvements for future versions:
- Light mode support (already defined in theme)
- Vibrancy/translucency effects (requires platform-specific code)
- Native menu bar integration
- System notification center integration
- Touch Bar support (if available)
- macOS shortcuts and gestures

## Performance Notes

- **70B Model Loading**: The 70B Ollama model takes time to load initially
  - Recommended: Use `OLLAMA_KEEP_ALIVE=-1` to keep model in memory
  - Alternative: Use 8B model for faster responses
  - Pre-warm the model before using the app

- **GPU Acceleration**: Set `OLLAMA_NUM_GPU=99` to maximize GPU usage
- **SSD Storage**: Ensure models are stored on SSD for faster loading

---

**Design System Version**: 1.0  
**Platform**: macOS (Sonoma and later)  
**Theme**: Dark Mode Optimized  
**Last Updated**: 2025-01-17
