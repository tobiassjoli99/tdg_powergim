import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_peak_demand():
    storylines = ['DE', 'GA', 'NT']
    storylines_dict = {'DE': 'Distributed Energy', 'GA': 'Global Ambition', 'NT': 'National Trends'}

    # Initialize an empty DataFrame
    df_all = pd.DataFrame()

    for storyline in storylines:
        df_storyline = pd.read_csv(
            f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/{storyline}_time_series/consumers_{storyline}_new.csv")
        df_storyline['node'] = df_storyline['node'].str.replace('_main', '')

        # Rename the demand_avg column to the corresponding storyline
        df_storyline.rename(columns={'demand_avg': storyline}, inplace=True)

        if df_all.empty:
            df_all = df_storyline[['node', storyline]].copy()
        else:
            df_all = pd.merge(df_all, df_storyline[['node', storyline]], on='node', how='outer')

    # Melt the DataFrame to get it in long-form
    df_all = df_all.melt(id_vars='node', var_name='Storyline', value_name='Peak Demand')

    # Replace the storyline codes with their full names
    df_all['Storyline'] = df_all['Storyline'].replace(storylines_dict)

    # Plot the data
    plt.figure(figsize=(12, 5))
    sns.barplot(x='node', y='Peak Demand', hue='Storyline', data=df_all)
    plt.title(f"Peak demand for all storylines")
    plt.ylabel('Peak demand [MW]')
    plt.xlabel('Country')
    plt.xticks(rotation=45)
    plt.legend(title='Storyline')

    # Show the plot
    plt.tight_layout()
    plt.show()


plot_peak_demand()


def plot_demand(time_series_files, scenario_files, scenario_names):
    # Read the time series data for each scenario
    time_series_data = []
    for time_series_file in time_series_files:
        time_series_data.append(pd.read_csv(time_series_file))

    # Read the scenario data for each scenario
    scenario_data = []
    for scenario_file in scenario_files:
        scenario_data.append(pd.read_csv(scenario_file))

    # Create the subplots
    fig, axes = plt.subplots(len(scenario_files), 1, figsize=(10, 5 * len(scenario_files)), sharex=True)

    # Iterate over each scenario
    for i, scenario_df in enumerate(scenario_data):
        # Create a copy of the time series data for this scenario
        demand_data = time_series_data[i].copy()

        # Iterate over each country
        for country in ['UK', 'DE', 'NO', 'DK', 'NL', 'BE']:
            col = 'demand_' + country

            # Multiply the demand_avg with the time series for the correct country and scenario
            avg_demand = scenario_df.loc[scenario_df['node'] == country + '_main', 'demand_avg'].values[0]
            demand_data[col] = demand_data[col] * avg_demand

            # Plot the demand_functions for the country
            axes[i].plot(demand_data[col], label=country)

        # Set the subplot title and labels
        axes[i].set_title(f'{scenario_names[i]}')
        axes[i].set_ylabel('Demand [MMW]')
        axes[i].legend()

    axes[-1].set_xlabel('Day')
    plt.tight_layout()
    plt.show()

"""
# Call the function with the time series files and scenario files
time_series_files = [
    '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/DE_time_series/time_series_sample_DE.csv',
    '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/GA_time_series/time_series_sample_GA.csv',
    '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/NT_time_series/time_series_sample_NT.csv'
]

scenario_files = [
    '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/DE_time_series/consumers_DE_new.csv',
    '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/GA_time_series/consumers_GA_new.csv',
    '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/NT_time_series/consumers_NT_new.csv'
]

scenario_names = ['Distributed Energy', 'Global Ambition', 'National Trends']

plot_demand(time_series_files, scenario_files, scenario_names)
"""


