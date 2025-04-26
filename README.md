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

The scripts generate various visualizations to help understand the data. These visualizations are organized into several directories. Below are all the visualizations with descriptions:

## Root Directory Visualizations

### Fee Trends Over Time
![Fee Trends Over Time](fee_trends_over_time.png)
- Shows how fee percentages have changed over time for the first product offered by financial advisers
- Tracks the average fee percentage for each tier across different years
- Helps identify if fees are trending upward or downward over time

### Fee Percentages by Tier
![Fee Percentages by Tier](fee_percentages_by_tier.png)
- Displays the distribution of fee percentages across different asset tiers
- Shows how advisers typically structure their fees based on client asset levels
- Demonstrates the common tiered pricing model where higher tiers have lower fee percentages

### Fee Distributions
![Fee Distributions](fee_distributions.png)
- Shows the overall distribution of fee percentages across all advisers
- Helps identify the most common fee ranges in the market
- Highlights outliers that charge significantly higher or lower fees than the industry average

### Minimum Investment Distribution
![Minimum Investment Distribution](minimum_investment_distribution.png)
- Displays the distribution of minimum investment requirements set by financial advisers
- Helps understand the entry barriers for clients seeking advisory services
- Identifies market segments targeted by different advisers

### Product Count Distribution
![Product Count Distribution](product_count_distribution.png)
- Shows how many different fee products/services advisers typically offer
- Reveals whether most advisers specialize in a single product or diversify across multiple offerings

### Tier Count Distribution
![Tier Count Distribution](tier_count_distribution.png)
- Displays the distribution of how many fee tiers advisers typically use in their pricing structures
- Helps understand the complexity of fee schedules in the industry

## Analysis Results Directory

### Fee Structure Types
![Fee Structure Types](analysis_results/fee_structure_types.png)
- Categorizes and displays the distribution of different fee structure types used by advisers
- Helps understand the prevalence of different pricing models in the industry

### Negotiable Fees
![Negotiable Fees](analysis_results/negotiable_fees.png)
- Shows the proportion of advisers who offer negotiable fees versus those with fixed fee structures
- Reveals flexibility in pricing across the industry

### Fee Percentages by Tier (Analysis Results)
![Fee Percentages by Tier](analysis_results/fee_percentages_by_tier.png)
- Alternative visualization of fee percentages across different asset tiers
- Formatted for inclusion in the final analysis report

### Fee Trends Over Time (Analysis Results)
![Fee Trends Over Time](analysis_results/fee_trends_over_time.png)
- Alternative visualization of fee trends over time
- Formatted for inclusion in the final analysis report

### Minimum Investment
![Minimum Investment](analysis_results/minimum_investment.png)
- Alternative visualization of minimum investment requirements
- Formatted for inclusion in the final analysis report

## Multiple Products Directory

### Product Count Distribution
![Product Count Distribution](multiple_products/product_count_distribution.png)
- Specifically focuses on advisers offering multiple products
- Shows the distribution of how many different products they typically offer

### Fee Difference Distribution
![Fee Difference Distribution](multiple_products/fee_difference_distribution.png)
- Shows the distribution of maximum fee differences between products offered by the same adviser
- Reveals how much price variation exists within an adviser's product lineup

### Product Count vs Fee Difference
![Product Count vs Fee Difference](multiple_products/product_count_vs_fee_diff.png)
- Examines the relationship between the number of products an adviser offers and the maximum fee difference
- Helps understand if advisers with more diverse product offerings tend to have greater fee variations

### Tier Difference Distribution
![Tier Difference Distribution](multiple_products/tier_difference_distribution.png)
- Shows the distribution of differences in tier counts between products offered by the same adviser
- Reveals how advisers vary the complexity of their fee structures across different products

### Pattern Distribution
![Pattern Distribution](multiple_products/pattern_distribution.png)
- Shows the distribution of common patterns in how advisers structure their multiple product offerings
- Identifies patterns such as having higher fees for specialized services or consistent fee structures

### Examples of Multiple Products

#### 2 Products Example
<img src="multiple_products/examples/2_products.png" alt="2 Products Example" width="800"/>

- Shows an example of an adviser offering 2 different products with their fee structures

#### 3 Products Example
<img src="multiple_products/examples/3_products.png" alt="3 Products Example" width="800"/>

- Shows an example of an adviser offering 3 different products with their fee structures

#### 4 Products Example
<img src="multiple_products/examples/4_products.png" alt="4 Products Example" width="800"/>

- Shows an example of an adviser offering 4 different products with their fee structures

## Visualizations Directory

### Product Count vs Max Tiers
![Product Count vs Max Tiers](visualizations/product_count_vs_max_tiers.png)
- Examines the relationship between the number of products an adviser offers and the maximum number of fee tiers
- Helps understand if product diversification correlates with more complex fee structures

### Fee Percentages by Product

#### Product 0 Fee Percentages
![Product 0 Fee Percentages](visualizations/fee_percentages_product_0.png)
- Shows the distribution of fee percentages by tier for the first product category

#### Product 1 Fee Percentages
![Product 1 Fee Percentages](visualizations/fee_percentages_product_1.png)
- Shows the distribution of fee percentages by tier for the second product category

#### Product 2 Fee Percentages
![Product 2 Fee Percentages](visualizations/fee_percentages_product_2.png)
- Shows the distribution of fee percentages by tier for the third product category

#### Product 3 Fee Percentages
![Product 3 Fee Percentages](visualizations/fee_percentages_product_3.png)
- Shows the distribution of fee percentages by tier for the fourth product category

### Example Visualizations

#### Single Product with Multiple Tiers
![Single Product Multi Tier Example](visualizations/examples/single_product_multi_tier.png)
- Provides a detailed example of an adviser offering a single product with multiple fee tiers
- Shows how fees decrease as asset levels increase

#### Multiple Products Example
![Multiple Products Example](visualizations/examples/multiple_products.png)
- Shows an example of an adviser offering multiple products with different fee structures
- Illustrates real-world product differentiation strategies

### Comparison Visualizations

#### First Tier Distribution
![First Tier Distribution](visualizations/comparison/first_tier_distribution.png)
- Shows the distribution of first-tier fees across all advisers
- Helps identify the most common entry-level fees in the market

#### First Tier By Year
![First Tier By Year](visualizations/comparison/first_tier_by_year.png)
- Tracks how first-tier fees have changed over time
- Reveals market pricing trends for entry-level advisory services

#### Adviser Fee Changes Over Time

##### Adviser 100 Fee Changes
![Adviser 100 Fee Changes](visualizations/comparison/adviser_100_fee_changes.png)
- Tracks how Adviser 100 has changed their fee structure over time

##### Adviser 1037 Fee Changes
![Adviser 1037 Fee Changes](visualizations/comparison/adviser_1037_fee_changes.png)
- Tracks how Adviser 1037 has changed their fee structure over time

##### Adviser 10046 Fee Changes
![Adviser 10046 Fee Changes](visualizations/comparison/adviser_10046_fee_changes.png)
- Tracks how Adviser 10046 has changed their fee structure over time

##### Adviser 10091 Fee Changes
![Adviser 10091 Fee Changes](visualizations/comparison/adviser_10091_fee_changes.png)
- Tracks how Adviser 10091 has changed their fee structure over time

##### Adviser 10105 Fee Changes
![Adviser 10105 Fee Changes](visualizations/comparison/adviser_10105_fee_changes.png)
- Tracks how Adviser 10105 has changed their fee structure over time

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
