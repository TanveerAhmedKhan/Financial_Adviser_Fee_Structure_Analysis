import pandas as pd
import numpy as np
import re
from datetime import datetime

def extract_adviser_info(filename):
    """
    Extract adviser IDs and filing date from filename
    Format: formadv_part2_1_extracted\ID1_ID2_SequenceNum_Date_fees_section.txt.txt
    """
    pattern = r'formadv_part2_1_extracted\\(\d+)_(\d+)_(\d+)_(\d+)_fees_section'
    match = re.search(pattern, filename)
    
    if match:
        adviser_id1 = int(match.group(1))
        adviser_id2 = int(match.group(2))
        sequence_num = int(match.group(3))
        date_str = match.group(4)
        
        # Convert YYYYMMDD to datetime
        if len(date_str) == 8:
            filing_date = datetime.strptime(date_str, '%Y%m%d')
        else:
            filing_date = None
            
        return {
            'adviser_id1': adviser_id1,
            'adviser_id2': adviser_id2,
            'sequence_num': sequence_num,
            'filing_date': filing_date
        }
    
    return {
        'adviser_id1': None,
        'adviser_id2': None,
        'sequence_num': None,
        'filing_date': None
    }

# Test the function with a sample filename
sample_filename = "formadv_part2_1_extracted\\10046_47037_1_20110331_fees_section.txt.txt"
result = extract_adviser_info(sample_filename)
print(f"Extracted adviser info: {result}")

# Load the CSV file
df = pd.read_csv('fee_analysis_formadv_part2_1_extracted.csv')
print(f"Loaded CSV with {len(df)} rows")

# Extract adviser info from filenames
df['filename'] = df['File Name']
adviser_info = df['filename'].apply(extract_adviser_info)

# Convert adviser_info dictionary to columns
adviser_df = pd.DataFrame(adviser_info.tolist())
df = pd.concat([df, adviser_df], axis=1)

# Display the first few rows with extracted adviser info
print("\nFirst few rows with extracted adviser info:")
print(df[['File Name', 'adviser_id1', 'adviser_id2', 'sequence_num', 'filing_date']].head())

# Save the results to a new CSV file
df.to_csv('step1_adviser_info.csv', index=False)
print("\nSaved results to step1_adviser_info.csv")
