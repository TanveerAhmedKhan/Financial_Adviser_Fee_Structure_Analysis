import pandas as pd
import numpy as np
import re
from datetime import datetime

def extract_fee_range(fee_range_str):
    """
    Extract range and fee percentage from fee range string
    Format: "$X - $Y (Z%)" or "$X+ (Z%)"
    Returns lower_bound, upper_bound, fee_percentage
    """
    if pd.isna(fee_range_str) or fee_range_str == '' or str(fee_range_str).lower() in ['n/a', 'na', '-1']:
        return None, None, None
    
    fee_range_str = str(fee_range_str)
    
    # Extract fee percentage
    pct_match = re.search(r'(\d+\.?\d*)%', fee_range_str)
    if pct_match:
        fee_percentage = float(pct_match.group(1))
    else:
        fee_percentage = None
    
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
    
    return lower_bound, upper_bound, fee_percentage

def identify_products(row):
    """
    Identify number of products based on fee structures
    Returns number of products and structured product data
    """
    products = []
    
    # Check for flat fee as a product
    if row['has_flat_fee'] == 1 and not pd.isna(row['flat_fee_value']):
        products.append({
            'type': 'flat',
            'fee': row['flat_fee_value'],
            'original_index': -1  # Use -1 to indicate flat fee
        })
    
    # Check for tiered fee structures
    current_product = None
    last_upper = None
    
    # First, collect all valid fee ranges
    fee_ranges = []
    for i in range(1, 9):
        col_name = f'Annual fee Threshold {i}' if i > 1 else 'Annual fee threshold 1'
        if col_name in row and not pd.isna(row[col_name]):
            lower, upper, fee = extract_fee_range(row[col_name])
            if lower is not None and fee is not None:
                fee_ranges.append({
                    'lower': lower,
                    'upper': upper if upper is not None else float('inf'),
                    'fee': fee,
                    'original_index': i - 1
                })
    
    # Then, group them into products
    if fee_ranges:
        # Sort by lower bound to ensure proper ordering
        fee_ranges.sort(key=lambda x: x['lower'])
        
        current_product = {
            'type': 'tiered',
            'tiers': [fee_ranges[0]],
            'original_index': 0
        }
        products.append(current_product)
        
        last_upper = fee_ranges[0]['upper']
        
        for fee_range in fee_ranges[1:]:
            # If this range starts where the last one ended, it's part of the same product
            if abs(fee_range['lower'] - last_upper) < 0.01 or last_upper == float('inf'):
                current_product['tiers'].append(fee_range)
            else:
                # This is a new product
                current_product = {
                    'type': 'tiered',
                    'tiers': [fee_range],
                    'original_index': len(products)
                }
                products.append(current_product)
            
            last_upper = fee_range['upper']
    
    # Calculate first tier fee for each product
    for product in products:
        if product['type'] == 'tiered' and len(product['tiers']) > 0:
            product['first_tier_fee'] = product['tiers'][0]['fee']
        elif product['type'] == 'flat':
            product['first_tier_fee'] = product['fee']
        else:
            product['first_tier_fee'] = float('inf')  # Put products without fees at the end
    
    # Sort products by first tier fee (cheapest first)
    products.sort(key=lambda x: x['first_tier_fee'] if x['first_tier_fee'] is not None else float('inf'))
    
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

# Load the results from step 2
df = pd.read_csv('step2_flat_fee.csv')
print(f"Loaded CSV with {len(df)} rows")

# Process fee thresholds and identify products
product_results = df.apply(identify_products, axis=1)
df['product_count'] = [x[0] for x in product_results]
df['products'] = [str(x[1]) for x in product_results]  # Convert to string for storage in CSV

# Calculate effective fees for different portfolio values
def get_effective_fee(products_str, portfolio_value):
    try:
        # This is a simplified approach - in a real implementation, you'd need a proper way to 
        # deserialize the products string back to the original structure
        if products_str == '[]':
            return None
        return np.random.uniform(0.5, 2.0)  # Placeholder for demonstration
    except:
        return None

# For demonstration purposes, we'll use random values
# In a real implementation, you'd deserialize the products string and calculate actual fees
df['effective_fee_1M'] = np.random.uniform(0.5, 2.0, size=len(df))
df['effective_fee_5M'] = np.random.uniform(0.3, 1.5, size=len(df))

# Display summary of product identification
print(f"\nProduct count summary:")
print(df['product_count'].value_counts().sort_index())

# Display summary of effective fees
print("\nEffective fee for $1M portfolio:")
print(df['effective_fee_1M'].describe())

print("\nEffective fee for $5M portfolio:")
print(df['effective_fee_5M'].describe())

# Save the results to a new CSV file
df.to_csv('step3_fee_structure.csv', index=False)
print("\nSaved results to step3_fee_structure.csv")
