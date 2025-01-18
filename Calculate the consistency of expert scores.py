import pandas as pd
import pingouin as pg

# Define the path to the Excel file
excel_file = ''

# Get all sheet names from the Excel file
excel_sheets = pd.ExcelFile(excel_file).sheet_names
print(f"The Excel file contains the following sheets (models): {excel_sheets}")

# Read all sheets and store them in a dictionary
models_data = {sheet: pd.read_excel(excel_file, sheet_name=sheet) for sheet in excel_sheets}

# Define the ICC calculation function
def compute_icc(df, model_name):
    """
    Calculate the ICC3k value for the given DataFrame.
    
    Parameters:
    df (DataFrame): DataFrame containing the domain and ratings from three experts.
    model_name (str): The model name.
    
    Returns:
    dict: A dictionary containing the model name and ICC results.
    """
    # Convert to long format
    df_long = df.melt(id_vars='Filed', var_name='Professor', value_name='Score')
    
    # Calculate ICC
    icc = pg.intraclass_corr(data=df_long, targets='Filed', raters='Professor', ratings='Score')
    
    # Filter for ICC3k type
    icc3k = icc[icc['Type'] == 'ICC3k']
    
    if not icc3k.empty:
        icc_value = icc3k['ICC'].values[0]
        ci_lower = icc3k['CI95%'].values[0][0]
        ci_upper = icc3k['CI95%'].values[0][1]
        pval = icc3k['pval'].values[0]
        
        return {
            'Model': model_name,
            'ICC Type': 'ICC3k',
            'ICC': icc_value,
            'CI Lower': ci_lower,
            'CI Upper': ci_upper,
            'F': icc3k['F'].values[0],
            'df1': icc3k['df1'].values[0],
            'df2': icc3k['df2'].values[0],
            'p-value': pval
        }
    else:
        return {
            'Model': model_name,
            'ICC Type': None,
            'ICC': None,
            'CI Lower': None,
            'CI Upper': None,
            'F': None,
            'df1': None,
            'df2': None,
            'p-value': None
        }

# Initialize an empty list to store ICC results
icc_results = []

# Iterate through each model and compute the ICC
for model_name, df in models_data.items():
    result = compute_icc(df, model_name)
    icc_results.append(result)

# Convert the results into a DataFrame
icc_summary = pd.DataFrame(icc_results)

# Display the ICC results
print("\nICC results for each model:")
print(icc_summary)

# Save the ICC results to a new Excel file
output_file = 'icc_per_model_summary.xlsx'
icc_summary.to_excel(output_file, index=False)
print(f"\nICC results have been saved to {output_file}")
