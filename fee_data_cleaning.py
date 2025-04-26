import pandas as pd
import numpy as np
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 100)

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

def clean_fee_thresholds(df):
    """
    Clean and standardize fee threshold columns
    """
    threshold_cols = [col for col in df.columns if 'threshold' in col.lower() or 'Annual fee range' in col]
    
    for col in threshold_cols:
        # Skip columns that don't exist
        if col not in df.columns:
            continue
            
        # Replace 'N/a', 'N/A', etc. with NaN
        df[col] = df[col].replace(['N/a', 'N/A', 'n/a', '-1'], np.nan)
        
        # Create a new column to store the cleaned threshold values
        new_col_name = f"{col}_clean"
        df[new_col_name] = np.nan
        
        # Create columns for lower bound, upper bound, and fee percentage
        lower_bound_col = f"{col}_lower_bound"
        upper_bound_col = f"{col}_upper_bound"
        fee_pct_col = f"{col}_fee_pct"
        
        df[lower_bound_col] = np.nan
        df[upper_bound_col] = np.nan
        df[fee_pct_col] = np.nan
        
        # Process each threshold entry
        for idx, value in enumerate(df[col]):
            if pd.isna(value) or value == '-1':
                continue
                
            try:
                # Extract the threshold range and fee percentage using regex
                # Pattern: "$X - $Y (Z%)" or similar
                threshold_pattern = r'(?:\$|)([0-9,.]+)(?:\s*-\s*\$|[\s+])([0-9,.+]+|\+)(?:.*?\(|.*?)([0-9.]+)(?:%|\s*-\s*[0-9.]+%|\))'
                
                match = re.search(threshold_pattern, str(value))
                if match:
                    lower_bound = match.group(1).replace(',', '')
                    upper_bound = match.group(2).replace(',', '')
                    fee_pct = match.group(3)
                    
                    # Handle special cases
                    if upper_bound == '+' or 'above' in upper_bound.lower() or 'plus' in upper_bound.lower():
                        upper_bound = 'Infinity'
                    
                    # Convert to numeric values
                    try:
                        df.loc[idx, lower_bound_col] = float(lower_bound)
                        if upper_bound != 'Infinity':
                            df.loc[idx, upper_bound_col] = float(upper_bound)
                        else:
                            df.loc[idx, upper_bound_col] = np.inf
                        df.loc[idx, fee_pct_col] = float(fee_pct)
                    except ValueError:
                        print(f"Could not convert to float: {lower_bound}, {upper_bound}, {fee_pct}")
                        
                    # Store the cleaned version
                    df.loc[idx, new_col_name] = f"${lower_bound} - ${upper_bound} ({fee_pct}%)"
                else:
                    # Handle cases where the pattern doesn't match
                    # This could be for flat fees or other irregular formats
                    print(f"No match for threshold pattern in: {value}")
            except Exception as e:
                print(f"Error processing threshold {value}: {e}")
    
    return df

def clean_flat_fee(df):
    """
    Clean and standardize flat fee column
    """
    if 'Flat Fee' not in df.columns:
        return df
        
    # Create a new column for cleaned flat fee
    df['flat_fee_clean'] = np.nan
    df['has_flat_fee'] = False
    
    for idx, value in enumerate(df['Flat Fee']):
        if pd.isna(value) or value == '-1' or value.lower() == 'no':
            continue
            
        try:
            # Check if it's a dollar amount
            dollar_pattern = r'\$([0-9,.]+)'
            match = re.search(dollar_pattern, str(value))
            if match:
                amount = match.group(1).replace(',', '')
                df.loc[idx, 'flat_fee_clean'] = float(amount)
                df.loc[idx, 'has_flat_fee'] = True
            # Check if it's a percentage
            elif '%' in str(value):
                pct_pattern = r'([0-9.]+)%'
                match = re.search(pct_pattern, str(value))
                if match:
                    df.loc[idx, 'flat_fee_clean'] = float(match.group(1))
                    df.loc[idx, 'has_flat_fee'] = True
        except Exception as e:
            print(f"Error processing flat fee {value}: {e}")
    
    return df

def clean_minimum_investment(df):
    """
    Clean and standardize minimum investment column
    """
    if 'Minimum investment (Amount/No)' not in df.columns:
        return df
        
    # Create a new column for cleaned minimum investment
    df['min_investment_clean'] = np.nan
    df['has_min_investment'] = False
    
    for idx, value in enumerate(df['Minimum investment (Amount/No)']):
        if pd.isna(value) or value == '-1' or value.lower() in ['no', 'n/a']:
            continue
            
        try:
            # Check if it's a dollar amount
            dollar_pattern = r'\$([0-9,.]+)'
            match = re.search(dollar_pattern, str(value))
            if match:
                amount = match.group(1).replace(',', '')
                df.loc[idx, 'min_investment_clean'] = float(amount)
                df.loc[idx, 'has_min_investment'] = True
        except Exception as e:
            print(f"Error processing minimum investment {value}: {e}")
    
    return df

def clean_negotiable(df):
    """
    Clean and standardize negotiable fee column
    """
    if 'Negotiable (Yes/No)' not in df.columns:
        return df
        
    # Create a new column for cleaned negotiable status
    df['negotiable_clean'] = False
    
    for idx, value in enumerate(df['Negotiable (Yes/No)']):
        if pd.isna(value) or value == '-1':
            continue
            
        if str(value).lower() == 'yes':
            df.loc[idx, 'negotiable_clean'] = True
    
    return df

def clean_negotiable_threshold(df):
    """
    Clean and standardize negotiable threshold column
    """
    if 'Negotiable threshold (Number/ N/A)' not in df.columns:
        return df
        
    # Create a new column for cleaned negotiable threshold
    df['negotiable_threshold_clean'] = np.nan
    
    for idx, value in enumerate(df['Negotiable threshold (Number/ N/A)']):
        if pd.isna(value) or value == '-1' or value.lower() in ['no', 'n/a']:
            continue
            
        try:
            # Check if it's a dollar amount
            dollar_pattern = r'\$([0-9,.]+)'
            match = re.search(dollar_pattern, str(value))
            if match:
                amount = match.group(1).replace(',', '')
                df.loc[idx, 'negotiable_threshold_clean'] = float(amount)
        except Exception as e:
            print(f"Error processing negotiable threshold {value}: {e}")
    
    return df

def identify_fee_structure_type(df):
    """
    Identify the type of fee structure for each adviser
    """
    # Create a new column for fee structure type
    df['fee_structure_type'] = 'Unknown'
    
    # Check for flat fee
    flat_fee_mask = df['has_flat_fee'] == True
    df.loc[flat_fee_mask, 'fee_structure_type'] = 'Flat Fee'
    
    # Check for tiered fee structure
    threshold_cols = [col for col in df.columns if '_fee_pct' in col]
    
    for idx, row in df.iterrows():
        if row['fee_structure_type'] != 'Unknown':
            continue
            
        # Count non-NaN threshold values
        threshold_count = sum(1 for col in threshold_cols if not pd.isna(row[col]))
        
        if threshold_count > 0:
            df.loc[idx, 'fee_structure_type'] = 'Tiered'
        else:
            # Check if there's any fee information
            if 'No fee information available' in str(row['Flat Fee']):
                df.loc[idx, 'fee_structure_type'] = 'No Fee Info'
    
    return df

def analyze_fee_structures(df):
    """
    Analyze fee structures and generate summary statistics
    """
    # Count fee structure types
    fee_structure_counts = df['fee_structure_type'].value_counts()
    print("\nFee Structure Types:")
    print(fee_structure_counts)
    
    # Analyze tiered fee structures
    tiered_df = df[df['fee_structure_type'] == 'Tiered']
    
    # Calculate average fee percentages for each threshold
    threshold_cols = [col for col in df.columns if '_fee_pct' in col]
    
    print("\nAverage Fee Percentages by Threshold:")
    for col in threshold_cols:
        avg_fee = tiered_df[col].mean()
        if not pd.isna(avg_fee):
            threshold_name = col.replace('_fee_pct', '')
            print(f"{threshold_name}: {avg_fee:.2f}%")
    
    # Analyze negotiable fees
    negotiable_count = df['negotiable_clean'].sum()
    total_with_info = df['negotiable_clean'].count()
    print(f"\nNegotiable Fees: {negotiable_count} out of {total_with_info} ({negotiable_count/total_with_info*100:.1f}%)")
    
    # Analyze minimum investments
    min_investment_df = df[df['has_min_investment'] == True]
    if not min_investment_df.empty:
        avg_min_investment = min_investment_df['min_investment_clean'].mean()
        median_min_investment = min_investment_df['min_investment_clean'].median()
        print(f"\nMinimum Investment:")
        print(f"Average: ${avg_min_investment:,.2f}")
        print(f"Median: ${median_min_investment:,.2f}")
    
    return fee_structure_counts

def plot_fee_distributions(df):
    """
    Create visualizations of fee distributions
    """
    # Set up the plotting environment
    plt.figure(figsize=(12, 8))
    
    # Filter to tiered fee structures
    tiered_df = df[df['fee_structure_type'] == 'Tiered']
    
    # Get fee percentage columns
    fee_pct_cols = [col for col in tiered_df.columns if '_fee_pct' in col]
    
    # Create a list to hold all fee percentages for a violin plot
    all_fees = []
    labels = []
    
    for col in fee_pct_cols:
        fees = tiered_df[col].dropna()
        if not fees.empty:
            all_fees.append(fees)
            # Create a more readable label
            label = col.replace('Annual fee threshold ', 'Tier ').replace('_fee_pct', '')
            labels.append(label)
    
    # Create violin plot
    plt.subplot(2, 1, 1)
    plt.violinplot(all_fees, showmeans=True, showmedians=True)
    plt.xticks(range(1, len(labels) + 1), labels, rotation=45)
    plt.ylabel('Fee Percentage')
    plt.title('Distribution of Fee Percentages by Tier')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Create a box plot for comparison
    plt.subplot(2, 1, 2)
    plt.boxplot(all_fees)
    plt.xticks(range(1, len(labels) + 1), labels, rotation=45)
    plt.ylabel('Fee Percentage')
    plt.title('Box Plot of Fee Percentages by Tier')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('fee_distributions.png')
    plt.close()
    
    # Create a histogram of minimum investments
    min_investment_df = df[df['has_min_investment'] == True]
    if not min_investment_df.empty:
        plt.figure(figsize=(10, 6))
        plt.hist(min_investment_df['min_investment_clean'], bins=20, edgecolor='black')
        plt.xlabel('Minimum Investment ($)')
        plt.ylabel('Count')
        plt.title('Distribution of Minimum Investment Requirements')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('minimum_investment_distribution.png')
        plt.close()
    
    return True

def analyze_multiple_products(df):
    """
    Identify and analyze advisers with multiple products/fee structures
    """
    # Create a column to count the number of fee tiers
    df['fee_tier_count'] = 0
    
    threshold_cols = [col for col in df.columns if '_fee_pct' in col]
    
    for idx, row in df.iterrows():
        # Count non-NaN threshold values
        tier_count = sum(1 for col in threshold_cols if not pd.isna(row[col]))
        df.loc[idx, 'fee_tier_count'] = tier_count
    
    # Identify potential multiple products by looking for gaps in the fee tiers
    df['potential_multiple_products'] = False
    
    for idx, row in df.iterrows():
        if row['fee_tier_count'] <= 1:
            continue
            
        # Check for gaps in the sequence of thresholds
        has_gap = False
        last_tier = None
        
        for i in range(1, 9):  # Assuming up to 8 thresholds
            current_col = f"Annual fee threshold {i}_fee_pct"
            if current_col not in df.columns:
                continue
                
            if not pd.isna(row[current_col]):
                if last_tier is not None and i > last_tier + 1:
                    has_gap = True
                    break
                last_tier = i
        
        if has_gap:
            df.loc[idx, 'potential_multiple_products'] = True
    
    # Count advisers with potential multiple products
    multiple_products_count = df['potential_multiple_products'].sum()
    print(f"\nAdvisers with Potential Multiple Products: {multiple_products_count}")
    
    return df

def analyze_fee_trends_over_time(df):
    """
    Analyze how fee structures change over time
    """
    # Ensure filing_date is datetime
    df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
    
    # Group by year and calculate average fees
    df['filing_year'] = df['filing_date'].dt.year
    
    # Filter out rows with missing years
    year_df = df.dropna(subset=['filing_year'])
    
    # Get fee percentage columns
    fee_pct_cols = [col for col in df.columns if '_fee_pct' in col]
    
    # Create a DataFrame to store yearly averages
    yearly_avgs = pd.DataFrame()
    
    for col in fee_pct_cols:
        # Group by year and calculate mean
        yearly_avg = year_df.groupby('filing_year')[col].mean()
        if not yearly_avg.empty:
            # Create a more readable column name
            col_name = col.replace('Annual fee threshold ', 'Tier ').replace('_fee_pct', '')
            yearly_avgs[col_name] = yearly_avg
    
    # Plot the trends
    if not yearly_avgs.empty:
        plt.figure(figsize=(12, 8))
        yearly_avgs.plot(marker='o')
        plt.xlabel('Year')
        plt.ylabel('Average Fee Percentage')
        plt.title('Trends in Fee Percentages Over Time')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(title='Fee Tier')
        plt.tight_layout()
        plt.savefig('fee_trends_over_time.png')
        plt.close()
    
    return yearly_avgs

def main():
    """
    Main function to run the data cleaning and analysis
    """
    # Load the data
    df = load_data('fee_analysis_formadv_part2_1_extracted.csv')
    
    if df is None:
        return
    
    # Initial data exploration
    print("\nInitial data columns:")
    print(df.columns.tolist())
    
    # Extract adviser information
    df = extract_adviser_info(df)
    
    # Clean fee thresholds
    df = clean_fee_thresholds(df)
    
    # Clean flat fee
    df = clean_flat_fee(df)
    
    # Clean minimum investment
    df = clean_minimum_investment(df)
    
    # Clean negotiable status
    df = clean_negotiable(df)
    
    # Clean negotiable threshold
    df = clean_negotiable_threshold(df)
    
    # Identify fee structure type
    df = identify_fee_structure_type(df)
    
    # Analyze fee structures
    fee_structure_counts = analyze_fee_structures(df)
    
    # Analyze multiple products
    df = analyze_multiple_products(df)
    
    # Analyze fee trends over time
    yearly_avgs = analyze_fee_trends_over_time(df)
    
    # Plot fee distributions
    plot_fee_distributions(df)
    
    # Save the cleaned data
    df.to_csv('cleaned_fee_data.csv', index=False)
    print("\nCleaned data saved to 'cleaned_fee_data.csv'")
    
    # Save a summary of the yearly averages
    if not yearly_avgs.empty:
        yearly_avgs.to_csv('fee_yearly_averages.csv')
        print("Yearly fee averages saved to 'fee_yearly_averages.csv'")
    
    print("\nData cleaning and analysis complete!")

if __name__ == "__main__":
    main()
