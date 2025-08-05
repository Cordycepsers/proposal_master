#!/usr/bin/env python3
"""
Proposal Master - AI-Powered Proposal Management System

This is the main entry point for the Proposal Master system.
A comprehensive solution for analyzing RFPs, generating proposals,
and managing the entire proposal lifecycle using AI agents.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import core components with fallback for missing modules
try:
    from agents.orchestrator_agent import OrchestratorAgent
    from core.communication_manager import CommunicationManager
    from config.settings import settings
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    # Fallback to existing components if orchestrator not available
    from core.document_processor import DocumentProcessor
    from core.rag_system import RAGSystem
    from core.similarity_engine import SimilarityEngine
    from utils.logging_config import setup_logging as existing_setup_logging
    ORCHESTRATOR_AVAILABLE = False

import logging

def setup_logging():
    """Setup logging configuration"""
    if ORCHESTRATOR_AVAILABLE and hasattr(settings, 'LOG_LEVEL'):
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(settings.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    else:
        # Use existing logging setup
        try:
            existing_setup_logging()
        except:
            # Basic logging fallback
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"logs/proposal_master_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                    logging.StreamHandler()
                ]
            )

def main():
    """Main entry point for the smart proposal system"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        print("🚀 Starting Smart Proposal System")
        print("=" * 50)
        
        if ORCHESTRATOR_AVAILABLE:
            print(f"System: {settings.SYSTEM_NAME}")
            print(f"Version: {settings.VERSION}")
        else:
            print("System: Proposal Master")
            print("Version: 1.0.0")
            
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        if ORCHESTRATOR_AVAILABLE:
            # Use new orchestrator-based system
            run_orchestrator_system(logger)
        else:
            # Use existing demo system
            run_demo_system(logger)
        
    except Exception as e:
        print(f"\n💥 System error occurred: {str(e)}")
        logger.error(f"System error: {str(e)}", exc_info=True)
        sys.exit(1)
    
    finally:
        print("=" * 50)
        print("System shutdown complete")
        print("=" * 50)

def run_orchestrator_system(logger):
    """Run the orchestrator-based system"""
    try:
        # Initialize communication manager
        comm_manager = CommunicationManager()
        logger.info("Communication manager initialized")
        
        # Initialize orchestrator agent
        orchestrator = OrchestratorAgent(comm_manager)
        logger.info("Orchestrator agent initialized")
        
        # Sample input data - this would typically come from API, file, or user input
        sample_document = {
            "document_id": "PROJ-2024-001",
            "title": "Cloud Migration Project",
            "content": "This is a detailed project description outlining requirements for cloud migration including security, scalability, and cost-effectiveness considerations.",
            "requirements": ["Security", "Scalability", "Cost-effectiveness"],
            "target_client": "TechCorp Inc.",
            "deadline": "2024-12-31",
            "budget": "$500,000",
            "project_type": "Cloud Migration"
        }
        
        print(f"Processing document: {sample_document['title']}")
        print(f"Document ID: {sample_document['document_id']}")
        print("-" * 50)
        
        # Process the document through the orchestrator
        result = orchestrator.process(sample_document)
        
        if result["status"] == "completed":
            print("\n✅ Process completed successfully!")
            print(f"Document ID: {result.get('document_id')}")
            print("Output generated and delivered.")
            
            # Save output to file (example)
            output_file = f"data/output/proposal_{sample_document['document_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w') as f:
                f.write(f"Proposal Generated: {result.get('document_id')}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
                # Add more output processing here
            
            print(f"Output saved to: {output_file}")
            
        else:
            print(f"\n❌ Process failed: {result.get('error')}")
            logger.error(f"Process failed: {result.get('error')}")
            
    except Exception as e:
        print(f"Error in orchestrator system: {e}")
        logger.error(f"Orchestrator system error: {e}")
        raise

def run_demo_system(logger):
    """Run the existing demo system"""
    print("Running in demo mode with existing components...")
    
    # Initialize core components
    logger.info("Initializing Proposal Master components...")
    
    doc_processor = DocumentProcessor()
    rag_system = RAGSystem()
    similarity_engine = SimilarityEngine()
    
    print("✅ Core components initialized successfully!")
    
    # Demo functionality
    print("\n📋 Available Operations:")
    print("1. Process Documents")
    print("2. Search Knowledge Base")
    print("3. Compare Proposals")
    print("4. Generate Proposal Content")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect operation (1-5): ").strip()
            
            if choice == '1':
                demo_document_processing(doc_processor)
            elif choice == '2':
                demo_knowledge_search(rag_system)
            elif choice == '3':
                demo_proposal_comparison(similarity_engine)
            elif choice == '4':
                demo_content_generation()
            elif choice == '5':
                print("👋 Thank you for using Proposal Master!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"❌ An error occurred: {e}")

def demo_document_processing(processor: DocumentProcessor):
    """Demo document processing functionality."""
    print("\n📄 Document Processing Demo")
    print("-" * 30)
    
    # Check for sample documents
    data_dir = Path("data/documents")
    sample_files = list(data_dir.glob("**/*.txt")) + list(data_dir.glob("**/*.md"))
    
    if not sample_files:
        print("No sample documents found. Creating a demo document...")
        demo_file = data_dir / "rfp_samples" / "demo_rfp.txt"
        demo_file.parent.mkdir(parents=True, exist_ok=True)
        demo_file.write_text("""
DEMO RFP - Technology Services

Project Overview:
We are seeking a technology partner to provide cloud infrastructure services
for our enterprise applications. The solution should include:

- Cloud hosting and management
- Security implementation
- Performance monitoring
- 24/7 support services

Budget: $100,000 - $150,000
Timeline: 6 months
        """.strip())
        sample_files = [demo_file]
    
    for file_path in sample_files[:3]:  # Process first 3 files
        try:
            result = processor.process_document(file_path)
            print(f"\n✅ Processed: {result['file_name']}")
            print(f"   Size: {result['file_size']} bytes")
            print(f"   Format: {result['format']}")
            content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
            print(f"   Preview: {content_preview}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

def demo_knowledge_search(rag_system: RAGSystem):
    """Demo RAG system search functionality."""
    print("\n🔍 Knowledge Base Search Demo")
    print("-" * 35)
    
    # Build index if not exists
    if not rag_system.is_loaded:
        print("Building knowledge base index...")
        doc_processor = DocumentProcessor()
        data_dir = Path("data/documents")
        
        # Find all documents
        all_files = []
        for pattern in ["**/*.txt", "**/*.md"]:
            all_files.extend(data_dir.glob(pattern))
        
        if all_files:
            documents = doc_processor.batch_process(all_files)
            rag_system.build_index(documents)
        else:
            print("No documents found to index.")
            return
    
    # Demo search
    sample_queries = [
        "cloud infrastructure services",
        "budget and timeline requirements",
        "security implementation"
    ]
    
    for query in sample_queries:
        print(f"\n🔎 Searching for: '{query}'")
        try:
            response = rag_system.query(query, top_k=2)
            print("📝 Response:")
            print(response[:300] + "..." if len(response) > 300 else response)
        except Exception as e:
            print(f"❌ Search error: {e}")

def demo_proposal_comparison(similarity_engine: SimilarityEngine):
    """Demo proposal comparison functionality."""
    print("\n🔄 Proposal Comparison Demo")
    print("-" * 32)
    
    # Create demo proposals
    proposal1 = {
        'file_name': 'proposal_a.txt',
        'content': 'We provide comprehensive cloud services including infrastructure management, security, and support.',
        'format': '.txt',
        'file_size': 1024
    }
    
    proposal2 = {
        'file_name': 'proposal_b.txt', 
        'content': 'Our cloud solutions offer infrastructure services, security implementation, and 24/7 technical support.',
        'format': '.txt',
        'file_size': 1100
    }
    
    print("Comparing two sample proposals...")
    
    try:
        comparison = similarity_engine.compare_proposals(proposal1, proposal2)
        
        print("\n📊 Similarity Analysis:")
        for metric, score in comparison.items():
            print(f"   {metric.capitalize()}: {score:.3f}")
            
        if comparison['overall'] > 0.7:
            print("\n✅ High similarity detected - proposals are very similar")
        elif comparison['overall'] > 0.4:
            print("\n⚠️  Moderate similarity - some overlap detected")
        else:
            print("\n📋 Low similarity - proposals are quite different")
            
    except Exception as e:
        print(f"❌ Comparison error: {e}")

def demo_content_generation():
    """Demo content generation functionality."""
    print("\n✍️  Content Generation Demo")
    print("-" * 30)
    
    print("🔧 Content generation modules are being initialized...")
    print("📝 This feature will integrate with AI agents for:")
    print("   • Proposal section generation")
    print("   • RFP requirement analysis")
    print("   • Competitive response creation")
    print("   • Compliance checking")
    
    print("\n🚧 Coming soon in the full implementation!")

if __name__ == "__main__":
    main()
