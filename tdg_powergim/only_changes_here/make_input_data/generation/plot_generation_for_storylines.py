import pandas as pd
import matplotlib.pyplot as plt


def make_generators_grouped(year):
    filename = "all_capacities_raw.csv"

    # read the csv file
    df = pd.read_csv(filename, sep=';')

    # Convert 'Value' column to string
    df['Value'] = df['Value'].astype(str)

    # Remove spaces from 'Value' column
    df['Value'] = df['Value'].str.replace(' ', '')

    # Convert 'Value' column to numeric, replacing non-numeric values with NaN
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    # Drop rows with NaN values in 'Value' column
    df = df.dropna(subset=['Value'])

    # Filter the dataframe by year
    df = df[df['Year'] == year]

    # Filter the dataframe by 'Distributed Energy' and 'Global Ambition'
    de_df = df[df['Scenario'] == 'Distributed Energy']
    ga_df = df[df['Scenario'] == 'Global Ambition']
    nt_df = df[df['Scenario'] == 'National Trends']

    # group by the first two letters of Node and Fuel, and sum the values for Distributed Energy, Global Ambition and
    # National Trends
    de_grouped = de_df.groupby([de_df['Node'].str[:2], 'Fuel'])['Value'].sum().reset_index()
    ga_grouped = ga_df.groupby([ga_df['Node'].str[:2], 'Fuel'])['Value'].sum().reset_index()
    nt_grouped = nt_df.groupby([nt_df['Node'].str[:2], 'Fuel'])['Value'].sum().reset_index()

    # save the output to a new csv file for Global Ambition and Distributed Energy
    ga_grouped.to_csv('ga_capacities_grouped.csv', index=False)
    de_grouped.to_csv('de_capacities_grouped.csv', index=False)
    nt_grouped.to_csv('nt_capacities_grouped.csv', index=False)

    return ga_grouped, de_grouped, nt_grouped


def make_plot(year):
    # get dataframes from make_time_series function
    ga_grouped, de_grouped, nt_grouped = make_generators_grouped(year)

    # Pivot the data to make Fuel as columns
    df_ga_pivot = ga_grouped.pivot(index='Node', columns='Fuel', values='Value')
    df_de_pivot = de_grouped.pivot(index='Node', columns='Fuel', values='Value')
    df_nt_pivot = nt_grouped.pivot(index='Node', columns='Fuel', values='Value')

    # Set the colors for each fuel type
    colors = {'Biofuels': '#E69F00', 'Gas': '#56B4E9', 'Hydro': '#009E73',
              'Oil': '#F0E442', 'Other Non RES': '#0072B2', 'Other RES': '#D55E00',
              'Solar': '#CC79A7', 'Wind Offshore': '#999999', 'Wind Onshore': '#E69F00',
              'Coal & Lignite': '#56B4E9', 'Nuclear': '#009E73'}

    # Create the subplots
    fig, (ax_ga, ax_de, ax_nt) = plt.subplots(1, 3, figsize=(15, 7))

    # Create the plot for Georgia
    df_ga_pivot.plot(kind='bar', stacked=True, color=colors, ax=ax_ga)

    # Set the x and y axis labels
    ax_ga.set_ylabel('Capacity [MW]')

    # Set the plot title
    ax_ga.set_title('Global Ambition')

    # Create the plot for Germany
    df_de_pivot.plot(kind='bar', stacked=True, color=colors, ax=ax_de)

    # Set the x and y axis labels
    ax_de.set_xlabel('Country')
    ax_de.set_ylabel('Capacity [MW]')

    # Set the plot title
    ax_de.set_title('Distributed Energy')

    # Create the plot for National Trends
    df_nt_pivot.plot(kind='bar', stacked=True, color=colors, ax=ax_nt)

    # Set the x and y axis labels
    ax_nt.set_xlabel('Country')
    ax_nt.set_ylabel('Capacity [MW]')

    # Set the plot title
    ax_nt.set_title('National Trends')

    # Adjust the spacing between subplots
    plt.subplots_adjust(wspace=0.4)

    # Create a common legend for all subplots
    handles, labels = ax_nt.get_legend_handles_labels()
    fig.legend(handles, labels, title='Fuel', bbox_to_anchor=(1.05, 10), loc='upper left', borderaxespad=0.)

    # Remove legend for the right and middle subplots
    ax_de.get_legend().remove()
    ax_ga.get_legend().remove()

    # Save the figure
    figure_path = "/Users/tobiassjoli/Documents/Master/Bilder_figurer/Method/Installed_capacity_plot"
    fig.savefig(f"{figure_path}/installed_capacity_{year}.png")

    # Show the plot
    plt.show()



if __name__ == "__main__":
    make_plot(2030)
