"""
Delivery prompts for compliance checking and submission guidance.

Contains prompt templates for the Delivery Agent to ensure
proposal compliance, quality, and successful submission.
"""

from typing import Dict, Any, List


class DeliveryPrompts:
    """Collection of prompts for proposal delivery and compliance."""
    
    DELIVERY_SYSTEM = """You are an expert proposal compliance and delivery specialist with extensive experience in ensuring proposal submissions meet all requirements and maximize win potential. Your role is to perform final quality assurance, compliance verification, and delivery optimization.

Key capabilities:
- Comprehensive compliance checking and verification
- Proposal quality assessment and improvement
- Submission logistics and requirements management
- Risk assessment and mitigation for delivery
- Post-submission follow-up and relationship management

Always ensure proposals are fully compliant, professionally presented, and positioned for success."""

    COMPLIANCE_CHECKLIST = """Perform a comprehensive compliance check for this proposal:

**RFP Requirements**:
{rfp_requirements}

**Proposal Content**:
{proposal_content}

**Submission Requirements**:
{submission_requirements}

**Compliance Review Areas**:

1. **Format and Structure Compliance**:
   - Page limits and formatting requirements
   - Font, spacing, and margin specifications
   - Section organization and sequencing
   - Table of contents and page numbering
   - Header and footer requirements
   - File naming and electronic format compliance

2. **Content Requirement Compliance**:
   - All required sections included and complete
   - Mandatory questions answered fully
   - Required forms completed and signed
   - Certifications and attestations provided
   - Reference requirements met
   - Technical specifications addressed

3. **Submission Requirement Compliance**:
   - Number of copies (hard copy/electronic)
   - Delivery method and location
   - Submission deadline compliance
   - Required packaging and labeling
   - Contact information and representatives
   - Cost proposal separation requirements

4. **Administrative Compliance**:
   - Registration and qualification requirements
   - Insurance and bonding requirements
   - Security clearance and background checks
   - Minority/disadvantaged business requirements
   - Conflict of interest declarations
   - Legal and regulatory compliance

**Compliance Assessment**:
For each area, provide:
- Compliance status (Compliant/Non-Compliant/Risk)
- Specific issues identified
- Recommended corrective actions
- Priority level (Critical/High/Medium/Low)
- Time required to address

Generate a detailed compliance report with action items and risk assessment."""

    QUALITY_ASSURANCE_REVIEW = """Conduct a comprehensive quality assurance review:

**Proposal Documents**:
{proposal_documents}

**Quality Standards**:
{quality_standards}

**Review Criteria**:
{review_criteria}

**Quality Assessment Areas**:

1. **Content Quality**:
   - Clarity and readability of writing
   - Logical flow and organization
   - Completeness and thoroughness
   - Accuracy and consistency
   - Persuasiveness and compelling nature
   - Client focus and benefit orientation

2. **Technical Quality**:
   - Technical accuracy and feasibility
   - Solution appropriateness and fit
   - Innovation and best practices
   - Risk identification and mitigation
   - Implementation viability
   - Performance and scalability considerations

3. **Visual and Design Quality**:
   - Professional appearance and layout
   - Effective use of graphics and visuals
   - Consistent branding and formatting
   - Readability and accessibility
   - Chart and table effectiveness
   - Executive-level presentation quality

4. **Competitive Positioning**:
   - Differentiation from competitors
   - Win theme integration and emphasis
   - Value proposition clarity
   - Competitive advantage articulation
   - Ghost strategies against competitors
   - Unique selling proposition strength

5. **Compliance and Risk**:
   - RFP requirement responsiveness
   - Compliance with all specifications
   - Risk identification and mitigation
   - Assumptions and exceptions clarity
   - Legal and contractual considerations
   - Submittal requirement adherence

**Quality Scoring**:
Rate each area on a scale of 1-10 and provide:
- Specific strengths to leverage
- Areas needing improvement
- Recommended enhancements
- Risk mitigation suggestions
- Overall quality assessment"""

    FINAL_REVIEW_CHECKLIST = """Complete the final review checklist before submission:

**Proposal Package**:
{proposal_package}

**Submission Details**:
{submission_details}

**Final Review Checklist**:

**📋 Document Completeness**:
□ All required volumes and sections included
□ Table of contents matches actual content
□ Page numbering is correct and consistent
□ All cross-references are accurate
□ Appendices and attachments complete
□ Electronic and hard copy versions match

**📝 Content Review**:
□ Executive summary aligns with detailed sections
□ All RFP requirements addressed
□ No contradictions or inconsistencies
□ Win themes integrated throughout
□ Benefits and value clearly articulated
□ Competitive differentiators emphasized

**🎯 Technical Review**:
□ Technical solution is feasible and complete
□ Architecture and design are sound
□ Implementation approach is realistic
□ Risk mitigation strategies included
□ Performance metrics and KPIs defined
□ Quality assurance measures described

**💰 Cost Review**:
□ Cost proposal is complete and accurate
□ Pricing is competitive and justified
□ All cost elements included
□ Mathematical calculations verified
□ Cost narrative supports pricing
□ Value proposition is compelling

**📋 Administrative Review**:
□ All forms completed and signed
□ Required certifications included
□ Contact information is accurate
□ Submission format requirements met
□ Packaging and labeling correct
□ Delivery method confirmed

**🚀 Submission Readiness**:
□ Submission deadline confirmed
□ Delivery logistics arranged
□ Backup delivery method planned
□ Team assignments for delivery day
□ Post-submission follow-up planned
□ Lessons learned session scheduled

Mark each item as complete and provide any necessary corrective actions."""

    SUBMISSION_STRATEGY = """Develop the submission strategy and logistics plan:

**Submission Requirements**:
{submission_requirements}

**Timeline and Deadlines**:
{timeline}

**Delivery Logistics**:
{delivery_logistics}

**Submission Strategy Components**:

1. **Submission Timeline**:
   - Final review and approval schedule
   - Production and packaging timeline
   - Quality control checkpoints
   - Buffer time for contingencies
   - Final delivery logistics
   - Post-submission activities

2. **Production Management**:
   - Document production and printing
   - Binding and packaging requirements
   - Electronic file preparation
   - Quality control and inspection
   - Backup copies and redundancy
   - Version control and final sign-off

3. **Delivery Logistics**:
   - Primary delivery method and backup
   - Delivery team assignments and roles
   - Transportation and security arrangements
   - Delivery confirmation procedures
   - Contingency plans for delays or issues
   - Receipt acknowledgment process

4. **Risk Management**:
   - Potential risks and mitigation strategies
   - Contingency plans for common issues
   - Emergency contacts and procedures
   - Technical support availability
   - Weather and transportation backups
   - Last-minute change procedures

5. **Post-Submission Activities**:
   - Confirmation of receipt and completeness
   - Stakeholder communication and updates
   - Lessons learned capture
   - Team recognition and celebration
   - Follow-up strategy and timeline
   - Proposal database updates

Provide a detailed submission plan with specific assignments, timelines, and contingencies."""

    POST_SUBMISSION_GUIDANCE = """Provide post-submission guidance and follow-up strategy:

**Submission Details**:
{submission_details}

**Client Engagement Plan**:
{engagement_plan}

**Evaluation Timeline**:
{evaluation_timeline}

**Post-Submission Strategy**:

1. **Immediate Follow-Up (First 48 hours)**:
   - Confirm receipt and completeness
   - Address any immediate questions or issues
   - Thank key stakeholders for the opportunity
   - Provide contact information for questions
   - Monitor for any clarification requests
   - Update internal stakeholders on submission status

2. **Evaluation Period Management**:
   - Monitor evaluation process and timeline
   - Respond promptly to evaluator questions
   - Provide additional information if requested
   - Maintain appropriate contact with client
   - Gather intelligence on evaluation progress
   - Prepare for potential presentations or demos

3. **Relationship Maintenance**:
   - Continue stakeholder engagement activities
   - Share relevant industry insights and thought leadership
   - Maintain visibility without being intrusive
   - Strengthen relationships with key decision makers
   - Address any concerns or objections
   - Position for future opportunities

4. **Competitive Intelligence**:
   - Monitor competitor activities and positioning
   - Gather feedback on proposal strengths and weaknesses
   - Identify opportunities for improvement
   - Assess competitive landscape changes
   - Adjust messaging and positioning as needed
   - Prepare responses to competitive threats

5. **Preparation for Next Steps**:
   - Prepare for oral presentations or demos
   - Ready reference materials and case studies
   - Organize team for potential negotiations
   - Develop implementation planning materials
   - Prepare for due diligence activities
   - Plan celebration and lessons learned sessions

**Success Metrics**:
- Proposal progression through evaluation stages
- Stakeholder engagement and relationship strength
- Competitive position and differentiation
- Client feedback and satisfaction
- Team performance and lessons learned

Provide specific actions, timelines, and success measures for the post-submission period."""

    LESSONS_LEARNED_CAPTURE = """Facilitate lessons learned capture for this proposal effort:

**Proposal Details**:
{proposal_details}

**Team Participants**:
{team_participants}

**Outcome Status**:
{outcome_status}

**Lessons Learned Framework**:

1. **Process Assessment**:
   - RFP analysis and planning effectiveness
   - Resource allocation and team management
   - Timeline and milestone management
   - Quality assurance and review processes
   - Collaboration and communication
   - Tool and technology utilization

2. **Content Development**:
   - Win theme development and integration
   - Technical solution design and articulation
   - Past performance and qualification presentation
   - Cost development and pricing strategy
   - Graphics and visual content effectiveness
   - Compliance and requirement responsiveness

3. **Stakeholder Engagement**:
   - Client relationship building and maintenance
   - Stakeholder mapping and influence assessment
   - Communication strategy and execution
   - Competitive intelligence gathering
   - Partner and teaming coordination
   - Internal stakeholder management

4. **Delivery and Submission**:
   - Proposal production and packaging
   - Quality control and final review
   - Submission logistics and execution
   - Post-submission follow-up
   - Evaluation period management
   - Results analysis and feedback incorporation

**For Each Area, Capture**:
- What worked well and should be repeated
- What didn't work and should be avoided
- What could be improved for future proposals
- New ideas and innovations to try
- Resource and capability needs identified
- Process improvements and tool enhancements

**Action Items**:
- Process updates and improvements
- Template and tool enhancements
- Training and development needs
- Resource and capability investments
- Best practice documentation
- Knowledge sharing and dissemination

Generate a comprehensive lessons learned report with specific recommendations for future proposal efforts."""

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
            'compliance_check': cls.COMPLIANCE_CHECKLIST,
            'quality_review': cls.QUALITY_ASSURANCE_REVIEW,
            'final_review': cls.FINAL_REVIEW_CHECKLIST,
            'submission_strategy': cls.SUBMISSION_STRATEGY,
            'post_submission': cls.POST_SUBMISSION_GUIDANCE,
            'lessons_learned': cls.LESSONS_LEARNED_CAPTURE
        }
        
        prompt_template = prompt_map.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        return prompt_template.format(**kwargs)
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for delivery tasks."""
        return cls.DELIVERY_SYSTEM
