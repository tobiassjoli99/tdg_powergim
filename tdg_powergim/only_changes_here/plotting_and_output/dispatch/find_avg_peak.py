import pandas as pd

def calculate_avg_peak(input_file, output_file, columns):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)

    # Calculate average and peak values for each column
    avg_values = df[columns].mean()
    peak_values = df[columns].max()

    # Create a new DataFrame for the output file
    output_df = pd.DataFrame({'Column': columns,
                              'Average': avg_values,
                              'Peak': peak_values})

    # Write the output DataFrame to a new CSV file
    output_df.to_csv(output_file, index=False)

    return output_df


input_file = '/only_changes_here/DE_time_series/time_series_sample_DE.csv'
output_file = '../demand_functions/consumer_avg_peak.csv'
columns = ['demand_UK', 'demand_DE', 'demand_NO', 'demand_DK', 'demand_NL', 'demand_BE']

result_df = calculate_avg_peak(input_file, output_file, columns)
print(result_df)
