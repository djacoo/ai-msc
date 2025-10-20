#!/usr/bin/env python3
"""
Grading Engine
Teacher-grade grading with rubrics and citations
"""

import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from ..utils.enhanced_grounding import EnhancedGroundingEngine


class GradingEngine:
    """Grade student answers with teacher-like rigor and citations."""
    
    def __init__(self, repo_root: str, ai_engine):
        """Initialize grading engine.
        
        Args:
            repo_root: Root directory of repository
            ai_engine: AI engine for grading
        """
        self.grounding = EnhancedGroundingEngine(repo_root)
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
        
        # Get AI grading using STRICT university-level evaluation
        try:
            response = self.ai.generate_json(
                prompt,
                "You are a strict university professor grading an exam. Apply rigorous academic standards - penalize inaccuracies, missing details, and imprecise language. Grade as if this were a formal university examination. Return only valid JSON.",
                temperature=0.15,  # Lower temperature for more consistent grading
                max_tokens=1000
            )
            
            if not response or "error" in response:
                # Fallback grading
                return self._fallback_grading(question, user_answer, canonical)
            
            # Parse new evaluation format
            is_correct = response.get("is_correct", False)
            score = response.get("score", 0.0)  # 0.0 to 1.0
            verdict = response.get("verdict", "incorrect")
            justification = response.get("justification", "")
            expected_summary = response.get("expected_summary", canonical)
            
            # Calculate points with university-level strictness
            max_points = sum(c.get("points", 0) for c in point_breakdown) if point_breakdown else 10
            
            # Apply stricter grading curve for university level
            # Score adjustment: penalize more heavily for incomplete answers
            adjusted_score = self._apply_university_grading_curve(score, verdict)
            points_awarded = int(adjusted_score * max_points)
            
            # FALSE POSITIVE GUARD: Detect minimal/empty answers
            user_answer_clean = user_answer.strip().replace(".", "").replace(",", "").replace("!", "").replace("?", "").strip()
            if len(user_answer_clean) < 5:
                # Answer too short - force fail
                print(f"⚠️ FALSE POSITIVE GUARD: Answer too short ({len(user_answer_clean)} chars), forcing 0 points")
                points_awarded = 0
                score = 0.0
                verdict = "incorrect"
                is_correct = False
                justification = f"Answer is too short/empty to evaluate ({len(user_answer_clean)} meaningful characters). {justification}"
            
            # Map verdict to decision (for backward compatibility)
            verdict_map = {
                "exact": "correct",
                "semantically_correct": "correct",
                "partially_correct": "partially_correct",
                "incorrect": "incorrect"
            }
            decision = verdict_map.get(verdict, "incorrect")
            
            # Build checks array for backward compatibility
            checks = []
            for criterion in point_breakdown:
                criterion_name = criterion.get("criterion", "")
                criterion_points = criterion.get("points", 0)
                # Proportionally assign met status based on score
                met = score >= 0.7  # If score is high, most criteria are met
                checks.append({
                    "criterion": criterion_name,
                    "met": met,
                    "evidence": justification
                })
            
            # Build detailed explanation with university-level feedback
            grade_percentage = (points_awarded / max_points * 100) if max_points > 0 else 0
            grade_letter = self._calculate_letter_grade(grade_percentage)
            
            explanation = f"""Grade: {grade_letter} ({points_awarded}/{max_points} points - {grade_percentage:.1f}%)

Assessment: {verdict.replace('_', ' ').title()}

{justification}

Model Answer:
{expected_summary}

Study Advice: {self._generate_study_advice(verdict, concepts)}"""
            
            grading = {
                "question_id": question.get("id"),
                "points_awarded": points_awarded,
                "points_possible": max_points,
                "decision": decision,
                "checks": checks,
                "explanation_to_student": explanation,
                "citations": grounding,
                "false_positive_guard": True,
                "false_negative_guard": True,
                # Add new format fields
                "is_correct": is_correct,
                "score": score,
                "verdict": verdict,
                "expected_summary": expected_summary
            }
            
            return {"grading": grading}
            
        except Exception as e:
            print(f"Grading error: {e}")
            return self._fallback_grading(question, user_answer, canonical)
    
    def _build_grading_prompt(self, question: str, user_answer: str,
                               canonical_answer: str, concepts_required: List[str],
                               point_breakdown: List[Dict], reference_content: str,
                               rubric: Dict) -> str:
        """Build prompt for AI grading using the new answer evaluation format.
        
        Returns:
            Grading prompt
        """
        # Build context section from reference content
        context_section = f"\nContext (optional, if available):\n{reference_content[:1500]}" if reference_content else ""
        
        return f"""Question:
{question}

Correct Answer:
{canonical_answer}

Student Answer:
{user_answer}{context_section}

Now grade the student's answer according to the schema and principles above.
Return **only JSON**, no commentary or markdown.

Expected JSON Schema:
{{
  "is_correct": boolean,
  "score": number,          // 0.0 to 1.0
  "verdict": "exact" | "semantically_correct" | "partially_correct" | "incorrect",
  "justification": string,  // brief academic feedback for the student
  "expected_summary": string // concise gold-standard answer
}}

UNIVERSITY-LEVEL GRADING PRINCIPLES:
- Apply STRICT academic standards as in a formal university examination
- Penalize heavily for:
  * Missing key concepts or details
  * Imprecise or vague language
  * Incomplete explanations
  * Incorrect terminology
  * Logical inconsistencies
  * Lack of depth in understanding
- Partial credit should be LIMITED:
  * 80-100%: Complete, precise answer with all key points
  * 60-79%: Good understanding but missing some details
  * 40-59%: Basic understanding with significant gaps
  * 0-39%: Poor understanding or major errors
- DO NOT give credit for:
  * Vague generalizations without specifics
  * Correct buzzwords without demonstration of understanding
  * Partial answers that miss core concepts
- Provide constructive but firm feedback that helps students learn
- Grade as if this determines their final course grade"""
    
    def _apply_university_grading_curve(self, base_score: float, verdict: str) -> float:
        """Apply strict university-level grading curve.
        
        Args:
            base_score: Initial score (0.0 to 1.0)
            verdict: Grading verdict
            
        Returns:
            Adjusted score with university-level strictness
        """
        # University grading is stricter - penalize partial understanding more
        curve_adjustments = {
            "exact": 1.0,  # Full marks only for perfect answers
            "semantically_correct": 0.85,  # Slight penalty even for correct meaning
            "partially_correct": 0.5,  # Heavy penalty for partial understanding
            "incorrect": 0.0  # No points for incorrect answers
        }
        
        adjustment = curve_adjustments.get(verdict, 0.5)
        adjusted = base_score * adjustment
        
        # Additional penalties for university level
        if base_score < 0.6 and verdict == "partially_correct":
            # If understanding is below 60%, apply additional penalty
            adjusted *= 0.8
        
        # Round down for strictness (university grading doesn't round up)
        return min(adjusted, 1.0)
    
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
    
    def _calculate_letter_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage using university scale.
        
        Args:
            percentage: Score percentage (0-100)
            
        Returns:
            Letter grade (A-F)
        """
        if percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "A-"
        elif percentage >= 80:
            return "B+"
        elif percentage >= 75:
            return "B"
        elif percentage >= 70:
            return "B-"
        elif percentage >= 65:
            return "C+"
        elif percentage >= 60:
            return "C"
        elif percentage >= 55:
            return "C-"
        elif percentage >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_study_advice(self, verdict: str, concepts: List[str]) -> str:
        """Generate personalized study advice based on performance.
        
        Args:
            verdict: Grading verdict
            concepts: Key concepts tested
            
        Returns:
            Study advice string
        """
        advice_map = {
            "exact": "Excellent work! Continue with this level of precision and detail in your responses.",
            "semantically_correct": "Good understanding! Focus on using more precise technical terminology and providing complete details.",
            "partially_correct": f"Review these key concepts thoroughly: {', '.join(concepts[:3]) if concepts else 'the material'}. Practice explaining them in detail with examples.",
            "incorrect": f"Fundamental review needed. Start with understanding: {', '.join(concepts[:2]) if concepts else 'the basics'}. Read the relevant chapter carefully and practice with simpler examples first."
        }
        
        return advice_map.get(verdict, "Review the material and practice more problems.")
