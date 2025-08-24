# How to use the ContentGenerator

The `ContentGenerator` is a specialized sub-agent responsible for generating proposal content based on requirements analysis, client profiles, and project specifications. It uses the Google Gemini API to generate dynamic and tailored content for each section of a proposal.

## Configuration

To use the `ContentGenerator`, you need to configure your Google Gemini API key. The `ContentGenerator` expects the API key to be in an environment variable named `GOOGLE_API_KEY`.

You can set this environment variable in a `.env` file in the root of the project. If the `.env` file does not exist, you can create it by copying the `.env.example` file:

```bash
cp .env.example .env
```

Then, edit the `.env` file and add your `GOOGLE_API_KEY`:

```
GOOGLE_API_KEY="your_google_api_key_here"
```

## Usage

The `ContentGenerator` is designed to be used as part of a larger workflow, orchestrated by an agent like the `OrchestratorAgent`. However, you can also use it directly.

Here's an example of how to use the `ContentGenerator` to generate proposal content:

```python
import asyncio
from src.modules.proposal.content_generator import ContentGenerator

async def main():
    # Initialize the ContentGenerator
    content_generator = ContentGenerator()

    # Prepare the input data
    input_data = {
        "requirements_analysis": {
            "summary": {"total_requirements": 15, "complexity_score": 7},
            "requirements": {"technical": ["REST API", "PostgreSQL database", "React frontend"]},
            "technical_specifications": {"technologies": ["Python", "FastAPI", "React", "PostgreSQL"]},
        },
        "client_profile": {"name": "Global Tech Inc.", "industry": "Technology"},
        "project_specifications": {"title": "New E-commerce Platform", "timeline": {"duration_months": 9}},
        "content_preferences": {
            "style": "formal",
            "sections": [
                "project_overview",
                "technical_approach",
                "timeline_deliverables",
                "team_qualifications",
                "budget_pricing"
            ]
        },
    }

    # Generate the proposal content
    result = await content_generator.process(input_data)

    # Print the result
    if result["status"] == "success":
        for section_name, section_data in result["generated_sections"].items():
            print(f"--- {section_data['title']} ---")
            print(section_data['content'])
            print("\n")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Input Data Structure

The `ContentGenerator`'s `process` method expects a dictionary with the following structure:

-   `requirements_analysis` (dict): A dictionary containing the analysis of the RFP requirements.
-   `client_profile` (dict): A dictionary with information about the client.
-   `project_specifications` (dict): A dictionary with details about the project.
-   `content_preferences` (dict): A dictionary with preferences for the generated content, such as the `style` and the list of `sections` to include.

### Output Data Structure

The `process` method returns a dictionary with the following structure:

-   `status` (str): "success" or "error".
-   `proposal_id` (str): A unique ID for the generated proposal.
-   `generated_sections` (dict): A dictionary where the keys are the section names and the values are dictionaries containing the `title`, `content`, `word_count`, etc. for each section.
-   `proposal_structure` (dict): A dictionary with information about the overall structure of the proposal.
-   `executive_summary` (str): The generated executive summary.
-   `content_metrics` (dict): A dictionary with metrics about the generated content.
-   `content_recommendations` (list): A list of recommendations for improving the content.
-   `error` (str): An error message if the status is "error".

## Extending the ContentGenerator

The `ContentGenerator` can be extended by:

-   **Adding new sections:** You can add new sections to the `content_sections` dictionary in the `__init__` method.
-   **Adding new content styles:** You can add new styles to the `content_styles` dictionary.
-   **Improving the prompts:** The prompts used to generate the content can be improved to produce better results. The main prompt is in the `_generate_section_content` method.
