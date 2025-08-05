# AI Agent & Prompt Integration Guide

This guide explains how prompts integrate with AI agents in the Proposal Master system to deliver intelligent, AI-powered proposal analysis and generation.

## 🏗 Architecture Overview

The integration follows a layered architecture:

```
📱 User Interface / API
    ↓
🤖 AI Agents (Analysis, Research, Client, Proposal, Delivery)
    ↓
📝 Prompt Templates (Structured, Context-Aware)
    ↓
🧠 AI Services (OpenAI, Anthropic, Azure, etc.)
    ↓
📊 Structured Results & Analysis
```

## 🔧 How Integration Works

### 1. Prompt Template System

Each agent has access to specialized prompt templates:

```python
from src.prompts.analysis_prompts import AnalysisPrompts

# Get a structured prompt with context
prompt = AnalysisPrompts.get_prompt(
    'requirement_extraction',
    document_content=rfp_text
)

# Get system prompt for AI persona
system_prompt = AnalysisPrompts.get_system_prompt()
```

### 2. AI Agent Integration

Agents use prompts to interact with AI services:

```python
from src.agents.analysis_agent import AnalysisAgent
from src.utils.ai_config import get_default_ai_client

# Create AI-powered agent
ai_client = get_default_ai_client('openai')
agent = AnalysisAgent(ai_client=ai_client)

# Process with AI integration
results = await agent.process({
    'content': document_text,
    'extract_requirements': True,
    'assess_risks': True
})
```

### 3. Fallback Mechanisms

Agents automatically fall back to rule-based analysis if AI fails:

```python
# AI service failure → automatic fallback
try:
    ai_result = await self._call_ai_service(prompt)
    return ai_result
except Exception as e:
    logger.warning(f"AI failed, using fallback: {e}")
    return await self._fallback_analysis(content)
```

## 📝 Prompt Categories

### Analysis Prompts
- **Requirements Extraction**: Structured JSON output
- **Risk Assessment**: Comprehensive risk analysis
- **Evaluation Criteria**: Scoring strategy insights
- **Win Probability**: Strategic opportunity assessment

### Research Prompts
- **Market Research**: Industry analysis and trends
- **Competitive Intelligence**: Competitor assessment
- **Technology Research**: Tech landscape analysis
- **Client Research**: Organization profiling

### Client Prompts
- **Stakeholder Mapping**: Decision-maker identification
- **Needs Assessment**: Requirement prioritization
- **Capability Matching**: Fit analysis
- **Relationship Strategy**: Engagement planning

### Proposal Prompts
- **Executive Summary**: Compelling overviews
- **Technical Approach**: Solution architecture
- **Win Theme Development**: Strategic messaging
- **Content Generation**: Section-specific writing

### Delivery Prompts
- **Compliance Checking**: Requirement verification
- **Quality Assurance**: Professional standards
- **Submission Strategy**: Logistics planning
- **Lessons Learned**: Process improvement

## 🚀 Benefits of Integration

### ✅ AI-Powered Intelligence
- **Advanced Analysis**: Beyond rule-based extraction
- **Contextual Understanding**: Nuanced interpretation
- **Strategic Insights**: Business intelligence
- **Quality Content**: Professional writing

### ✅ Reliability & Resilience
- **Fallback Mechanisms**: Never fails completely
- **Graceful Degradation**: Maintains functionality
- **Error Handling**: Robust error management
- **Logging & Monitoring**: Full visibility

### ✅ Scalability & Flexibility
- **Multiple AI Services**: OpenAI, Anthropic, Azure
- **Customizable Prompts**: Tailored to use cases
- **Modular Architecture**: Independent components
- **Easy Configuration**: Simple setup

## 🔌 AI Service Integration

### OpenAI Integration
```python
from src.utils.ai_config import AIServiceConfig, AIServiceFactory

config = AIServiceConfig(
    service_type='openai',
    api_key='your_api_key',
    model_name='gpt-4',
    temperature=0.1
)

client = AIServiceFactory.create_client(config)
agent = AnalysisAgent(ai_client=client)
```

### Anthropic Integration
```python
config = AIServiceConfig(
    service_type='anthropic',
    api_key='your_api_key',
    model_name='claude-3-sonnet-20240229'
)

client = AIServiceFactory.create_client(config)
agent = AnalysisAgent(ai_client=client)
```

### Environment Variables
```bash
# OpenAI
export OPENAI_API_KEY="your_openai_key"

# Anthropic
export ANTHROPIC_API_KEY="your_anthropic_key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your_azure_key"
export AZURE_OPENAI_ENDPOINT="your_azure_endpoint"
```

## 📊 Example Workflow

### Complete RFP Analysis Pipeline

```python
async def analyze_rfp_with_ai():
    # 1. Setup AI client
    ai_client = get_default_ai_client('openai')
    
    # 2. Create specialized agents
    analysis_agent = AnalysisAgent(ai_client)
    research_agent = ResearchAgent(ai_client)
    client_agent = ClientAgent(ai_client)
    
    # 3. Process RFP document
    rfp_analysis = await analysis_agent.process({
        'file_path': 'data/documents/rfp_samples/cloud_rfp.pdf',
        'extract_requirements': True,
        'assess_risks': True,
        'analyze_criteria': True
    })
    
    # 4. Research competitive landscape
    market_research = await research_agent.process({
        'industry': 'cloud_infrastructure',
        'competitors': ['AWS', 'Microsoft', 'Google'],
        'research_type': 'competitive_intelligence'
    })
    
    # 5. Analyze client organization
    client_profile = await client_agent.process({
        'client_name': 'TechCorp Inc',
        'industry': 'technology',
        'analysis_type': 'comprehensive_profile'
    })
    
    # 6. Combine insights for proposal strategy
    proposal_strategy = {
        'requirements': rfp_analysis['requirements'],
        'competitive_landscape': market_research['competition'],
        'client_insights': client_profile['profile'],
        'win_themes': generate_win_themes(rfp_analysis, client_profile)
    }
    
    return proposal_strategy
```

## 🎯 Best Practices

### Prompt Design
- ✅ **Clear Instructions**: Specific, actionable prompts
- ✅ **Structured Output**: JSON schemas for consistency
- ✅ **Context Variables**: Dynamic content substitution
- ✅ **Professional Persona**: Expert system prompts

### Error Handling
- ✅ **Graceful Fallbacks**: Always have backup methods
- ✅ **Comprehensive Logging**: Track all operations
- ✅ **Timeout Management**: Handle service delays
- ✅ **Rate Limiting**: Respect API limits

### Performance Optimization
- ✅ **Result Caching**: Cache expensive AI calls
- ✅ **Batch Processing**: Group related requests
- ✅ **Async Operations**: Non-blocking execution
- ✅ **Resource Management**: Efficient memory usage

## 🔧 Customization Examples

### Custom Prompt Templates
```python
# Create specialized prompt for government RFPs
GOV_RFP_ANALYSIS = """Analyze this government RFP with focus on:

1. **Compliance Requirements**: FAR/DFAR regulations
2. **Security Classifications**: Clearance requirements
3. **Socioeconomic Goals**: Small business requirements
4. **Evaluation Factors**: Government-specific criteria

RFP Document: {document_content}
Contract Type: {contract_type}
Agency: {government_agency}

Provide government-specific analysis..."""

# Add to prompt class
AnalysisPrompts.GOV_RFP_ANALYSIS = GOV_RFP_ANALYSIS
```

### Custom AI Client
```python
class CustomAIClient:
    """Custom AI client for specialized models."""
    
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Custom implementation for your AI service
        response = await your_ai_service.generate(
            system=system_prompt,
            prompt=user_prompt
        )
        return response.text

# Use with agents
custom_client = CustomAIClient()
agent = AnalysisAgent(ai_client=custom_client)
```

## 📈 Monitoring & Analytics

The system provides comprehensive monitoring:

- **📊 Performance Metrics**: Response times, success rates
- **🔍 Usage Analytics**: Most used prompts, popular features
- **⚠️ Error Tracking**: Failure modes, recovery success
- **💰 Cost Monitoring**: AI service usage and costs
- **🎯 Quality Metrics**: Result accuracy and relevance

## 🎉 Conclusion

The Proposal Master system's integration of AI prompts with specialized agents creates a powerful, intelligent proposal development platform that:

- **Scales from simple analysis to complex multi-agent workflows**
- **Provides consistent, professional-quality results**
- **Adapts to different AI services and deployment scenarios**
- **Maintains reliability through robust fallback mechanisms**
- **Enables customization for specific business needs**

This architecture represents the future of AI-powered business development tools! 🚀
