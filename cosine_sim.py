def preprocess_sentence(sentence):
    # Remove punctuation and convert to lowercase
    sentence = sentence.lower().strip()
    sentence = ''.join(c for c in sentence if c.isalnum() or c.isspace())
    return sentence

def calculate_similarity(sentence1, sentence2):
    # Preprocess the sentences
    sentence1 = preprocess_sentence(sentence1)
    sentence2 = preprocess_sentence(sentence2)

    # Tokenize the sentences into words
    words1 = sentence1.split()
    words2 = sentence2.split()

    # Create a set of unique words from both sentences
    unique_words = set(words1).union(set(words2))

    # Initialize word frequency dictionaries
    frequency1 = dict.fromkeys(unique_words, 0)
    frequency2 = dict.fromkeys(unique_words, 0)

    # Calculate word frequencies in the first sentence
    for word in words1:
        frequency1[word] += 1

    # Calculate word frequencies in the second sentence
    for word in words2:
        frequency2[word] += 1

    # Calculate the dot product and magnitudes
    dot_product = sum(frequency1[word] * frequency2[word] for word in unique_words)
    magnitude1 = sum(frequency1[word] ** 2 for word in unique_words) ** 0.5
    magnitude2 = sum(frequency2[word] ** 2 for word in unique_words) ** 0.5

    # Calculate cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)

    return similarity

# Example usage
# sentence1 = "You've been selected for a government grant. Send a small processing fee to receive the funds."
# sentence2 = "You've been selected for a government grant. Send a small processing fee to receive the funds."

# similarity_score = calculate_similarity(sentence1, sentence2)
# print(f"Similarity: {similarity_score}")
