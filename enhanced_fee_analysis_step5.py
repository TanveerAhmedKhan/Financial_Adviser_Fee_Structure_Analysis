import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Create output directory for visualizations
output_dir = 'enhanced_analysis_results'
os.makedirs(output_dir, exist_ok=True)

# Load the results from step 4
df = pd.read_csv('step4_min_inv_negotiable.csv')
print(f"Loaded CSV with {len(df)} rows")

# Convert filing_date to datetime
df['filing_date'] = pd.to_datetime(df['filing_date'])

# Extract year from filing_date
df['filing_year'] = df['filing_date'].dt.year

# Generate summary statistics
stats = {}

# Number of unique advisers
stats['unique_advisers'] = df['adviser_id1'].nunique()

# Number of unique advisers by year
yearly_counts = df.groupby('filing_year')['adviser_id1'].nunique()
stats['unique_advisers_by_year'] = yearly_counts.to_dict()

# Number of unique advisers with extracted fee information
has_fee_df = df[(df['has_flat_fee'] == 1) | (df['product_count'] > 0)]
stats['unique_advisers_with_fees'] = has_fee_df['adviser_id1'].nunique()

# Number of unique advisers with extracted fee information by year
yearly_fee_counts = has_fee_df.groupby('filing_year')['adviser_id1'].nunique()
stats['unique_advisers_with_fees_by_year'] = yearly_fee_counts.to_dict()

# Frequency of different contracts (flat fee vs. AUM-based)
df['contract_type'] = 'No Fee Info'
df.loc[(df['has_flat_fee'] == 1) & (df['product_count'] == 0), 'contract_type'] = 'Flat Fee Only'
df.loc[(df['has_flat_fee'] == 0) & (df['product_count'] > 0), 'contract_type'] = 'AUM-Based Only'
df.loc[(df['has_flat_fee'] == 1) & (df['product_count'] > 0), 'contract_type'] = 'Both'

contract_types = df['contract_type'].value_counts()
stats['contract_types'] = contract_types.to_dict()

# Frequency of different contracts by year
contract_types_by_year = df.groupby(['filing_year', 'contract_type']).size().unstack().fillna(0)
stats['contract_types_by_year'] = contract_types_by_year.to_dict()

# Flat fee sum stats
flat_fee_stats = df[df['has_flat_fee'] == 1]['flat_fee_value'].describe()
stats['flat_fee_stats'] = flat_fee_stats.to_dict()

# Flat fee sum stats by year
flat_fee_stats_by_year = df[df['has_flat_fee'] == 1].groupby('filing_year')['flat_fee_value'].describe()
stats['flat_fee_stats_by_year'] = {str(year): values.to_dict() for year, values in flat_fee_stats_by_year.iterrows()}

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

# Save summary statistics to a text file
with open(f'{output_dir}/summary_statistics.txt', 'w') as f:
    f.write("ENHANCED FEE ANALYSIS SUMMARY STATISTICS\n")
    f.write("=======================================\n\n")
    
    f.write(f"Total records: {len(df)}\n")
    f.write(f"Unique advisers: {stats['unique_advisers']}\n")
    f.write(f"Unique advisers with fee information: {stats['unique_advisers_with_fees']}\n\n")
    
    f.write("Unique advisers by year:\n")
    for year, count in sorted(stats['unique_advisers_by_year'].items()):
        f.write(f"  {year}: {count}\n")
    f.write("\n")
    
    f.write("Contract types:\n")
    for contract_type, count in stats['contract_types'].items():
        f.write(f"  {contract_type}: {count} ({count/len(df)*100:.1f}%)\n")
    f.write("\n")
    
    f.write("Flat fee statistics:\n")
    for stat, value in stats['flat_fee_stats'].items():
        f.write(f"  {stat}: {value}\n")
    f.write("\n")
    
    f.write("Effective fee on $1M portfolio:\n")
    for stat, value in stats['effective_fee_1M_stats'].items():
        f.write(f"  {stat}: {value}\n")
    f.write("\n")
    
    f.write("Effective fee on $5M portfolio:\n")
    for stat, value in stats['effective_fee_5M_stats'].items():
        f.write(f"  {stat}: {value}\n")
    f.write("\n")
    
    f.write("Minimum investment statistics:\n")
    for stat, value in stats['min_investment_stats'].items():
        f.write(f"  {stat}: {value}\n")
    f.write("\n")
    
    f.write(f"Negotiable fee percentage: {stats['negotiable_percentage']:.1f}%\n")

print(f"Saved summary statistics to {output_dir}/summary_statistics.txt")

# Create visualizations

# 1. Contract types
plt.figure(figsize=(10, 6))
contract_counts = df['contract_type'].value_counts()
contract_counts.plot(kind='bar')
plt.xlabel('Contract Type')
plt.ylabel('Count')
plt.title('Distribution of Contract Types')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'{output_dir}/contract_type_distribution.png')
plt.close()

# 2. Effective fees comparison
plt.figure(figsize=(10, 6))
fee_comparison = pd.DataFrame({
    'Portfolio Size': ['$1M'] * len(df['effective_fee_1M'].dropna()) + ['$5M'] * len(df['effective_fee_5M'].dropna()),
    'Effective Fee (%)': list(df['effective_fee_1M'].dropna()) + list(df['effective_fee_5M'].dropna())
})
sns.boxplot(x='Portfolio Size', y='Effective Fee (%)', data=fee_comparison)
plt.title('Comparison of Effective Fees for Different Portfolio Sizes')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{output_dir}/effective_fee_comparison.png')
plt.close()

# 3. Minimum investment distribution
plt.figure(figsize=(10, 6))
min_inv_data = df[df['has_min_investment'] == 1]['min_investment_amount'].dropna()
if len(min_inv_data) > 0:
    sns.histplot(min_inv_data, bins=20, kde=True)
    plt.xlabel('Minimum Investment Amount ($)')
    plt.ylabel('Count')
    plt.title('Distribution of Minimum Investment Amounts')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xscale('log')  # Use log scale for better visualization
    plt.savefig(f'{output_dir}/min_investment_distribution.png')
plt.close()

# 4. Negotiable vs. Non-negotiable fees
plt.figure(figsize=(8, 8))
negotiable_counts = df['is_negotiable'].value_counts()
plt.pie(negotiable_counts, labels=['Negotiable', 'Non-negotiable'], autopct='%1.1f%%', startangle=90)
plt.title('Negotiable vs. Non-negotiable Fees')
plt.savefig(f'{output_dir}/negotiable_fee_distribution.png')
plt.close()

# 5. Product count distribution
plt.figure(figsize=(10, 6))
sns.countplot(x='product_count', data=df)
plt.xlabel('Number of Products')
plt.ylabel('Count')
plt.title('Distribution of Product Counts')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{output_dir}/product_count_distribution.png')
plt.close()

# 6. Contract types by year
plt.figure(figsize=(12, 8))
contract_pivot = df.pivot_table(index='filing_year', columns='contract_type', aggfunc='size', fill_value=0)
contract_pivot.plot(kind='bar', stacked=True)
plt.xlabel('Filing Year')
plt.ylabel('Count')
plt.title('Contract Types by Year')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='Contract Type')
plt.tight_layout()
plt.savefig(f'{output_dir}/contract_types_by_year.png')
plt.close()

# 7. Effective fees by year
plt.figure(figsize=(12, 6))
sns.boxplot(x='filing_year', y='effective_fee_1M', data=df)
plt.xlabel('Filing Year')
plt.ylabel('Effective Fee for $1M Portfolio (%)')
plt.title('Effective Fees by Year ($1M Portfolio)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{output_dir}/effective_fees_by_year.png')
plt.close()

# 8. Minimum investment by year
plt.figure(figsize=(12, 6))
min_inv_by_year = df[df['has_min_investment'] == 1].pivot_table(
    index='filing_year', 
    values='min_investment_amount',
    aggfunc=['mean', 'median']
)
min_inv_by_year.plot(kind='bar')
plt.xlabel('Filing Year')
plt.ylabel('Minimum Investment Amount ($)')
plt.title('Minimum Investment by Year')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(['Mean', 'Median'])
plt.tight_layout()
plt.savefig(f'{output_dir}/min_investment_by_year.png')
plt.close()

print(f"Created visualizations in {output_dir}/")

# Create a consolidated CSV file with the most important columns
consolidated_df = df[[
    'adviser_id1', 'adviser_id2', 'filing_date', 'filing_year',
    'has_flat_fee', 'flat_fee_value', 'product_count', 'contract_type',
    'effective_fee_1M', 'effective_fee_5M',
    'has_min_investment', 'min_investment_amount',
    'is_negotiable', 'has_negotiable_threshold', 'negotiable_threshold_amount'
]]

consolidated_df.to_csv(f'{output_dir}/consolidated_fee_data.csv', index=False)
print(f"Saved consolidated data to {output_dir}/consolidated_fee_data.csv")

print("\nEnhanced fee analysis complete!")
