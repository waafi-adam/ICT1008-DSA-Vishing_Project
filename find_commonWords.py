import pandas as pd
import pprint

# Load the cleaned dataset
df = pd.read_csv('cleaned_file.csv')

# Convert the 'Transcript' column back to a list of words
df['Transcript'] = df['Transcript'].apply(eval)

# Create dictionaries to store word frequencies for each spam type
spam_types = df['Spam_Type'].unique()
word_freq = {spam_type: {} for spam_type in spam_types}

# Iterate over each row of the tokenized dataset
for index, row in df.iterrows():
    spam_type = row['Spam_Type']
    # Iterate over each word in the tokenized row
    for word in row['Transcript']:
        # Check if the word already exists in the dictionary for the specific spam type
        if word in word_freq[spam_type]:
            # Increment its frequency by 1
            word_freq[spam_type][word] += 1
        else:
            # Add the word to the dictionary with a frequency of 1
            word_freq[spam_type][word] = 1

# Print the top 20 most common words for each spam type in descending order
top_n = 20
for spam_type in spam_types:
    print(f'Spam Type: {spam_type}')
    sorted_word_freq = sorted(word_freq[spam_type].items(), key=lambda x: x[1], reverse=True)
    for word, freq in sorted_word_freq[:top_n]:
        print(f'{word}: {freq}')
    print()


####################################################
def kmp_algorithm(text, word_freq):
    # Initialize a list to store the failure function values
    failure = [0] * len(text)
    j = 0  # Index for the pattern

    # Preprocess the pattern to calculate the failure function values
    for i in range(1, len(text)):
        if text[i] == text[j]:
            j += 1
            failure[i] = j
        else:
            if j != 0:
                j = failure[j - 1]
                i -= 1
            else:
                failure[i] = 0

    # Count the occurrences of spam words in the text
    spam_count = 0
    for word, freq in word_freq.items():
        pattern = word.lower()
        i, j = 0, 0
        while i < len(text):
            if pattern[j] == text[i]:
                i += 1
                j += 1

                if j == len(pattern):
                    spam_count += freq[word]
                    j = failure[j - 1]
            else:
                if j != 0:
                    j = failure[j - 1]
                else:
                    i += 1

    # Calculate the likelihood of spam
    total_freq = sum(sum(spam_type_freq.values()) for spam_type_freq in word_freq.values())
    likelihood = (spam_count / total_freq) * 100

    return likelihood


# Input samples
input_samples = [
    "Congratulations! You've won the grand prize of $1,000,000. Please provide your personal and bank details to claim your prize immediately.",
    "Dear Customer, we noticed some unusual activities in your account. For security purposes, please verify your account details by clicking the link below.",
    "Hello, this is a reminder to submit your tax documents by the due date. Failure to comply may result in penalties. Please ensure timely submission.",
    "URGENT: Your credit card has been compromised. We detected multiple unauthorized transactions. Please call our hotline immediately to secure your account."
]

# Loop through input samples
for idx, input_sample in enumerate(input_samples, 1):
    likelihood = kmp_algorithm(input_sample, word_freq)
    print(f"Input Sample {idx}:")
    print(f"Text: {input_sample}")
    print(f"Likelihood of spam: {likelihood:.2f}%")
    print()
