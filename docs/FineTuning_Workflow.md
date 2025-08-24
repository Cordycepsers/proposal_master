# Fine-Tuning Workflow for the ContentGenerator

This document outlines the process for fine-tuning the Gemini model using the user feedback collected by the "Proposal Master" application.

## 1. Data Preparation

The first step is to prepare the training data. The `scripts/prepare_finetuning_data.py` script is provided for this purpose.

### How it works

The script connects to the application's database, fetches the user feedback, and processes it to generate a JSONL file with training examples. The logic for generating the training examples is as follows:

-   **Positive Examples:** Feedback with a rating of 4 or 5 is considered a "good" example. The script will create a training example with the original prompt and the generated response.
-   **Improved Examples:** Feedback with a rating of 1 or 2 and a comment is used to generate an "improved" example. The script uses the Gemini API to generate a new, improved response based on the original prompt, the original response, and the user's comment.

### How to run

To run the script, execute the following command from the root of the project:

```bash
python scripts/prepare_finetuning_data.py
```

This will generate a `finetuning_data.jsonl` file in the root of the project. This file contains the training data in the format required for fine-tuning the Gemini model.

**Note:** The script currently uses placeholder data for the original prompts and responses. In a real implementation, you would need to log the generated content to be able to use it in the data preparation script.

## 2. Fine-Tuning on Google Cloud's AI Platform

Once you have the `finetuning_data.jsonl` file, you can use it to fine-tune the Gemini model on Google Cloud's AI Platform.

### Prerequisites

-   A Google Cloud Platform project with billing enabled.
-   The Generative AI API enabled in your project.
-   The `gcloud` command-line tool installed and configured.

### Steps

1.  **Upload the training data to Google Cloud Storage:**
    ```bash
    gsutil cp finetuning_data.jsonl gs://your-bucket-name/
    ```

2.  **Create a fine-tuning job:** You can do this using the `gcloud` command-line tool or through the Google Cloud Console. Here's an example using `gcloud`:

    ```bash
    gcloud ai-platform jobs submit tuning "proposal_master_tuning_job_$(date +%Y%m%d_%H%M%S)" \
        --project "your-gcp-project-id" \
        --region "us-central1" \
        --tuned-model-display-name "proposal-master-gemini-v1" \
        --base-model "gemini-pro" \
        --training-data-uri "gs://your-bucket-name/finetuning_data.jsonl" \
        --tuning-job-location "us-central1"
    ```

3.  **Monitor the fine-tuning job:** You can monitor the progress of the job in the Google Cloud Console.

4.  **Get the ID of the fine-tuned model:** Once the job is complete, you will get an ID for your new, fine-tuned model. You will need this ID to use the model in the application.

## 3. Using the Fine-Tuned Model

To use the fine-tuned model in the "Proposal Master" application, you will need to:

1.  **Update the configuration:** Add a new environment variable to your `.env` file to store the ID of the fine-tuned model, for example:
    ```
    FINETUNED_MODEL_ID="your_finetuned_model_id"
    ```

2.  **Modify the `ContentGenerator`:** Update the `ContentGenerator` to use the fine-tuned model ID when initializing the `GenerativeModel`. You can get the model ID from the environment variable.

    ```python
    # in src/modules/proposal/content_generator.py

    class ContentGenerator:
        def __init__(self):
            # ...
            model_id = os.getenv("FINETUNED_MODEL_ID", "gemini-pro")
            self.model = genai.GenerativeModel(model_id)
            # ...
    ```

By following this workflow, you can continuously improve the quality of the AI-generated content based on user feedback.
