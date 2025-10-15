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
        
        Args:
            question: Question object
            user_answer: User's answer (e.g., "A,C" or "A, C")
            
        Returns:
            Grading result
        """
        answer_key = question.get("answer_key", {})
        correct = answer_key.get("correct", [])
        max_points = question.get("answer_key", {}).get("max_points", 10)
        
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
        
        # Calculate score
        true_positives = len(user_choices & correct_choices)
        false_positives = len(user_choices - correct_choices)
        false_negatives = len(correct_choices - user_choices)
        
        # Partial credit: (TP - FP) / total_correct, clamped to [0, 1]
        if len(correct_choices) == 0:
            score_ratio = 0
        else:
            score_ratio = max(0, (true_positives - false_positives) / len(correct_choices))
        
        points = int(score_ratio * max_points)
        
        # Decision
        if score_ratio >= 1.0:
            decision = "correct"
        elif score_ratio >= 0.5:
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
                    "criterion": "Selected all correct options",
                    "met": false_negatives == 0,
                    "evidence": f"Correct options: {sorted(correct_choices)}, you selected: {sorted(user_choices)}"
                },
                {
                    "criterion": "No incorrect options selected",
                    "met": false_positives == 0,
                    "evidence": f"False positives: {sorted(user_choices - correct_choices) if false_positives > 0 else 'none'}"
                }
            ],
            "explanation_to_student": (
                f"Score: {points}/{max_points}. "
                f"Correct selections: {true_positives}/{len(correct_choices)}. "
                f"Incorrect selections: {false_positives}. "
                f"Correct answer: {sorted(correct_choices)}"
            ),
            "citations": question.get("grounding", []),
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
            
            # Determine decision
            if points_awarded >= max_points * 0.9:
                decision = "correct"
            elif points_awarded >= max_points * 0.5:
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
        """Build prompt for AI grading.
        
        Returns:
            Grading prompt
        """
        rubric_text = "\n".join([
            f"- {c['criterion']}: {c['points']} points"
            for c in point_breakdown
        ])
        
        concepts_text = ", ".join(concepts_required)
        
        return f"""Grade this student answer with teacher-like rigor.

QUESTION: {question}

REFERENCE CONTENT FROM COURSE NOTES:
{reference_content[:1500]}

CANONICAL ANSWER:
{canonical_answer}

REQUIRED CONCEPTS: {concepts_text}

RUBRIC (point breakdown):
{rubric_text}

STUDENT'S ANSWER:
{user_answer}

GRADING INSTRUCTIONS:
1. Check each rubric criterion against the student's answer
2. Award points ONLY if the criterion is met based on the reference content
3. Accept synonyms and equivalent formulations if semantically identical
4. For math: accept symbolic or numeric equivalence (tolerance ±1e-6)
5. Penalize contradictions or missing core concepts
6. If answer contradicts reference, award 0 points for that criterion
7. Be strict but fair - don't invent requirements not in the rubric

FALSE POSITIVE PREVENTION:
- Does the student's statement appear in or follow logically from the reference? 
- If not, do NOT award credit

FALSE NEGATIVE PREVENTION:
- Did the student use an equivalent formulation present elsewhere in the notes?
- If yes, award credit and cite that location

Respond with JSON:
{{
    "points_awarded": <total points as integer>,
    "checks": [
        {{
            "criterion": "criterion text",
            "met": true/false,
            "evidence": "brief explanation why met/not met, referencing the notes"
        }}
    ],
    "explanation": "1-2 sentence summary for student, with page numbers from reference"
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
        
        if ratio >= 0.7:
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
