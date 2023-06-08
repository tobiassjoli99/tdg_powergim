import pandas as pd
import matplotlib.pyplot as plt


def make_dispatch_grouped():
    folder_path = '/only_changes_here/make_input_data'
    filename = f"{folder_path}/dispatch_raw.csv"

    # read the csv file
    df = pd.read_csv(filename, sep=';')

    df['Value'] = df['Value'].astype(float)

    # filter the dataframe by 'Distributed Energy' and 'Global Ambition'
    de_df = df[df['Scenario'] == 'Distributed Energy']
    ga_df = df[df['Scenario'] == 'Global Ambition']

    # group by the first two letters of Node and Fuel, and sum the values for Distributed Energy
    de_grouped = de_df.groupby([de_df['Node'].str[:2], 'Fuel'])['Value'].sum().reset_index()
    ga_grouped = ga_df.groupby([ga_df['Node'].str[:2], 'Fuel'])['Value'].sum().reset_index()

    # save the output to a new csv file for Global Ambition and Distributed Energy
    ga_grouped.to_csv('ga_dispatch_grouped.csv', index=False)
    de_grouped.to_csv('de_dispatch_grouped.csv', index=False)

    return ga_grouped, de_grouped


def create_excel_table():
    # get dataframes from make_time_series function
    ga_grouped, de_grouped = make_dispatch_grouped()

    print(de_grouped)

    # create pivot tables for Distributed Energy and Global Ambition
    de_table = pd.pivot_table(de_grouped, values='Value', index=['Node'], columns=['Fuel'], fill_value=0)
    ga_table = pd.pivot_table(ga_grouped, values='Value', index=['Node'], columns=['Fuel'], fill_value=0)

    # create a new Excel file and write the pivot tables to it
    with pd.ExcelWriter('dispatch_grouped.xlsx') as writer:
        de_table.to_excel(writer, sheet_name='Distributed Energy')
        ga_table.to_excel(writer, sheet_name='Global Ambition')

        # save workbook
        writer.save()


def make_plot():
    # get dataframes from make_time_series function
    ga_grouped, de_grouped = make_dispatch_grouped()

    # Pivot the data to make Fuel as columns
    df_ga_pivot = ga_grouped.pivot(index='Node', columns='Fuel', values='Value')
    df_de_pivot = de_grouped.pivot(index='Node', columns='Fuel', values='Value')

    # Set the colors for each fuel type
    colors = {'Biofuels': 'blue', 'Gas': 'orange', 'Hydro': 'green',
              'Oil': 'red', 'Other Non RES': 'purple', 'Other RES': 'gray',
              'Solar': 'yellow', 'Solar_standalone': 'pink',
              'Wind Offshore': 'brown', 'Wind Onshore': 'cyan',
              'OffshoreWind_standalone': 'black', 'Coal & Lignite': 'turquoise',
              'Nuclear': 'magenta'}

    # Create the subplots
    fig, (ax_ga, ax_de) = plt.subplots(1, 2)

    # Create the plot for Georgia
    df_ga_pivot.plot(kind='bar', stacked=True, color=colors, ax=ax_ga)

    # Set the x and y axis labels
    ax_ga.set_xlabel('Country')
    ax_ga.set_ylabel('Generation dispatch [GWh]')

    # Set the legend title
    ax_ga.legend(title='Fuel')

    # Set the plot title
    ax_ga.set_title('Global Ambition')

    # Create the plot for Germany
    df_de_pivot.plot(kind='bar', stacked=True, color=colors, ax=ax_de)

    # Set the x and y axis labels
    ax_de.set_xlabel('Country')
    ax_de.set_ylabel('Generation dispatch [GWh]')

    # Set the legend title
    ax_de.legend(title='Fuel')

    # Set the plot title
    ax_de.set_title('Distributed Energy')

    # Show the plot
    plt.show()


if __name__ == "__main__":
    create_excel_table()

