import os
import streamlit as st
import requests
import time
import uuid
from datetime import datetime, timezone, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path
#from st_pages import add_page_title,get_nav_from_toml


# Page Configuration
st.set_page_config(page_title="GenAI Auto-Grading with Maria", layout="wide")

# CSS Styling to Add Padding at the Top
st.markdown(
    """
    <style>
        .main > div {
            padding-top: 50px;  /* Adjust the padding value as needed */
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# Your Content
st.title("GenAI Auto-Grading with Maria")
st.write("Select a question to get started with automated grading.")

# Load environment variables
load_dotenv(override=True)

background_image_url = "https://mariagana.blob.core.windows.net/uservideos/avatar_image3.jpg"

# Azure Speech and Blob Configurations
SPEECH_ENDPOINT = "https://westus2.api.cognitive.microsoft.com"
SUBSCRIPTION_KEY = "*"
BLOB_CONNECTION_STRING = (
    *
)
BLOB_CONTAINER_NAME = "uservideos"
API_VERSION = "2024-04-15-preview"

# Initialize Azure OpenAI and Blob Storage clients
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

# Define Model Deployments
GPT35_DEPLOYMENT = "gpt-35-turbo-16k"
GPT4_FINE_TUNED_DEPLOYMENT = "gpt-4o-2024-08-finetuned_autograding"

# Sidebar User Inputs
with st.sidebar:
    st.header("User Information")
    username = st.text_input("Username", value="")
    industry_vertical = st.selectbox(
        "Industry Vertical", 
        ["Education", "Healthcare", "Manufacturing", "Telecom", "Finance", "Other"]
    )
    customer_name = st.text_input("Customer Name", value="")
    school_name = st.text_input("School Name", value="")
    date = st.date_input("Date", value=datetime.now().date())

    st.header("Subtitle Language Options")
    target_language = st.selectbox(
        "Select Language for Captions",
        {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "zh-Hans": "Simplified Chinese"},
        index=0
    )
# Greet the Student once the name is entered
if username:
    st.write(f"👋 Hello, **{username}**! Automated GenAI Grading Hub .")  
    st.write("Use **Maria's help** to explore questions and get them done with ease! Let's start learning 🎓.")

# Function to generate 100-word introduction for a question
def generate_question_intro(question):
    prompt = f"Provide a concise 25-word quicktip to help understand the topic: '{question}'."
    response = client.chat.completions.create(
        model=GPT35_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Display introduction for the selected question
#st.subheader("Maria's Introduction Help")
selected_question = st.selectbox("Select a Question", [
    "What is the purpose of an activation function in neural networks?",
    "What is a lambda function in Python?",
    "What is the significance of p-value in hypothesis testing?"
])
introduction = generate_question_intro(selected_question)  # Generate introduction
# Use st.expander to make the introduction collapsible
with st.expander("Show/Hide Introduction", expanded=False):
    st.write(introduction)

# Helper function to store video in session state
def store_video_in_session(local_video_path):
    """Store the video in session state for later download."""
    with open(local_video_path, "rb") as video_file:
        st.session_state["video_data"] = video_file.read()
        st.session_state["video_name"] = local_video_path


# Maria Lecture Video Generation Function

def create_job_id():
    """Generate and return a unique Job ID."""
    return str(uuid.uuid4())

def _authenticate(subscription_key):
    return {'Ocp-Apim-Subscription-Key': subscription_key}

def submit_synthesis(job_id, input_text):
    """Submit the synthesis job to Azure."""
    url = f"{SPEECH_ENDPOINT}/avatar/batchsyntheses/{job_id}?api-version={API_VERSION}"
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    payload = {
        'synthesisConfig': {
            "voice": 'Marrie VoiceNeural',
    # Add word boundary data for timestamping
            "outputFormat": "riff-24khz-16bit-mono-pcm",
            "wordBoundary": True  # This adds word-level timestamping
        },
        'customVoices': {
            "Marrie VoiceNeural": "f173fead-5911-4129-9ada-e0c1e62903b1"
        },
        "inputKind": "plainText",
        "inputs": [
            {"content": input_text},
        ],
        "avatarConfig": {
            "customized": True,
            "talkingAvatarCharacter": "Marrie-B",
            "talkingAvatarStyle": "Marrie-B-2",
            "videoFormat": "mp4",
            "videoCodec": "h264",
            "subtitleType": "hard_embedded",
            "backgroundColor": "#FFFFFFFF",
            "backgroundImage": background_image_url
        }
    }

    response = requests.put(url, json=payload, headers=headers)
    if response.status_code < 400:
        return response.json()["id"]
    else:
        st.error(f'Failed to submit job: {response.text}')
        return None

def sanitize_filename(filename):
    """Remove or replace invalid characters from the filename."""
    invalid_chars = r'<>:"/\|?*'
    sanitized = ''.join(char if char not in invalid_chars else '_' for char in filename)
    return sanitized

def upload_to_blob(local_file_path, blob_name):
    """Upload the file to Azure Blob Storage and return the Blob URL."""
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=blob_name)
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    st.success(f"Video uploaded to Blob Storage as '{blob_name}'")
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{blob_name}"
    #return blob_client.url

def get_synthesis(job_id):
    """Check the status of the synthesis job and get the video URL if complete."""
    url = f"{SPEECH_ENDPOINT}/avatar/batchsyntheses/{job_id}?api-version={API_VERSION}"
    headers = {'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['outputs']['result'] if data['status'] == 'Succeeded' else None

def store_video_in_session(local_video_path):
    """Store the video in session state for later download."""
    with open(local_video_path, "rb") as video_file:
        st.session_state["video_data"] = video_file.read()
        st.session_state["video_name"] = local_video_path

def generate_video_and_display():
    """Generate Maria Lecture Video, store it in session, and upload to Blob Storage."""
    job_id = create_job_id()  # Create a unique job ID for this request

    # Sanitize the filename to avoid invalid characters
    sanitized_question = sanitize_filename(selected_question.replace(' ', '_')) 
    local_video_path = f"{sanitized_question}_Maria_Lecture.mp4"
    blob_name = f"{sanitized_question}_Maria_Lecture.mp4"

    max_retries = 20  # Maximum retries (1 minute with 5-second intervals)
    retries = 0

    if submit_synthesis(job_id, introduction):
        with st.spinner("Generating Maria Lecture Video..."):
            while retries < max_retries:
                video_url = get_synthesis(job_id)

                if video_url:
                    # Save the video locally
                    with requests.get(video_url, stream=True) as r:
                        r.raise_for_status()
                        with open(local_video_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)

                    # Store the video in session state
                    store_video_in_session(local_video_path)

                    # Upload to Blob Storage and get the Blob URL
                    blob_url = upload_to_blob(local_file_path=local_video_path, blob_name=blob_name)

                    # Success message, video playback, and display the Blob URL
                    st.success("Video generated and uploaded successfully!")
                    st.video(local_video_path)
                    st.write(f"[View Video in Blob Storage]({blob_url})")

                    return  # Exit after successful generation and upload

                retries += 1
                time.sleep(5)  # Wait before the next retry

            # If we exhaust all retries
            st.error("Video generation took too long. Please try again.")

# Download Button for the Video from Session
if "video_data" in st.session_state:
    st.download_button(
        label="Download Maria Video",
        data=st.session_state["video_data"],
        file_name=st.session_state["video_name"],
        mime='video/mp4',
        key=f"download_{st.session_state['video_name']}"
    )

def generate_sas_token(blob_name):
    """Generate a SAS token for accessing the blob."""
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=BLOB_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1)  # Valid for 1 hour
    )
    return sas_token

# Function to query GPT-3.5 for feedback and grading
def query_gpt35_model(question, answer):
    """Send the question and answer to GPT-3.5 for feedback and grading."""
    prompt = f"Question: {question}\nAnswer: {answer}\n\nProvide feedback and a score from 1 to 10."
    response = client.chat.completions.create(
        model=GPT35_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Function to query Fine-tuned GPT-4 model for feedback and grading
def query_fine_tuned_gpt4_model(question, answer):
    """Send the question and answer to the fine-tuned GPT-4 model for feedback and grading."""
    prompt = f"Question: {question}\nAnswer: {answer}\n\nProvide feedback and a score from 1 to 10."
    response = client.chat.completions.create(
        model=GPT4_FINE_TUNED_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Function to store grading result in blob storage
def store_submission(question, answer, feedback_gpt35, feedback_gpt4):
    """Store the submission details with feedback in Azure Blob Storage."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = sanitize_filename(f"{username}_{customer_name}_{timestamp}.txt")
    content = f"""
    Username: {username}
    Customer: {customer_name}
    Question: {question}
    Answer: {answer}

    GPT-3.5 Feedback:
    {feedback_gpt35}

    GPT-4 (Fine-tuned) Feedback:
    {feedback_gpt4}

    Timestamp: {timestamp}
    """
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=filename)
    blob_client.upload_blob(content)
    st.success(f"Submission saved as '{filename}' in blob storage.")

def generate_filename(username, industry, customer, file_type, extension):
    """Generate a filename with the format `username_industry_customer_Maria_typeCount.extension`."""
    file_prefix = f"{username}_{industry}_{customer}_Maria_{file_type}"
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
    existing_files = container_client.list_blobs(name_starts_with=file_prefix)
    count = sum(1 for _ in existing_files) + 1  # Increment the count based on existing files
    return f"{file_prefix}{count}.{extension}"


# Auto-grading function
def query_autograde(question, answer):
    prompt = f"Question: {question}\nAnswer: {answer}\n\nGrade the answer and provide feedback."
    response = client.chat.completions.create(
        model=GPT4_FINE_TUNED_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Answer submission and grading
selected_answer = st.radio("Select the correct answer", [
    "It introduces non-linearity to the network.",
    "An anonymous function defined using the lambda keyword.",
    "It helps determine statistical significance."
])

# Button to Submit Answer for Auto-Grading
if st.button("Submit Answer", key="submit_answer"):
    with st.spinner("Submitting your answer for grading..."):
        # Get feedback from both GPT-3.5 and fine-tuned GPT-4 models
        feedback_gpt35 = query_gpt35_model(selected_question, selected_answer)
        feedback_gpt4 = query_fine_tuned_gpt4_model(selected_question, selected_answer)

        # Store submission with feedback in blob storage
        store_submission(selected_question, selected_answer, feedback_gpt35, feedback_gpt4)

        # Display feedback from both models
        st.subheader("GPT-3.5 Feedback")
        st.write(feedback_gpt35)

        st.subheader("GPT-4 (Fine-tuned) Feedback")
        st.write(feedback_gpt4)

        st.success("Answer submitted and graded successfully!")

# Video generation button
if st.button("Maria Brain Boost - Lecture"):
    generate_video_and_display()
