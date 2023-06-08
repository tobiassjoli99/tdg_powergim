import pandas as pd

def extract_2009_column(input_file1, input_file2):
    # Load the input CSV files
    df1 = pd.read_csv(input_file1)
    df2 = pd.read_csv(input_file2)

    # Extract the '2009' column and overwrite the original CSV files
    df1[['2009.0']].to_csv(input_file1, index=False)
    df2[['2009.0']].to_csv(input_file2, index=False)


# Call the function with the input filenames
extract_2009_column('DKE1_demand_data_2030_NT.csv', 'NOS0_demand_data_2030_NT.csv')
