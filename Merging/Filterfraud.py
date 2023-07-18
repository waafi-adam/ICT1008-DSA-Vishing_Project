import pandas as pd

df = pd.read_csv('Project/cs/Dataset/df_data.csv')

# Filter df to fraud only
filtered_df = df[df['Label'] == 1]

'''
numrows = len(filtered_df)

filtered_df.insert(0, 'id', range(251, 251+numrows))

filtered_df = filtered_df.rename(
    columns={'id': 'id', 'translated_words': 'text'})

filtered_df.drop('Label', axis=1, inplace=True)

filtered_df.to_csv('Project/cs/Merging/Fraud.csv', index=False, quoting=0)
'''

#Filter for waafi's codes
filtered_df.drop('Label', axis=1, inplace=True)

filtered_df = filtered_df.rename(
    columns={'translated_words': 'Transcript'})

filtered_df.to_csv('Project/cs/Merging/Fraud.csv', index=False)
