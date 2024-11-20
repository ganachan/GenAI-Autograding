import openai
import os
import time
from IPython.display import clear_output

# Set up Azure OpenAI credentials using environment variables
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-09-01-preview"  # Ensure the API version supports fine-tuning

# Fine-tuning job ID
job_id = "ftjob-c9dcbf2f55264a7a92ea59f12395e765"

start_time = time.time()

# Track the status of the fine-tuning job
response = client.FineTuningJob.retrieve(id=job_id)
status = response.status

# Poll every 10 seconds until the job is finished
while status not in ["succeeded", "failed"]:
    time.sleep(10)
    response = openai.FineTuningJob.retrieve(id=job_id)
    
    # List and print the latest events for the fine-tuning job
    events_response = client.FineTuningJob.list_events(fine_tuning_job_id=job_id, limit=10)
    print(events_response.model_dump_json(indent=2))

    # Print elapsed time and job status
    elapsed_minutes = int((time.time() - start_time) // 60)
    elapsed_seconds = int((time.time() - start_time) % 60)
    print(f"Elapsed time: {elapsed_minutes} minutes {elapsed_seconds} seconds")
    
    status = response.status
    print(f'Status: {status}')
    clear_output(wait=True)

# Print the final status of the job
print(f'Fine-tuning job {job_id} finished with status: {status}')

# List all fine-tuning jobs for this resource
print('Checking other fine-tune jobs for this resource.')
response = openai.FineTuningJob.list()
print(f'Found {len(response.data)} fine-tune jobs.')