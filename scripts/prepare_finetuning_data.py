import asyncio
import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.config.database import AsyncSessionLocal, Base, engine
from src.models.core import Feedback, Proposal
import google.generativeai as genai
import os

async def improve_response(prompt, original_response, comment):
    """
    Use Gemini to generate an improved response based on user feedback.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found. Cannot improve response.")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    improvement_prompt = f"""
    The following is a prompt and a response that a user has rated poorly.
    The user's comment was: "{comment}"

    Original prompt:
    ---
    {prompt}
    ---

    Original response:
    ---
    {original_response}
    ---

    Please generate a new, improved response that addresses the user's feedback.
    """

    try:
        response = await model.generate_content_async(improvement_prompt)
        return response.text
    except Exception as e:
        print(f"Error improving response: {e}")
        return None

async def prepare_data():
    """
    Prepare data for fine-tuning by processing user feedback.
    """
    async with AsyncSessionLocal() as db:
        # Fetch feedback with associated proposals
        result = await db.execute(
            select(Feedback).options(selectinload(Feedback.proposal))
        )
        feedback_list = result.scalars().all()

        training_data = []
        for feedback in feedback_list:
            # This is a simplified example. In a real scenario, you would need to reconstruct
            # the exact prompt that was used to generate the original response.
            # For now, we'll use the proposal title as a stand-in for the prompt.
            prompt = f"Generate a proposal section for: {feedback.proposal.title}"

            if feedback.rating >= 4:
                # High rating, use as a positive example
                # We need the original response, which is not stored.
                # For this example, we'll just use a placeholder.
                # In a real implementation, you would need to log the generated content.
                original_response = "This is a placeholder for the original good response."
                training_data.append({"prompt": prompt, "response": original_response})
            elif feedback.rating <= 2 and feedback.comment:
                # Low rating with a comment, use to generate an improved example
                original_response = "This is a placeholder for the original bad response."
                improved_response = await improve_response(prompt, original_response, feedback.comment)
                if improved_response:
                    training_data.append({"prompt": prompt, "response": improved_response})

    # Save to a JSONL file
    with open("finetuning_data.jsonl", "w") as f:
        for item in training_data:
            f.write(json.dumps(item) + "\n")

    print(f"Generated {len(training_data)} training examples.")

if __name__ == "__main__":
    asyncio.run(prepare_data())
