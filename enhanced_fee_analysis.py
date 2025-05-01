import pandas as pd
import numpy as np
import re
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

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
    pct_match = re.search(r'(\d+\.?\d*)%', fee_str)
    if pct_match:
        return 1, float(pct_match.group(1))
    
    # Check for dollar amount
    dollar_match = re.search(r'\$(\d+,?\d*\.?\d*)', fee_str)
    if dollar_match:
        # Remove commas and convert to float
        amount = dollar_match.group(1).replace(',', '')
        return 1, float(amount)
    
    # If it's just "Yes" or some other indication
    if fee_str.lower() in ['yes', 'y', 'true']:
        return 1, None
    
    # Try to extract any number
    num_match = re.search(r'(\d+\.?\d*)', fee_str)
    if num_match:
        return 1, float(num_match.group(1))
    
    # If we can't parse it but it's not "No"
    return 1, None

def extract_fee_range(fee_range_str):
    """
    Extract range and fee percentage from fee range string
    Format: "$X - $Y (Z%)" or "$X+ (Z%)"
    Returns lower_bound, upper_bound, fee_percentage
    """
    if pd.isna(fee_range_str) or fee_range_str.lower() == 'n/a' or fee_range_str.strip() == '':
        return None, None, None
    
    # Extract dollar range
    range_match = re.search(r'\$(\d+,?\d*\.?\d*)\s*-\s*\$(\d+,?\d*\.?\d*)', fee_range_str)
    if range_match:
        lower = range_match.group(1).replace(',', '')
        upper = range_match.group(2).replace(',', '')
        lower_bound = float(lower)
        upper_bound = float(upper)
    else:
        # Check for "$X+" format
        plus_match = re.search(r'\$(\d+,?\d*\.?\d*)\+', fee_range_str)
        if plus_match:
            lower = plus_match.group(1).replace(',', '')
            lower_bound = float(lower)
            upper_bound = float('inf')
        else:
            # Try to find any dollar amount
            dollar_match = re.search(r'\$(\d+,?\d*\.?\d*)', fee_range_str)
            if dollar_match:
                amount = dollar_match.group(1).replace(',', '')
                lower_bound = float(amount)
                upper_bound = None
            else:
                lower_bound = None
                upper_bound = None
    
    # Extract fee percentage
    pct_match = re.search(r'(\d+\.?\d*)%', fee_range_str)
    if pct_match:
        fee_percentage = float(pct_match.group(1))
    else:
        fee_percentage = None
    
    return lower_bound, upper_bound, fee_percentage

def process_minimum_investment(min_inv_str):
    """
    Process minimum investment information
    Returns has_min_inv (0/1) and min_inv_amount
    """
    if pd.isna(min_inv_str) or min_inv_str.lower() in ['no', 'n/a'] or min_inv_str.strip() == '':
        return 0, None
    
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
    if pd.isna(neg_str) or neg_str.strip() == '':
        return 0
    
    if neg_str.lower() in ['yes', 'y', 'true', 'negotiable']:
        return 1
    
    return 0

def process_negotiable_threshold(neg_thresh_str):
    """
    Process negotiable threshold information
    Returns has_neg_thresh (0/1) and neg_thresh_amount
    """
    if pd.isna(neg_thresh_str) or neg_thresh_str.lower() in ['no', 'n/a'] or neg_thresh_str.strip() == '':
        return 0, None
    
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

def identify_products(row):
    """
    Identify number of products based on fee structures
    Returns number of products and ordered product indices
    """
    products = []
    
    # Check for flat fee as a product
    if row['has_flat_fee'] == 1:
        products.append({
            'type': 'flat',
            'fee': row['flat_fee_value'],
            'original_index': -1  # Use -1 to indicate flat fee
        })
    
    # Check for tiered fee structures
    for i in range(1, 9):  # 8 possible fee ranges
        col_name = f'annual_fee_range_{i}'
        if col_name in row and not pd.isna(row[col_name]) and row[col_name] != 'N/A':
            lower, upper, fee = extract_fee_range(row[col_name])
            
            if fee is not None and lower is not None:
                # Check if this is a new product or continuation of existing tiered product
                new_product = True
                
                for product in products:
                    if product['type'] == 'tiered' and 'tiers' in product:
                        # Check if this range continues from the last tier's upper bound
                        last_tier = product['tiers'][-1]
                        if abs(last_tier['upper'] - lower) < 0.01 or last_tier['upper'] == float('inf'):
                            # This is a continuation of the existing product
                            product['tiers'].append({
                                'lower': lower,
                                'upper': upper if upper is not None else float('inf'),
                                'fee': fee
                            })
                            new_product = False
                            break
                
                if new_product:
                    # This is a new product
                    products.append({
                        'type': 'tiered',
                        'tiers': [{
                            'lower': lower,
                            'upper': upper if upper is not None else float('inf'),
                            'fee': fee
                        }],
                        'original_index': len(products)
                    })
    
    # Order products from cheapest to most expensive based on first tier fee
    for i, product in enumerate(products):
        if product['type'] == 'tiered' and 'tiers' in product and len(product['tiers']) > 0:
            product['first_tier_fee'] = product['tiers'][0]['fee']
        elif product['type'] == 'flat':
            product['first_tier_fee'] = product['fee']
        else:
            product['first_tier_fee'] = float('inf')  # Put products without fees at the end
    
    # Sort products by first tier fee
    products.sort(key=lambda x: x['first_tier_fee'] if x['first_tier_fee'] is not None else float('inf'))
    
    # Return number of products and ordered indices
    return len(products), products

def calculate_effective_fee(products, portfolio_value):
    """
    Calculate effective fee for a given portfolio value
    Returns effective fee percentage
    """
    if not products:
        return None
    
    # Try to find a tiered product first
    tiered_products = [p for p in products if p['type'] == 'tiered']
    
    if tiered_products:
        # Use the first (cheapest) tiered product
        product = tiered_products[0]
        
        total_fee = 0
        remaining_value = portfolio_value
        
        for tier in product['tiers']:
            lower = tier['lower']
            upper = tier['upper']
            fee_pct = tier['fee']
            
            if remaining_value <= 0:
                break
                
            if upper == float('inf'):
                # This is the highest tier
                tier_fee = remaining_value * (fee_pct / 100)
                total_fee += tier_fee
                remaining_value = 0
            else:
                # Calculate fee for this tier
                tier_value = min(upper - lower, remaining_value)
                tier_fee = tier_value * (fee_pct / 100)
                total_fee += tier_fee
                remaining_value -= tier_value
        
        return (total_fee / portfolio_value) * 100
    
    # If no tiered products, use flat fee
    flat_products = [p for p in products if p['type'] == 'flat']
    
    if flat_products and flat_products[0]['fee'] is not None:
        return flat_products[0]['fee']
    
    return None

def process_csv_file(file_path):
    """
    Process a single CSV file with fee data
    Returns a DataFrame with cleaned data
    """
    try:
        df = pd.read_csv(file_path)
        
        # Extract adviser info from filename
        df['filename'] = df['File Name']
        adviser_info = df['filename'].apply(extract_adviser_info)
        
        # Convert adviser_info dictionary to columns
        adviser_df = pd.DataFrame(adviser_info.tolist())
        df = pd.concat([df, adviser_df], axis=1)
        
        # Process flat fee
        flat_fee_results = df['Flat Rate (Fee % or $ amount / No)'].apply(process_flat_fee)
        df['has_flat_fee'] = [x[0] for x in flat_fee_results]
        df['flat_fee_value'] = [x[1] for x in flat_fee_results]
        
        # Process fee ranges
        for i in range(1, 9):
            col_name = f'Annual fee range {i} (Range and fee % / N/A)'
            new_col_name = f'annual_fee_range_{i}'
            df[new_col_name] = df[col_name]
        
        # Process minimum investment
        min_inv_results = df['Minimum investment (Amount / No)'].apply(process_minimum_investment)
        df['has_min_investment'] = [x[0] for x in min_inv_results]
        df['min_investment_amount'] = [x[1] for x in min_inv_results]
        
        # Process negotiable
        df['is_negotiable'] = df['Negotiable (Yes/No)'].apply(process_negotiable)
        
        # Process negotiable threshold
        neg_thresh_results = df['Negotiable threshold (Number / No)'].apply(process_negotiable_threshold)
        df['has_negotiable_threshold'] = [x[0] for x in neg_thresh_results]
        df['negotiable_threshold_amount'] = [x[1] for x in neg_thresh_results]
        
        # Calculate verification ratio
        if 'Verification Summary' in df.columns:
            df['verification_count'] = df['Verification Summary'].str.count(',') + 1
            df['extracted_count'] = df.apply(lambda row: sum([1 for col in row.index if 'Annual fee range' in col and not pd.isna(row[col]) and row[col] != 'N/A']), axis=1)
            df['verification_ratio'] = df['extracted_count'] / df['verification_count']
        
        # Identify products
        product_results = df.apply(identify_products, axis=1)
        df['product_count'] = [x[0] for x in product_results]
        df['products'] = [x[1] for x in product_results]
        
        # Calculate effective fees for different portfolio values
        df['effective_fee_1M'] = df['products'].apply(lambda x: calculate_effective_fee(x, 1000000))
        df['effective_fee_5M'] = df['products'].apply(lambda x: calculate_effective_fee(x, 5000000))
        
        # Extract first tier fee for Product 1 (cheapest)
        def get_first_tier_fee(products):
            if not products:
                return None
            
            for product in products:
                if product['type'] == 'tiered' and 'tiers' in product and len(product['tiers']) > 0:
                    return product['tiers'][0]['fee']
                elif product['type'] == 'flat':
                    return product['fee']
            
            return None
        
        df['first_tier_fee_product1'] = df['products'].apply(get_first_tier_fee)
        
        # Extract first tier fee for Product 3 (if available)
        def get_product3_first_tier_fee(products):
            if len(products) < 3:
                return None
            
            product = products[2]  # 0-indexed, so 2 is the third product
            
            if product['type'] == 'tiered' and 'tiers' in product and len(product['tiers']) > 0:
                return product['tiers'][0]['fee']
            elif product['type'] == 'flat':
                return product['fee']
            
            return None
        
        df['first_tier_fee_product3'] = df['products'].apply(get_product3_first_tier_fee)
        
        return df
    
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def clean_and_consolidate_data(dataframes):
    """
    Clean and consolidate multiple DataFrames
    Returns a single cleaned DataFrame
    """
    if not dataframes:
        return None
    
    # Concatenate all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Convert filing_date to datetime if it's not already
    if 'filing_date' in combined_df.columns and combined_df['filing_date'].dtype != 'datetime64[ns]':
        combined_df['filing_date'] = pd.to_datetime(combined_df['filing_date'], errors='coerce')
    
    # Extract year from filing_date
    combined_df['filing_year'] = combined_df['filing_date'].dt.year
    
    # Drop duplicates, keeping the latest observation with valid fee info per adviser per year
    combined_df['has_fee_info'] = combined_df.apply(
        lambda row: row['has_flat_fee'] == 1 or row['product_count'] > 0, 
        axis=1
    )
    
    # Sort by filing_date (descending) to keep the latest observation
    combined_df = combined_df.sort_values('filing_date', ascending=False)
    
    # Drop duplicates
    combined_df = combined_df.drop_duplicates(
        subset=['adviser_id1', 'adviser_id2', 'filing_year', 'has_fee_info'],
        keep='first'
    )
    
    # Handle outliers
    # Remove implausible AUM-based fees (above 5% or zero)
    combined_df = combined_df[
        ~((combined_df['first_tier_fee_product1'] > 5) | 
          (combined_df['first_tier_fee_product1'] == 0))
    ]
    
    return combined_df

def generate_summary_statistics(df):
    """
    Generate summary statistics from the cleaned data
    Returns a dictionary of summary statistics
    """
    stats = {}
    
    # Number of unique advisers
    stats['unique_advisers'] = df['adviser_id1'].nunique()
    
    # Number of unique advisers by year
    yearly_counts = df.groupby('filing_year')['adviser_id1'].nunique()
    stats['unique_advisers_by_year'] = yearly_counts.to_dict()
    
    # Number of unique advisers with extracted fee information
    has_fee_df = df[df['has_fee_info'] == True]
    stats['unique_advisers_with_fees'] = has_fee_df['adviser_id1'].nunique()
    
    # Number of unique advisers with extracted fee information by year
    yearly_fee_counts = has_fee_df.groupby('filing_year')['adviser_id1'].nunique()
    stats['unique_advisers_with_fees_by_year'] = yearly_fee_counts.to_dict()
    
    # Frequency of different contracts (flat fee vs. AUM-based)
    contract_types = df.groupby(['has_flat_fee', 'product_count']).size()
    stats['contract_types'] = contract_types.to_dict()
    
    # Frequency of different contracts by year
    contract_types_by_year = df.groupby(['filing_year', 'has_flat_fee', 'product_count']).size().unstack().fillna(0)
    stats['contract_types_by_year'] = contract_types_by_year.to_dict()
    
    # Flat fee sum stats
    flat_fee_stats = df[df['has_flat_fee'] == 1]['flat_fee_value'].describe()
    stats['flat_fee_stats'] = flat_fee_stats.to_dict()
    
    # Flat fee sum stats by year
    flat_fee_stats_by_year = df[df['has_flat_fee'] == 1].groupby('filing_year')['flat_fee_value'].describe()
    stats['flat_fee_stats_by_year'] = flat_fee_stats_by_year.to_dict()
    
    # Initial AUM-based fee of Product 1 (the cheapest one)
    initial_fee_stats = df['first_tier_fee_product1'].describe()
    stats['initial_fee_stats'] = initial_fee_stats.to_dict()
    
    # Initial AUM-based fee of Product 1 by year
    initial_fee_stats_by_year = df.groupby('filing_year')['first_tier_fee_product1'].describe()
    stats['initial_fee_stats_by_year'] = initial_fee_stats_by_year.to_dict()
    
    # Effective fee on $1,000,000 portfolio
    effective_fee_1M_stats = df['effective_fee_1M'].describe()
    stats['effective_fee_1M_stats'] = effective_fee_1M_stats.to_dict()
    
    # Effective fee on $5,000,000 portfolio
    effective_fee_5M_stats = df['effective_fee_5M'].describe()
    stats['effective_fee_5M_stats'] = effective_fee_5M_stats.to_dict()
    
    # Minimum investment stats
    min_inv_stats = df[df['has_min_investment'] == 1]['min_investment_amount'].describe()
    stats['min_investment_stats'] = min_inv_stats.to_dict()
    
    # Negotiable fee percentage
    negotiable_pct = df['is_negotiable'].mean() * 100
    stats['negotiable_percentage'] = negotiable_pct
    
    return stats

def create_visualizations(df, output_dir='enhanced_analysis_results'):
    """
    Create visualizations from the cleaned data
    Saves visualizations to the specified output directory
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Distribution of first tier fees
    plt.figure(figsize=(10, 6))
    sns.histplot(df['first_tier_fee_product1'].dropna(), bins=20, kde=True)
    plt.xlabel('First Tier Fee (%)')
    plt.ylabel('Count')
    plt.title('Distribution of First Tier Fees (Product 1)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/first_tier_fee_distribution.png')
    plt.close()
    
    # 2. First tier fees by year
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='filing_year', y='first_tier_fee_product1', data=df)
    plt.xlabel('Filing Year')
    plt.ylabel('First Tier Fee (%)')
    plt.title('First Tier Fees by Year (Product 1)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/first_tier_fee_by_year.png')
    plt.close()
    
    # 3. Distribution of effective fees for $1M portfolio
    plt.figure(figsize=(10, 6))
    sns.histplot(df['effective_fee_1M'].dropna(), bins=20, kde=True)
    plt.xlabel('Effective Fee (%)')
    plt.ylabel('Count')
    plt.title('Distribution of Effective Fees for $1M Portfolio')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/effective_fee_1M_distribution.png')
    plt.close()
    
    # 4. Distribution of effective fees for $5M portfolio
    plt.figure(figsize=(10, 6))
    sns.histplot(df['effective_fee_5M'].dropna(), bins=20, kde=True)
    plt.xlabel('Effective Fee (%)')
    plt.ylabel('Count')
    plt.title('Distribution of Effective Fees for $5M Portfolio')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/effective_fee_5M_distribution.png')
    plt.close()
    
    # 5. Comparison of effective fees for $1M vs $5M portfolios
    plt.figure(figsize=(10, 6))
    
    # Create a DataFrame with both fees for plotting
    fee_comparison = pd.DataFrame({
        'Portfolio Size': ['$1M'] * len(df['effective_fee_1M'].dropna()) + ['$5M'] * len(df['effective_fee_5M'].dropna()),
        'Effective Fee (%)': list(df['effective_fee_1M'].dropna()) + list(df['effective_fee_5M'].dropna())
    })
    
    sns.boxplot(x='Portfolio Size', y='Effective Fee (%)', data=fee_comparison)
    plt.title('Comparison of Effective Fees for Different Portfolio Sizes')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/effective_fee_comparison.png')
    plt.close()
    
    # 6. Distribution of minimum investment amounts
    plt.figure(figsize=(10, 6))
    sns.histplot(df[df['has_min_investment'] == 1]['min_investment_amount'].dropna(), bins=20, kde=True)
    plt.xlabel('Minimum Investment Amount ($)')
    plt.ylabel('Count')
    plt.title('Distribution of Minimum Investment Amounts')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xscale('log')  # Use log scale for better visualization
    plt.savefig(f'{output_dir}/min_investment_distribution.png')
    plt.close()
    
    # 7. Contract types (flat fee vs. AUM-based)
    plt.figure(figsize=(10, 6))
    contract_counts = df.groupby(['has_flat_fee', 'product_count']).size().reset_index(name='count')
    contract_counts['contract_type'] = contract_counts.apply(
        lambda row: 'Flat Fee Only' if row['has_flat_fee'] == 1 and row['product_count'] == 0 else
                   'AUM-Based Only' if row['has_flat_fee'] == 0 and row['product_count'] > 0 else
                   'Both' if row['has_flat_fee'] == 1 and row['product_count'] > 0 else
                   'No Fee Info',
        axis=1
    )
    
    sns.barplot(x='contract_type', y='count', data=contract_counts)
    plt.xlabel('Contract Type')
    plt.ylabel('Count')
    plt.title('Distribution of Contract Types')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/contract_type_distribution.png')
    plt.close()
    
    # 8. Negotiable vs. Non-negotiable fees
    plt.figure(figsize=(8, 8))
    negotiable_counts = df['is_negotiable'].value_counts()
    plt.pie(negotiable_counts, labels=['Negotiable', 'Non-negotiable'], autopct='%1.1f%%', startangle=90)
    plt.title('Negotiable vs. Non-negotiable Fees')
    plt.savefig(f'{output_dir}/negotiable_fee_distribution.png')
    plt.close()
    
    # 9. Product count distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(x='product_count', data=df)
    plt.xlabel('Number of Products')
    plt.ylabel('Count')
    plt.title('Distribution of Product Counts')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'{output_dir}/product_count_distribution.png')
    plt.close()
    
    # 10. Verification ratio distribution
    if 'verification_ratio' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(df['verification_ratio'].dropna(), bins=20, kde=True)
        plt.xlabel('Verification Ratio')
        plt.ylabel('Count')
        plt.title('Distribution of Verification Ratios')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(f'{output_dir}/verification_ratio_distribution.png')
        plt.close()

def main():
    """
    Main function to run the enhanced fee analysis
    """
    print("Starting enhanced fee analysis...")
    
    # Get all CSV files in the current directory
    csv_files = glob.glob('*.csv')
    
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    
    print(f"Found {len(csv_files)} CSV files.")
    
    # Process each CSV file
    dataframes = []
    
    for file_path in csv_files:
        print(f"Processing {file_path}...")
        df = process_csv_file(file_path)
        
        if df is not None:
            dataframes.append(df)
    
    if not dataframes:
        print("No valid data found in CSV files.")
        return
    
    # Clean and consolidate data
    print("Cleaning and consolidating data...")
    cleaned_df = clean_and_consolidate_data(dataframes)
    
    if cleaned_df is None:
        print("Failed to clean and consolidate data.")
        return
    
    # Save the cleaned data
    print("Saving cleaned data...")
    cleaned_df.to_csv('enhanced_cleaned_fee_data.csv', index=False)
    
    # Generate summary statistics
    print("Generating summary statistics...")
    stats = generate_summary_statistics(cleaned_df)
    
    # Save summary statistics
    print("Saving summary statistics...")
    with open('enhanced_fee_analysis_summary.txt', 'w') as f:
        for key, value in stats.items():
            f.write(f"{key}:\n")
            f.write(f"{value}\n\n")
    
    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(cleaned_df)
    
    print("Enhanced fee analysis complete!")

if __name__ == "__main__":
    main()
