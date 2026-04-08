import json
import re
import pandas as pd

# 1. Load the JSON data
with open('raw_data/plot_data.json', 'r') as file:
    plot_data = json.load(file)

# 2. Navigate to the 'text' array in the second trace
# Note: data[0] is the fill area, data[1] contains the hover text
text_array = plot_data['x']['data'][1]['text']

# 3. Use Regex to extract the Force (N) and Percentile values
# Matches "Result: <number> N" and "Percentile: <number>"
pattern = re.compile(r"Result:\s*([\d.]+)\ss*<br />Percentile:\s*([\d.]+)")

extracted_data = []
for item in text_array:
    match = pattern.search(item)
    if match:
        result_n = float(match.group(1))
        percentile = float(match.group(2))
        extracted_data.append({'Result_N': result_n, 'Percentile': percentile})

# 4. Convert to a Pandas DataFrame
df = pd.DataFrame(extracted_data)

# 5. Filter for integer percentiles 1-100
# Since the plot has fractional percentiles (e.g., 1.3, 1.4), we round to the nearest integer
df['Integer_Percentile'] = df['Percentile'].round().astype(int)

# Keep only 1-100 and drop duplicate rounded percentiles (keeping the first match)
final_df = df[(df['Integer_Percentile'] >= 1) & (df['Integer_Percentile'] <= 100)]
final_df = final_df.drop_duplicates(subset=['Integer_Percentile'], keep='first')

# Reorder columns and reset index
final_df = final_df[['Integer_Percentile', 'Result_N']].reset_index(drop=True)

# 6. Export to CSV (Ready for Excel or Teamworks AMS)
final_df.to_csv('contact_time_normative_percentiles_1_to_100.csv', index=False)
print("Extraction complete. File saved as 'contact_time_normative_percentiles_1_to_100.csv'.")