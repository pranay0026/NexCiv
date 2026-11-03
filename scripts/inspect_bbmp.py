import sys
import pandas as pd
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('bbmp_test.csv.gz', compression='gzip', nrows=20000)
print('Total read:', len(df))
print('Sub Category counts:')
print(df['Sub Category'].value_counts().head(15))
print('\nUnique Wards:', df['Ward Name'].nunique())
print('Sample Rows:')
for i in range(5):
    r = df.iloc[i]
    print(f"ID={r['Complaint ID']}, SubCategory={r['Sub Category']}, Ward={r['Ward Name']}, Date={r['Grievance Date']}")
