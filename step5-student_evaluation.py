import os
from openai import AzureOpenAI

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Function to evaluate a submission with a specific model
def evaluate_submission_with_model(model_name, question, student_answer):
    """Send question and answer to the specified model for grading."""
    
    messages = [
        {"role": "system", "content": "You are an AI assistant specializing in autograding. Your primary goal is to assist with grading student submissions creatively and accurately."},
        {"role": "user", "content": f"Question: {question}\nAnswer: {student_answer}\n\nFeedback:"}
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    
    return response.choices[0].message.content  # Correct way to access content

# Example student submissions
submissions = [
    {"question": "What is supervised learning?", "answer": "A type of machine learning where the model learns from labeled data."},
    {"question": "What is the purpose of Python's __init__ method?", "answer": "It is used to initiate a loop."},
    {"question": "What is the significance of p-value in hypothesis testing?", "answer": "It shows the percentage of the data analyzed."}
]

# Model names (replace with your deployment names)
gpt35_model = "gpt-35-turbo-0125-ft-autograding"  # Example GPT-3.5 model deployment name
gpt4_model = "gpt-4o-2024-08-finetuned_autograding"  # Example GPT-4 model deployment name

# Run the evaluation for both models and print results side-by-side
for submission in submissions:
    question = submission["question"]
    answer = submission["answer"]

    # Get feedback from both models
    feedback_gpt35 = evaluate_submission_with_model(gpt35_model, question, answer)
    feedback_gpt4 = evaluate_submission_with_model(gpt4_model, question, answer)

    # Print the comparison results
    print(f"Question: {question}")
    print(f"Student Answer: {answer}\n")
    print(f"GPT-3.5 Feedback: {feedback_gpt35}")
    print(f"GPT-4 Feedback: {feedback_gpt4}")
    print("-" * 50)