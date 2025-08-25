"""
Approval System Module

This module provides functionality for human-in-the-loop approval processes.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
class QualityChecker:
    """Basic quality checker for content validation."""
    
    def __init__(self):
        self.min_quality_score = 0.7
        self.review_threshold = 0.5
    
    def check_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Check content quality and return results."""
        quality_score = self._calculate_quality_score(content, content_type)
        suggestions = self._generate_suggestions(content, quality_score)
        
        return {
            "quality_score": quality_score,
            "suggestions": suggestions,
            "content_type": content_type,
            "content_length": len(content)
        }
    
    def requires_human_review(self, quality_results: Dict[str, Any]) -> bool:
        """Determine if content requires human review."""
        return quality_results["quality_score"] < self.review_threshold
    
    def _calculate_quality_score(self, content: str, content_type: str) -> float:
        """Calculate basic quality score based on content characteristics."""
        if not content or len(content.strip()) < 10:
            return 0.1
        
        score = 0.5  # Base score
        
        # Length check
        if len(content) > 100:
            score += 0.2
        
        # Basic completeness check
        if content_type == "rfp_response" and any(keyword in content.lower() 
                                                for keyword in ["proposal", "solution", "approach"]):
            score += 0.2
        
        # Grammar/structure check (basic)
        sentences = content.split('.')
        if len(sentences) > 3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_suggestions(self, content: str, quality_score: float) -> List[str]:
        """Generate improvement suggestions based on quality score."""
        suggestions = []
        
        if quality_score < 0.3:
            suggestions.append("Content appears incomplete or too short")
        
        if quality_score < 0.5:
            suggestions.append("Consider adding more detail and structure")
        
        if len(content) < 50:
            suggestions.append("Content may be too brief for effective communication")
        
        return suggestions

class ApprovalSystem:
    def __init__(self):
        """Initialize the approval system."""
        self.pending_approvals = {}
        self.approval_history = []
        self.quality_checker = QualityChecker()
    
    def submit_for_approval(self, content: str, content_type: str, metadata: Dict[str, Any] = None) -> str:
        """
        Submit content for human approval.
        
        Args:
            content (str): Content to be reviewed
            content_type (str): Type of content (e.g., 'rfp_response', 'proposal', 'questionnaire')
            metadata (dict): Additional metadata about the content
            
        Returns:
            str: Approval task ID
        """
        task_id = str(uuid.uuid4())
        
        # Perform automated quality check
        quality_results = self.quality_checker.check_content(content, content_type)
        
        # Determine if human review is required
        requires_review = self.quality_checker.requires_human_review(quality_results)
        
        approval_task = {
            "task_id": task_id,
            "content": content,
            "content_type": content_type,
            "metadata": metadata or {},
            "quality_results": quality_results,
            "requires_review": requires_review,
            "submitted_at": datetime.now().isoformat(),
            "status": "pending_review" if requires_review else "auto_approved",
            "reviewer": None,
            "reviewed_at": None,
            "feedback": None,
            "approved": not requires_review  # Auto-approve if quality is high enough
        }
        
        if requires_review:
            self.pending_approvals[task_id] = approval_task
            print(f"Task {task_id} submitted for human review (Quality Score: {quality_results['quality_score']:.1f})")
        else:
            # Auto-approve high-quality content
            approval_task["approved"] = True
            approval_task["status"] = "auto_approved"
            approval_task["reviewed_at"] = datetime.now().isoformat()
            self.approval_history.append(approval_task)
            print(f"Task {task_id} auto-approved (Quality Score: {quality_results['quality_score']:.1f})")
        
        return task_id
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval tasks."""
        return list(self.pending_approvals.values())
    
    def get_approval_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific approval task."""
        if task_id in self.pending_approvals:
            return self.pending_approvals[task_id]
        
        # Check approval history
        for task in self.approval_history:
            if task["task_id"] == task_id:
                return task
        
        return None
    
    def process_approval(self, task_id: str, approved: bool, reviewer: str, feedback: str = None) -> bool:
        """
        Process a human approval decision.
        
        Args:
            task_id (str): ID of the task being reviewed
            approved (bool): Whether the content is approved
            reviewer (str): Name/ID of the reviewer
            feedback (str): Optional feedback from the reviewer
            
        Returns:
            bool: True if approval was processed successfully
        """
        if task_id not in self.pending_approvals:
            print(f"Task {task_id} not found in pending approvals")
            return False
        
        task = self.pending_approvals[task_id]
        task["approved"] = approved
        task["reviewer"] = reviewer
        task["reviewed_at"] = datetime.now().isoformat()
        task["feedback"] = feedback
        task["status"] = "approved" if approved else "rejected"
        
        # Move to history
        self.approval_history.append(task)
        del self.pending_approvals[task_id]
        
        print(f"Task {task_id} {'approved' if approved else 'rejected'} by {reviewer}")
        if feedback:
            print(f"Feedback: {feedback}")
        
        return True
    
    def get_approval_summary(self) -> Dict[str, Any]:
        """Get a summary of approval statistics."""
        total_tasks = len(self.approval_history) + len(self.pending_approvals)
        approved_tasks = len([t for t in self.approval_history if t["approved"]])
        rejected_tasks = len([t for t in self.approval_history if not t["approved"]])
        pending_tasks = len(self.pending_approvals)
        auto_approved_tasks = len([t for t in self.approval_history if t["status"] == "auto_approved"])
        
        return {
            "total_tasks": total_tasks,
            "approved_tasks": approved_tasks,
            "rejected_tasks": rejected_tasks,
            "pending_tasks": pending_tasks,
            "auto_approved_tasks": auto_approved_tasks,
            "approval_rate": (approved_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def flag_for_review(self, content: str, reason: str, priority: str = "normal") -> str:
        """
        Flag content for human review with a specific reason.
        
        Args:
            content (str): Content to flag
            reason (str): Reason for flagging
            priority (str): Priority level ('low', 'normal', 'high', 'urgent')
            
        Returns:
            str: Task ID for the flagged content
        """
        metadata = {
            "flag_reason": reason,
            "priority": priority,
            "flagged_by": "system"
        }
        
        return self.submit_for_approval(content, "flagged_content", metadata)
    
    def get_high_priority_tasks(self) -> List[Dict[str, Any]]:
        """Get pending approval tasks with high or urgent priority."""
        high_priority_tasks = []
        for task in self.pending_approvals.values():
            priority = task.get("metadata", {}).get("priority", "normal")
            if priority in ["high", "urgent"]:
                high_priority_tasks.append(task)
        
        # Sort by priority (urgent first, then high)
        high_priority_tasks.sort(key=lambda x: 0 if x["metadata"]["priority"] == "urgent" else 1)
        return high_priority_tasks
