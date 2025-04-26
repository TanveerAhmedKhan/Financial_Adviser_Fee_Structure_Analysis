import pandas as pd
import numpy as np
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_data(file_path):
    """
    Load the CSV file containing fee structure data
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded data with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def extract_adviser_info(df):
    """
    Extract adviser IDs and filing dates from the filename
    Format: formadv_part2_1_extracted\ID1_ID2_SequenceNum_Date_fees_section.txt.txt
    """
    # Create new columns for extracted information
    df['adviser_id1'] = None
    df['adviser_id2'] = None
    df['sequence_num'] = None
    df['filing_date'] = None
    
    # Extract information using regex
    pattern = r'formadv_part2_1_extracted\\(\d+)_(\d+)_(\d+)_(\d+)_fees_section'
    
    for idx, filename in enumerate(df['File Name']):
        try:
            match = re.search(pattern, filename)
            if match:
                df.loc[idx, 'adviser_id1'] = match.group(1)
                df.loc[idx, 'adviser_id2'] = match.group(2)
                df.loc[idx, 'sequence_num'] = match.group(3)
                date_str = match.group(4)
                # Convert YYYYMMDD to datetime
                if len(date_str) == 8:
                    df.loc[idx, 'filing_date'] = datetime.strptime(date_str, '%Y%m%d')
        except Exception as e:
            print(f"Error processing filename {filename}: {e}")
    
    # Convert ID columns to appropriate types
    df['adviser_id1'] = pd.to_numeric(df['adviser_id1'], errors='coerce')
    df['adviser_id2'] = pd.to_numeric(df['adviser_id2'], errors='coerce')
    df['sequence_num'] = pd.to_numeric(df['sequence_num'], errors='coerce')
    
    return df

def detect_misplaced_answers(df):
    """
    Detect and correct cases where ChatGPT placed answers in incorrect columns
    """
    # Create a new DataFrame to store corrected data
    corrected_df = df.copy()
    
    # Identify columns that should contain fee thresholds
    threshold_cols = [col for col in df.columns if 'threshold' in col.lower() or 'Annual fee range' in col]
    
    # Define patterns to identify fee thresholds
    threshold_pattern = r'(?:\$|)([0-9,.]+)(?:\s*-\s*\$|[\s+])([0-9,.+]+|\+)(?:.*?\(|.*?)([0-9.]+)(?:%|\s*-\s*[0-9.]+%|\))'
    
    # Track misplaced answers
    misplaced_count = 0
    
    # Check each row for misplaced answers
    for idx, row in df.iterrows():
        # Check if there are empty threshold columns but fee information in other columns
        empty_thresholds = sum(1 for col in threshold_cols if pd.isna(row[col]) or row[col] == '-1' or row[col] == 'N/a')
        
        if empty_thresholds == len(threshold_cols):
            # All threshold columns are empty, check other columns for fee information
            for col in df.columns:
                if col in threshold_cols or col == 'File Name':
                    continue
                    
                value = row[col]
                if pd.isna(value) or value == '-1':
                    continue
                    
                # Check if the value matches a fee threshold pattern
                if isinstance(value, str) and re.search(threshold_pattern, value):
                    # Found a misplaced answer
                    print(f"Found misplaced fee threshold in row {idx}, column '{col}': {value}")
                    
                    # Find the first empty threshold column
                    for threshold_col in threshold_cols:
                        if pd.isna(row[threshold_col]) or row[threshold_col] == '-1' or row[threshold_col] == 'N/a':
                            # Move the value to the threshold column
                            corrected_df.loc[idx, threshold_col] = value
                            corrected_df.loc[idx, col] = np.nan
                            misplaced_count += 1
                            break
    
    print(f"Corrected {misplaced_count} misplaced answers")
    
    return corrected_df

def extract_fee_structures(df):
    """
    Extract and structure fee information from the threshold columns
    """
    # Create a new DataFrame to store structured fee data
    fee_df = pd.DataFrame()
    
    # Add identifier columns
    fee_df['File Name'] = df['File Name']
    fee_df['adviser_id1'] = df['adviser_id1']
    fee_df['adviser_id2'] = df['adviser_id2']
    fee_df['filing_date'] = df['filing_date']
    
    # Identify threshold columns
    threshold_cols = [col for col in df.columns if 'threshold' in col.lower() or 'Annual fee range' in col]
    
    # Define pattern to extract fee information
    threshold_pattern = r'(?:\$|)([0-9,.]+)(?:\s*-\s*\$|[\s+])([0-9,.+]+|\+)(?:.*?\(|.*?)([0-9.]+)(?:%|\s*-\s*[0-9.]+%|\))'
    
    # Create columns for structured fee data
    fee_df['has_fee_info'] = False
    fee_df['product_count'] = 0
    fee_df['max_tiers'] = 0
    
    # Process each row
    for idx, row in df.iterrows():
        # Check if there's any fee information
        if 'No fee information available' in str(row['Flat Fee']):
            continue
            
        # Track products and tiers
        current_product = 0
        current_tier = 0
        max_tiers = 0
        
        # Process each threshold column
        for col in threshold_cols:
            if col not in df.columns:
                continue
                
            value = row[col]
            if pd.isna(value) or value == '-1' or value == 'N/a':
                continue
                
            # Extract fee information
            match = re.search(threshold_pattern, str(value))
            if match:
                # Found a fee threshold
                fee_df.loc[idx, 'has_fee_info'] = True
                
                lower_bound = match.group(1).replace(',', '')
                upper_bound = match.group(2).replace(',', '')
                fee_pct = match.group(3)
                
                # Handle special cases for upper bound
                if upper_bound == '+' or 'above' in upper_bound.lower() or 'plus' in upper_bound.lower():
                    upper_bound = 'Infinity'
                
                # Detect if this is a new product or continuation of current product
                # Heuristic: If the lower bound is 0 or very low, it's likely a new product
                try:
                    lower_bound_val = float(lower_bound)
                    if lower_bound_val <= 1000 and current_tier > 0:
                        current_product += 1
                        current_tier = 0
                except ValueError:
                    pass
                
                # Store the fee information
                product_col = f"product_{current_product}"
                tier_col = f"tier_{current_tier}"
                
                # Create columns if they don't exist
                if f"{product_col}_{tier_col}_lower" not in fee_df.columns:
                    fee_df[f"{product_col}_{tier_col}_lower"] = np.nan
                    fee_df[f"{product_col}_{tier_col}_upper"] = np.nan
                    fee_df[f"{product_col}_{tier_col}_fee_pct"] = np.nan
                
                # Store the values
                try:
                    fee_df.loc[idx, f"{product_col}_{tier_col}_lower"] = float(lower_bound)
                    if upper_bound != 'Infinity':
                        fee_df.loc[idx, f"{product_col}_{tier_col}_upper"] = float(upper_bound)
                    else:
                        fee_df.loc[idx, f"{product_col}_{tier_col}_upper"] = np.inf
                    fee_df.loc[idx, f"{product_col}_{tier_col}_fee_pct"] = float(fee_pct)
                except ValueError:
                    print(f"Could not convert to float: {lower_bound}, {upper_bound}, {fee_pct}")
                
                current_tier += 1
                max_tiers = max(max_tiers, current_tier)
        
        # Update product and tier counts
        fee_df.loc[idx, 'product_count'] = current_product + 1  # +1 because we start from 0
        fee_df.loc[idx, 'max_tiers'] = max_tiers
    
    return fee_df

def analyze_fee_structures(fee_df):
    """
    Analyze the extracted fee structures
    """
    # Count advisers with fee information
    fee_info_count = fee_df['has_fee_info'].sum()
    print(f"\nAdvisers with fee information: {fee_info_count} out of {len(fee_df)} ({fee_info_count/len(fee_df)*100:.1f}%)")
    
    # Count advisers with multiple products
    multiple_products_df = fee_df[fee_df['product_count'] > 1]
    print(f"Advisers with multiple products: {len(multiple_products_df)} ({len(multiple_products_df)/fee_info_count*100:.1f}% of those with fee info)")
    
    # Analyze tier counts
    tier_counts = fee_df['max_tiers'].value_counts().sort_index()
    print("\nDistribution of maximum tiers per adviser:")
    print(tier_counts)
    
    # Calculate average fee percentages by tier
    print("\nAverage fee percentages by tier:")
    
    # Get all product-tier combinations
    product_tier_cols = [col for col in fee_df.columns if '_fee_pct' in col]
    
    for col in product_tier_cols:
        avg_fee = fee_df[col].mean()
        if not pd.isna(avg_fee):
            print(f"{col}: {avg_fee:.2f}%")
    
    return tier_counts

def plot_fee_structure_analysis(fee_df, tier_counts):
    """
    Create visualizations of the fee structure analysis
    """
    # Plot distribution of product counts
    plt.figure(figsize=(10, 6))
    product_counts = fee_df['product_count'].value_counts().sort_index()
    product_counts.plot(kind='bar')
    plt.xlabel('Number of Products')
    plt.ylabel('Count of Advisers')
    plt.title('Distribution of Product Counts per Adviser')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('product_count_distribution.png')
    plt.close()
    
    # Plot distribution of tier counts
    plt.figure(figsize=(10, 6))
    tier_counts.plot(kind='bar')
    plt.xlabel('Maximum Number of Tiers')
    plt.ylabel('Count of Advisers')
    plt.title('Distribution of Maximum Tiers per Adviser')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('tier_count_distribution.png')
    plt.close()
    
    # Plot fee percentages by tier for the first product
    plt.figure(figsize=(12, 8))
    
    # Get fee percentage columns for the first product
    product0_cols = [col for col in fee_df.columns if 'product_0' in col and '_fee_pct' in col]
    
    # Create a list to hold all fee percentages for a box plot
    all_fees = []
    labels = []
    
    for col in product0_cols:
        fees = fee_df[col].dropna()
        if not fees.empty:
            all_fees.append(fees)
            # Create a more readable label
            tier_num = col.split('_')[1]
            labels.append(f"Tier {tier_num}")
    
    # Create box plot
    plt.boxplot(all_fees)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.ylabel('Fee Percentage')
    plt.title('Distribution of Fee Percentages by Tier (First Product)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('fee_percentages_by_tier.png')
    plt.close()
    
    return True

def main():
    """
    Main function to run the fee structure analysis
    """
    # Load the data
    df = load_data('fee_analysis_formadv_part2_1_extracted.csv')
    
    if df is None:
        return
    
    # Extract adviser information
    df = extract_adviser_info(df)
    
    # Detect and correct misplaced answers
    corrected_df = detect_misplaced_answers(df)
    
    # Extract fee structures
    fee_df = extract_fee_structures(corrected_df)
    
    # Analyze fee structures
    tier_counts = analyze_fee_structures(fee_df)
    
    # Plot fee structure analysis
    plot_fee_structure_analysis(fee_df, tier_counts)
    
    # Save the structured fee data
    fee_df.to_csv('structured_fee_data.csv', index=False)
    print("\nStructured fee data saved to 'structured_fee_data.csv'")
    
    print("\nFee structure analysis complete!")

if __name__ == "__main__":
    main()
