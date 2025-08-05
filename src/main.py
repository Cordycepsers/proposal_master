# src/main.py
import sys
from agents.orchestrator_agent import OrchestratorAgent
from core.communication_manager import CommunicationManager

def main():
    """Main entry point for the smart proposal system"""
    
    # Initialize communication manager
    comm_manager = CommunicationManager()
    
    # Initialize orchestrator agent
    orchestrator = OrchestratorAgent(comm_manager)
    
    # Sample input data
    sample_document = {
        "document_id": "PROJ-2024-001",
        "title": "Cloud Migration Project",
        "content": "This is a detailed project description...",
        "requirements": ["Security", "Scalability", "Cost-effectiveness"],
        "target_client": "TechCorp Inc.",
        "deadline": "2024-12-31"
    }
    
    print("🚀 Starting Smart Proposal System")
    print("=" * 50)
    
    # Process the document
    result = orchestrator.process(sample_document)
    
    if result["status"] == "completed":
        print("\n✅ Process completed successfully!")
        print(f"Document ID: {result.get('document_id')}")
        print("Output generated and delivered.")
    else:
        print(f"\n❌ Process failed: {result.get('error')}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
