import os
import sys
import time
import pandas as pd

def run_script(script_name, description):
    """
    Run a Python script and print its output
    """
    print(f"\n{'='*80}")
    print(f"Running {script_name}: {description}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    exit_code = os.system(f"python {script_name}")
    end_time = time.time()
    
    if exit_code == 0:
        print(f"\n{script_name} completed successfully in {end_time - start_time:.2f} seconds")
    else:
        print(f"\n{script_name} failed with exit code {exit_code}")
    
    return exit_code == 0

def main():
    """
    Run all fee analysis scripts in sequence
    """
    print("Starting fee structure analysis pipeline")
    
    # Check if the data file exists
    if not os.path.exists('fee_analysis_formadv_part2_1_extracted.csv'):
        print("Error: fee_analysis_formadv_part2_1_extracted.csv not found")
        return False
    
    # Create output directories
    os.makedirs('output', exist_ok=True)
    
    # Step 1: Run the basic data cleaning and analysis
    if not run_script('fee_data_cleaning.py', 'Basic data cleaning and analysis'):
        print("Error in basic data cleaning. Stopping pipeline.")
        return False
    
    # Step 2: Run the fee structure analysis
    if not run_script('fee_structure_analysis.py', 'Fee structure analysis'):
        print("Error in fee structure analysis. Continuing with other analyses.")
    
    # Step 3: Run the fee visualization
    if not run_script('fee_visualization.py', 'Fee visualization'):
        print("Error in fee visualization. Continuing with other analyses.")
    
    # Step 4: Run the multiple products analysis
    if not run_script('multiple_products_analysis.py', 'Multiple products analysis'):
        print("Error in multiple products analysis.")
    
    # Step 5: Generate a summary report
    try:
        generate_summary_report()
    except Exception as e:
        print(f"Error generating summary report: {e}")
    
    print("\nFee structure analysis pipeline completed")
    return True

def generate_summary_report():
    """
    Generate a summary report of all analyses
    """
    print("\nGenerating summary report...")
    
    # Check if the cleaned data exists
    if os.path.exists('cleaned_fee_data.csv'):
        cleaned_df = pd.read_csv('cleaned_fee_data.csv')
    else:
        print("Warning: cleaned_fee_data.csv not found")
        cleaned_df = None
    
    # Check if the structured data exists
    if os.path.exists('structured_fee_data.csv'):
        structured_df = pd.read_csv('structured_fee_data.csv')
    else:
        print("Warning: structured_fee_data.csv not found")
        structured_df = None
    
    # Create the report
    report = []
    report.append("# Fee Structure Analysis Summary Report")
    report.append("\n## Dataset Overview")
    
    if cleaned_df is not None:
        report.append(f"- Total records: {len(cleaned_df)}")
        report.append(f"- Unique advisers: {cleaned_df['adviser_id1'].nunique()}")
        report.append(f"- Date range: {cleaned_df['filing_date'].min()} to {cleaned_df['filing_date'].max()}")
    
    report.append("\n## Fee Structure Types")
    
    if cleaned_df is not None and 'fee_structure_type' in cleaned_df.columns:
        fee_structure_counts = cleaned_df['fee_structure_type'].value_counts()
        report.append("| Fee Structure Type | Count | Percentage |")
        report.append("|-------------------|-------|------------|")
        for structure_type, count in fee_structure_counts.items():
            percentage = count / len(cleaned_df) * 100
            report.append(f"| {structure_type} | {count} | {percentage:.1f}% |")
    
    report.append("\n## Multiple Products Analysis")
    
    if structured_df is not None and 'product_count' in structured_df.columns:
        product_counts = structured_df['product_count'].value_counts().sort_index()
        report.append("| Number of Products | Count | Percentage |")
        report.append("|-------------------|-------|------------|")
        for product_count, count in product_counts.items():
            percentage = count / len(structured_df) * 100
            report.append(f"| {product_count} | {count} | {percentage:.1f}% |")
    
    report.append("\n## Fee Percentages by Tier")
    
    if structured_df is not None:
        # Get fee percentage columns for the first product
        fee_pct_cols = [col for col in structured_df.columns if 'product_0_tier_' in col and '_fee_pct' in col]
        
        if fee_pct_cols:
            report.append("| Tier | Average Fee | Median Fee | Min Fee | Max Fee |")
            report.append("|------|-------------|------------|---------|---------|")
            
            for col in fee_pct_cols:
                tier = col.split('_')[2]
                fees = structured_df[col].dropna()
                
                if not fees.empty:
                    avg_fee = fees.mean()
                    median_fee = fees.median()
                    min_fee = fees.min()
                    max_fee = fees.max()
                    
                    report.append(f"| {tier} | {avg_fee:.2f}% | {median_fee:.2f}% | {min_fee:.2f}% | {max_fee:.2f}% |")
    
    report.append("\n## Visualizations")
    report.append("The following visualizations were generated:")
    
    # List all PNG files
    png_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.png'):
                png_files.append(os.path.join(root, file))
    
    for png_file in sorted(png_files):
        report.append(f"- {png_file}")
    
    # Write the report to a file
    with open('fee_analysis_summary.md', 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Summary report saved to fee_analysis_summary.md")

if __name__ == "__main__":
    main()
