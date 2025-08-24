from typing import List, Dict, Any
from collections import Counter
from ...models.core import Feedback

class FeedbackAnalyzer:
    """Analyzes user feedback to generate insights."""

    def analyze_feedback(self, feedback_list: List[Feedback]) -> Dict[str, Any]:
        """
        Analyzes a list of feedback objects and returns a summary.

        Args:
            feedback_list: A list of Feedback objects.

        Returns:
            A dictionary containing feedback analysis.
        """
        if not feedback_list:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "common_keywords": []
            }

        total_feedback = len(feedback_list)
        average_rating = sum(f.rating for f in feedback_list) / total_feedback

        rating_distribution = Counter(f.rating for f in feedback_list)

        # Simple keyword analysis from comments
        all_comments = " ".join(f.comment for f in feedback_list if isinstance(f.comment, str) and f.comment)
        words = all_comments.lower().split() if all_comments else []
        common_keywords = Counter(w for w in words if len(w) > 3).most_common(10)

        return {
            "total_feedback": total_feedback,
            "average_rating": round(average_rating, 2),
            "rating_distribution": dict(rating_distribution),
            "common_keywords": [k for k, v in common_keywords]
        }
