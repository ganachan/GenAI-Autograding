# GenAI Auto-Grading with Custom-Avatar

A comprehensive Streamlit application that leverages Azure OpenAI GPT models, fine-tuned GPT-4, and Azure Speech services to create an interactive learning and grading platform. The app features a custom avatar, Maria, who serves as a lecture assistant and helps with auto-grading student responses.

## Features

### 1. Multi-Agent Model Integration
- **Fine-Tuned GPT-4 Auto-Grading:** Provides precise feedback and grading for student submissions.
- **GPT-3.5 Assistance:** Generates concise explanations and feedback for questions.
- **Dual-Model Feedback:** Students receive insights from both models for a comprehensive learning experience.

### 2. Custom Avatar Lectures
- Generates Maria's personalized lecture videos using Azure Speech Services.
- Provides captions in multiple languages, including English, Spanish, French, and Chinese.

### 3. Interactive UI for Learning and Assessment
- Allows users to select questions and submit answers for grading.
- Provides a user-friendly interface to explore AI-assisted learning features.

### 4. Question Bank and Personalized Feedback
- Generates question introductions to help students better understand topics.
- Stores submissions and feedback in Azure Blob Storage for easy access.

### 5. Seamless Integration with Azure
- **Azure Blob Storage:** Stores lecture videos and submission details securely.
- **Azure OpenAI GPT-3.5 and GPT-4 Models:** Powers feedback and grading capabilities.

## Requirements

- Python 3.8 or higher
- Azure OpenAI services credentials
- Azure Blob Storage account
- Azure Speech services subscription

### Dependencies
The application requires the following Python libraries:
- `streamlit`
- `openai`
- `dotenv`
- `requests`
- `azure-storage-blob`

Install the required dependencies using:
```bash
pip install -r requirements.txt
