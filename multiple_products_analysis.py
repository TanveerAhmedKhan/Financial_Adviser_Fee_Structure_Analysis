import pandas as pd
import numpy as np
import re
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

def detect_multiple_products(df):
    """
    Detect and analyze advisers with multiple products
    """
    # Filter to advisers with fee information
    fee_df = df[df['has_fee_info'] == True].copy()

    # Count advisers with multiple products
    multiple_products_df = fee_df[fee_df['product_count'] > 1]
    print(f"Advisers with multiple products: {len(multiple_products_df)} out of {len(fee_df)} ({len(multiple_products_df)/len(fee_df)*100:.1f}%)")

    # Create a directory for visualizations
    os.makedirs('multiple_products', exist_ok=True)

    # Analyze the distribution of product counts
    product_counts = fee_df['product_count'].value_counts().sort_index()
    print("\nDistribution of product counts:")
    print(product_counts)

    # Plot the distribution
    plt.figure(figsize=(10, 6))
    product_counts.plot(kind='bar')
    plt.xlabel('Number of Products')
    plt.ylabel('Count of Advisers')
    plt.title('Distribution of Product Counts per Adviser')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('multiple_products/product_count_distribution.png')
    plt.close()

    return multiple_products_df

def analyze_product_fee_differences(multiple_products_df):
    """
    Analyze fee differences between products for the same adviser
    """
    # Create a DataFrame to store fee differences
    fee_diff_df = pd.DataFrame()

    # Add identifier columns
    fee_diff_df['File Name'] = multiple_products_df['File Name']
    fee_diff_df['adviser_id1'] = multiple_products_df['adviser_id1']
    fee_diff_df['adviser_id2'] = multiple_products_df['adviser_id2']
    fee_diff_df['filing_date'] = multiple_products_df['filing_date']
    fee_diff_df['product_count'] = multiple_products_df['product_count']

    # Calculate fee differences between products
    for idx, row in multiple_products_df.iterrows():
        product_count = int(row['product_count'])

        if product_count <= 1:
            continue

        # Compare the first tier of each product
        first_tier_fees = []

        for product in range(product_count):
            fee_col = f'product_{product}_tier_0_fee_pct'

            if fee_col in row.index and not pd.isna(row[fee_col]):
                first_tier_fees.append(row[fee_col])

        if len(first_tier_fees) > 1:
            # Calculate max difference between products
            max_diff = max(first_tier_fees) - min(first_tier_fees)
            fee_diff_df.loc[idx, 'max_fee_diff'] = max_diff

            # Calculate average fee
            avg_fee = sum(first_tier_fees) / len(first_tier_fees)
            fee_diff_df.loc[idx, 'avg_fee'] = avg_fee

            # Calculate relative difference
            fee_diff_df.loc[idx, 'relative_diff'] = max_diff / avg_fee if avg_fee > 0 else np.nan

    # Filter to rows with fee differences
    fee_diff_df = fee_diff_df.dropna(subset=['max_fee_diff'])

    # Analyze the distribution of fee differences
    print("\nFee differences between products:")
    print(f"Average maximum fee difference: {fee_diff_df['max_fee_diff'].mean():.2f} percentage points")
    print(f"Median maximum fee difference: {fee_diff_df['max_fee_diff'].median():.2f} percentage points")
    print(f"Average relative difference: {fee_diff_df['relative_diff'].mean()*100:.1f}%")

    # Plot the distribution of fee differences
    plt.figure(figsize=(10, 6))
    sns.histplot(fee_diff_df['max_fee_diff'], bins=20, kde=True)
    plt.xlabel('Maximum Fee Difference (percentage points)')
    plt.ylabel('Count')
    plt.title('Distribution of Maximum Fee Differences Between Products')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('multiple_products/fee_difference_distribution.png')
    plt.close()

    # Plot the relationship between product count and fee difference
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='product_count', y='max_fee_diff', data=fee_diff_df)
    plt.xlabel('Number of Products')
    plt.ylabel('Maximum Fee Difference (percentage points)')
    plt.title('Relationship Between Product Count and Fee Difference')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('multiple_products/product_count_vs_fee_diff.png')
    plt.close()

    return fee_diff_df

def analyze_product_structure_differences(multiple_products_df):
    """
    Analyze differences in fee structure (number of tiers) between products
    """
    # Create a DataFrame to store structure differences
    structure_diff_df = pd.DataFrame()

    # Add identifier columns
    structure_diff_df['File Name'] = multiple_products_df['File Name']
    structure_diff_df['adviser_id1'] = multiple_products_df['adviser_id1']
    structure_diff_df['adviser_id2'] = multiple_products_df['adviser_id2']
    structure_diff_df['filing_date'] = multiple_products_df['filing_date']
    structure_diff_df['product_count'] = multiple_products_df['product_count']

    # Calculate structure differences between products
    for idx, row in multiple_products_df.iterrows():
        product_count = int(row['product_count'])

        if product_count <= 1:
            continue

        # Count tiers for each product
        product_tiers = []

        for product in range(product_count):
            # Count non-NaN fee percentages for this product
            tier_count = 0

            for col in row.index:
                if f'product_{product}_tier_' in col and '_fee_pct' in col and not pd.isna(row[col]):
                    tier_count += 1

            if tier_count > 0:
                product_tiers.append(tier_count)
                structure_diff_df.loc[idx, f'product_{product}_tiers'] = tier_count

        if len(product_tiers) > 1:
            # Calculate max difference in tier count
            max_tier_diff = max(product_tiers) - min(product_tiers)
            structure_diff_df.loc[idx, 'max_tier_diff'] = max_tier_diff

            # Calculate average tier count
            avg_tiers = sum(product_tiers) / len(product_tiers)
            structure_diff_df.loc[idx, 'avg_tiers'] = avg_tiers

    # Filter to rows with structure differences
    structure_diff_df = structure_diff_df.dropna(subset=['max_tier_diff'])

    # Analyze the distribution of structure differences
    print("\nStructure differences between products:")
    print(f"Average maximum tier difference: {structure_diff_df['max_tier_diff'].mean():.2f} tiers")
    print(f"Median maximum tier difference: {structure_diff_df['max_tier_diff'].median():.2f} tiers")

    # Plot the distribution of tier differences
    plt.figure(figsize=(10, 6))
    tier_diff_counts = structure_diff_df['max_tier_diff'].value_counts().sort_index()
    tier_diff_counts.plot(kind='bar')
    plt.xlabel('Maximum Tier Difference')
    plt.ylabel('Count')
    plt.title('Distribution of Maximum Tier Differences Between Products')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('multiple_products/tier_difference_distribution.png')
    plt.close()

    return structure_diff_df

def visualize_multiple_product_examples(multiple_products_df):
    """
    Visualize examples of advisers with multiple products
    """
    # Create a directory for examples
    os.makedirs('multiple_products/examples', exist_ok=True)

    print("\nGenerating multiple product examples:")
    print(f"Total advisers with multiple products: {len(multiple_products_df)}")

    # Select a few examples with different product counts
    for product_count in range(2, min(6, multiple_products_df['product_count'].max() + 1)):
        # Find advisers with this product count
        examples = multiple_products_df[multiple_products_df['product_count'] == product_count]
        print(f"\nAdvisers with {product_count} products: {len(examples)}")

        if examples.empty:
            continue

        # Find advisers with actual fee tier data
        valid_examples = []
        for idx, row in examples.iterrows():
            has_data = False
            for product in range(product_count):
                for i in range(5):  # Check up to 5 tiers
                    fee_pct_col = f'product_{product}_tier_{i}_fee_pct'
                    lower_col = f'product_{product}_tier_{i}_lower'
                    if fee_pct_col in row.index and lower_col in row.index:
                        if not pd.isna(row[fee_pct_col]) and not pd.isna(row[lower_col]):
                            has_data = True
                            break
                if has_data:
                    break
            if has_data:
                valid_examples.append(idx)

        if not valid_examples:
            print(f"No advisers with {product_count} products have valid fee tier data. Skipping.")
            continue

        # Take the first valid example
        example = multiple_products_df.loc[valid_examples[0]]
        print(f"Selected adviser ID: {example['adviser_id1']}")

        # Create a figure with subplots for each product
        fig, axes = plt.subplots(product_count, 1, figsize=(12, 4 * product_count))

        # If there's only one product, axes will be a single axis, not an array
        if product_count == 1:
            axes = [axes]

        # Plot each product
        for product in range(product_count):
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

            print(f"  Product {product+1} has maximum {max_tier} tiers")

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

                        print(f"    Tier {i+1}: {labels[-1]} = {fee_pct}%")

            # Plot the tiers for this product
            if tiers:
                axes[product].bar(labels, tiers)
                axes[product].set_xlabel('Asset Range')
                axes[product].set_ylabel('Fee Percentage')
                axes[product].set_title(f'Product {product+1}')
                axes[product].tick_params(axis='x', rotation=45)
                axes[product].grid(True, linestyle='--', alpha=0.7)
            else:
                print(f"    WARNING: No valid tiers found for Product {product+1}")
                # Add text to the empty subplot
                axes[product].text(0.5, 0.5, 'No fee tier data available',
                                 horizontalalignment='center',
                                 verticalalignment='center',
                                 transform=axes[product].transAxes,
                                 fontsize=14)
                axes[product].set_title(f'Product {product+1} - No Data')
                axes[product].axis('off')

        plt.suptitle(f'Example: {product_count} Products (Adviser ID: {example["adviser_id1"]})')
        plt.tight_layout()
        plt.savefig(f'multiple_products/examples/{product_count}_products.png')
        plt.close()
        print(f"  Saved visualization to multiple_products/examples/{product_count}_products.png")

    return True

def analyze_product_patterns(multiple_products_df):
    """
    Analyze patterns in how products are structured
    """
    # Create a DataFrame to store pattern information
    pattern_df = pd.DataFrame()

    # Add identifier columns
    pattern_df['File Name'] = multiple_products_df['File Name']
    pattern_df['adviser_id1'] = multiple_products_df['adviser_id1']
    pattern_df['adviser_id2'] = multiple_products_df['adviser_id2']
    pattern_df['filing_date'] = multiple_products_df['filing_date']
    pattern_df['product_count'] = multiple_products_df['product_count']

    # Define patterns to check
    patterns = {
        'decreasing_fees': 'First product has higher fees than second product',
        'increasing_fees': 'First product has lower fees than second product',
        'different_tier_structure': 'Products have different tier structures',
        'similar_structure_different_fees': 'Products have similar structure but different fees',
    }

    # Initialize pattern columns
    for pattern in patterns:
        pattern_df[pattern] = False

    # Check patterns for each adviser
    for idx, row in multiple_products_df.iterrows():
        product_count = int(row['product_count'])

        if product_count <= 1:
            continue

        # Compare the first tier of the first two products
        product0_fee_col = 'product_0_tier_0_fee_pct'
        product1_fee_col = 'product_1_tier_0_fee_pct'

        if product0_fee_col in row.index and product1_fee_col in row.index and not pd.isna(row[product0_fee_col]) and not pd.isna(row[product1_fee_col]):
            # Check fee relationship
            if row[product0_fee_col] > row[product1_fee_col]:
                pattern_df.loc[idx, 'decreasing_fees'] = True
            elif row[product0_fee_col] < row[product1_fee_col]:
                pattern_df.loc[idx, 'increasing_fees'] = True

        # Count tiers for each product
        product0_tiers = 0
        product1_tiers = 0

        for col in row.index:
            if 'product_0_tier_' in col and '_fee_pct' in col and not pd.isna(row[col]):
                product0_tiers += 1
            elif 'product_1_tier_' in col and '_fee_pct' in col and not pd.isna(row[col]):
                product1_tiers += 1

        # Check tier structure relationship
        if product0_tiers > 0 and product1_tiers > 0:
            if abs(product0_tiers - product1_tiers) >= 2:
                pattern_df.loc[idx, 'different_tier_structure'] = True
            elif abs(product0_tiers - product1_tiers) < 2:
                # Check if fees are different
                fee_diff = False

                for i in range(min(product0_tiers, product1_tiers)):
                    product0_fee_col = f'product_0_tier_{i}_fee_pct'
                    product1_fee_col = f'product_1_tier_{i}_fee_pct'

                    if product0_fee_col in row.index and product1_fee_col in row.index and not pd.isna(row[product0_fee_col]) and not pd.isna(row[product1_fee_col]):
                        if abs(row[product0_fee_col] - row[product1_fee_col]) > 0.1:  # 10 basis points difference
                            fee_diff = True
                            break

                if fee_diff:
                    pattern_df.loc[idx, 'similar_structure_different_fees'] = True

    # Count occurrences of each pattern
    print("\nPatterns in multiple products:")
    for pattern, description in patterns.items():
        count = pattern_df[pattern].sum()
        percentage = count / len(pattern_df) * 100
        print(f"{description}: {count} ({percentage:.1f}%)")

    # Plot pattern distribution
    plt.figure(figsize=(12, 6))
    pattern_counts = [pattern_df[pattern].sum() for pattern in patterns]
    plt.bar(patterns.values(), pattern_counts)
    plt.xlabel('Pattern')
    plt.ylabel('Count')
    plt.title('Distribution of Multiple Product Patterns')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('multiple_products/pattern_distribution.png')
    plt.close()

    return pattern_df

def main():
    """
    Main function to run the multiple products analysis
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

    # Detect multiple products
    multiple_products_df = detect_multiple_products(df)

    # Analyze fee differences between products
    fee_diff_df = analyze_product_fee_differences(multiple_products_df)

    # Analyze structure differences between products
    structure_diff_df = analyze_product_structure_differences(multiple_products_df)

    # Visualize examples of multiple products
    visualize_multiple_product_examples(multiple_products_df)

    # Analyze patterns in multiple products
    pattern_df = analyze_product_patterns(multiple_products_df)

    print("\nMultiple products analysis complete!")

if __name__ == "__main__":
    main()
