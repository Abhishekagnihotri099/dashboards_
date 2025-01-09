# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/process_csv.py
import pandas as pd

# Define the path to the CSV file
csv_file_path = r'C:\Users\digvijay221046\Desktop\Git-AG-DJ\dashboards_\backend\backend_app\dsoutcome_0.1.csv'
output_csv_file_path = r'C:\Users\digvijay221046\Desktop\Git-AG-DJ\dashboards_\backend\backend_app\dsoutcome_0.2.csv'

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Process column names: convert to lowercase and replace spaces with underscores
df.columns = [col.lower().replace(' ', '_') for col in df.columns]

# Extract 'lob' from 'indicator_name' column
df['lob'] = df['team_name'].apply(lambda x: x.split()[0] if pd.notnull(x) else '')

# Save the processed DataFrame to a new CSV file
df.to_csv(output_csv_file_path, index=False)

print(f"Processed CSV saved to {output_csv_file_path}")