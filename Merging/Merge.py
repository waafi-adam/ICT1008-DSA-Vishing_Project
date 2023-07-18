import pandas as pd

df1 = pd.read_csv('Project/Waafi/test_cases.csv')
df2 = pd.read_csv('Project/cs/Merging/modified_testcases.csv')

merged_df = pd.concat([df1, df2], ignore_index=True)

merged_df.to_csv('Project/Waafi/merged_test_cases.csv', index=False)
