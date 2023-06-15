import pandas as pd

# Load the cleaned dataset
df = pd.read_csv('cleaned_file.csv')

# Convert the 'Transcript' column back to a list of words
df['Transcript'] = df['Transcript'].apply(eval)

# Create a dictionary to store word frequencies
word_freq = {}

# Iterate over each row of the tokenized dataset
for index, row in df.iterrows():
    # Iterate over each word in the tokenized row
    for word in row['Transcript']:
        # Check if the word already exists in the dictionary
        if word in word_freq:
            # Increment its frequency by 1
            word_freq[word] += 1
        else:
            # Add the word to the dictionary with a frequency of 1
            word_freq[word] = 1

# Sort the dictionary based on frequency in descending order
sorted_word_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

# Print the top N most common words and their frequencies
top_n = 50  # Specify the number of top words you want to retrieve
for word, freq in sorted_word_freq[:top_n]:
    print(f'{word}')
