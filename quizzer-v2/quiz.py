#!/usr/bin/env python3
"""
Quiz Logic Engine
Core quiz functionality and AI integration
"""

import os
import re
import sys
import subprocess
from pathlib import Path
import json

# Try to import local AI
try:
    from local_ai import LocalAI
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class CourseQuiz:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.courses_dir = self.repo_root / "courses"
        self.streak = 0
        self.perfect_count = 0
        self.good_count = 0
        self.api_key = None
        self.local_ai = None
        self.use_local_ai = False
        self.use_ai = self.setup_ai()
        
        # AI is required (either local or OpenAI)
        if not self.use_ai and not self.use_local_ai:
            print("\n⚠️  This quiz requires AI (either local or OpenAI).")
            print("\nRun the launcher: python3 run.py")
            sys.exit(1)
        
    def get_courses(self):
        """Get list of available courses."""
        if not self.courses_dir.exists():
            print(f"Error: Courses directory not found at {self.courses_dir}")
            sys.exit(1)
        
        courses = [d for d in self.courses_dir.iterdir() 
                   if d.is_dir() and not d.name.startswith('.')]
        return sorted(courses)
    
    def setup_ai(self):
        """Setup AI evaluation - try local Ollama first, then OpenAI."""
        # Try LOCAL AI first (Ollama)
        if OLLAMA_AVAILABLE:
            try:
                # Check if ollama is installed and running
                result = subprocess.run(['ollama', 'list'], 
                                      capture_output=True, 
                                      text=True,
                                      timeout=5)
                if result.returncode == 0:
                    print("✓ Using LOCAL AI (Ollama) - FREE, no API key needed!")
                    self.local_ai = LocalAI("llama3.2:3b")
                    self.use_local_ai = True
                    return False  # Don't need OpenAI
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass  # Ollama not available, try OpenAI
        
        # Fall back to OpenAI API
        print("ℹ️  Local AI not available, trying OpenAI...")
        
        # Check for API key in environment variable
        self.api_key = os.environ.get('OPENAI_API_KEY')
        
        # If not in environment, check for .env file
        if not self.api_key:
            env_file = self.repo_root / '.env'
            if env_file.exists():
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith('OPENAI_API_KEY'):
                                self.api_key = line.split('=')[1].strip().strip('"').strip("'")
                                break
                except Exception:
                    pass
        
        if self.api_key:
            print("✓ AI-powered quiz enabled (using API key from .env file)")
            return True
        
        return False
    
    def find_tex_files(self, course_dir):
        """Find all .tex files in course directory."""
        return list(course_dir.glob('**/*.tex'))
    
    def extract_content_chunks(self, tex_file):
        """Extract content chunks from tex file."""
        chunks = []
        
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return chunks
        
        # Extract definitions
        definitions = re.findall(
            r'\\begin{definition}(?:\[([^\]]+)\])?\s*(.*?)\\end{definition}',
            content,
            re.DOTALL
        )
        for title, body in definitions:
            cleaned = self.clean_latex(body)
            if cleaned:
                chunks.append(('definition', title or 'Definition', cleaned))
        
        # Extract theorems
        theorems = re.findall(
            r'\\begin{theorem}(?:\[([^\]]+)\])?\s*(.*?)\\end{theorem}',
            content,
            re.DOTALL
        )
        for title, body in theorems:
            cleaned = self.clean_latex(body)
            if cleaned:
                chunks.append(('theorem', title or 'Theorem', cleaned))
        
        # Extract propositions
        propositions = re.findall(
            r'\\begin{proposition}(?:\[([^\]]+)\])?\s*(.*?)\\end{proposition}',
            content,
            re.DOTALL
        )
        for title, body in propositions:
            cleaned = self.clean_latex(body)
            if cleaned:
                chunks.append(('proposition', title or 'Proposition', cleaned))
        
        # Extract lemmas
        lemmas = re.findall(
            r'\\begin{lemma}(?:\[([^\]]+)\])?\s*(.*?)\\end{lemma}',
            content,
            re.DOTALL
        )
        for title, body in lemmas:
            cleaned = self.clean_latex(body)
            if cleaned:
                chunks.append(('lemma', title or 'Lemma', cleaned))
        
        return chunks
    
    def clean_latex(self, text):
        """Clean LaTeX formatting from text."""
        # Remove comments
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
        
        # Remove itemize/enumerate environments but keep content
        text = re.sub(r'\\begin{(?:itemize|enumerate)}', '', text)
        text = re.sub(r'\\end{(?:itemize|enumerate)}', '', text)
        text = re.sub(r'\\item', '•', text)
        
        # Remove math mode delimiters but keep content
        text = re.sub(r'\$\$([^$]+)\$\$', r'\1', text)
        text = re.sub(r'\$([^$]+)\$', r'\1', text)
        text = re.sub(r'\\\[([^\]]+)\\\]', r'\1', text)
        text = re.sub(r'\\\(([^)]+)\\\)', r'\1', text)
        
        # Remove section commands
        text = re.sub(r'\\section\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\subsection\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\subsubsection\{([^}]+)\}', r'\1', text)
        
        # Remove remaining backslash commands
        text = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        
        # Clean up extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text[:500] if len(text) > 500 else text  # Limit length
    
    def generate_question_from_chunk(self, chunk_type, title, content):
        """Use AI to generate a specific question from content chunk."""
        prompt = f"""Based on this {chunk_type} from course notes, generate ONE specific, detailed question that tests deep understanding of "{title}".

Title: {title}
Content: {content}

Requirements:
- The question must DIRECTLY test understanding of the concept: "{title}"
- Ask about the SPECIFIC content provided, not tangential or general topics
- The question should require the student to explain/apply concepts from the reference content above
- Make it challenging but answerable using the content provided
- The question should be unambiguous about what concept is being tested

Respond with ONLY a JSON object:
{{
    "question": "your generated question here (must clearly test '{title}')"
}}"""
        
        # Use LOCAL AI if available
        if self.use_local_ai and self.local_ai:
            try:
                response = self.local_ai.generate_json(
                    prompt,
                    "You are a professor creating challenging but clear quiz questions. Make questions unambiguous about what type of answer is expected (calculation, definition, explanation). Respond with valid JSON only.",
                    temperature=0.7,
                    max_tokens=200
                )
                if response and "question" in response:
                    return response["question"]
                else:
                    # Fallback to simple question
                    return f"Explain the {chunk_type}: {title}"
            except Exception:
                return f"Explain the {chunk_type}: {title}"
        
        # Otherwise use OpenAI
        import urllib.request
        
        try:
            data = json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a professor creating challenging quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }).encode('utf-8')
            
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                content_text = result['choices'][0]['message']['content'].strip()
                
                # Try to parse JSON response
                try:
                    parsed = json.loads(content_text)
                    return parsed.get('question', f"Explain the {chunk_type}: {title}")
                except json.JSONDecodeError:
                    return f"Explain the {chunk_type}: {title}"
        except Exception:
            return f"Explain the {chunk_type}: {title}"
    
    def evaluate_answer_5_level(self, user_answer, reference_content, title, concept_type):
        """Use AI to evaluate answer on 5-level scale."""
        
        # Detect question type from user_answer context
        answer_lower = user_answer.lower()
        has_calculation = any(char.isdigit() for char in user_answer) or '=' in user_answer
        has_formula = '/' in user_answer or '*' in user_answer or '+' in user_answer
        is_short_factual = len(user_answer.strip()) < 100 and has_calculation
        
        # Pre-check: Very short answers (< 15 chars) without any content are likely wrong
        if len(user_answer.strip()) < 10:
            return "WRONG", "Answer is too brief to demonstrate understanding of the concept."
        
        # Build context-aware grading instructions based on answer characteristics
        question_type_hint = ""
        if has_calculation and has_formula:
            question_type_hint = "\n**QUESTION TYPE DETECTED: CALCULATION/NUMERICAL**\nFor calculation questions, a PERFECT answer provides: (1) correct formula, (2) correct substitution, (3) correct numerical result. DO NOT penalize for not explaining concepts beyond what's needed for the calculation."
        elif is_short_factual and (has_calculation or any(word in answer_lower for word in ['time', 'times', 'once', 'twice', 'iteration', 'fold'])):
            question_type_hint = "\n**QUESTION TYPE DETECTED: FACTUAL/NUMERICAL ANSWER**\nThis appears to be asking for a specific fact or number, not a definition. A PERFECT answer correctly states the fact/number. DO NOT penalize for not providing a full definition if only a specific fact was asked."
        
        prompt = f"""You are a STRICT but FAIR professor grading a student's answer. Be rigorous and precise.

CONCEPT: {title} ({concept_type})
REFERENCE CONTENT FROM COURSE NOTES: {reference_content}

STUDENT'S ANSWER: {user_answer}
{question_type_hint}

STRICT GRADING SCALE:
- PERFECT: Answer is complete, accurate, directly addresses the concept, and aligns with reference content
- GOOD: Answer covers MOST main concepts from reference correctly with only MINOR gaps
- PARTIAL: Answer shows GENUINE partial understanding - gets some specific facts right but misses important points (NOT just vague relevance)
- WEAK: Answer has MAJOR conceptual errors or misses most important points (barely any correct content)
- WRONG: Answer is completely incorrect, contradicts reference, or is completely off-topic

CRITICAL GRADING RULES:
1. **CONTRADICTION = WRONG**: If answer states the OPPOSITE of what reference says → mark WRONG (not PARTIAL)
2. **Answer must DIRECTLY address what was asked** → if completely off-topic, mark WRONG
3. **Check for contradictions carefully**: 
   - Does answer say "without X" when reference says "with X"? → WRONG
   - Does answer say "randomly" when reference says "maintains proportion"? → WRONG
   - Does answer negate a key concept from reference? → WRONG
4. **NEVER invent requirements not in the question** → Only grade what was ACTUALLY ASKED FOR
5. **For CALCULATION questions**: Correct formula + result = PERFECT (don't require extra explanations)
6. **For FACTUAL/NUMERICAL questions**: Correct fact/number = PERFECT (don't require full definitions if not asked)
7. **For DEFINITION questions**: Must explain the concept with key terms from reference
8. **For EXPLANATION questions**: Must provide reasoning aligned with reference content
9. **Be FAIR**: Don't mark correct answers as wrong just because they could be more detailed
10. **CRITICAL**: If the question asks "what is the number", a correct number = PERFECT (not PARTIAL)
11. **PARTIAL vs WRONG**: PARTIAL = incomplete but directionally correct. WRONG = contradicts or completely incorrect

EVALUATION STEPS:
1. Determine question type from the answer format (calculation/factual/definition/explanation)
2. **FIRST CHECK FOR CONTRADICTIONS**: Does the answer say the OPPOSITE of what the reference says?
   - If YES → mark WRONG immediately (don't continue to other steps)
   - Examples: "without" vs "with", "random" vs "maintains proportion", "doesn't consider" vs "ensures"
3. Check if answer directly addresses what was asked about "{title}"
4. Compare answer against REFERENCE - is the core fact/calculation CORRECT?
5. Does the answer fulfill ONLY what was asked (not what could have been asked)?
6. If the core answer is correct, don't downgrade for missing unrequested details

**CRITICAL DECISION TREE**:
- Contradicts reference? → WRONG
- Completely off-topic? → WRONG
- Core answer correct but missing requested details? → GOOD or PARTIAL
- Core answer correct and complete? → PERFECT

**IMPORTANT**: Before marking PARTIAL, ask yourself: 
1. "Does the answer CONTRADICT the reference?" If yes → WRONG
2. "Did the question actually ask for the missing information, or am I inventing requirements?"

Respond with ONLY a JSON object:
{{
    "level": "PERFECT|GOOD|PARTIAL|WEAK|WRONG",
    "explanation": "Brief explanation: (1) Question type, (2) Any contradictions found? (3) Is core answer correct vs reference? (4) If not perfect, what was ASKED FOR that's missing? (5) Final grade."
}}"""
        
        # Use LOCAL AI if available
        if self.use_local_ai and self.local_ai:
            try:
                response = self.local_ai.generate_json(
                    prompt,
                    "You are a STRICT professor. MOST IMPORTANT: CHECK FOR CONTRADICTIONS FIRST - if the answer says the OPPOSITE of the reference (e.g., 'without X' when reference says 'with X', or 'randomly' when reference says 'maintains proportion'), mark WRONG immediately. Contradictions are WRONG, not PARTIAL. For correct answers: if question asks for NUMBER/FACT and student gives correct number/fact, that's PERFECT. Only penalize for missing information that was ACTUALLY REQUESTED. Respond with valid JSON only.",
                    temperature=0.2,
                    max_tokens=500
                )
                
                if response:
                    # Check for error in response
                    if "error" in response:
                        error_msg = response.get("error", "Unknown error")
                        raw = response.get("raw_response", "")[:200]
                        return "WRONG", f"AI parsing error: {error_msg}. Raw response: {raw}"
                    
                    # Check for level field
                    if "level" in response:
                        level = response.get("level", "WRONG").upper()
                        explanation = response.get("explanation", "Unable to evaluate")
                        return level, explanation
                    else:
                        # Show what fields were actually returned
                        fields = list(response.keys())
                        return "WRONG", f"AI response missing 'level' field. Got fields: {fields}. Response: {str(response)[:200]}"
                else:
                    return "WRONG", "Local AI returned no response. Try again or check if Ollama is running properly."
            except Exception as e:
                return "WRONG", f"Local AI evaluation error: {str(e)}"
        
        # Otherwise use OpenAI
        import urllib.request
        import urllib.error
        
        try:
            data = json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a STRICT professor. MOST IMPORTANT: CHECK FOR CONTRADICTIONS FIRST - if the answer says the OPPOSITE of the reference (e.g., 'without X' when reference says 'with X', or 'randomly' when reference says 'maintains proportion'), mark WRONG immediately. Contradictions are WRONG, not PARTIAL. For correct answers: if question asks for NUMBER/FACT and student gives correct number/fact, that's PERFECT. Only penalize for missing information that was ACTUALLY REQUESTED."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 400
            }).encode('utf-8')
            
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                content_text = result['choices'][0]['message']['content'].strip()
                
                try:
                    evaluation = json.loads(content_text)
                    level = evaluation.get('level', 'WRONG').upper()
                    explanation = evaluation.get('explanation', 'Unable to provide detailed feedback')
                    return level, explanation
                except json.JSONDecodeError:
                    return "WRONG", "Evaluation failed"
        except Exception:
            return "WRONG", "API error during evaluation"
    
    def format_reference(self, content, formatted=None):
        """Format reference content for display."""
        if formatted:
            return formatted
        return content
