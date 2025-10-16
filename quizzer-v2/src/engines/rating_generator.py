#!/usr/bin/env python3
"""
Rating Generator
Generates AI-powered player ratings and descriptions
"""

from typing import Dict


class RatingGenerator:
    """Generate player ratings using AI based on stats."""
    
    def __init__(self, ai_engine):
        """Initialize rating generator.
        
        Args:
            ai_engine: AI engine for generating descriptions
        """
        self.ai = ai_engine
    
    def generate_rating(self, stats: Dict) -> Dict:
        """Generate a rating and description for a player.
        
        Args:
            stats: User statistics dictionary
            
        Returns:
            Dictionary with rating, title, description, and emoji
        """
        # Calculate rating tier
        tier = self._calculate_tier(stats)
        
        # Generate AI description
        description = self._generate_ai_description(stats, tier)
        
        return {
            'tier': tier['name'],
            'title': tier['title'],
            'emoji': tier['emoji'],
            'description': description,
            'stats_summary': self._format_stats_summary(stats)
        }
    
    def _calculate_tier(self, stats: Dict) -> Dict:
        """Calculate player tier based on stats.
        
        Args:
            stats: User statistics
            
        Returns:
            Tier dictionary
        """
        accuracy = stats.get('accuracy', 0)
        total_stars = stats.get('total_stars', 0)
        total_quizzes = stats.get('total_quizzes', 0)
        
        # Calculate overall score
        score = (accuracy * 0.5) + (min(total_stars, 100) * 0.3) + (min(total_quizzes, 50) * 0.2)
        
        # Tier system
        if score >= 80:
            return {
                'name': 'Master Scholar',
                'title': '🏆 Master Scholar',
                'emoji': '🏆',
                'level': 5
            }
        elif score >= 60:
            return {
                'name': 'Expert Learner',
                'title': '⭐ Expert Learner',
                'emoji': '⭐',
                'level': 4
            }
        elif score >= 40:
            return {
                'name': 'Proficient Student',
                'title': '📚 Proficient Student',
                'emoji': '📚',
                'level': 3
            }
        elif score >= 20:
            return {
                'name': 'Emerging Scholar',
                'title': '🌱 Emerging Scholar',
                'emoji': '🌱',
                'level': 2
            }
        else:
            return {
                'name': 'Beginner',
                'title': '🎓 Beginner',
                'emoji': '🎓',
                'level': 1
            }
    
    def _generate_ai_description(self, stats: Dict, tier: Dict) -> str:
        """Generate AI description of player performance.
        
        Args:
            stats: User statistics
            tier: Player tier information
            
        Returns:
            AI-generated description
        """
        # Build prompt for AI
        prompt = f"""Based on these quiz performance stats, write a SHORT 2-sentence motivational description of the player:

Stats:
- Quizzes completed: {stats.get('total_quizzes', 0)}
- Questions answered: {stats.get('total_questions', 0)}
- Accuracy: {stats.get('accuracy', 0):.1f}%
- Stars earned: {stats.get('total_stars', 0)}
- Average score: {stats.get('average_score', 0):.1f}%
- Tier: {tier['name']}

Write 2 sentences that are encouraging and highlight their strengths. Be specific about their performance."""
        
        try:
            response = self.ai.generate(
                prompt,
                "You are an encouraging academic coach. Write brief, motivational descriptions.",
                temperature=0.7,
                max_tokens=100
            )
            
            if response:
                # Clean up response
                description = response.strip()
                # Ensure it's not too long
                sentences = description.split('.')[:2]
                return '. '.join(s.strip() for s in sentences if s.strip()) + '.'
            else:
                # Fallback description
                return self._fallback_description(stats, tier)
                
        except Exception as e:
            print(f"AI description generation failed: {e}")
            return self._fallback_description(stats, tier)
    
    def _fallback_description(self, stats: Dict, tier: Dict) -> str:
        """Generate fallback description without AI.
        
        Args:
            stats: User statistics
            tier: Player tier information
            
        Returns:
            Description string
        """
        accuracy = stats.get('accuracy', 0)
        total_quizzes = stats.get('total_quizzes', 0)
        total_stars = stats.get('total_stars', 0)
        
        if accuracy >= 80:
            performance = "exceptional accuracy"
        elif accuracy >= 60:
            performance = "strong performance"
        elif accuracy >= 40:
            performance = "solid progress"
        else:
            performance = "steady improvement"
        
        return f"You've completed {total_quizzes} quizzes with {performance}. Keep up the great work and continue earning stars!"
    
    def _format_stats_summary(self, stats: Dict) -> str:
        """Format a brief stats summary.
        
        Args:
            stats: User statistics
            
        Returns:
            Formatted summary string
        """
        return f"{stats.get('total_quizzes', 0)} quizzes | {stats.get('accuracy', 0):.0f}% accuracy | {stats.get('total_stars', 0)} ⭐"


def main():
    """Test rating generator."""
    from local_ai import LocalAI
    
    print("🧪 Testing Rating Generator\n")
    
    ai = LocalAI("llama3.2:3b")
    generator = RatingGenerator(ai)
    
    # Test with sample stats
    test_stats = {
        'username': 'TestUser',
        'total_quizzes': 25,
        'total_questions': 150,
        'correct_answers': 120,
        'incorrect_answers': 30,
        'accuracy': 80.0,
        'total_stars': 45,
        'average_score': 78.5,
        'favorite_course': 'ml-dl'
    }
    
    print("Testing with high-performing user...")
    rating = generator.generate_rating(test_stats)
    
    print(f"\nTier: {rating['tier']}")
    print(f"Title: {rating['title']}")
    print(f"Description: {rating['description']}")
    print(f"Summary: {rating['stats_summary']}")
    
    print("\n✅ Rating generator tests complete!")


if __name__ == "__main__":
    main()
