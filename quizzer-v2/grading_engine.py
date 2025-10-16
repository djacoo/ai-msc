#!/usr/bin/env python3
"""
Grading Engine
Teacher-grade grading with rubrics and citations
"""

import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from pdf_grounding import PDFGroundingEngine


class GradingEngine:
    """Grade student answers with teacher-like rigor and citations."""
    
    def __init__(self, repo_root: str, ai_engine):
        """Initialize grading engine.
        
        Args:
            repo_root: Root directory of repository
            ai_engine: AI engine for grading
        """
        self.grounding = PDFGroundingEngine(repo_root)
        self.ai = ai_engine
        self.repo_root = Path(repo_root)
    
    def grade_answer(self, question: Dict, user_answer: str) -> Dict:
        """Grade a user's answer to a question.
        
        Args:
            question: Question object with answer_key and rubric
            user_answer: User's submitted answer
            
        Returns:
            Grading object with score, decision, checks, and explanation
        """
        qtype = question.get("type", "short_answer")
        
        if qtype == "mcq_single":
            return self._grade_mcq_single(question, user_answer)
        elif qtype == "mcq_multi":
            return self._grade_mcq_multi(question, user_answer)
        else:
            return self._grade_open_ended(question, user_answer)
    
    def _grade_mcq_single(self, question: Dict, user_answer: str) -> Dict:
        """Grade single-choice MCQ.
        
        Args:
            question: Question object
            user_answer: User's answer (e.g., "A" or "B")
            
        Returns:
            Grading result
        """
        answer_key = question.get("answer_key", {})
        correct = answer_key.get("correct", [])
        max_points = question.get("answer_key", {}).get("max_points", 10)
        
        # Normalize answer
        user_choice = user_answer.strip().upper()
        if len(user_choice) > 1:
            user_choice = user_choice[0]  # Take first char
        
        correct_choices = [c.strip().upper()[0] if c else "" for c in correct]
        
        # Check if correct
        is_correct = user_choice in correct_choices
        
        grading = {
            "question_id": question.get("id"),
            "points_awarded": max_points if is_correct else 0,
            "points_possible": max_points,
            "decision": "correct" if is_correct else "incorrect",
            "checks": [
                {
                    "criterion": "Selected correct option",
                    "met": is_correct,
                    "evidence": f"User selected '{user_choice}', correct is {correct_choices}"
                }
            ],
            "explanation_to_student": (
                f"✓ Correct! The answer is {correct_choices[0]}."
                if is_correct else
                f"✗ Incorrect. You selected '{user_choice}' but the correct answer is {correct_choices[0]}."
            ),
            "citations": question.get("grounding", []),
            "false_positive_guard": True,
            "false_negative_guard": True
        }
        
        return {"grading": grading}
    
    def _grade_mcq_multi(self, question: Dict, user_answer: str) -> Dict:
        """Grade multi-choice MCQ with partial credit.
        
        Formula: (# correct chosen / total correct) - (# incorrect chosen / total incorrect)
        Clamped to [0, 1], then apply thresholds: ≥90% correct, 40-89% partial, <40% incorrect
        
        Args:
            question: Question object
            user_answer: User's answer (e.g., "A,C" or "A, C")
            
        Returns:
            Grading result
        """
        answer_key = question.get("answer_key", {})
        correct = answer_key.get("correct", [])
        max_points = answer_key.get("max_points", 10)
        
        # Parse user answer
        user_choices = set()
        for choice in user_answer.upper().replace(" ", "").split(","):
            if choice and choice[0].isalpha():
                user_choices.add(choice[0])
        
        # Parse correct answer
        correct_choices = set()
        for c in correct:
            if c:
                correct_choices.add(c.strip().upper()[0])
        
        # Get all options from question
        all_options = set()
        for opt in question.get("options", []):
            if opt and opt[0].isalpha():
                all_options.add(opt[0].upper())
        
        incorrect_choices = all_options - correct_choices
        
        # Calculate components
        correct_chosen = len(user_choices & correct_choices)
        incorrect_chosen = len(user_choices & incorrect_choices)
        
        # Apply formula from specification
        if len(correct_choices) == 0:
            score_ratio = 0
        else:
            ratio_correct = correct_chosen / len(correct_choices)
            ratio_incorrect = incorrect_chosen / len(incorrect_choices) if len(incorrect_choices) > 0 else 0
            score_ratio = max(0.0, min(1.0, ratio_correct - ratio_incorrect))
        
        points = round(score_ratio * max_points)
        
        # Decision thresholds per specification: ≥90%, 40-89%, <40%
        if score_ratio >= 0.9:
            decision = "correct"
        elif score_ratio >= 0.4:
            decision = "partially_correct"
        else:
            decision = "incorrect"
        
        # Build explanation with grounding
        grounding = question.get("grounding", [])
        citation_text = ""
        if grounding:
            g = grounding[0]
            citation_text = f" (See {g.get('path', 'notes')}, p. {g.get('page', '?')})"
        
        explanation = f"""{decision.replace('_', ' ').title()}. Score: {points}/{max_points} points.
✓ Correct options chosen: {correct_chosen}/{len(correct_choices)}
✗ Incorrect options chosen: {incorrect_chosen}
Correct answer: {', '.join(sorted(correct_choices))}{citation_text}"""
        
        grading = {
            "question_id": question.get("id"),
            "points_awarded": points,
            "points_possible": max_points,
            "decision": decision,
            "checks": [
                {
                    "criterion": "Selected all correct options",
                    "met": correct_chosen == len(correct_choices),
                    "evidence": f"Chose {correct_chosen}/{len(correct_choices)} correct options: {sorted(user_choices & correct_choices)}"
                },
                {
                    "criterion": "No incorrect options selected",
                    "met": incorrect_chosen == 0,
                    "evidence": f"Chose {incorrect_chosen} incorrect options: {sorted(user_choices & incorrect_choices) if incorrect_chosen > 0 else 'none'}"
                }
            ],
            "explanation_to_student": explanation,
            "citations": grounding,
            "false_positive_guard": True,
            "false_negative_guard": True
        }
        
        return {"grading": grading}
    
    def _grade_open_ended(self, question: Dict, user_answer: str) -> Dict:
        """Grade open-ended question using AI with rubric.
        
        Args:
            question: Question object
            user_answer: User's answer
            
        Returns:
            Grading result
        """
        answer_key = question.get("answer_key", {})
        canonical = answer_key.get("canonical_answer", "")
        concepts = answer_key.get("concepts_required", [])
        point_breakdown = answer_key.get("point_breakdown", [])
        rubric = question.get("rubric", {})
        grounding = question.get("grounding", [])
        
        # Get reference content from grounding
        reference_texts = []
        for g in grounding:
            pdf_path = self.repo_root / g.get("path", "")
            page = g.get("page", 1)
            
            if pdf_path.exists():
                content = self.grounding.get_page_content(pdf_path, page)
                if content:
                    reference_texts.append(content[:1000])
        
        reference_content = "\n".join(reference_texts) if reference_texts else canonical
        
        # Build grading prompt
        prompt = self._build_grading_prompt(
            question=question.get("prompt", ""),
            user_answer=user_answer,
            canonical_answer=canonical,
            concepts_required=concepts,
            point_breakdown=point_breakdown,
            reference_content=reference_content,
            rubric=rubric
        )
        
        # Get AI grading
        try:
            response = self.ai.generate_json(
                prompt,
                "You are a rigorous professor grading student work. Check EVERY criterion carefully against the reference content. Be strict but fair. Respond with valid JSON only.",
                temperature=0.2,
                max_tokens=1000
            )
            
            if not response or "error" in response:
                # Fallback grading
                return self._fallback_grading(question, user_answer, canonical)
            
            # Parse grading response
            checks = response.get("checks", [])
            points_awarded = response.get("points_awarded", 0)
            max_points = sum(c.get("points", 0) for c in point_breakdown)
            
            # FALSE POSITIVE GUARD: Detect minimal/empty answers
            user_answer_clean = user_answer.strip().replace(".", "").replace(",", "").replace("!", "").replace("?", "").strip()
            if len(user_answer_clean) < 5:
                # Answer too short - force fail
                print(f"⚠️ FALSE POSITIVE GUARD: Answer too short ({len(user_answer_clean)} chars), forcing 0 points")
                points_awarded = 0
                # Mark all checks as not met
                for check in checks:
                    check["met"] = False
                    check["evidence"] = f"Answer is too short/empty to evaluate ({len(user_answer_clean)} meaningful characters)"
            
            # Determine decision per specification: ≥90%, 40-89%, <40%
            percentage = points_awarded / max_points if max_points > 0 else 0
            if percentage >= 0.9:
                decision = "correct"
            elif percentage >= 0.4:
                decision = "partially_correct"
            else:
                decision = "incorrect"
            
            grading = {
                "question_id": question.get("id"),
                "points_awarded": points_awarded,
                "points_possible": max_points,
                "decision": decision,
                "checks": checks,
                "explanation_to_student": response.get("explanation", ""),
                "citations": grounding,
                "false_positive_guard": True,
                "false_negative_guard": True
            }
            
            return {"grading": grading}
            
        except Exception as e:
            print(f"Grading error: {e}")
            return self._fallback_grading(question, user_answer, canonical)
    
    def _build_grading_prompt(self, question: str, user_answer: str,
                               canonical_answer: str, concepts_required: List[str],
                               point_breakdown: List[Dict], reference_content: str,
                               rubric: Dict) -> str:
        """Build prompt for AI grading following academic specification.
        
        Returns:
            Grading prompt
        """
        rubric_text = "\n".join([
            f"- {c['criterion']}: {c['points']} points"
            for c in point_breakdown
        ])
        
        concepts_text = "\n".join([f"  • {c}" for c in concepts_required])
        
        return f"""You are an academic-grade reasoning engine. Your role is to grade this student answer with PERFECT fairness.

KNOWLEDGE CONSTRAINTS:
- The ONLY valid reference is the course notes content below
- No external knowledge allowed
- If a concept isn't in the notes, treat it as unknown

QUESTION:
{question}

REFERENCE CONTENT FROM COURSE NOTES:
{reference_content[:1500]}

CANONICAL ANSWER (from notes):
{canonical_answer}

REQUIRED CONCEPTS (must extract from student answer):
{concepts_text}

RUBRIC - Point Breakdown:
{rubric_text}

STUDENT'S ANSWER:
{user_answer}

⚠️ CRITICAL: Check if the student answer is substantive!
- If answer is empty, just punctuation, or < 5 meaningful words: ALL criteria = NOT MET, 0 points
- Single word/symbol answers almost never satisfy rubric criteria
- Be extremely strict with minimal answers

EVALUATION ALGORITHM:

1. CRITERION MATCHING:
   - For EACH criterion in the rubric, verify if student's answer satisfies it
   - Match = answer includes correct definition/explanation OR exact paraphrase from notes
   - Fail = missing, wrong, or contradicts notes

2. CONCEPT COVERAGE:
   - Extract all required concepts from student's answer
   - Award points ONLY for correctly used concepts
   - Missing or wrong concepts = lose corresponding points

3. REASONING VALIDITY:
   - Logical flow must follow what is taught in notes
   - Alternative reasoning from same notes = correct
   - Reasoning not in notes = incorrect

4. SEMANTIC UNDERSTANDING:
   - Parse semantically, not just lexically
   - Accept synonyms and rephrasings IF they match the concept
   - For numbers: tolerance ±1e-6
   - Minor notation differences OK if semantically correct

5. FALSE POSITIVE PREVENTION:
   - Re-check EACH awarded point against grounding evidence
   - If student statement isn't logically supported by notes, REMOVE credit
   - Never award credit for plausible-sounding but ungrounded statements

6. FALSE NEGATIVE PREVENTION:
   - Check if student used different but correct explanation from notes
   - If found in notes (even different section), ADD credit
   - Don't penalize valid alternative approaches from the same notes

7. FINAL SCORING:
   - Sum all awarded points
   - Report each criterion with ✅ (met) or ❌ (not met)

Respond with JSON:
{{
    "points_awarded": <total points as integer>,
    "checks": [
        {{
            "criterion": "<criterion from rubric>",
            "met": true/false,
            "evidence": "<Why met/not met, quote or cite specific part of reference notes>"
        }}
    ],
    "explanation": "<Start with verdict (correct/partially correct/incorrect), then list ✅/❌ for each criterion with brief evidence from notes. End with learning remark.>"
}}"""
    
    def _fallback_grading(self, question: Dict, user_answer: str,
                          canonical: str) -> Dict:
        """Fallback grading when AI fails.
        
        Returns:
            Basic grading result
        """
        # Simple keyword matching
        answer_lower = user_answer.lower()
        canonical_lower = canonical.lower()
        
        # Extract key terms from canonical
        key_terms = [w for w in canonical_lower.split() if len(w) > 4]
        
        # Count matches
        matches = sum(1 for term in key_terms if term in answer_lower)
        ratio = matches / len(key_terms) if key_terms else 0
        
        max_points = 10
        points = int(ratio * max_points)
        
        # Apply specification thresholds: ≥90%, 40-89%, <40%
        if ratio >= 0.9:
            decision = "correct"
        elif ratio >= 0.4:
            decision = "partially_correct"
        else:
            decision = "incorrect"
        
        grading = {
            "question_id": question.get("id"),
            "points_awarded": points,
            "points_possible": max_points,
            "decision": decision,
            "checks": [
                {
                    "criterion": "Answer completeness",
                    "met": ratio >= 0.7,
                    "evidence": f"Matched {matches}/{len(key_terms)} key concepts"
                }
            ],
            "explanation_to_student": f"Basic grading: {points}/{max_points} points. Matched {matches}/{len(key_terms)} key concepts.",
            "citations": question.get("grounding", []),
            "false_positive_guard": False,
            "false_negative_guard": False
        }
        
        return {"grading": grading}
