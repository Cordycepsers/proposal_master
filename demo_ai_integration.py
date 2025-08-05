#!/usr/bin/env python3
"""
Demonstration of AI Agent and Prompt Integration

This script shows how the Proposal Master system integrates
AI prompts with specialized agents for comprehensive analysis.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agents.analysis_agent import AnalysisAgent
from src.prompts.analysis_prompts import AnalysisPrompts
from src.utils.logging_config import setup_logging


class MockAIClient:
    """Mock AI client for demonstration purposes."""
    
    def __init__(self):
        self.call_count = 0
    
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        """Mock AI response generation."""
        self.call_count += 1
        
        # Simulate different responses based on prompt content
        if "requirement" in user_prompt.lower():
            return self._mock_requirement_response()
        elif "risk" in user_prompt.lower():
            return self._mock_risk_response()
        elif "evaluation" in user_prompt.lower():
            return self._mock_evaluation_response()
        elif "summary" in user_prompt.lower():
            return self._mock_summary_response()
        elif "win probability" in user_prompt.lower():
            return self._mock_win_probability_response()
        else:
            return self._mock_generic_response()
    
    def _mock_requirement_response(self) -> str:
        """Mock requirement extraction response."""
        return """{
  "requirements": [
    {
      "id": "REQ-001",
      "text": "The system must provide cloud-based infrastructure with 99.9% uptime",
      "type": "technical",
      "priority": "mandatory",
      "complexity": "high",
      "dependencies": ["REQ-002"],
      "section": "Technical Requirements"
    },
    {
      "id": "REQ-002", 
      "text": "All data must be encrypted at rest and in transit",
      "type": "compliance",
      "priority": "mandatory",
      "complexity": "medium",
      "dependencies": [],
      "section": "Security Requirements"
    },
    {
      "id": "REQ-003",
      "text": "System should support 10,000 concurrent users",
      "type": "functional",
      "priority": "important",
      "complexity": "high",
      "dependencies": ["REQ-001"],
      "section": "Performance Requirements"
    }
  ],
  "summary": {
    "total_requirements": 3,
    "mandatory_count": 2,
    "complexity_breakdown": {"low": 0, "medium": 1, "high": 2}
  }
}"""
    
    def _mock_risk_response(self) -> str:
        """Mock risk assessment response."""
        return """**COMPREHENSIVE RISK ASSESSMENT**

**Technical Risks - HIGH IMPACT**:
- Complex cloud infrastructure requirements may present integration challenges
- 99.9% uptime requirement is aggressive and requires robust architecture
- Scalability to 10,000 concurrent users demands significant resources

**Schedule Risks - MEDIUM IMPACT**:
- 6-month timeline appears aggressive for full implementation
- Integration with existing systems may cause delays
- Testing and security certification could extend timeline

**Commercial Risks - LOW IMPACT**:
- Budget appears adequate for scope
- Standard payment terms reduce financial risk

**Competitive Risks - MEDIUM IMPACT**:
- Multiple qualified vendors likely to bid
- Incumbent may have advantage with existing relationships

**Overall Risk Rating: MEDIUM-HIGH**

**Key Mitigation Strategies**:
1. Implement phased delivery approach
2. Early engagement with security certification teams
3. Detailed architecture review and validation
4. Strong project management and milestone tracking"""
    
    def _mock_evaluation_response(self) -> str:
        """Mock evaluation criteria response."""
        return """**EVALUATION CRITERIA ANALYSIS**

**Scoring Categories**:
- Technical Approach: 40 points (40%)
- Past Performance: 25 points (25%) 
- Management Approach: 20 points (20%)
- Cost: 15 points (15%)

**Evaluation Method**:
- Best Value tradeoff using weighted scoring
- Technical proposals evaluated first
- Cost proposals opened only for technically acceptable offers

**Pass/Fail Criteria**:
- Minimum technical score: 28/40 points (70%)
- Required security clearances for key personnel
- Mandatory past performance references

**Strategic Recommendations**:
1. Focus heavily on technical solution differentiation (40% weight)
2. Emphasize relevant past performance with similar complexity
3. Competitive pricing important but secondary to technical strength
4. Ensure all pass/fail criteria are clearly addressed"""
    
    def _mock_summary_response(self) -> str:
        """Mock document summary response."""
        return """**EXECUTIVE SUMMARY - CLOUD INFRASTRUCTURE RFP**

**Project Overview**:
The client seeks a comprehensive cloud infrastructure solution to modernize their technology platform and support business growth. The project involves migrating critical applications to a secure, scalable cloud environment.

**Key Requirements**:
1. Cloud infrastructure with 99.9% uptime guarantee
2. Support for 10,000 concurrent users
3. Advanced security with encryption and compliance
4. Integration with existing enterprise systems
5. 24/7 monitoring and support services

**Evaluation Approach**:
Best value selection based on technical merit (40%), past performance (25%), management approach (20%), and cost (15%). Minimum technical score of 70% required.

**Critical Dates**:
- Proposal Due: March 15, 2025
- Contract Award: April 30, 2025
- Implementation Start: May 15, 2025
- Go-live Target: November 15, 2025

**Budget Information**:
Estimated value $2.5M - $3.5M over 3 years including implementation and support services.

**Success Factors**:
- Proven cloud architecture expertise
- Strong security and compliance track record
- Relevant past performance with similar scale
- Competitive pricing with clear value proposition"""
    
    def _mock_win_probability_response(self) -> str:
        """Mock win probability response."""
        return """**WIN PROBABILITY ASSESSMENT: 65%**

**Key Factors Influencing Probability**:

**Positive Factors** (+):
- Strong technical capabilities align with requirements
- Excellent past performance in cloud implementations  
- Established security expertise and certifications
- Competitive pricing model and cost structure
- Good client relationship and previous interactions

**Negative Factors** (-):
- Incumbent vendor has existing relationship advantage
- High competition expected from major cloud providers
- Aggressive timeline may favor larger organizations
- Limited local presence compared to some competitors

**Strategies to Improve Win Rate**:
1. Emphasize unique technical differentiators in proposal
2. Showcase most relevant past performance examples
3. Develop compelling cost/value proposition
4. Strengthen relationships with key decision makers
5. Consider strategic partnerships to address capability gaps

**Go/No-Go Recommendation: GO**
While competitive, our capabilities align well with requirements and the opportunity represents significant strategic value. Recommend full pursuit with focused bid strategy."""
    
    def _mock_generic_response(self) -> str:
        """Mock generic AI response."""
        return """This is a mock AI response demonstrating the integration between 
the Proposal Master system's prompts and AI agents. In a production environment, 
this would be replaced with actual AI service calls to providers like OpenAI, 
Anthropic, or other language models."""


async def demonstrate_prompt_integration():
    """Demonstrate how prompts integrate with AI agents."""
    
    print("🤖 Proposal Master AI Agent & Prompt Integration Demo")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Create mock AI client
    ai_client = MockAIClient()
    
    # Initialize Analysis Agent with AI client
    analysis_agent = AnalysisAgent(ai_client=ai_client)
    
    # Sample RFP content for analysis
    sample_rfp = """
    REQUEST FOR PROPOSAL - CLOUD INFRASTRUCTURE SERVICES
    
    1. PROJECT OVERVIEW
    Our organization requires a comprehensive cloud infrastructure solution 
    to support our digital transformation initiative. The system must provide 
    scalable, secure, and reliable cloud services.
    
    2. TECHNICAL REQUIREMENTS
    - Cloud infrastructure with 99.9% uptime SLA
    - Support for 10,000 concurrent users
    - Data encryption at rest and in transit
    - Integration with existing enterprise systems
    - Automated backup and disaster recovery
    
    3. EVALUATION CRITERIA
    Proposals will be evaluated based on:
    - Technical Approach (40 points)
    - Past Performance (25 points) 
    - Management Approach (20 points)
    - Cost (15 points)
    
    4. TIMELINE
    - Proposal Due Date: March 15, 2025
    - Contract Award: April 30, 2025
    - Implementation: 6 months from award
    
    5. BUDGET
    Estimated project value: $2.5M - $3.5M over 3 years
    """
    
    # Sample capabilities for win probability assessment
    our_capabilities = """
    Our Capabilities:
    - 15+ years cloud infrastructure experience
    - 500+ successful cloud migrations
    - AWS, Azure, GCP certified architects
    - 24/7 NOC with 99.95% uptime track record
    - Federal security clearances and certifications
    - Local presence with dedicated account team
    """
    
    print("\n📋 1. DIRECT PROMPT USAGE")
    print("-" * 30)
    
    # Demonstrate direct prompt usage
    prompts = AnalysisPrompts()
    
    # Get a specific prompt
    requirement_prompt = prompts.get_prompt('requirement_extraction', document_content=sample_rfp)
    print("📝 Generated Requirement Extraction Prompt:")
    print(requirement_prompt[:200] + "...\n")
    
    # Get system prompt
    system_prompt = prompts.get_system_prompt()
    print("🤖 System Prompt for Analysis Agent:")
    print(system_prompt[:150] + "...\n")
    
    print("\n🔧 2. AGENT-INTEGRATED ANALYSIS")
    print("-" * 35)
    
    # Demonstrate full agent analysis with AI integration
    input_data = {
        'content': sample_rfp,
        'extract_requirements': True,
        'analyze_criteria': True,
        'assess_risks': True,
        'generate_summary': True,
        'our_capabilities': our_capabilities
    }
    
    print("⚡ Running comprehensive AI-powered analysis...")
    
    # Process with the AI-integrated agent
    results = await analysis_agent.process(input_data)
    
    print("\n📊 ANALYSIS RESULTS")
    print("-" * 20)
    
    # Display requirements analysis
    if 'requirements' in results and isinstance(results['requirements'], dict):
        req_data = results['requirements']
        if 'requirements' in req_data:
            print(f"✅ Requirements Extracted: {len(req_data['requirements'])} found")
            for req in req_data['requirements'][:2]:  # Show first 2
                print(f"   • {req['id']}: {req['text'][:60]}...")
        print()
    
    # Display risk assessment
    if 'risks' in results:
        risk_data = results['risks']
        if isinstance(risk_data, dict) and 'overall_risk_level' in risk_data:
            print(f"⚠️  Overall Risk Level: {risk_data['overall_risk_level'].upper()}")
        print()
    
    # Display win probability
    if 'win_probability' in results:
        win_data = results['win_probability']
        if isinstance(win_data, dict) and 'probability_score' in win_data:
            score = win_data['probability_score']
            if score:
                print(f"🎯 Win Probability: {score:.1%}")
        print()
    
    # Display summary
    if 'document_summary' in results:
        summary_data = results['document_summary']
        if isinstance(summary_data, dict) and 'executive_summary' in summary_data:
            summary = summary_data['executive_summary']
            print(f"📄 Executive Summary Generated: {len(summary)} characters")
            print(f"   Preview: {summary[:100]}...")
        print()
    
    print(f"🔢 Total AI Service Calls: {ai_client.call_count}")
    print(f"📈 Analysis Components: {len([k for k in results.keys() if not k.startswith('_')])}")
    
    print("\n🎯 3. PROMPT CUSTOMIZATION EXAMPLE")
    print("-" * 38)
    
    # Show how prompts can be customized
    custom_risk_prompt = prompts.get_prompt(
        'risk_assessment',
        document_content=sample_rfp
    )
    
    print("🛠️  Customized Risk Assessment Prompt:")
    print("   Variables substituted: document_content")
    print("   Ready for AI service call")
    print("   Structured output expected")
    
    print("\n✨ 4. INTEGRATION BENEFITS")
    print("-" * 28)
    
    benefits = [
        "🤖 AI-powered analysis with structured prompts",
        "🔄 Fallback to rule-based methods if AI fails",
        "📊 Consistent, professional analysis output",
        "⚡ Scalable to multiple document types",
        "🎯 Customizable prompts for specific use cases",
        "📈 Improved accuracy over rule-based alone"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print(f"\n🎉 Demo completed! The Proposal Master system successfully")
    print(f"   integrates AI prompts with specialized agents for")
    print(f"   comprehensive, intelligent proposal analysis.")


async def demonstrate_multi_agent_workflow():
    """Demonstrate a multi-agent workflow using different prompt types."""
    
    print("\n" + "=" * 60)
    print("🔀 MULTI-AGENT WORKFLOW DEMONSTRATION")
    print("=" * 60)
    
    # This would show how multiple agents work together
    # using different prompt templates for a complete proposal workflow
    
    workflow_steps = [
        "📄 Analysis Agent: RFP analysis and requirements extraction",
        "🔍 Research Agent: Competitive intelligence and market research", 
        "👥 Client Agent: Stakeholder mapping and needs assessment",
        "✍️  Proposal Agent: Content generation and win theme development",
        "🚀 Delivery Agent: Compliance checking and submission preparation"
    ]
    
    print("Multi-Agent Proposal Development Workflow:")
    for i, step in enumerate(workflow_steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n💡 Each agent uses specialized prompts from its prompt class:")
    print(f"   • AnalysisPrompts for document analysis")
    print(f"   • ResearchPrompts for market intelligence") 
    print(f"   • ClientPrompts for relationship management")
    print(f"   • ProposalPrompts for content generation")
    print(f"   • DeliveryPrompts for quality assurance")
    
    print(f"\n🔗 Agents share context and build upon each other's results")
    print(f"   to create a comprehensive, winning proposal.")


if __name__ == "__main__":
    print("Starting Proposal Master AI Integration Demo...\n")
    
    # Run the demonstration
    asyncio.run(demonstrate_prompt_integration())
    asyncio.run(demonstrate_multi_agent_workflow())
    
    print(f"\n🎯 This demonstrates the powerful integration between")
    print(f"   AI prompts and specialized agents in the Proposal Master system!")
