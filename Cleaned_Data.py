import pandas as pd
import numpy as np

# 1. Load the raw dataset
# Replace 'raw_dirty_cloud_resources_data.csv' with your actual file path
df = pd.read_csv('raw_dirty_cloud_resources_data.csv')

print(f"Original dataset shape: {df.shape}")

# 2. Resource_ID: Clean duplicates and force uppercase
df['Resource_ID'] = df['Resource_ID'].astype(str).str.strip().str.upper()
df = df.drop_duplicates(subset=['Resource_ID']) # Keep the first instance of a resource

# 3. Resource_Type: Standardize naming conventions
# Fixes 'VM', '  VM  ', 'virtual_machine' -> 'Virtual Machine'
df['Resource_Type'] = df['Resource_Type'].astype(str).str.strip().str.lower()
type_mapping = {
    'vm': 'Virtual Machine',
    'virtual_machine': 'Virtual Machine',
    'virtual machine': 'Virtual Machine',
    'storage': 'Storage Bucket',
    'database': 'Database Instance',
    'db': 'Database Instance'
}
df['Resource_Type'] = df['Resource_Type'].map(type_mapping).fillna('Other')

# 4. Cloud_Provider: Standardize brand names
df['Cloud_Provider'] = df['Cloud_Provider'].astype(str).str.strip().str.upper()
provider_mapping = {
    'AWS': 'AWS', 'AMAZON': 'AWS',
    'GCP': 'Google Cloud', 'GOOGLE CLOUD': 'Google Cloud',
    'AZURE': 'Azure', 'MICROSOFT AZURE': 'Azure'
}
df['Cloud_Provider'] = df['Cloud_Provider'].map(provider_mapping).fillna('Unknown')

# 5. Hourly_Cost: Strip currency signs, remove negatives, handle missing values
df['Hourly_Cost'] = df['Hourly_Cost'].astype(str).str.replace('$', '', regex=False).str.strip()
df['Hourly_Cost'] = pd.to_numeric(df['Hourly_Cost'], errors='coerce')
# Replace negative costs or missing values with the median cost
median_cost = df[df['Hourly_Cost'] > 0]['Hourly_Cost'].median()
df['Hourly_Cost'] = df['Hourly_Cost'].apply(lambda x: x if x > 0 else median_cost)

# 6. CPU_Utilization_Pct: Strip '%', remove errors, cap boundaries (0-100%)
df['CPU_Utilization_Pct'] = df['CPU_Utilization_Pct'].astype(str).str.replace('%', '', regex=False).str.strip()
df['CPU_Utilization_Pct'] = pd.to_numeric(df['CPU_Utilization_Pct'], errors='coerce')
# Drop rows where CPU utilization is fundamentally corrupted or > 100%
df = df[(df['CPU_Utilization_Pct'] >= 0) & (df['CPU_Utilization_Pct'] <= 100)]

# 7. Creation_Date: Fix corrupt date formats
df['Creation_Date'] = pd.to_datetime(df['Creation_Date'], errors='coerce')
# Fill missing/corrupted dates with a placeholder or drop them
df = df.dropna(subset=['Creation_Date'])

# 8. Save the polished file
df.to_csv('cleaned_cloud_resources_data.csv', index=False)
print(f"Cleaned dataset shape: {df.shape}")
print("Data successfully cleaned and exported!")
