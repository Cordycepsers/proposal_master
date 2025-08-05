"""
Research prompts for market research and competitive intelligence.

Contains prompt templates for the Research Agent to perform
market analysis, competitor research, and industry intelligence gathering.
"""

from typing import Dict, Any, List


class ResearchPrompts:
    """Collection of prompts for research and intelligence gathering."""
    
    RESEARCH_SYSTEM = """You are an expert market researcher and competitive intelligence analyst specializing in business-to-business markets. Your role is to gather, analyze, and synthesize information to support strategic decision-making in proposal development.

Key capabilities:
- Market trend analysis and forecasting
- Competitive landscape assessment
- Industry best practices identification
- Technology trend analysis
- Client organization research

Always provide data-driven insights with credible sources and actionable recommendations."""

    MARKET_RESEARCH = """Conduct comprehensive market research for the following industry and opportunity:

**Industry**: {industry}
**Market Segment**: {market_segment}
**Geographic Scope**: {geographic_scope}
**Opportunity Type**: {opportunity_type}

Research Focus Areas:

1. **Market Size & Growth**:
   - Current market size and growth rate
   - Market projections for next 3-5 years
   - Key growth drivers and barriers

2. **Industry Trends**:
   - Emerging technologies and innovations
   - Regulatory changes and impacts
   - Digital transformation trends
   - Sustainability and ESG factors

3. **Key Players**:
   - Market leaders and their market share
   - Emerging players and disruptors
   - Partnership and acquisition activity

4. **Client Needs & Pain Points**:
   - Common challenges in this market
   - Unmet needs and opportunities
   - Decision-making criteria and processes

5. **Pricing & Commercial Models**:
   - Typical pricing structures
   - Contract terms and conditions
   - Value proposition frameworks

Provide detailed findings with supporting data and strategic implications for our proposal approach."""

    COMPETITIVE_INTELLIGENCE = """Gather competitive intelligence on the following competitors for this opportunity:

**Primary Competitors**:
{primary_competitors}

**Secondary Competitors**:
{secondary_competitors}

**RFP Context**:
{rfp_summary}

For each competitor, research and analyze:

1. **Company Profile**:
   - Size, revenue, and market position
   - Core competencies and service offerings
   - Recent wins and notable clients
   - Financial health and stability

2. **Relevant Experience**:
   - Similar projects and contracts
   - Industry expertise and specializations
   - Geographic presence and capabilities
   - Technology platforms and partnerships

3. **Competitive Strengths**:
   - Key differentiators and advantages
   - Pricing competitiveness
   - Delivery capabilities and resources
   - Client relationships and reputation

4. **Potential Weaknesses**:
   - Capability gaps or limitations
   - Past performance issues
   - Resource constraints
   - Market positioning challenges

5. **Likely Strategy**:
   - Expected pricing approach
   - Key win themes and messaging
   - Team composition and leadership
   - Partnership or subcontracting strategies

Conclude with strategic recommendations for positioning against each competitor."""

    TECHNOLOGY_RESEARCH = """Research current and emerging technologies relevant to this opportunity:

**Technology Domain**: {technology_domain}
**Use Case**: {use_case}
**Requirements**: {technical_requirements}

Research Areas:

1. **Current State Analysis**:
   - Leading technology platforms and vendors
   - Maturity levels and adoption rates
   - Industry standards and frameworks
   - Integration capabilities and APIs

2. **Emerging Technologies**:
   - Next-generation solutions in development
   - Breakthrough innovations and patents
   - Research and development trends
   - Timeline for commercial availability

3. **Best Practices**:
   - Implementation methodologies
   - Architecture patterns and designs
   - Security and compliance considerations
   - Performance optimization techniques

4. **Vendor Landscape**:
   - Market leaders and their offerings
   - Specialized niche players
   - Partnership ecosystems
   - Pricing and licensing models

5. **Implementation Considerations**:
   - Common challenges and risks
   - Success factors and lessons learned
   - Resource requirements and timelines
   - Change management implications

Provide technology recommendations aligned with the client's requirements and strategic objectives."""

    CLIENT_RESEARCH = """Conduct comprehensive research on the client organization:

**Client Organization**: {client_name}
**Industry**: {client_industry}
**Geography**: {client_location}

Research Focus:

1. **Organization Profile**:
   - Mission, vision, and strategic priorities
   - Organizational structure and leadership
   - Size, budget, and financial position
   - Recent news and developments

2. **Business Context**:
   - Current challenges and pain points
   - Strategic initiatives and transformation programs
   - Regulatory and compliance requirements
   - Competitive pressures and market position

3. **IT Environment**:
   - Current technology infrastructure
   - Recent IT investments and projects
   - Technology standards and preferences
   - Digital transformation initiatives

4. **Procurement History**:
   - Past RFPs and contract awards
   - Preferred vendors and partners
   - Evaluation criteria and decision factors
   - Contract terms and negotiation patterns

5. **Key Stakeholders**:
   - Decision makers and influencers
   - Technical and business contacts
   - Past interactions and relationships
   - Communication preferences and styles

6. **Cultural Factors**:
   - Organizational culture and values
   - Risk tolerance and innovation appetite
   - Decision-making processes
   - Success metrics and KPIs

Use this research to inform our client engagement strategy and proposal positioning."""

    INDUSTRY_ANALYSIS = """Perform an industry analysis for the {industry_name} sector:

**Analysis Scope**:
- Industry segment: {industry_segment}
- Geographic focus: {geographic_focus}
- Time horizon: {time_horizon}

Analysis Framework:

1. **Industry Structure**:
   - Market size and segmentation
   - Value chain analysis
   - Concentration and competition levels
   - Barriers to entry and exit

2. **Competitive Dynamics**:
   - Porter's Five Forces analysis
   - Competitive positioning and strategies
   - Market share distribution
   - Merger and acquisition activity

3. **Growth Drivers**:
   - Demand drivers and market catalysts
   - Technology and innovation impacts
   - Regulatory and policy influences
   - Economic and demographic factors

4. **Industry Challenges**:
   - Key pain points and inefficiencies
   - Regulatory and compliance burdens
   - Technology disruption threats
   - Talent and resource constraints

5. **Future Outlook**:
   - Growth projections and scenarios
   - Emerging opportunities and threats
   - Technology and business model evolution
   - Strategic implications and recommendations

Provide strategic insights for positioning our capabilities and developing winning proposals in this industry."""

    BEST_PRACTICES_RESEARCH = """Research industry best practices for:

**Domain**: {practice_domain}
**Context**: {implementation_context}
**Objectives**: {business_objectives}

Research Scope:

1. **Leading Practices**:
   - Industry benchmarks and standards
   - Award-winning implementations
   - Case studies and success stories
   - Lessons learned and pitfalls to avoid

2. **Methodologies & Frameworks**:
   - Proven implementation approaches
   - Project management methodologies
   - Quality assurance frameworks
   - Risk management practices

3. **Technology Approaches**:
   - Architecture patterns and designs
   - Technology stacks and platforms
   - Integration strategies
   - Security and compliance measures

4. **Organizational Factors**:
   - Change management strategies
   - Training and adoption approaches
   - Governance and oversight models
   - Performance measurement systems

5. **Innovation & Trends**:
   - Emerging best practices
   - Next-generation approaches
   - Technology innovations
   - Future evolution trends

Synthesize findings into actionable recommendations for our proposal solution design."""

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
            'market_research': cls.MARKET_RESEARCH,
            'competitive_intelligence': cls.COMPETITIVE_INTELLIGENCE,
            'technology_research': cls.TECHNOLOGY_RESEARCH,
            'client_research': cls.CLIENT_RESEARCH,
            'industry_analysis': cls.INDUSTRY_ANALYSIS,
            'best_practices': cls.BEST_PRACTICES_RESEARCH
        }
        
        prompt_template = prompt_map.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        return prompt_template.format(**kwargs)
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for research tasks."""
        return cls.RESEARCH_SYSTEM
