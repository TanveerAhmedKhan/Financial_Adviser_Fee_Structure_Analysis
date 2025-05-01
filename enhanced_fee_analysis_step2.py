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

def process_flat_fee(fee_str):
    """
    Process flat fee information
    Returns has_flat_fee (0/1) and flat_fee_value
    """
    if pd.isna(fee_str) or fee_str.lower() == 'no' or fee_str.strip() == '':
        return 0, None
    
    # Check for percentage
    pct_match = re.search(r'(\d+\.?\d*)%', str(fee_str))
    if pct_match:
        return 1, float(pct_match.group(1))
    
    # Check for dollar amount
    dollar_match = re.search(r'\$(\d+,?\d*\.?\d*)', str(fee_str))
    if dollar_match:
        # Remove commas and convert to float
        amount = dollar_match.group(1).replace(',', '')
        return 1, float(amount)
    
    # If it's just "Yes" or some other indication
    if str(fee_str).lower() in ['yes', 'y', 'true']:
        return 1, None
    
    # Try to extract any number
    num_match = re.search(r'(\d+\.?\d*)', str(fee_str))
    if num_match:
        return 1, float(num_match.group(1))
    
    # If we can't parse it but it's not "No"
    return 1, None

# Load the results from step 1
df = pd.read_csv('step1_adviser_info.csv')
print(f"Loaded CSV with {len(df)} rows")

# Process flat fee
flat_fee_results = df['Flat Fee'].apply(process_flat_fee)
df['has_flat_fee'] = [x[0] for x in flat_fee_results]
df['flat_fee_value'] = [x[1] for x in flat_fee_results]

# Display summary of flat fee processing
flat_fee_count = df['has_flat_fee'].sum()
print(f"\nFlat fee summary:")
print(f"Total advisers with flat fee: {flat_fee_count} ({flat_fee_count/len(df)*100:.1f}%)")

# Display distribution of flat fee values
print("\nFlat fee value distribution:")
print(df[df['has_flat_fee'] == 1]['flat_fee_value'].describe())

# Save the results to a new CSV file
df.to_csv('step2_flat_fee.csv', index=False)
print("\nSaved results to step2_flat_fee.csv")
