import pandas as pd
import numpy as np
import re
from datetime import datetime

def process_minimum_investment(min_inv_str):
    """
    Process minimum investment information
    Returns has_min_inv (0/1) and min_inv_amount
    """
    if pd.isna(min_inv_str) or str(min_inv_str).lower() in ['no', 'n/a', 'na', '-1', ''] or min_inv_str == '':
        return 0, None
    
    min_inv_str = str(min_inv_str)
    
    # Check for dollar amount
    dollar_match = re.search(r'\$(\d+,?\d*\.?\d*)', min_inv_str)
    if dollar_match:
        # Remove commas and convert to float
        amount = dollar_match.group(1).replace(',', '')
        return 1, float(amount)
    
    # Try to extract any number
    num_match = re.search(r'(\d+,?\d*\.?\d*)', min_inv_str)
    if num_match:
        amount = num_match.group(1).replace(',', '')
        return 1, float(amount)
    
    # If it's just "Yes" or some other indication
    if min_inv_str.lower() in ['yes', 'y', 'true']:
        return 1, None
    
    return 0, None

def process_negotiable(neg_str):
    """
    Process negotiable fee information
    Returns is_negotiable (0/1)
    """
    if pd.isna(neg_str) or neg_str == '':
        return 0
    
    neg_str = str(neg_str).lower()
    if neg_str in ['yes', 'y', 'true', 'negotiable']:
        return 1
    
    return 0

def process_negotiable_threshold(neg_thresh_str):
    """
    Process negotiable threshold information
    Returns has_neg_thresh (0/1) and neg_thresh_amount
    """
    if pd.isna(neg_thresh_str) or str(neg_thresh_str).lower() in ['no', 'n/a', 'na', '-1', ''] or neg_thresh_str == '':
        return 0, None
    
    neg_thresh_str = str(neg_thresh_str)
    
    # Check for dollar amount
    dollar_match = re.search(r'\$(\d+,?\d*\.?\d*)', neg_thresh_str)
    if dollar_match:
        # Remove commas and convert to float
        amount = dollar_match.group(1).replace(',', '')
        return 1, float(amount)
    
    # Try to extract any number
    num_match = re.search(r'(\d+,?\d*\.?\d*)', neg_thresh_str)
    if num_match:
        amount = num_match.group(1).replace(',', '')
        return 1, float(amount)
    
    return 0, None

# Load the results from step 3
df = pd.read_csv('step3_fee_structure.csv')
print(f"Loaded CSV with {len(df)} rows")

# Process minimum investment
min_inv_col = 'Minimum investment (Amount/No)'
if min_inv_col in df.columns:
    min_inv_results = df[min_inv_col].apply(process_minimum_investment)
    df['has_min_investment'] = [x[0] for x in min_inv_results]
    df['min_investment_amount'] = [x[1] for x in min_inv_results]

# Process negotiable
neg_col = 'Negotiable (Yes/No)'
if neg_col in df.columns:
    df['is_negotiable'] = df[neg_col].apply(process_negotiable)

# Process negotiable threshold
neg_thresh_col = 'Negotiable threshold (Number/ N/A)'
if neg_thresh_col in df.columns:
    neg_thresh_results = df[neg_thresh_col].apply(process_negotiable_threshold)
    df['has_negotiable_threshold'] = [x[0] for x in neg_thresh_results]
    df['negotiable_threshold_amount'] = [x[1] for x in neg_thresh_results]

# Display summary of minimum investment
min_inv_count = df['has_min_investment'].sum()
print(f"\nMinimum investment summary:")
print(f"Total advisers with minimum investment: {min_inv_count} ({min_inv_count/len(df)*100:.1f}%)")
print("\nMinimum investment amount distribution:")
print(df[df['has_min_investment'] == 1]['min_investment_amount'].describe())

# Display summary of negotiable fees
negotiable_count = df['is_negotiable'].sum()
print(f"\nNegotiable fee summary:")
print(f"Total advisers with negotiable fees: {negotiable_count} ({negotiable_count/len(df)*100:.1f}%)")

# Display summary of negotiable thresholds
neg_thresh_count = df['has_negotiable_threshold'].sum()
print(f"\nNegotiable threshold summary:")
print(f"Total advisers with negotiable thresholds: {neg_thresh_count} ({neg_thresh_count/len(df)*100:.1f}%)")
print("\nNegotiable threshold amount distribution:")
print(df[df['has_negotiable_threshold'] == 1]['negotiable_threshold_amount'].describe())

# Save the results to a new CSV file
df.to_csv('step4_min_inv_negotiable.csv', index=False)
print("\nSaved results to step4_min_inv_negotiable.csv")
