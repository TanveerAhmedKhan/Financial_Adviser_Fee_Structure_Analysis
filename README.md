# Financial Adviser Fee Structure Analysis

## Project Overview

This project analyzes fee structures of financial advisers based on data extracted from regulatory filings (Form ADV Part 2). The dataset contains 1,734 records from different advisers, with information about their fee structures, minimum investment requirements, and negotiability of fees.

The data comes from 114 CSV files, each containing 18 columns and approximately 1,500 rows. The file naming convention includes adviser IDs and filing dates, which are extracted and used in the analysis.

## Codebase Structure

The project consists of several Python scripts, each focusing on different aspects of the data cleaning and analysis:

### Main Scripts

1. **`fee_data_cleaning.py`**
   - Performs basic data cleaning and initial analysis
   - Extracts adviser IDs and filing dates from filenames
   - Cleans fee thresholds, flat fees, minimum investment, and negotiable status
   - Identifies fee structure types (flat, tiered, etc.)
   - Generates summary statistics and basic visualizations

2. **`fee_structure_analysis.py`**
   - Focuses on analyzing fee structures in more detail
   - Detects and corrects misplaced answers in the data
   - Extracts structured fee data with product and tier information
   - Analyzes fee structures and generates visualizations

3. **`fee_visualization.py`**
   - Creates detailed visualizations of fee structures
   - Visualizes fee trends over time
   - Shows patterns in fee structures
   - Provides examples of different fee structure types
   - Compares fee structures across different advisers

4. **`multiple_products_analysis.py`**
   - Specifically analyzes advisers with multiple products
   - Calculates fee differences between products
   - Analyzes structure differences between products
   - Visualizes examples of multiple product offerings
   - Identifies patterns in how products are structured

5. **`analyze_fee_data.py`**
   - A simplified script that combines the most important analyses
   - More robust handling of data irregularities
   - Generates key visualizations and statistics
   - Detects multiple products using a different approach

6. **`run_fee_analysis.py`**
   - Orchestrates the execution of all analysis scripts
   - Runs scripts in sequence and handles errors
   - Generates a summary report of all analyses

### Output Files

1. **`cleaned_fee_data.csv`**
   - Contains the cleaned data with extracted adviser information
   - Includes cleaned fee thresholds, flat fees, minimum investment, etc.
   - Identifies fee structure types

2. **`structured_fee_data.csv`**
   - Contains structured fee data with product and tier information
   - Organizes fee thresholds and percentages by product and tier
   - Includes counts of products and tiers

3. **`fee_yearly_averages.csv`**
   - Contains average fee percentages by tier and year
   - Shows trends in fee percentages over time

4. **`fee_analysis_summary.md`**
   - Provides a summary of the analysis results
   - Includes key statistics and findings
   - Lists generated visualizations

5. **`fee_analysis_detailed_report.md`**
   - Provides a more detailed report of the analysis
   - Includes key findings, challenges, and recommendations
   - Discusses data irregularities and future work

### Visualizations

The scripts generate various visualizations to help understand the data:

1. **Fee Structure Types**
   - Distribution of flat fee vs. tiered fee structures

2. **Fee Percentages by Tier**
   - Box plots and violin plots showing the distribution of fee percentages for each tier

3. **Fee Trends Over Time**
   - Line charts showing changes in average fee percentages over time

4. **Minimum Investment**
   - Histograms showing the distribution of minimum investment requirements

5. **Multiple Products**
   - Examples of advisers with multiple products
   - Distributions of product counts and tier differences
   - Relationships between product count and fee differences

## Key Findings

1. **Fee Structure Types**
   - Tiered fee structures: 59.7% of advisers
   - Flat fee structures: 11.0% of advisers
   - No fee information: 29.3% of advisers

2. **Fee Percentages**
   - Average fee for the first tier: 1.22%
   - Average fee for the second tier: 1.02%
   - Average fee for the third tier: 0.86%
   - Clear pattern of decreasing fees as AUM increases

3. **Negotiable Fees**
   - 89.4% of advisers offer negotiable fees
   - 10.6% have non-negotiable fees

4. **Minimum Investment**
   - Median minimum investment: $100,000
   - Average minimum investment: $1,985,895
   - Large variation in minimum requirements

5. **Multiple Products**
   - 54.2% of advisers potentially offer multiple products
   - Average fee difference between products: 0.42 percentage points
   - Average tier difference between products: 0.86 tiers

## Data Challenges and Solutions

1. **Inconsistent Formatting**
   - Challenge: Fee thresholds and percentages were not consistently formatted
   - Solution: Used regular expressions to extract values with different formats

2. **Misplaced Information**
   - Challenge: ChatGPT sometimes placed fee information in incorrect columns
   - Solution: Implemented detection and correction of misplaced answers

3. **Multiple Products**
   - Challenge: Many advisers have multiple products with different fee structures
   - Solution: Developed algorithms to identify and analyze multiple products

4. **Missing Data**
   - Challenge: About 29% of records had no fee information available
   - Solution: Handled missing data appropriately in the analysis

## How to Use the Code

1. **Basic Analysis**
   ```
   python analyze_fee_data.py
   ```
   This will perform a simplified analysis and generate key visualizations.

2. **Complete Analysis Pipeline**
   ```
   python run_fee_analysis.py
   ```
   This will run all analysis scripts in sequence and generate a comprehensive report.

3. **Individual Analyses**
   - For data cleaning: `python fee_data_cleaning.py`
   - For fee structure analysis: `python fee_structure_analysis.py`
   - For visualizations: `python fee_visualization.py`
   - For multiple products analysis: `python multiple_products_analysis.py`

## Future Work

1. **Product Classification**
   - Develop a more sophisticated algorithm to identify and classify different products

2. **Competitive Analysis**
   - Compare fee structures across advisers to identify competitive positioning

3. **Temporal Analysis**
   - Analyze how fee structures have changed over time for the same adviser

4. **Correlation Analysis**
   - Investigate relationships between fee structures and other adviser characteristics

5. **Market Segmentation**
   - Identify different market segments based on fee structures and minimum investment requirements

## Dependencies

- pandas
- numpy
- matplotlib
- seaborn
- re (regular expressions)
- datetime

## Conclusion

This project provides a comprehensive analysis of financial adviser fee structures, revealing patterns in how fees are structured and how they vary across advisers. The code is designed to be reusable for future data, making it easy to analyze additional datasets as they become available.

The analysis reveals that tiered fee structures are the most common approach, with fees generally decreasing as AUM increases. Most advisers offer negotiable fees, and many have multiple products with different fee structures. The median minimum investment requirement is $100,000, but there is significant variation across advisers.

These insights can be used for benchmarking, competitive analysis, and market segmentation in the financial advisory industry.
