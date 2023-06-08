import pandas as pd
import os


def generate_output_data():
    # Read the data from an Excel file
    excel_file = 'electricity_modelling_results.xlsx'
    sheet_name = 'Capacity&Dispatch'
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Drop unnecessary columns with NaN values
    df = df.dropna(axis=1, how='all')
    # Drop rows containing NaN values
    df = df.dropna(axis=0, how='all')
    # Drop the 'Unnamed: 9' column
    if 'Unnamed: 9' in df.columns:
        df = df.drop('Unnamed: 9', axis=1)
    df = df.dropna(subset=['Node', 'Scenario', 'Year'])

    # Update node_country_mapping to include all countries and their respective nodes
    node_country_mapping = {
        'BE_main': ['BE00'],
        'BE_wind': ['BE00'],
        'DE_main': ['DE00'],
        'DE_wind': ['DE00'],
        'DK_main': ['DKW1', 'DKE1', 'DKKF'],
        'DK_wind': ['DKW1', 'DKE1', 'DKKF'],
        'NL_main': ['NL00'],
        'NL_wind': ['NL00'],
        'NO_main': ['NON1', 'NOM1', 'NOS1'],
        'NO_wind': ['NON1', 'NOM1', 'NOS1'],
        'UK_main': ['UK00', 'UKNI'],
        'UK_wind': ['UK00', 'UKNI']
    }

    """
    # Update node_country_mapping to include all countries and their respective nodes
    node_country_mapping = {
        'BE00': ['BE_main', 'BE_coast', 'BE_wind'],
        'DE00': ['DE_main', 'DE_coast_1', 'DE_coast_2', 'DE_wind'],
        'DKW1': ['DK_main', 'DK_coast_1', 'DK_coast_2', 'DK_wind'],
        'DKE1': ['DK_main', 'DK_coast_1', 'DK_coast_2', 'DK_wind'],  # DKE and DK belong to the same country
        'DKKF': ['DK_main', 'DK_coast_1', 'DK_coast_2', 'DK_wind'],
        'NL00': ['NL_main', 'NL_coast_1', 'NL_coast_2', 'NL_wind_1', 'NL_wind_2'],
        'NON1': ['NO_main', 'NO_coast_1', 'NO_wind_1', 'NO_wind_2'],
        'NOM1': ['NO_main', 'NO_coast_1', 'NO_wind_1', 'NO_wind_2'],
        'NOS1': ['NO_main', 'NO_coast_1', 'NO_wind_1', 'NO_wind_2'],
        'UK00': ['UK_main', 'UK_coast_1', 'UK_coast_2', 'UK_wind_1', 'UK_wind_2'],
        'UKNI': ['UK_main', 'UK_coast_1', 'UK_coast_2', 'UK_wind_1', 'UK_wind_2'],
    }
    """
    scenarios = ['Global Ambition', 'Distributed Energy', 'National Trends']

    for scenario in scenarios:
        scenario_data = df[df['Scenario'] == scenario]
        output_data = []  # Reset output data for each scenario

        for new_node, original_node in node_country_mapping.items():
            if isinstance(original_node, list):
                node_data = scenario_data[scenario_data['Node'].isin(original_node)]
            else:
                node_data = scenario_data[scenario_data['Node'] == original_node]
            capacity_data = {'capacity_2030': 0, 'capacity_2040': 0, 'capacity_2050': 0}

            for year in [2030, 2040, 2050]:
                year_data = node_data[node_data['Year'] == year]
                wind_offshore_data = year_data[year_data['Fuel'] == 'Offshore Wind']
                non_wind_offshore_data = year_data[year_data['Fuel'] != 'Offshore Wind']

                if 'wind' in new_node:
                    capacity_data[f'capacity_{year}'] = wind_offshore_data['Value'].sum()
                else:
                    capacity_data[f'capacity_{year}'] = non_wind_offshore_data['Value'].sum()

            # Initialize a dictionary to store node data
            node_output_data = {
                'desc': new_node[:2],
                'type': 'alt',
                'node': new_node,
                'capacity_2030': capacity_data['capacity_2030'],
                'capacity_2040': capacity_data['capacity_2040'],
                'capacity_2050': capacity_data['capacity_2050'],
                'pmin': 1,
                'allow_curtailment': 1,
                'fuelcost': 'const',
                'fuelcost_ref': 0,
                'pavg': 1,
                'inflow_fac': 'const',
                'inflow_ref': 1,
                'cost_scaling': '',
                'p_maxNew': '',
                'storage_cap': '',
                'storage_price': '',
                'storage_ini': '',
                'storval_filling_ref': '',
                'storval_time_ref': '',
                'pump_cap': '',
                'pump_efficiency': '',
                'pump_deadband': ''
            }
            output_data.append(node_output_data)

        output_df = pd.DataFrame(output_data)
        file_name = f"{scenario.replace(' ', '_')}.csv"
        output_path = os.path.join('output', file_name)

        if not os.path.exists('output'):
            os.makedirs('output')

        output_df.to_csv(output_path, index=False)

    return


if __name__ == "__main__":
    generate_output_data()
