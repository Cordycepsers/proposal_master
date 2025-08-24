import logging
from typing import Dict, Any

from src.agents.base_agent import BaseAgent
from src.core.document_processor import DocumentProcessor
from src.modules.analysis.document_analyzer import DocumentAnalyzer
from src.modules.proposal.content_generator import ContentGenerator
from src.agents.submission_agent import SubmissionAgent

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent that coordinates the end-to-end proposal generation workflow.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="Orchestrator Agent", description="Central coordinator for the proposal generation workflow.")
        self.agent_type = "orchestrator"

        # Initialize the agents that will be used in the workflow
        self.document_processor = DocumentProcessor()
        self.document_analyzer = DocumentAnalyzer()
        self.content_generator = ContentGenerator()
        self.submission_agent = SubmissionAgent()

        logger.info("Orchestrator Agent initialized")

    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Processes a document from a file path and generates a proposal.

        Args:
            file_path: The path to the document to process.

        Returns:
            A dictionary containing the generated proposal.
        """
        try:
            logger.info(f"Starting end-to-end workflow for document: {file_path}")

            # Step 1: Process the document
            logger.info("Step 1: Processing document...")
            document = self.document_processor.process(file_path)
            if not document:
                logger.error("Document processing failed.")
                return {"status": "error", "message": "Document processing failed."}
            logger.info("Document processing successful.")

            # Step 2: Analyze the document
            logger.info("Step 2: Analyzing document...")
            analysis_results = self.document_analyzer.analyze(document)
            if not analysis_results:
                logger.error("Document analysis failed.")
                return {"status": "error", "message": "Document analysis failed."}
            logger.info("Document analysis successful.")

            # Step 3: Generate the proposal content
            logger.info("Step 3: Generating proposal content...")
            proposal_content = await self.content_generator.process(analysis_results)
            if not proposal_content or proposal_content.get("status") != "success":
                logger.error("Proposal content generation failed.")
                return {"status": "error", "message": "Proposal content generation failed."}
            logger.info("Proposal content generation successful.")

            # Step 4: Submit the proposal
            logger.info("Step 4: Submitting proposal...")
            submission_result = self.submission_agent.submit(proposal_content)
            if not submission_result or submission_result.get("status") != "success":
                logger.error("Proposal submission failed.")
                return {"status": "error", "message": "Proposal submission failed."}
            logger.info("Proposal submission successful.")


            logger.info("End-to-end workflow completed successfully.")
            return {
                "status": "success",
                "proposal": proposal_content,
                "analysis": analysis_results,
                "submission": submission_result,
            }

        except Exception as e:
            logger.error(f"An error occurred during the end-to-end workflow: {e}")
            return {"status": "error", "message": str(e)}
