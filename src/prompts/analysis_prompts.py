"""
Analysis prompts for RFP and document analysis.

Contains prompt templates for the Analysis Agent to perform
comprehensive RFP analysis, requirement extraction, and risk assessment.
"""

from typing import Dict, Any


class AnalysisPrompts:
    """Collection of prompts for document and RFP analysis."""
    
    RFP_ANALYSIS_SYSTEM = """You are an expert RFP analyst with deep experience in government and enterprise procurement processes. Your role is to analyze RFP documents and extract key information that will help create winning proposals.

Key capabilities:
- Identify mandatory vs. optional requirements
- Extract evaluation criteria and scoring weights
- Assess timeline and budget constraints
- Identify potential risks and challenges
- Determine win probability factors

Always provide structured, actionable insights."""

    REQUIREMENT_EXTRACTION = """Analyze the following RFP document and extract all requirements. For each requirement, identify:

1. **Requirement Text**: The exact text of the requirement
2. **Type**: Functional, Technical, or Compliance
3. **Priority**: Mandatory, Important, or Optional
4. **Complexity**: Low, Medium, or High
5. **Dependencies**: Any related requirements

RFP Document:
{document_content}

Format your response as structured JSON with the following schema:
{{
  "requirements": [
    {{
      "id": "REQ-001",
      "text": "requirement description",
      "type": "functional|technical|compliance",
      "priority": "mandatory|important|optional",
      "complexity": "low|medium|high",
      "dependencies": ["REQ-002", "REQ-003"],
      "section": "section where found"
    }}
  ],
  "summary": {{
    "total_requirements": 0,
    "mandatory_count": 0,
    "complexity_breakdown": {{"low": 0, "medium": 0, "high": 0}}
  }}
}}"""

    EVALUATION_CRITERIA_ANALYSIS = """Extract and analyze the evaluation criteria from this RFP document. Focus on:

1. **Scoring Categories**: Technical, Cost, Experience, etc.
2. **Weight Distribution**: Percentage or points for each category
3. **Evaluation Method**: How proposals will be scored
4. **Pass/Fail Criteria**: Minimum requirements that must be met
5. **Tie-Breaking Rules**: How ties will be resolved

RFP Document:
{document_content}

Provide a detailed analysis of how proposals will be evaluated and strategic recommendations for maximizing score."""

    RISK_ASSESSMENT = """Perform a comprehensive risk assessment for this RFP opportunity. Analyze:

**Technical Risks**:
- Complex integration requirements
- Unproven technologies
- Tight technical constraints

**Schedule Risks**:
- Aggressive timelines
- Dependency on external factors
- Milestone complexity

**Commercial Risks**:
- Budget constraints
- Payment terms
- Contract conditions

**Competitive Risks**:
- Incumbent advantages
- Specialized requirements
- Market competition

RFP Document:
{document_content}

For each identified risk, provide:
- Risk description
- Probability (Low/Medium/High)
- Impact (Low/Medium/High)
- Mitigation strategies
- Overall risk rating"""

    COMPLIANCE_CHECK = """Review this proposal content against the RFP requirements and identify any compliance issues:

RFP Requirements:
{rfp_requirements}

Proposal Content:
{proposal_content}

Check for:
1. **Missing Requirements**: Required elements not addressed
2. **Format Violations**: Incorrect formatting or structure
3. **Page Limit Issues**: Content exceeding specified limits
4. **Deadline Compliance**: Submission timing requirements
5. **Technical Specifications**: Meeting all technical criteria

Provide a detailed compliance report with:
- Compliance score (percentage)
- Critical issues that could lead to disqualification
- Recommendations for improvement
- Checklist of items to address"""

    WIN_PROBABILITY_ASSESSMENT = """Assess the win probability for this RFP opportunity based on:

**Opportunity Factors**:
- Market conditions
- Competition level
- Client relationship
- Solution fit

**Our Strengths**:
- Relevant experience
- Technical capabilities
- Team qualifications
- Past performance

**Challenges**:
- Competitive disadvantages
- Resource constraints
- Technical gaps
- Timeline pressures

RFP Document:
{document_content}

Our Capabilities:
{our_capabilities}

Provide:
- Win probability percentage (0-100%)
- Key factors influencing probability
- Strategies to improve win rate
- Go/No-go recommendation with rationale"""

    COMPETITIVE_ANALYSIS = """Analyze the competitive landscape for this RFP:

RFP Document:
{document_content}

Known Competitors:
{competitors_info}

Assess:
1. **Likely Competitors**: Who will probably bid
2. **Competitive Advantages**: What each competitor brings
3. **Our Differentiation**: How we can stand out
4. **Pricing Strategy**: Competitive positioning approach
5. **Win Themes**: Key messages to emphasize

Provide strategic recommendations for positioning our proposal competitively."""

    DOCUMENT_SUMMARY = """Create an executive summary of this RFP document:

{document_content}

Include:
- **Project Overview**: What the client wants to achieve
- **Key Requirements**: Top 5-7 most important requirements
- **Evaluation Approach**: How proposals will be scored
- **Critical Dates**: Key milestones and deadlines
- **Budget Information**: Cost expectations and constraints
- **Success Factors**: What will make a proposal successful

Keep the summary concise but comprehensive, suitable for executive review."""

    @classmethod
    def get_prompt(cls, prompt_type: str, **kwargs) -> str:
        """
        Get a formatted prompt template.
        
        Args:
            prompt_type: Type of prompt to retrieve
            **kwargs: Variables to substitute in the prompt
            
        Returns:
            Formatted prompt string
        """
        prompt_map = {
            'requirement_extraction': cls.REQUIREMENT_EXTRACTION,
            'evaluation_criteria': cls.EVALUATION_CRITERIA_ANALYSIS,
            'risk_assessment': cls.RISK_ASSESSMENT,
            'compliance_check': cls.COMPLIANCE_CHECK,
            'win_probability': cls.WIN_PROBABILITY_ASSESSMENT,
            'competitive_analysis': cls.COMPETITIVE_ANALYSIS,
            'document_summary': cls.DOCUMENT_SUMMARY
        }
        
        prompt_template = prompt_map.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        return prompt_template.format(**kwargs)
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for analysis tasks."""
        return cls.RFP_ANALYSIS_SYSTEM
