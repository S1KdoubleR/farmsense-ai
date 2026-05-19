import pandas as pd
df = pd.read_csv('data/crop_data.csv')
print('Rows:', len(df), '  Crops:', df['label'].nunique())
print(df['label'].value_counts().to_string())
print(df.head(3).to_string())
