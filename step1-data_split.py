import json
import random
import os

# Load the original dataset from the JSONL file
input_file = "./Data/autograding_conversations.jsonl"

# Verify if the input file exists
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    exit(1)

print(f"Loading dataset from: {input_file}")

with open(input_file, "r") as f:
    data = [json.loads(line) for line in f]

# Verify if the dataset is loaded
if not data:
    print("Error: Dataset is empty.")
    exit(1)

print(f"Total samples loaded: {len(data)}")

# Shuffle the data to ensure randomness
random.shuffle(data)

# Split the data into 80% training and 20% validation
split_index = int(0.8 * len(data))
training_data = data[:split_index]
validation_data = data[split_index:]

# Save the training set to 'training_set.jsonl'
training_file = "training_set.jsonl"
with open(training_file, "w") as train_file:
    for entry in training_data:
        json.dump(entry, train_file)
        train_file.write("\n")

# Verify training set creation
if os.path.exists(training_file):
    print(f"Training set saved to {training_file} with {len(training_data)} samples.")
else:
    print(f"Error: Failed to create {training_file}.")

# Save the validation set to 'validation_set.jsonl'
validation_file = "validation_set.jsonl"
with open(validation_file, "w") as val_file:
    for entry in validation_data:
        json.dump(entry, val_file)
        val_file.write("\n")

# Verify validation set creation
if os.path.exists(validation_file):
    print(f"Validation set saved to {validation_file} with {len(validation_data)} samples.")
else:
    print(f"Error: Failed to create {validation_file}.")

# Final output summary
print(f"Training set size: {len(training_data)}")
print(f"Validation set size: {len(validation_data)}")
