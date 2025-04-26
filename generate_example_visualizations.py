import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def main():
    # Load the structured data
    df = pd.read_csv('structured_fee_data.csv')
    print(f"Loaded structured data with {df.shape[0]} rows and {df.shape[1]} columns")
    
    # Filter to advisers with multiple products
    multi_df = df[df['product_count'] > 1]
    print(f"Advisers with multiple products: {len(multi_df)}")
    
    # Create directory for examples
    os.makedirs('multiple_products/examples', exist_ok=True)
    
    # Generate examples for different product counts
    for product_count in range(2, 5):
        # Find advisers with this product count
        examples = multi_df[multi_df['product_count'] == product_count]
        print(f"\nAdvisers with {product_count} products: {len(examples)}")
        
        if len(examples) == 0:
            continue
        
        # Find an example with fee data for all products
        for idx, row in examples.iterrows():
            has_all_data = True
            for product in range(product_count):
                fee_col = f'product_{product}_tier_0_fee_pct'
                if fee_col not in row.index or pd.isna(row[fee_col]):
                    has_all_data = False
                    break
            
            if has_all_data:
                example = row
                print(f"Found example with adviser ID: {example['adviser_id1']}")
                
                # Create figure with subplots
                fig, axes = plt.subplots(product_count, 1, figsize=(12, 4 * product_count))
                
                # If there's only one product, axes will be a single axis, not an array
                if product_count == 1:
                    axes = [axes]
                
                # Plot each product
                for product in range(product_count):
                    # Get the fee tiers for this product
                    tiers = []
                    labels = []
                    
                    # Check each tier
                    for tier in range(6):  # Check up to 6 tiers
                        fee_col = f'product_{product}_tier_{tier}_fee_pct'
                        lower_col = f'product_{product}_tier_{tier}_lower'
                        upper_col = f'product_{product}_tier_{tier}_upper'
                        
                        if fee_col in example.index and lower_col in example.index and not pd.isna(example[fee_col]) and not pd.isna(example[lower_col]):
                            fee = example[fee_col]
                            lower = example[lower_col]
                            upper = example[upper_col] if upper_col in example.index and not pd.isna(example[upper_col]) else np.inf
                            
                            tiers.append(fee)
                            
                            # Format the label
                            if upper == np.inf:
                                labels.append(f"${lower:,.0f}+")
                            else:
                                labels.append(f"${lower:,.0f}-${upper:,.0f}")
                            
                            print(f"  Product {product+1}, Tier {tier+1}: {labels[-1]} = {fee}%")
                    
                    # Plot the tiers
                    if tiers:
                        axes[product].bar(labels, tiers)
                        axes[product].set_xlabel('Asset Range')
                        axes[product].set_ylabel('Fee Percentage')
                        axes[product].set_title(f'Product {product+1}')
                        axes[product].tick_params(axis='x', rotation=45)
                        axes[product].grid(True, linestyle='--', alpha=0.7)
                    else:
                        print(f"  WARNING: No valid tiers found for Product {product+1}")
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
                
                # We found an example, so break the loop
                break
    
    print("\nExample visualizations complete!")

if __name__ == "__main__":
    main()
