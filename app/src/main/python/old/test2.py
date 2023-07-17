import pandas as pd
import string
import re
from collections import Counter

# Function to preprocess and tokenize text
def tokenize_text(text):
    # Convert to lower case
    text = text.lower()

    # Remove salutations and names following them
    text = re.sub(r'(mr|mrs|ms|miss|dr|prof|officer)\.\s+\w+', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize - convert from string to list of words
    tokens = text.split()

    # Filter out stopwords, greetings, pronouns
    with open('stopwords_greetings_pronouns.txt', 'r') as f:
        stop_words = f.read().splitlines()
    words = [w for w in tokens if not w in stop_words]

    # Get word counts
    word_counts = Counter(words)

    return words, word_counts

# Function to calculate word frequencies
def calculate_frequencies(df, column):
    word_freq = Counter()
    for index, row in df.iterrows():
        word_freq.update(row[column])
    return word_freq

# Function to prepare failure function for KMP
def prepare_failure_function(word):
    failure = [0]
    j = 0
    for i in range(1, len(word)):
        while j > 0 and word[i] != word[j]:
            j = failure[j-1]
        if word[i] == word[j]:
            j += 1
        failure.append(j)
    return failure

# Load the datasets
spam_df = pd.read_csv('spam_dataset.csv')
nonspam_df = pd.read_csv('nonSpam_datasets.csv')

# Preprocess and tokenize text
spam_df['Transcript'], spam_df['Word_Counts'] = zip(*spam_df['Transcript'].apply(tokenize_text))
nonspam_df['Non_Spams'], nonspam_df['Word_Counts'] = zip(*nonspam_df['Non_Spams'].apply(tokenize_text))

# Calculate word frequencies
spam_word_freq = calculate_frequencies(spam_df, 'Transcript')
nonspam_word_freq = calculate_frequencies(nonspam_df, 'Non_Spams')

# Calculate total word counts for each spam type
spam_type_word_counts = spam_df.groupby('Spam_Type')['Word_Counts'].apply(lambda x: sum([c for wc in x for c in wc.values()]))

# Remove common words from the spam word frequencies based on the non-spam word frequencies
for word in nonspam_word_freq:
    if word in spam_word_freq:
        del spam_word_freq[word]

# Get top 20 words for each spam type
top_n = 20
spam_types = spam_df['Spam_Type'].unique()
top_words = {spam_type: {} for spam_type in spam_types}

for spam_type in spam_types:
    # Filter spam words by spam type
    spam_type_words = spam_df[spam_df['Spam_Type'] == spam_type]['Word_Counts'].explode()
    # Merge the Counters and get the top n words
    merged_word_counts = sum((Counter(item) for item in spam_type_words), Counter())
    top_spam_type_words_freqs = merged_word_counts.most_common(top_n)

    for word, freq in top_spam_type_words_freqs:
        # Prepare failure function for KMP
        failure_function = prepare_failure_function(word)
        # Calculate proportion of word in spam type
        proportion = freq / spam_type_word_counts[spam_type]
        top_words[spam_type][word] = {'failure_function': failure_function, 'proportion': proportion}

# KMP search function
def kmp_search(text, pattern, failure):
    i, j = 0, 0
    matches = 0

    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
            if j == len(pattern):
                matches += 1
                j = failure[j - 1]
        else:
            if j != 0:
                j = failure[j - 1]
            else:
                i += 1
    return matches

# Input samples
input_samples = [
    "Congratulations! You've won the grand prize of $1,000,000. Please provide your personal and bank details to claim your prize immediately.",
    "Dear Customer, we noticed some unusual activities in your account. For security purposes, please verify your account details by clicking the link below.",
    "Hello, this is a reminder to submit your tax documents by the due date. Failure to comply may result in penalties. Please ensure timely submission.",
    "URGENT: Your credit card has been compromised. We detected multiple unauthorized transactions. Please call our hotline immediately to secure your account.",
    "Hey John, hope you're doing well. Just wanted to touch base on our project. Can we have a meeting tomorrow?",
    "Congratulations on winning the annual employee award! I noticed some unusual activities in your performance, you've really stepped up your game this year!",
    "Congratulations! You've won our grand prize draw! Click the link below to claim your prize immediately. Hurry up!",
    "Congratulations! You've won our grand prize draw! Click the link below to claim your prize immediately. Hurry up!",
    "Dear Customer, you've been selected for an exclusive offer! Click below to verify your account and claim your gift.",
    "Hey there, just wanted to let you know about the new sale at our store. Also, you've been selected for a chance to win a $1,000 gift card! Click below to claim your gift."
]

# Loop through input samples
for idx, input_sample in enumerate(input_samples, 1):
    # Prepare text input
    text = re.sub(r'\W+', ' ', input_sample.lower())
    spam_type_matches = {spam_type: 0 for spam_type in spam_types}

    # Apply KMP algorithm to each word in our `word_freq` object
    for spam_type in spam_types:
        for word, info in top_words[spam_type].items():
            matches = kmp_search(text, word, info['failure_function'])
            spam_type_matches[spam_type] += matches * info['proportion']

    # Calculate likelihood of spam based on the matches found
    total_matches = sum(spam_type_matches.values())
    spam_likelihood = total_matches * 100

    # Identify most likely spam type
    most_likely_spam_type = max(spam_type_matches, key=spam_type_matches.get)

    print(f"Input Sample {idx}:")
    print(f"Text: {input_sample}")
    print(f"Likelihood of spam: {spam_likelihood:.2f}%")
    print(f"Most likely spam type: {most_likely_spam_type}")
    print()
