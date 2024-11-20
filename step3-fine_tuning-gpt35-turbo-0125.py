import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

training_file_id="file-036cd32fda1d4a2584ff6130a30867c0"
validation_file_id="file-594b6349c1714baab5dcb4f0bcbe926e"

# Retrieve Azure OpenAI credentials
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Check if the environment variables are loaded correctly
if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
    print("Error: Missing Azure OpenAI credentials.")
    exit(1)

# Initialize the Azure OpenAI client
try:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-05-01-preview"  # Ensure correct API version
    )
except Exception as e:
    print(f"Error initializing Azure OpenAI client: {e}")
    exit(1)

# Validate that training_file_id and validation_file_id exist
if 'training_file_id' not in globals() or 'validation_file_id' not in globals():
    print("Error: Missing training or validation file IDs.")
    exit(1)

# Fine-tuning job creation using the correct model and files
try:
    response = client.fine_tuning.jobs.create(
        training_file=training_file_id,  # ID of the uploaded training set
        validation_file=validation_file_id,  # ID of the uploaded validation set
        model="gpt-35-turbo-0125",  # Fine-tune on the optimized GPT-4o model
        seed=105  # Optional: Seed for reproducibility
    )

    # Retrieve and print the job ID
    job_id = response.id
    print("Fine-tuning job submitted!")
    print("Job ID:", job_id)
    print("Initial Status:", response.status)

    # Print the full JSON response (for debugging and logging)
    print(response.model_dump_json(indent=2))

except Exception as e:
    print(f"Error submitting fine-tuning job: {e}")