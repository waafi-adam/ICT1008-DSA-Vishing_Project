from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import spacy
from nltk.corpus import stopwords
import string
import re
from cosine_sim import calculate_similarity

from collections import Counter


def preprocess_sentence(sentence):
    # Remove special characters
    sentence = re.sub(r"[^\w\s']", "", sentence)
    # Tokenize the sentence into words
    tokens = word_tokenize(sentence)
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token.lower() not in stop_words]
    # Remove punctuations
    tokens = [token for token in tokens if token not in string.punctuation]
    # Join the tokens back into a sentence string
    preprocessed_sentence = " ".join(tokens)
    # Manually remove single quotation marks
    preprocessed_sentence = preprocessed_sentence.replace("'", "")
    return preprocessed_sentence


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


# Function to preprocess and tokenize text
def tokenize_text(text):
    # Convert to lower case
    text = text.lower()

    # Remove salutations and names following them
    text = re.sub(r"(mr|mrs|ms|miss|dr|prof|officer)\.\s+\w+", "", text)

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize - convert from string to list of words
    tokens = text.split()

    # Calculate total number of tokens before removing stop words
    word_count = len(tokens)

    # Filter out stopwords, greetings, pronouns
    with open("stopwords_greetings_pronouns.txt", "r") as f:
        stop_words = f.read().splitlines()
    words = [w for w in tokens if not w in stop_words]

    return words, word_count


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
            j = failure[j - 1]
        if word[i] == word[j]:
            j += 1
        failure.append(j)
    return failure


def spamLikelihood(refSent):
    # Load the datasets
    spam_df = pd.read_csv("spam_dataset.csv")
    nonspam_df = pd.read_csv("non_spam_dataset.csv")
    fraud_df = pd.read_csv("preprocessfraudtest.csv")

    # Preprocess and tokenize text
    spam_df["Transcript"], spam_df["Word_Count"] = zip(
        *spam_df["Transcript"].apply(tokenize_text)
    )
    nonspam_df["Non_Spams"], nonspam_df["Word_Count"] = zip(
        *nonspam_df["Non_Spams"].apply(tokenize_text)
    )
    fraud_df["text"], fraud_df["Word_Count"] = zip(
        *fraud_df["text"].apply(tokenize_text)
    )

    # Calculate total words
    total_words_spam = spam_df["Word_Count"].sum()
    total_words_nonspam = nonspam_df["Word_Count"].sum()
    total_words_fraud = fraud_df["Word_Count"].sum()

    # Calculate word frequencies
    spam_word_freq = calculate_frequencies(spam_df, "Transcript")
    nonspam_word_freq = calculate_frequencies(nonspam_df, "Non_Spams")
    fraud_word_freq = calculate_frequencies(fraud_df, "text")

    # Remove common words from the spam word frequencies based on the non-spam word frequencies
    for word in nonspam_word_freq:
        if word in spam_word_freq:
            del spam_word_freq[word]

    for word in nonspam_word_freq:
        if word in fraud_word_freq:
            del fraud_word_freq[word]

    # Combine fraud word frequencies with spam word frequencies
    combined_word_freq = spam_word_freq.copy()  # Make a copy of spam_word_freq
    for word, freq in fraud_word_freq.items():
        combined_word_freq[word] = {"freq": freq}

    # Get top 20 words for each spam type
    top_n = 20
    spam_types = spam_df["Spam_Type"].unique()
    top_words = {spam_type: {} for spam_type in spam_types}

    for spam_type in spam_types:
        # Filter spam words by spam type
        spam_type_words = spam_df[spam_df["Spam_Type"] == spam_type][
            "Transcript"
        ].explode()
        # Count the word frequencies and get the top n words
        top_spam_type_words = spam_type_words.value_counts().head(top_n)

        for word, freq in top_spam_type_words.items():
            # Prepare failure function for KMP
            failure_function = prepare_failure_function(word)
            top_words[spam_type][word] = {
                "freq": freq,
                "failure_function": failure_function,
            }

    # Now you can use `top_words` dictionary in your further analysis

    # print(top_words)

    # Input samples
    input_samples = [refSent]

    # Calculate the sum of the word frequencies in top_words
    # sum_freq_top_words = sum(word_info['freq'] for spam_type in top_words for word_info in top_words[spam_type].values())

    # Calculate the sum of the word frequencies in combined_word_freq
    sum_freq_combined_words = sum(
        word_info.get("freq", 0)
        for word_info in combined_word_freq.values()
        if isinstance(word_info, dict)
    )

    # Calculate the percentages
    # perc_top_words_spam = (sum_freq_top_words / total_words_spam) * 100
    # perc_top_words_nonspam = (sum_freq_top_words / total_words_nonspam) * 100

    # Calculate the percentages
    perc_combined_words_spam = (sum_freq_combined_words / total_words_spam) * 100
    perc_combined_words_nonspam = (sum_freq_combined_words / total_words_nonspam) * 100

    # Loop through input samples
    for idx, input_sample in enumerate(input_samples, 1):
        # Prepare text input
        text = re.sub(r"\W+", " ", input_sample.lower())
        total_matches = 0
        spam_type_matches = {spam_type: 0 for spam_type in spam_types}

        # Apply KMP algorithm to each word in our `top_words` object
        for spam_type in spam_types:
            for word, word_info in top_words[spam_type].items():
                matches = kmp_search(text, word, word_info["failure_function"])
                total_matches += matches
                spam_type_matches[spam_type] += matches

        # Calculate percentage of matches
        perc_matches = (total_matches / len(text.split())) * 100 if total_matches else 0

        # Determine spam likelihood based on comparison with calculated percentage for top spam words
        spam_likelihood = (perc_matches / perc_combined_words_spam) * 100
        # Ensuring the percentage stays in the range [0, 100]
        spam_likelihood = max(0, min(100, spam_likelihood))

        # Identify most likely spam type
        most_likely_spam_type = max(spam_type_matches, key=spam_type_matches.get)

        # print(f"Input Sample {idx}:")
        # print(f"Text: {input_sample}")
        print(f"Likelihood of spam: {spam_likelihood:.2f}%")
        print(f"Most likely spam type: {most_likely_spam_type}")

    return spam_likelihood


def vishingProg(statement):
    nlp = spacy.load("en_core_web_lg")

    # Load the fraud dataset
    fraudDataSet = pd.read_csv("fraudtest.csv")
    # Preprocess the "text" column using the preprocess_sentence function
    fraudDataSet["text"] = fraudDataSet["text"].apply(preprocess_sentence)
    # Save the preprocessed dataset to a new CSV file
    fraudDataSet.to_csv("preprocessfraudtest.csv", index=False, columns=["id", "text"])

    # Load the non-fraud dataset
    nonFraudDataSet = pd.read_csv("nonfraudtest.csv")
    # Preprocess the "text" column using the preprocess_sentence function
    nonFraudDataSet["text"] = nonFraudDataSet["text"].apply(preprocess_sentence)
    # Save the preprocessed dataset to a new CSV file
    nonFraudDataSet.to_csv(
        "preprocessnonfraudtest.csv", index=False, columns=["id", "text"]
    )

    # Define the reference sentence
    refSentence = statement
    preprocessedRefSentence = preprocess_sentence(refSentence)

    totalFraudSimilarity = 0.0
    numFraudSentences = 0
    # Iterate through each row of the fraud dataset
    for index, row in fraudDataSet.iterrows():
        sentence = row["text"]
        similarity = calculate_similarity(sentence, preprocessedRefSentence)
        totalFraudSimilarity += similarity
        numFraudSentences += 1

    if numFraudSentences > 0:
        avgFraudSimilarity = totalFraudSimilarity / numFraudSentences
    else:
        avgFraudSimilarity = 0.0

    # print("Average fraud similarity:", avgFraudSimilarity)

    totalNonFraudSimilarity = 0.0
    numNonFraudSentences = 0
    # Iterate through each row of the non-fraud dataset
    for index, row in nonFraudDataSet.iterrows():
        sentence = row["text"]
        similarity = calculate_similarity(sentence, preprocessedRefSentence)
        totalNonFraudSimilarity += similarity
        numNonFraudSentences += 1

    if numNonFraudSentences > 0:
        avgNonFraudSimilarity = totalNonFraudSimilarity / numNonFraudSentences
    else:
        avgNonFraudSimilarity = 0.0

    # print("Average non-fraud similarity:", avgNonFraudSimilarity)

    # Normalize the similarity scores to the range [0, 1]
    similarity_range = max(avgFraudSimilarity, avgNonFraudSimilarity) - min(
        avgFraudSimilarity, avgNonFraudSimilarity
    )
    if similarity_range > 0:
        normalizedFraudSimilarity = (
            avgFraudSimilarity - min(avgFraudSimilarity, avgNonFraudSimilarity)
        ) / similarity_range
        normalizedNonFraudSimilarity = (
            avgNonFraudSimilarity - min(avgFraudSimilarity, avgNonFraudSimilarity)
        ) / similarity_range
    else:
        normalizedFraudSimilarity = 0.0
        normalizedNonFraudSimilarity = 0.0

    print("Normalized fraud similarity:", normalizedFraudSimilarity)
    print("Normalized non-fraud similarity:", normalizedNonFraudSimilarity)

    # prediction = normalizedFraudSimilarity * 100
    # print("Vishing prediction:", prediction)

    # ======================================================================

    if normalizedFraudSimilarity > 0 and normalizedNonFraudSimilarity < 1:
        # refSentence = nlp(refSentence)
        # fraudDataSet = [nlp(row) for row in fraudDataSet["text"]]
        # sims = []
        # docId = []
        # for i in range(len(fraudDataSet)):
        #     sentence = row["text"]
        #     # Preprocess the sentence
        #     preprocessedSentence = preprocess_sentence(sentence)
        #     # Calculate similarity using spaCy
        #     similarity = nlp(preprocessedSentence).similarity(
        #         nlp(preprocessedRefSentence)
        #     )
        #     sims.append(similarity)
        #     docId.append(index)
        # # Create a DataFrame to store document IDs and similarity scores
        # simsDocs = pd.DataFrame(
        #     list(zip(docId, sims)), columns=["doc_id", "similarity"]
        # )
        # # Calculate the total percentage value
        # total_similarity_percentage = sum(sims) / len(sims) * 100
        # # print("Total similarity percentage:", total_similarity_percentage)
        # return total_similarity_percentage
        return spamLikelihood(refSentence)
    else:
        return 0


input_samples = [
    "Hi, this is a courtesy call to remind you about your upcoming appointment with the dentist.",
    "Hello, we are calling to confirm your reservation for the upcoming workshop.",
    "Urgent! Your social media account has been hacked. Provide your login credentials for immediate assistance.",
    "Good evening! We are calling to inform you about a special promotion at our store.",
    "Congratulations! You have won a shopping spree. Share your personal information to claim it.",
    "Hello, I'm calling from your internet service provider to discuss an upgrade option.",
    "Hi, this is a reminder to review your recent purchase on our online store.",
    "Your account has been compromised. Share your username and password to secure it.",
    "Good day! We are conducting a customer feedback survey to improve our services.",
    "You have won a free vacation package. Provide your personal details to claim it.",
    "Hello, we are calling to schedule a maintenance appointment for your vehicle.",
    "We have noticed suspicious activity on your bank account. Please confirm your details for verification.",
    "This is a courtesy call to inform you about an upcoming event in your area.",
    "You are selected as the winner of our monthly lottery. Kindly provide your information to claim the prize.",
    "We have detected a virus on your computer. Please provide remote access for immediate removal.",
    "Hello, we are calling from the credit card company to offer you a lower interest rate.",
    "You have won a free trip to a tropical paradise. Share your personal details to claim your prize.",
    "This is a reminder to renew your subscription before it expires.",
    "Congratulations! Your mobile number has been chosen as the lucky winner. Provide your details for verification.",
    "We are calling to discuss an exclusive investment opportunity. Please share your financial information.",
    "Your package delivery is scheduled for tomorrow. Confirm your availability for a smooth delivery process.",
    "You have been selected for a survey. Share your opinions to win exciting rewards.",
    "We are calling to inform you about a discount offer on your favorite products.",
    "Your bank account has been locked. Provide your account details to unlock it.",
    "You have been pre-approved for a credit card. Share your personal information to proceed with the application.",
    "This is a courtesy call to remind you about your upcoming bill payment.",
    "You are the lucky winner of a luxury car. Share your information to claim your prize.",
    "We have noticed unauthorized activity on your PayPal account. Please provide your account details for verification.",
    "Hello, we are calling to invite you to our exclusive VIP event. RSVP to secure your spot.",
    "Your credit card has been charged for an expensive purchase. Call us immediately to cancel and secure your account.",
    "You have won a cash prize. Provide your bank account details for the prize transfer.",
    "We are conducting a short survey on customer satisfaction. Share your feedback for a chance to win a gift card.",
    "Congratulations! You have been selected for a free home security system. Provide your address for installation.",
    "Your computer has been infected with malware. Call our technical support for immediate assistance.",
    "We are calling to confirm your appointment with the doctor tomorrow.",
    "You have won a dream vacation. Share your personal information to claim your prize.",
    "This is a courtesy call to inform you about a change in your flight schedule.",
    "You are eligible for a free upgrade on your mobile phone plan. Call us to avail the offer.",
    "Your credit card has been blocked due to suspiciousactivity. Provide your card details to unblock it.",
    "Hello, we are calling to offer you a special discount on your next purchase.",
    "You have won a gift voucher. Share your details to claim your prize.",
    "We have detected a security breach in your email account. Provide your password for immediate resolution.",
    "Good afternoon! We are conducting a survey to gather feedback on our recent product release.",
    "You have been selected for a free trial of our premium membership. Provide your details to activate it.",
    "We are calling to remind you about the upcoming deadline for your bill payment.",
    "Congratulations! You have won a brand new smartphone. Share your information to claim it.",
    "This is a courtesy call to inform you about an exciting event happening in your city.",
    "You have been randomly selected for a customer satisfaction survey. Share your feedback to win a prize.",
    "We are calling to inform you about a limited-time offer on your favorite clothing brand.",
    "Your bank account is suspected of fraudulent activity. Share your account details for investigation.",
    "You have won a trip to a luxury resort. Provide your personal information to book your stay.",
    "This is a reminder to update your password for better account security.",
    "You are eligible for a special discount on your next flight booking. Call us to avail the offer.",
    "Your credit card has been charged for an unauthorized transaction. Call us immediately to report and reverse it.",
    "You have won a gift card. Share your details to receive your prize.",
    "We are conducting a market research survey. Share your opinions for a chance to win a reward.",
    "Congratulations! You have won a cash prize. Provide your bank account details for the prize transfer.",
    "This is a courtesy call to remind you about your upcoming subscription renewal.",
    "You have been selected for a free home makeover. Provide your address for a consultation.",
    "We have detected a virus on your phone. Please provide remote access for immediate removal.",
    "We are calling to confirm your appointment with the hairstylist.",
    "You have won a luxury cruise vacation. Share your personal information to claim your prize.",
    "Hello, we are calling to inform you about a change in your credit card terms and conditions.",
    "You have been selected for a loyalty program. Provide your details to enroll and enjoy exclusive benefits.",
    "Your email account has been temporarily suspended. Provide your account information to reactivate it.",
    "We are calling to remind you about the upcoming deadline for your tax filing.",
    "You have won a discount voucher for your favorite restaurant. Share your details to receive it.",
    "This is a courtesy call to inform you about a product recall for safety reasons.",
    "You have been selected for a free trial of our software. Provide your details to activate the trial.",
    "We are calling to offer you a complimentary magazine subscription. Provide your address to receive it.",
    "Your credit card has been randomly selected for a cashback offer. Share your details to avail it.",
    "You have won a gift hamper. Share your details to receive your prize.",
    "We are conducting a survey on consumer preferences. Share your feedback to win a reward.",
    "Congratulations! You have won a vacation package. Provide your personal information to claim it.",
    "This is a courtesy call to remind you about your upcoming doctor's appointment.",
    "You have been chosen as a beta tester for our new mobile app. Provide your details to participate.",
    "We are calling to inform you about a special discount on your favorite online store.",
    "Your bank account needs verification. Share your account details to complete the process.",
    "You have won a gift card for your favoriterestaurant. Share your details to receive it.",
    "This is a courtesy call to inform you about a product recall for safety reasons.",
    "You have been selected for a free trial of our software. Provide your details to activate the trial.",
    "We are calling to offer you a complimentary magazine subscription. Provide your address to receive it.",
    "Your credit card has been randomly selected for a cashback offer. Share your details to avail it.",
    "You have won a gift hamper. Share your details to receive your prize.",
    "We are conducting a survey on consumer preferences. Share your feedback to win a reward.",
    "Congratulations! You have won a vacation package. Provide your personal information to claim it.",
    "This is a courtesy call to remind you about your upcoming doctor's appointment.",
    "You have been chosen as a beta tester for our new mobile app. Provide your details to participate.",
    "We are calling to inform you about a special discount on your favorite online store.",
    "Your bank account needs verification. Share your account details to complete the process.",
    "You have won a gift card for your favorite restaurant. Share your details to receive it.",
    "This is a reminder to update your password for better account security.",
    "You are eligible for a special discount on your next flight booking. Call us to avail the offer.",
    "Your credit card has been charged for an unauthorized transaction. Call us immediately to report and reverse it.",
    "You have won a gift card. Share your details to receive your prize.",
    "We are conducting a market research survey. Share your opinions for a chance to win a reward.",
    "Congratulations! You have won a cash prize. Provide your bank account details for the prize transfer.",
    "This is a courtesy call to remind you about your upcoming subscription renewal.",
    "You have been selected for a free home makeover. Provide your address for a consultation.",
    "We have detected a virus on your phone. Please provide remote access for immediate removal.",
    "We are calling to confirm your appointment with the hairstylist.",
    "You have won a luxury cruise vacation. Share your personal information to claim your prize.",
    "Hello, we are calling to inform you about a change in your credit card terms and conditions.",
    "You have been selected for a loyalty program. Provide your details to enroll and enjoy exclusive benefits.",
    "Your email account has been temporarily suspended. Provide your account information to reactivate it.",
    "We are calling to remind you about the upcoming deadline for your tax filing.",
    "You have won a discount voucher for your favorite restaurant. Share your details to receive it.",
    "This is a courtesy call to inform you about a product recall for safety reasons.",
    "You have been selected for a free trial of our software. Provide your details to activate the trial.",
    "We are calling to offer you a complimentary magazine subscription. Provide your address to receive it.",
    "Your credit card has been randomly selected for a cashback offer. Share your details to avail it.",
    "You have won a gift hamper. Share your details to receive your prize.",
    "We are conducting a survey on consumer preferences. Share your feedback to win a reward.",
    "Congratulations! You have won a vacation package. Provide your personal information to claim it.",
    "This is a courtesy call to remind you about your upcoming doctor's appointment.",
    "You have been chosen as a beta tester for our new mobile app. Provide your details to participate.",
    "We are calling to inform you about a special discount on your favorite online store.",
    "Your bank account needs verification. Share your account details to complete the process.",
    "You have won a gift card for your favoriterestaurant. Share your details to receive it.",
    "This is a reminder to update your password for better account security.",
    "You are eligible for a special discount on your next flight booking. Call us to avail the offer.",
    "Your credit card has been charged for an unauthorized transaction. Call us immediately to report and reverse it.",
    "You have won a gift card. Share your details to receive your prize.",
    "We are conducting a market research survey. Share your opinions for a chance to win a reward.",
    "Congratulations! You have won a cash prize. Provide your bank account details for the prize transfer.",
    "This is a courtesy call to remind you about your upcoming subscription renewal.",
    "You have been selected for a free home makeover. Provide your address for a consultation.",
    "We have detected a virus on your phone. Please provide remote access for immediate removal.",
    "We are calling to confirm your appointment with the hairstylist.",
    "You have won a luxury cruise vacation. Share your personal information to claim your prize.",
    "Hello, we are calling to inform you about a change in your credit card terms and conditions.",
    "You have been selected for a loyalty program. Provide your details to enroll and enjoy exclusive benefits.",
    "Your email account has been temporarily suspended. Provide your account information to reactivate it.",
    "We are calling to remind you about the upcoming deadline for your tax filing.",
    "You have won a discount voucher for your favorite restaurant. Share your details to receive it.",
    "This is a courtesy call to inform you about a product recall for safety reasons.",
    "You have been selected for a free trial of our software. Provide your details to activate the trial.",
    "We are calling to offer you a complimentary magazine subscription. Provide your address to receive it.",
    "Your credit card has been randomly selected for a cashback offer. Share your details to avail it.",
    "You have won a gift hamper. Share your details to receive your prize.",
    "We are conducting a survey on consumer preferences. Share your feedback to win a reward.",
    "Congratulations! You have won a vacation package. Provide your personal information to claim it.",
    "This is a courtesy call to remind you about your upcoming doctor's appointment.",
    "You have been chosen as a beta tester for our new mobile app. Provide your details to participate.",
    "We are calling to inform you about a special discount on your favorite online store.",
    "Your bank account needs verification. Share your account details to complete the process.",
    "You have won a gift card for your favorite restaurant. Share your details to receive it.",
]


totalSim = 0
num_sentences = len(input_samples)

for sentence in input_samples:
    print("============ testing ============")
    print("Current Input: ", sentence)
    totalSim = totalSim + vishingProg(sentence)


print(totalSim / num_sentences)

# print(vishingProg("You have won a gift card for your favorite restaurant. Share your details to receive it."))
