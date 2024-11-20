# Upload fine-tuning files to Azure OpenAI

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Reload variables from the .env file
load_dotenv(override=True)

# Retrieve environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Verify that the variables are reloaded
print("Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("API Key:", os.getenv("AZURE_OPENAI_API_KEY"))

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-05-01-preview"  # Ensure this API version or later is used
)

# File names for training and validation datasets
training_file_name = 'training_set.jsonl'
validation_file_name = 'validation_set.jsonl'

# Upload the training dataset file
with open(training_file_name, "rb") as training_file:
    training_response = client.files.create(
        file=training_file, 
        purpose="fine-tune"
    )
    training_file_id = training_response.id

# Upload the validation dataset file
with open(validation_file_name, "rb") as validation_file:
    validation_response = client.files.create(
        file=validation_file, 
        purpose="fine-tune"
    )
    validation_file_id = validation_response.id

# Print the file IDs
print("Training file ID:", training_file_id)
print("Validation file ID:", validation_file_id)
