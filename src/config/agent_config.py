# src/config/agent_config.py
AGENT_CONFIGS = {
    "analysis_agent": {
        "max_workers": 4,
        "timeout": 30,
        "priority": 1
    },
    "research_agent": {
        "max_workers": 2,
        "timeout": 60,
        "priority": 2
    },
    "client_agent": {
        "max_workers": 1,
        "timeout": 45,
        "priority": 3
    },
    "proposal_agent": {
        "max_workers": 3,
        "timeout": 120,
        "priority": 4
    },
    "delivery_agent": {
        "max_workers": 1,
        "timeout": 30,
        "priority": 5
    }
}
