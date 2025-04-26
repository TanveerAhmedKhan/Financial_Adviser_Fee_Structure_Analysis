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

The scripts generate various visualizations to help understand the data. These visualizations are organized into several directories:

#### Root Directory Visualizations

1. **`fee_trends_over_time.png`**
   - Shows how fee percentages have changed over time for the first product offered by financial advisers
   - Tracks the average fee percentage for each tier across different years
   - Helps identify if fees are trending upward or downward over time
   - Provides insights into market pricing evolution in the financial advisory industry

2. **`fee_percentages_by_tier.png`**
   - Displays the distribution of fee percentages across different asset tiers
   - Shows how advisers typically structure their fees based on client asset levels
   - Demonstrates the common tiered pricing model where higher tiers (larger asset amounts) generally have lower fee percentages

3. **`fee_distributions.png`**
   - Shows the overall distribution of fee percentages across all advisers
   - Helps identify the most common fee ranges in the market
   - Highlights outliers that charge significantly higher or lower fees than the industry average

4. **`minimum_investment_distribution.png`**
   - Displays the distribution of minimum investment requirements set by financial advisers
   - Helps understand the entry barriers for clients seeking advisory services
   - Identifies market segments targeted by different advisers

5. **`product_count_distribution.png`**
   - Shows how many different fee products/services advisers typically offer
   - Reveals whether most advisers specialize in a single product or diversify across multiple offerings

6. **`tier_count_distribution.png`**
   - Displays the distribution of how many fee tiers advisers typically use in their pricing structures
   - Helps understand the complexity of fee schedules in the industry

#### Multiple Products Directory (`multiple_products/`)

1. **`product_count_distribution.png`**
   - Specifically focuses on advisers offering multiple products
   - Shows the distribution of how many different products they typically offer
   - Helps identify the level of service diversification in the industry

2. **`fee_difference_distribution.png`**
   - Shows the distribution of maximum fee differences between different products offered by the same adviser
   - Reveals how much price variation exists within an adviser's product lineup
   - Indicates potential value differentiation or market segmentation strategies

3. **`product_count_vs_fee_diff.png`**
   - Examines the relationship between the number of products an adviser offers and the maximum fee difference between those products
   - Helps understand if advisers with more diverse product offerings tend to have greater fee variations

4. **`tier_difference_distribution.png`**
   - Shows the distribution of differences in tier counts between products offered by the same adviser
   - Reveals how advisers vary the complexity of their fee structures across different products

5. **`pattern_distribution.png`**
   - Shows the distribution of common patterns in how advisers structure their multiple product offerings
   - Identifies patterns such as having higher fees for specialized services or consistent fee structures across products

6. **Examples Directory (`multiple_products/examples/`)**
   - **`2_products.png`, `3_products.png`, `4_products.png`**: Provide specific examples of fee structures for advisers offering 2, 3, and 4 different products respectively
   - Serve as case studies to understand real-world fee structure variations

#### Visualizations Directory (`visualizations/`)

1. **`product_count_vs_max_tiers.png`**
   - Examines the relationship between the number of products an adviser offers and the maximum number of fee tiers they use
   - Helps understand if product diversification correlates with more complex fee structures

2. **`fee_percentages_product_0.png`, `fee_percentages_product_1.png`, etc.**
   - Show the distribution of fee percentages by tier for each product category (0, 1, 2, 3)
   - Help compare fee structures across different types of advisory services

3. **Examples Directory (`visualizations/examples/`)**
   - **`single_product_multi_tier.png`**: Provides a detailed example of an adviser offering a single product with multiple fee tiers, showing how fees decrease as asset levels increase
   - **`multiple_products.png`**: Shows an example of an adviser offering multiple products with different fee structures, illustrating real-world product differentiation strategies

4. **Comparison Directory (`visualizations/comparison/`)**
   - **`first_tier_distribution.png`**: Shows the distribution of first-tier fees across all advisers, helping identify the most common entry-level fees in the market
   - **`first_tier_by_year.png`**: Tracks how first-tier fees have changed over time, revealing market pricing trends for entry-level advisory services
   - **`adviser_*_fee_changes.png`**: Track how specific advisers have changed their fee structures over time, providing case studies of individual pricing strategies and adaptations

#### Analysis Results Directory (`analysis_results/`)

1. **`fee_structure_types.png`**
   - Categorizes and displays the distribution of different fee structure types used by advisers (e.g., tiered, flat, hybrid)
   - Helps understand the prevalence of different pricing models in the industry

2. **`negotiable_fees.png`**
   - Shows the proportion of advisers who offer negotiable fees versus those with fixed fee structures
   - Reveals flexibility in pricing across the industry

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

- pandas >= 1.3.0
- numpy >= 1.20.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0
- requests >= 2.25.0
- re (regular expressions, standard library)
- datetime (standard library)
- os (standard library)
- sys (standard library)
- time (standard library)
- json (standard library)
- getpass (standard library)
- csv (standard library)

## Conclusion

This project provides a comprehensive analysis of financial adviser fee structures, revealing patterns in how fees are structured and how they vary across advisers. The code is designed to be reusable for future data, making it easy to analyze additional datasets as they become available.

The analysis reveals that tiered fee structures are the most common approach, with fees generally decreasing as AUM increases. Most advisers offer negotiable fees, and many have multiple products with different fee structures. The median minimum investment requirement is $100,000, but there is significant variation across advisers.

The extensive visualizations created in this project provide deep insights into fee structures, helping to understand:
- How fees vary across different asset tiers
- How fee structures have evolved over time
- The complexity of fee schedules in the industry
- How advisers differentiate their products through pricing
- The relationship between product diversity and fee structure complexity

These insights can be used for benchmarking, competitive analysis, and market segmentation in the financial advisory industry.

## Repository Information

This repository is maintained by TanveerAhmedKhan. The analysis was performed on a dataset of 114 CSV files containing financial adviser fee structures, with each file containing approximately 1,500 rows across 18 columns.
