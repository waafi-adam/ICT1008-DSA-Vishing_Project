import pandas as pd

df = pd.read_csv('Project/cs/Dataset/df_data.csv')


# Filter df to fraud only
filtered_df = df[df['Label'] == 0]

'''
numrows = len(filtered_df)

filtered_df.insert(0, 'id', range(351, 351+numrows))

filtered_df = filtered_df.rename(
    columns={'id': 'id', 'translated_words': 'Non_Frauds'})

filtered_df['text'] = df['translated_words'].str.replace('"', '')

filtered_df.drop('Label', axis=1, inplace=True)

filtered_df.to_csv('Project/cs/Merging/Fraud.csv', index=False)
'''

#Filter for waafi's codes
filtered_df.drop('Label', axis=1, inplace=True)

filtered_df = filtered_df.rename(
    columns={'translated_words': 'Non_Frauds'})

filtered_df.to_csv('Project/cs/Merging/NonFraud.csv', index=False)