"""
Client assessment prompts for client profiling and capability evaluation.

Contains prompt templates for the Client Agent to perform
client analysis, needs assessment, and capability matching.
"""

from typing import Dict, Any, List


class ClientPrompts:
    """Collection of prompts for client assessment and profiling."""
    
    CLIENT_SYSTEM = """You are an expert client relationship manager and business analyst with deep experience in understanding client needs, organizational dynamics, and capability requirements. Your role is to analyze client organizations and assess the fit between their needs and our capabilities.

Key capabilities:
- Client organizational analysis
- Stakeholder mapping and influence assessment
- Needs analysis and requirement prioritization
- Capability gap analysis
- Relationship strategy development

Always provide insights that enable better client engagement and solution positioning."""

    CLIENT_PROFILE_ANALYSIS = """Create a comprehensive client profile for:

**Client Organization**: {client_name}
**Industry**: {industry}
**Size**: {organization_size}
**Geography**: {location}

**Available Information**:
{client_information}

Profile Analysis Areas:

1. **Organizational Overview**:
   - Mission, vision, and core values
   - Business model and revenue streams
   - Strategic priorities and initiatives
   - Recent performance and trajectory
   - Competitive position and challenges

2. **Leadership & Culture**:
   - Executive leadership team and backgrounds
   - Organizational culture and values
   - Decision-making style and processes
   - Risk tolerance and innovation appetite
   - Communication preferences

3. **Operational Context**:
   - Current operational challenges
   - Technology infrastructure and maturity
   - Process efficiency and automation levels
   - Resource constraints and capabilities
   - Performance metrics and KPIs

4. **Strategic Drivers**:
   - Growth objectives and expansion plans
   - Digital transformation initiatives
   - Regulatory and compliance requirements
   - Cost optimization pressures
   - Competitive response strategies

5. **Procurement Characteristics**:
   - Typical procurement processes
   - Evaluation criteria and priorities
   - Contract preferences and terms
   - Vendor relationship approach
   - Budget cycles and approval processes

Synthesize this into a client profile that informs our engagement and solution approach."""

    STAKEHOLDER_MAPPING = """Map the key stakeholders for this opportunity:

**Client Organization**: {client_name}
**Opportunity**: {opportunity_description}
**Known Contacts**: {known_contacts}

Stakeholder Analysis:

1. **Decision Makers**:
   - Ultimate decision authority
   - Budget approval responsibility
   - Strategic alignment influence
   - Risk and compliance oversight

2. **Influencers**:
   - Technical advisors and SMEs
   - User community representatives
   - Internal champions and advocates
   - External advisors and consultants

3. **Evaluators**:
   - Proposal evaluation committee
   - Technical review teams
   - Reference check contacts
   - Due diligence specialists

4. **End Users**:
   - Primary system/service users
   - Operational staff and managers
   - Support and maintenance teams
   - Training and adoption leaders

For each stakeholder category, identify:
- Key individuals and their roles
- Influence level and decision authority
- Primary concerns and success criteria
- Communication preferences and channels
- Relationship status and engagement strategy

Provide a stakeholder engagement plan with prioritized outreach recommendations."""

    NEEDS_ASSESSMENT = """Conduct a comprehensive needs assessment:

**Client Context**:
- Organization: {client_name}
- Current situation: {current_state}
- Desired outcomes: {desired_outcomes}
- Constraints: {constraints}

**Assessment Framework**:

1. **Business Needs**:
   - Strategic objectives alignment
   - Operational efficiency requirements
   - Growth and scalability needs
   - Cost optimization goals
   - Risk mitigation priorities

2. **Functional Requirements**:
   - Core functionality needs
   - Integration requirements
   - Performance and capacity needs
   - User experience expectations
   - Workflow and process support

3. **Technical Requirements**:
   - Technology platform preferences
   - Architecture and infrastructure needs
   - Security and compliance requirements
   - Data management and analytics needs
   - Mobile and accessibility requirements

4. **Organizational Requirements**:
   - Change management needs
   - Training and support requirements
   - Governance and control needs
   - Resource allocation considerations
   - Timeline and implementation constraints

5. **Success Criteria**:
   - Key performance indicators
   - Success metrics and targets
   - Value realization expectations
   - Return on investment requirements
   - Risk tolerance and mitigation needs

Prioritize needs by importance and urgency, and identify potential gaps or conflicts."""

    CAPABILITY_MATCHING = """Assess the match between client needs and our capabilities:

**Client Needs**:
{client_needs}

**Our Capabilities**:
{our_capabilities}

**Competitive Context**:
{competitive_landscape}

**Matching Analysis**:

1. **Strong Fit Areas**:
   - Direct capability matches
   - Proven experience and expertise
   - Competitive advantages
   - Unique differentiators
   - Reference-able successes

2. **Partial Fit Areas**:
   - Capabilities requiring adaptation
   - Experience in adjacent domains
   - Partner or subcontractor opportunities
   - Skill development requirements
   - Innovation and customization needs

3. **Gap Areas**:
   - Missing capabilities or experience
   - Resource or capacity constraints
   - Technology or skill limitations
   - Geographic or scale challenges
   - Competitive disadvantages

4. **Risk Assessment**:
   - High-risk capability gaps
   - Delivery and performance risks
   - Resource availability risks
   - Technology and integration risks
   - Client acceptance risks

5. **Gap Mitigation Strategies**:
   - Partnership and teaming options
   - Skill development and training
   - Technology acquisition or licensing
   - Subcontractor engagement
   - Phased delivery approaches

Provide recommendations for positioning our capabilities and addressing gaps."""

    CLIENT_PAIN_POINT_ANALYSIS = """Analyze the client's key pain points and challenges:

**Client Information**:
{client_context}

**Industry Context**:
{industry_challenges}

**Pain Point Categories**:

1. **Operational Pain Points**:
   - Process inefficiencies and bottlenecks
   - Manual tasks and automation gaps
   - Data silos and integration challenges
   - Quality and consistency issues
   - Resource utilization problems

2. **Strategic Pain Points**:
   - Growth and scalability limitations
   - Competitive pressure and market share
   - Innovation and digital transformation
   - Regulatory and compliance burdens
   - Customer experience shortfalls

3. **Technology Pain Points**:
   - Legacy system limitations
   - Integration and interoperability issues
   - Security and compliance gaps
   - Performance and reliability problems
   - User experience and adoption challenges

4. **Financial Pain Points**:
   - Cost optimization pressures
   - Budget and resource constraints
   - ROI and value realization challenges
   - Risk and liability concerns
   - Investment prioritization difficulties

5. **People and Process Pain Points**:
   - Skill gaps and talent shortages
   - Change resistance and adoption issues
   - Communication and collaboration problems
   - Training and knowledge management
   - Performance measurement and accountability

For each pain point, assess:
- Severity and business impact
- Root causes and contributing factors
- Current mitigation efforts
- Solution requirements and priorities
- Our ability to address the pain point

Prioritize pain points and develop targeted value propositions."""

    RELATIONSHIP_STRATEGY = """Develop a relationship strategy for this client:

**Client Profile**:
{client_profile}

**Current Relationship Status**:
{relationship_status}

**Opportunity Context**:
{opportunity_details}

**Strategy Development**:

1. **Relationship Objectives**:
   - Short-term engagement goals
   - Long-term partnership vision
   - Revenue and growth targets
   - Strategic account development
   - Market position strengthening

2. **Stakeholder Engagement Plan**:
   - Key stakeholder priorities
   - Engagement tactics and channels
   - Meeting and communication schedule
   - Value demonstration opportunities
   - Trust-building initiatives

3. **Value Proposition Development**:
   - Unique value differentiators
   - Competitive positioning themes
   - Client-specific benefits
   - Risk mitigation messages
   - Success story relevance

4. **Relationship Building Activities**:
   - Executive relationship development
   - Technical engagement and demos
   - Industry event participation
   - Thought leadership sharing
   - Reference and peer connections

5. **Success Metrics**:
   - Relationship strength indicators
   - Engagement quality measures
   - Opportunity advancement metrics
   - Win rate improvements
   - Long-term account value

Provide a detailed relationship strategy with specific actions, timelines, and success measures."""

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
            'client_profile': cls.CLIENT_PROFILE_ANALYSIS,
            'stakeholder_mapping': cls.STAKEHOLDER_MAPPING,
            'needs_assessment': cls.NEEDS_ASSESSMENT,
            'capability_matching': cls.CAPABILITY_MATCHING,
            'pain_point_analysis': cls.CLIENT_PAIN_POINT_ANALYSIS,
            'relationship_strategy': cls.RELATIONSHIP_STRATEGY
        }
        
        prompt_template = prompt_map.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        return prompt_template.format(**kwargs)
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for client assessment tasks."""
        return cls.CLIENT_SYSTEM
