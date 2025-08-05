"""
Proposal writing prompts for content generation and optimization.

Contains prompt templates for the Proposal Agent to generate
high-quality proposal content, sections, and responses.
"""

from typing import Dict, Any, List


class ProposalPrompts:
    """Collection of prompts for proposal writing and content generation."""
    
    PROPOSAL_SYSTEM = """You are an expert proposal writer with extensive experience in government and enterprise procurement. You excel at creating compelling, compliant, and winning proposal content that resonates with evaluators and decision-makers.

Key capabilities:
- Strategic proposal positioning and win themes
- Compliant and responsive content development
- Technical solution articulation
- Benefit-focused value propositions
- Executive summary and narrative development
- Graphics and visual content guidance

Always ensure content is client-focused, benefit-oriented, and differentiates our solution from competitors."""

    EXECUTIVE_SUMMARY = """Write a compelling executive summary for this proposal:

**RFP Requirements**:
{rfp_requirements}

**Our Solution Overview**:
{solution_overview}

**Key Differentiators**:
{differentiators}

**Client Profile**:
{client_profile}

**Win Themes**:
{win_themes}

**Executive Summary Guidelines**:

1. **Opening Hook**: Start with a powerful statement that resonates with the client's key challenge or opportunity

2. **Understanding**: Demonstrate deep understanding of the client's needs, situation, and desired outcomes

3. **Solution Overview**: Present our solution approach in clear, benefit-focused terms

4. **Key Benefits**: Highlight the top 3-5 benefits the client will realize

5. **Differentiators**: Articulate what makes us uniquely qualified and different from competitors

6. **Confidence Statement**: Close with a confident commitment to success

**Requirements**:
- Length: 1-2 pages maximum
- Tone: Professional, confident, client-focused
- Structure: Clear sections with compelling subheadings
- Style: Active voice, benefit-oriented language
- Compliance: Address all key RFP requirements

Write an executive summary that will compel evaluators to score our proposal highly."""

    TECHNICAL_APPROACH = """Develop the technical approach section for this proposal:

**Technical Requirements**:
{technical_requirements}

**Our Technical Solution**:
{technical_solution}

**Architecture Overview**:
{architecture_overview}

**Technology Stack**:
{technology_stack}

**Implementation Methodology**:
{methodology}

**Technical Approach Structure**:

1. **Solution Architecture**:
   - High-level architecture overview
   - Key components and their relationships
   - Technology choices and rationale
   - Scalability and performance considerations
   - Security and compliance measures

2. **Implementation Methodology**:
   - Development approach and methodology
   - Project phases and key milestones
   - Quality assurance and testing strategy
   - Risk mitigation and contingency planning
   - Change management and deployment approach

3. **Technical Innovation**:
   - Innovative aspects of our solution
   - Technology advantages and benefits
   - Future-proofing and evolution path
   - Best practices and lessons learned
   - Industry benchmarks and standards compliance

4. **Integration Strategy**:
   - Existing system integration approach
   - Data migration and synchronization
   - API and interface specifications
   - Testing and validation procedures
   - Cutover and rollback planning

Write a technical approach that demonstrates deep expertise while remaining accessible to non-technical evaluators."""

    MANAGEMENT_APPROACH = """Create the management approach section:

**Project Requirements**:
{project_requirements}

**Timeline and Milestones**:
{timeline}

**Our Project Management Approach**:
{pm_approach}

**Team Structure**:
{team_structure}

**Risk Management Strategy**:
{risk_strategy}

**Management Approach Elements**:

1. **Project Management Framework**:
   - Methodology and standards (Agile, Waterfall, hybrid)
   - Governance structure and decision rights
   - Communication and reporting protocols
   - Quality management and assurance
   - Change control and scope management

2. **Organization and Staffing**:
   - Project team structure and roles
   - Key personnel qualifications and experience
   - Staffing plan and resource allocation
   - Succession planning and backup resources
   - Team motivation and retention strategies

3. **Schedule and Milestone Management**:
   - Detailed project schedule and work breakdown
   - Critical path analysis and dependencies
   - Milestone tracking and reporting
   - Schedule risk assessment and mitigation
   - Acceleration and recovery strategies

4. **Risk and Issue Management**:
   - Risk identification and assessment process
   - Risk mitigation and contingency planning
   - Issue escalation and resolution procedures
   - Performance monitoring and corrective actions
   - Lessons learned and continuous improvement

Emphasize our proven track record and ability to deliver on time and within budget."""

    PAST_PERFORMANCE = """Write the past performance section showcasing relevant experience:

**RFP Requirements for Experience**:
{experience_requirements}

**Our Relevant Projects**:
{relevant_projects}

**Key Personnel Experience**:
{personnel_experience}

**Success Metrics**:
{success_metrics}

**Past Performance Structure**:

1. **Relevant Experience Overview**:
   - Summary of relevant experience and expertise
   - Industry knowledge and domain expertise
   - Geographic coverage and local presence
   - Technology platform experience
   - Similar project scope and complexity

2. **Key Project Examples**:
   For each relevant project, include:
   - Client organization and project context
   - Project scope, timeline, and budget
   - Our role and responsibilities
   - Challenges overcome and solutions delivered
   - Results achieved and client benefits
   - Lessons learned and best practices
   - Client references and testimonials

3. **Personnel Qualifications**:
   - Key team member backgrounds and expertise
   - Relevant certifications and credentials
   - Project leadership experience
   - Technical skills and specializations
   - Client relationship and communication skills

4. **Performance Metrics**:
   - On-time delivery record
   - Budget performance and cost control
   - Quality metrics and client satisfaction
   - Award recognition and industry accolades
   - Long-term client relationships

Focus on projects most similar to the current opportunity and quantify results wherever possible."""

    COST_PROPOSAL_NARRATIVE = """Develop the cost proposal narrative and justification:

**Cost Requirements**:
{cost_requirements}

**Our Pricing Structure**:
{pricing_structure}

**Value Justification**:
{value_justification}

**Competitive Positioning**:
{competitive_context}

**Cost Narrative Elements**:

1. **Pricing Philosophy**:
   - Value-based pricing approach
   - Competitive positioning strategy
   - Cost transparency and breakdown
   - Risk sharing and incentive alignment
   - Long-term partnership commitment

2. **Cost Breakdown and Justification**:
   - Labor costs and resource allocation
   - Technology and infrastructure costs
   - Third-party and subcontractor costs
   - Travel and other direct costs
   - Overhead and administrative costs
   - Contingency and risk provisions

3. **Value Proposition**:
   - Total cost of ownership analysis
   - Return on investment calculations
   - Cost savings and efficiency gains
   - Risk reduction and mitigation value
   - Intangible benefits and strategic value

4. **Cost Management**:
   - Budget management and controls
   - Change order and scope management
   - Cost reporting and transparency
   - Performance incentives and penalties
   - Cost optimization opportunities

Present pricing as an investment in value and outcomes, not just a cost."""

    RESPONSE_TO_REQUIREMENTS = """Generate responses to specific RFP requirements:

**Requirement Section**: {requirement_section}
**Specific Requirements**:
{requirements_list}

**Our Capabilities**:
{our_capabilities}

**Solution Details**:
{solution_details}

**Response Guidelines**:

1. **Requirement Understanding**:
   - Restate the requirement in our own words
   - Demonstrate understanding of the underlying need
   - Acknowledge any assumptions or clarifications needed

2. **Our Approach**:
   - Describe how we will meet or exceed the requirement
   - Explain our methodology and process
   - Highlight relevant experience and expertise
   - Address any potential challenges or risks

3. **Benefits and Value**:
   - Articulate the benefits the client will receive
   - Quantify value where possible
   - Connect to broader business objectives
   - Differentiate from competitors

4. **Compliance Confirmation**:
   - Explicitly confirm compliance with the requirement
   - Reference supporting documentation or evidence
   - Address any exceptions or alternatives
   - Provide implementation timeline

For each requirement, provide a comprehensive, compliant, and compelling response."""

    WIN_THEME_DEVELOPMENT = """Develop compelling win themes for this proposal:

**Client Analysis**:
{client_analysis}

**Competitive Assessment**:
{competitive_assessment}

**Our Strengths**:
{our_strengths}

**Opportunity Context**:
{opportunity_context}

**Win Theme Framework**:

1. **Primary Win Themes** (3-5 main themes):
   Each theme should include:
   - Theme statement (what we want evaluators to believe)
   - Proof points (evidence that supports the theme)
   - Benefits (how this helps the client)
   - Discriminators (why we're better than competitors)

2. **Theme Integration Strategy**:
   - How themes will be woven throughout the proposal
   - Section-specific theme emphasis
   - Visual and graphic support
   - Executive summary positioning
   - Presentation and orals messaging

3. **Competitive Positioning**:
   - How themes counter competitor strengths
   - Messages that highlight competitor weaknesses
   - Unique positioning that differentiates us
   - Value propositions competitors can't match

4. **Theme Validation**:
   - Client hot buttons and evaluation criteria alignment
   - Stakeholder resonance and appeal
   - Evidence strength and credibility
   - Competitive vulnerability assessment

Develop win themes that are believable, defensible, and compelling to the target audience."""

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
            'executive_summary': cls.EXECUTIVE_SUMMARY,
            'technical_approach': cls.TECHNICAL_APPROACH,
            'management_approach': cls.MANAGEMENT_APPROACH,
            'past_performance': cls.PAST_PERFORMANCE,
            'cost_narrative': cls.COST_PROPOSAL_NARRATIVE,
            'requirement_response': cls.RESPONSE_TO_REQUIREMENTS,
            'win_themes': cls.WIN_THEME_DEVELOPMENT
        }
        
        prompt_template = prompt_map.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        return prompt_template.format(**kwargs)
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for proposal writing tasks."""
        return cls.PROPOSAL_SYSTEM
