import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def load_data(file_path='fee_analysis_formadv_part2_1_extracted.csv'):
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
    import re
    
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

def analyze_fee_structure(df):
    """
    Analyze the fee structure data
    """
    # Create output directory
    os.makedirs('analysis_results', exist_ok=True)
    
    # Count flat fee vs tiered fee structures
    flat_fee_count = df[df['Flat Fee'].str.contains(r'\$|%', na=False)].shape[0]
    no_flat_fee_count = df[df['Flat Fee'] == 'No'].shape[0]
    no_fee_info_count = df[df['Flat Fee'].str.contains('No fee information', na=False)].shape[0]
    
    print(f"Flat fee structures: {flat_fee_count}")
    print(f"Tiered fee structures: {no_flat_fee_count}")
    print(f"No fee information: {no_fee_info_count}")
    
    # Plot the distribution
    plt.figure(figsize=(10, 6))
    fee_structure_counts = pd.Series({
        'Flat Fee': flat_fee_count,
        'Tiered Fee': no_flat_fee_count,
        'No Fee Info': no_fee_info_count
    })
    fee_structure_counts.plot(kind='bar')
    plt.title('Distribution of Fee Structure Types')
    plt.ylabel('Count')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('analysis_results/fee_structure_types.png')
    plt.close()
    
    # Analyze negotiable fees
    negotiable_count = df[df['Negotiable (Yes/No)'] == 'Yes'].shape[0]
    non_negotiable_count = df[df['Negotiable (Yes/No)'] == 'No'].shape[0]
    
    print(f"Negotiable fees: {negotiable_count}")
    print(f"Non-negotiable fees: {non_negotiable_count}")
    
    # Plot the distribution
    plt.figure(figsize=(8, 6))
    negotiable_counts = pd.Series({
        'Negotiable': negotiable_count,
        'Non-negotiable': non_negotiable_count
    })
    negotiable_counts.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Negotiable vs Non-negotiable Fees')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('analysis_results/negotiable_fees.png')
    plt.close()
    
    # Analyze minimum investment
    min_investment_values = []
    
    for value in df['Minimum investment (Amount/No)']:
        if pd.isna(value) or value == '-1' or value.lower() in ['no', 'n/a']:
            continue
            
        try:
            # Extract dollar amount
            import re
            match = re.search(r'\$([0-9,]+)', str(value))
            if match:
                amount = match.group(1).replace(',', '')
                min_investment_values.append(float(amount))
        except Exception as e:
            print(f"Error processing minimum investment {value}: {e}")
    
    if min_investment_values:
        print(f"Average minimum investment: ${np.mean(min_investment_values):,.2f}")
        print(f"Median minimum investment: ${np.median(min_investment_values):,.2f}")
        
        # Plot the distribution
        plt.figure(figsize=(10, 6))
        plt.hist(min_investment_values, bins=20, edgecolor='black')
        plt.title('Distribution of Minimum Investment Requirements')
        plt.xlabel('Minimum Investment ($)')
        plt.ylabel('Count')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('analysis_results/minimum_investment.png')
        plt.close()
    
    return df

def analyze_fee_thresholds(df):
    """
    Analyze the fee thresholds and percentages
    """
    import re
    
    # Create lists to store extracted fee percentages
    tier_fees = {
        'Tier 1': [],
        'Tier 2': [],
        'Tier 3': [],
        'Tier 4': [],
        'Tier 5': [],
        'Tier 6': [],
        'Tier 7': [],
        'Tier 8': []
    }
    
    # Define columns for each tier
    tier_columns = {
        'Tier 1': 'Annual fee threshold 1',
        'Tier 2': 'Annual fee Threshold 2',
        'Tier 3': 'Annual fee Threshold 3',
        'Tier 4': 'Annual fee Threshold 4',
        'Tier 5': 'Annual fee Threshold 5',
        'Tier 6': 'Annual fee Threshold 6',
        'Tier 7': 'Annual fee Threshold 7',
        'Tier 8': 'Annual fee Threshold 8'
    }
    
    # Extract fee percentages
    for tier, column in tier_columns.items():
        if column not in df.columns:
            continue
            
        for value in df[column]:
            if pd.isna(value) or value == '-1' or value == 'N/a':
                continue
                
            try:
                # Extract percentage
                match = re.search(r'(\d+\.?\d*)%', str(value))
                if match:
                    fee_pct = float(match.group(1))
                    tier_fees[tier].append(fee_pct)
            except Exception as e:
                print(f"Error processing {tier} fee {value}: {e}")
    
    # Calculate statistics
    for tier, fees in tier_fees.items():
        if fees:
            print(f"{tier} - Average fee: {np.mean(fees):.2f}%, Median: {np.median(fees):.2f}%, Min: {np.min(fees):.2f}%, Max: {np.max(fees):.2f}%")
    
    # Plot the fee distributions
    plt.figure(figsize=(12, 8))
    
    # Create box plots for each tier
    data = [fees for tier, fees in tier_fees.items() if fees]
    labels = [tier for tier, fees in tier_fees.items() if fees]
    
    plt.boxplot(data)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.title('Distribution of Fee Percentages by Tier')
    plt.ylabel('Fee Percentage')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('analysis_results/fee_percentages_by_tier.png')
    plt.close()
    
    return tier_fees

def detect_multiple_products(df):
    """
    Detect advisers with multiple products
    """
    import re
    
    # Create a column to track potential multiple products
    df['potential_multiple_products'] = False
    
    # Define columns for each tier
    tier_columns = [
        'Annual fee threshold 1',
        'Annual fee Threshold 2',
        'Annual fee Threshold 3',
        'Annual fee Threshold 4',
        'Annual fee Threshold 5',
        'Annual fee Threshold 6',
        'Annual fee Threshold 7',
        'Annual fee Threshold 8'
    ]
    
    # Check for patterns that indicate multiple products
    for idx, row in df.iterrows():
        # Skip rows with no fee information
        if pd.isna(row['Flat Fee']) or row['Flat Fee'] == '-1' or 'No fee information' in str(row['Flat Fee']):
            continue
            
        # Check for multiple starting tiers (tiers that start at $0 or low values)
        low_start_tiers = 0
        
        for column in tier_columns:
            if column not in df.columns:
                continue
                
            value = row[column]
            if pd.isna(value) or value == '-1' or value == 'N/a':
                continue
                
            # Check if this tier starts at $0 or a low value
            match = re.search(r'\$(\d+)', str(value))
            if match:
                start_value = int(match.group(1))
                if start_value <= 1000:
                    low_start_tiers += 1
        
        # If there are multiple tiers starting at low values, it might indicate multiple products
        if low_start_tiers > 1:
            df.loc[idx, 'potential_multiple_products'] = True
    
    # Count advisers with potential multiple products
    multiple_products_count = df['potential_multiple_products'].sum()
    print(f"Advisers with potential multiple products: {multiple_products_count}")
    
    # Get examples of advisers with multiple products
    multiple_products_df = df[df['potential_multiple_products'] == True]
    
    if not multiple_products_df.empty:
        # Take a few examples
        examples = multiple_products_df.head(3)
        
        print("\nExamples of advisers with multiple products:")
        for idx, example in examples.iterrows():
            print(f"\nAdviser ID: {example['adviser_id1']}")
            
            for column in tier_columns:
                if column not in df.columns:
                    continue
                    
                value = example[column]
                if pd.isna(value) or value == '-1' or value == 'N/a':
                    continue
                    
                print(f"  {column}: {value}")
    
    return multiple_products_df

def analyze_fee_trends_over_time(df):
    """
    Analyze how fee structures change over time
    """
    import re
    
    # Ensure filing_date is datetime
    df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
    
    # Group by year
    df['filing_year'] = df['filing_date'].dt.year
    
    # Filter out rows with missing years
    year_df = df.dropna(subset=['filing_year'])
    
    # Define columns for each tier
    tier_columns = {
        'Tier 1': 'Annual fee threshold 1',
        'Tier 2': 'Annual fee Threshold 2',
        'Tier 3': 'Annual fee Threshold 3',
        'Tier 4': 'Annual fee Threshold 4'
    }
    
    # Create a DataFrame to store yearly averages
    yearly_avgs = pd.DataFrame()
    
    # Extract fee percentages and calculate yearly averages
    for tier, column in tier_columns.items():
        if column not in df.columns:
            continue
            
        # Create a column to store extracted percentages
        percentage_col = f"{tier}_percentage"
        year_df[percentage_col] = np.nan
        
        for idx, value in enumerate(year_df[column]):
            if pd.isna(value) or value == '-1' or value == 'N/a':
                continue
                
            try:
                # Extract percentage
                match = re.search(r'(\d+\.?\d*)%', str(value))
                if match:
                    fee_pct = float(match.group(1))
                    year_df.loc[year_df.index[idx], percentage_col] = fee_pct
            except Exception as e:
                print(f"Error processing {tier} fee {value}: {e}")
        
        # Group by year and calculate mean
        tier_yearly_avg = year_df.groupby('filing_year')[percentage_col].mean()
        if not tier_yearly_avg.empty:
            yearly_avgs[tier] = tier_yearly_avg
    
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
        plt.savefig('analysis_results/fee_trends_over_time.png')
        plt.close()
        
        # Save the yearly averages
        yearly_avgs.to_csv('analysis_results/fee_yearly_averages.csv')
        print("Yearly fee averages saved to 'analysis_results/fee_yearly_averages.csv'")
    
    return yearly_avgs

def main():
    """
    Main function to run the fee data analysis
    """
    # Load the data
    df = load_data()
    
    if df is None:
        return
    
    # Extract adviser information
    df = extract_adviser_info(df)
    
    # Analyze fee structure
    df = analyze_fee_structure(df)
    
    # Analyze fee thresholds
    tier_fees = analyze_fee_thresholds(df)
    
    # Detect multiple products
    multiple_products_df = detect_multiple_products(df)
    
    # Analyze fee trends over time
    yearly_avgs = analyze_fee_trends_over_time(df)
    
    print("\nFee data analysis complete!")

if __name__ == "__main__":
    main()
