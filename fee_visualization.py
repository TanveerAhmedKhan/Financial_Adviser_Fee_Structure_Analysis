import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def load_structured_data(file_path='structured_fee_data.csv'):
    """
    Load the structured fee data
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded structured data with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        print(f"Error loading structured data: {e}")
        return None

def visualize_fee_trends_over_time(df):
    """
    Visualize how fee structures change over time
    """
    # Ensure filing_date is datetime
    df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')

    # Group by year
    df['filing_year'] = df['filing_date'].dt.year

    # Filter out rows with missing years
    year_df = df.dropna(subset=['filing_year'])

    # Get fee percentage columns for the first product (most common)
    fee_pct_cols = [col for col in df.columns if 'product_0' in col and '_fee_pct' in col]

    # Create a DataFrame to store yearly averages
    yearly_avgs = pd.DataFrame()

    for col in fee_pct_cols:
        # Group by year and calculate mean
        yearly_avg = year_df.groupby('filing_year')[col].mean()
        if not yearly_avg.empty:
            # Create a more readable column name
            tier_num = col.split('_')[1]
            col_name = f"Tier {tier_num}"
            yearly_avgs[col_name] = yearly_avg

    # Plot the trends
    if not yearly_avgs.empty:
        plt.figure(figsize=(12, 8))
        yearly_avgs.plot(marker='o')
        plt.xlabel('Year')
        plt.ylabel('Average Fee Percentage')
        plt.title('Trends in Fee Percentages Over Time (First Product)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(title='Fee Tier')
        plt.tight_layout()
        plt.savefig('fee_trends_over_time.png')
        plt.close()

        # Save the yearly averages
        yearly_avgs.to_csv('fee_yearly_averages.csv')
        print("Yearly fee averages saved to 'fee_yearly_averages.csv'")

    return yearly_avgs

def visualize_fee_structure_patterns(df):
    """
    Visualize patterns in fee structures
    """
    # Create a directory for visualizations
    os.makedirs('visualizations', exist_ok=True)

    # Filter to advisers with fee information
    fee_df = df[df['has_fee_info'] == True]

    # 1. Visualize relationship between product count and max tiers
    plt.figure(figsize=(10, 6))
    sns.countplot(x='product_count', hue='max_tiers', data=fee_df)
    plt.xlabel('Number of Products')
    plt.ylabel('Count')
    plt.title('Relationship Between Product Count and Maximum Tiers')
    plt.legend(title='Max Tiers')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('visualizations/product_count_vs_max_tiers.png')
    plt.close()

    # 2. Visualize fee percentages across tiers for different products
    # Get all product-tier combinations
    product_tier_cols = {}

    for col in fee_df.columns:
        if '_fee_pct' in col:
            parts = col.split('_')
            product = parts[0] + '_' + parts[1]
            tier = parts[2]

            if product not in product_tier_cols:
                product_tier_cols[product] = []

            product_tier_cols[product].append(col)

    # Plot fee percentages for each product
    for product, cols in product_tier_cols.items():
        if len(cols) == 0:
            continue

        plt.figure(figsize=(12, 8))

        # Create a list to hold all fee percentages for a box plot
        all_fees = []
        labels = []

        for col in cols:
            fees = fee_df[col].dropna()
            if not fees.empty:
                all_fees.append(fees)
                # Create a more readable label
                tier_num = col.split('_')[2]
                labels.append(f"Tier {tier_num}")

        if len(all_fees) == 0:
            plt.close()
            continue

        # Create box plot
        plt.boxplot(all_fees)
        plt.xticks(range(1, len(labels) + 1), labels)
        plt.ylabel('Fee Percentage')
        plt.title(f'Distribution of Fee Percentages by Tier ({product.replace("_", " ").title()})')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'visualizations/fee_percentages_{product}.png')
        plt.close()

    return True

def visualize_fee_structure_examples(df):
    """
    Visualize examples of different fee structures
    """
    # Create a directory for visualizations
    os.makedirs('visualizations/examples', exist_ok=True)

    # Filter to advisers with fee information
    fee_df = df[df['has_fee_info'] == True]

    # Find examples of different fee structures
    # 1. Single product with multiple tiers
    single_product_multi_tier = fee_df[(fee_df['product_count'] == 1) & (fee_df['max_tiers'] > 3)]

    if not single_product_multi_tier.empty:
        # Take the first example
        example = single_product_multi_tier.iloc[0]

        # Get the fee tiers
        tiers = []
        labels = []

        for i in range(int(example['max_tiers'])):
            lower = example[f'product_0_tier_{i}_lower']
            upper = example[f'product_0_tier_{i}_upper']
            fee_pct = example[f'product_0_tier_{i}_fee_pct']

            if not pd.isna(lower) and not pd.isna(fee_pct):
                tiers.append(fee_pct)

                # Format the label
                if pd.isna(upper) or upper == np.inf:
                    labels.append(f"${lower:,.0f}+")
                else:
                    labels.append(f"${lower:,.0f}-${upper:,.0f}")

        # Plot the example
        plt.figure(figsize=(12, 6))
        plt.bar(labels, tiers)
        plt.xlabel('Asset Range')
        plt.ylabel('Fee Percentage')
        plt.title(f'Example: Single Product with Multiple Tiers (Adviser ID: {example["adviser_id1"]})')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('visualizations/examples/single_product_multi_tier.png')
        plt.close()

    # 2. Multiple products
    multi_product = fee_df[fee_df['product_count'] > 1]

    if not multi_product.empty:
        # Take the first example
        example = multi_product.iloc[0]

        # Create a figure with subplots for each product
        fig, axes = plt.subplots(int(example['product_count']), 1, figsize=(12, 4 * int(example['product_count'])))

        # If there's only one product, axes will be a single axis, not an array
        if example['product_count'] == 1:
            axes = [axes]

        # Plot each product
        for product in range(int(example['product_count'])):
            # Get the fee tiers for this product
            tiers = []
            labels = []

            # Find the maximum tier for this product
            max_tier = 0
            for col in example.index:
                if f'product_{product}_tier_' in col and '_fee_pct' in col:
                    try:
                        tier_num = int(col.split('_')[2])
                        max_tier = max(max_tier, tier_num + 1)
                    except ValueError:
                        # Skip columns that don't have a numeric tier
                        continue

            for i in range(max_tier):
                lower_col = f'product_{product}_tier_{i}_lower'
                upper_col = f'product_{product}_tier_{i}_upper'
                fee_pct_col = f'product_{product}_tier_{i}_fee_pct'

                if lower_col in example.index and fee_pct_col in example.index:
                    lower = example[lower_col]
                    upper = example[upper_col] if upper_col in example.index else np.nan
                    fee_pct = example[fee_pct_col]

                    if not pd.isna(lower) and not pd.isna(fee_pct):
                        tiers.append(fee_pct)

                        # Format the label
                        if pd.isna(upper) or upper == np.inf:
                            labels.append(f"${lower:,.0f}+")
                        else:
                            labels.append(f"${lower:,.0f}-${upper:,.0f}")

            # Plot the tiers for this product
            if tiers:
                axes[product].bar(labels, tiers)
                axes[product].set_xlabel('Asset Range')
                axes[product].set_ylabel('Fee Percentage')
                axes[product].set_title(f'Product {product+1}')
                axes[product].tick_params(axis='x', rotation=45)
                axes[product].grid(True, linestyle='--', alpha=0.7)

        plt.suptitle(f'Example: Multiple Products (Adviser ID: {example["adviser_id1"]})')
        plt.tight_layout()
        plt.savefig('visualizations/examples/multiple_products.png')
        plt.close()

    return True

def visualize_fee_structure_comparison(df):
    """
    Compare fee structures across different advisers
    """
    # Create a directory for visualizations
    os.makedirs('visualizations/comparison', exist_ok=True)

    # Filter to advisers with fee information
    fee_df = df[df['has_fee_info'] == True]

    # Focus on the first product and first tier (most common)
    first_tier_col = 'product_0_tier_0_fee_pct'

    if first_tier_col not in fee_df.columns:
        print(f"Column {first_tier_col} not found in the data")
        return False

    # Filter to rows with first tier information
    first_tier_df = fee_df.dropna(subset=[first_tier_col])

    if first_tier_df.empty:
        print("No data available for the first tier")
        return False

    # 1. Distribution of first tier fees
    plt.figure(figsize=(10, 6))
    sns.histplot(first_tier_df[first_tier_col], bins=20, kde=True)
    plt.xlabel('Fee Percentage')
    plt.ylabel('Count')
    plt.title('Distribution of First Tier Fee Percentages')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('visualizations/comparison/first_tier_distribution.png')
    plt.close()

    # 2. Fee percentages by year
    first_tier_df['filing_year'] = pd.to_datetime(first_tier_df['filing_date']).dt.year

    plt.figure(figsize=(12, 6))
    sns.boxplot(x='filing_year', y=first_tier_col, data=first_tier_df)
    plt.xlabel('Filing Year')
    plt.ylabel('Fee Percentage')
    plt.title('First Tier Fee Percentages by Year')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('visualizations/comparison/first_tier_by_year.png')
    plt.close()

    # 3. Compare fee structures for advisers with multiple filings
    # Group by adviser ID and count filings
    adviser_counts = fee_df.groupby('adviser_id1').size()
    advisers_with_multiple_filings = adviser_counts[adviser_counts > 1].index

    if len(advisers_with_multiple_filings) > 0:
        # Select a few advisers with multiple filings
        selected_advisers = advisers_with_multiple_filings[:5]

        for adviser_id in selected_advisers:
            # Get the filings for this adviser
            adviser_df = fee_df[fee_df['adviser_id1'] == adviser_id].sort_values('filing_date')

            # Check if there's fee information
            if not adviser_df[first_tier_col].dropna().empty:
                plt.figure(figsize=(12, 6))

                # Plot the first tier fee over time
                plt.plot(adviser_df['filing_date'], adviser_df[first_tier_col], marker='o')
                plt.xlabel('Filing Date')
                plt.ylabel('Fee Percentage')
                plt.title(f'First Tier Fee Changes Over Time (Adviser ID: {adviser_id})')
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.savefig(f'visualizations/comparison/adviser_{adviser_id}_fee_changes.png')
                plt.close()

    return True

def main():
    """
    Main function to run the fee visualization
    """
    # Load the structured data
    df = load_structured_data()

    if df is None:
        # Try loading the original data and running the structure extraction
        print("Structured data not found. Loading original data...")
        from fee_structure_analysis import load_data, extract_adviser_info, detect_misplaced_answers, extract_fee_structures

        original_df = load_data('fee_analysis_formadv_part2_1_extracted.csv')

        if original_df is None:
            print("Could not load original data. Exiting.")
            return

        # Extract adviser information
        original_df = extract_adviser_info(original_df)

        # Detect and correct misplaced answers
        corrected_df = detect_misplaced_answers(original_df)

        # Extract fee structures
        df = extract_fee_structures(corrected_df)

        # Save the structured fee data
        df.to_csv('structured_fee_data.csv', index=False)
        print("Structured fee data saved to 'structured_fee_data.csv'")

    # Visualize fee trends over time
    yearly_avgs = visualize_fee_trends_over_time(df)

    # Visualize fee structure patterns
    visualize_fee_structure_patterns(df)

    # Visualize fee structure examples
    visualize_fee_structure_examples(df)

    # Visualize fee structure comparison
    visualize_fee_structure_comparison(df)

    print("\nFee visualization complete!")

if __name__ == "__main__":
    main()
