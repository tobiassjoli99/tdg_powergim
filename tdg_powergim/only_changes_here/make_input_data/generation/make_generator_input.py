import pandas as pd


def make_generator_input(scenario):
    countries = ['NO', 'DK', 'DE', 'NL', 'BE', 'UK']
    filename = "all_capacities_raw.csv"

    df = pd.read_csv(filename, sep=';')
    df.drop_duplicates(inplace=True)

    df = df.dropna(subset=['Value'])
    df = df[df['Scenario'] == scenario]

    # Get the country code from the first two characters of 'Node' column
    df['Country'] = df['Node'].str.slice(0, 2)

    # Initialize a dictionary to store the capacities for each country, fuel type, and year
    capacities = {}

    for country in countries:
        for year in [2030, 2040]:
            print(f"Processing data for country {country} and year {year}")

            # Filter data for the current country and year
            df_country_year = df[(df['Country'] == country) & (df['Year'] == year)]

            # Get unique fuel types for the current country and year
            fuel_types = df_country_year['Fuel'].unique()

            for fuel_type in fuel_types:
                # Calculate the generation for the current fuel type
                gen = df_country_year[df_country_year['Fuel'] == fuel_type]['Value'].sum()

                # Exclude generators with 0 capacity
                if gen != 0:
                    # Store the capacity in the dictionary
                    capacities[(country, fuel_type, year)] = gen

    fuel_type_mapping = {
        'Biofuels': 'bio',
        'Gas': 'gas',
        'Hydro': 'hydro',
        'Oil': 'oil',
        'Other Non RES': 'other_non_res',
        'Other RES': 'other_res',
        'Solar': 'solar',
        'Wind Offshore': 'wind',
        'Wind Onshore': 'onshore_wind',
        'Coal & Lignite': 'hard_coal',
        'Nuclear': 'nuclear'
    }

    # Create the final DataFrame
    data = []
    for country in countries:
        for fuel_type in fuel_type_mapping.keys():
            # Replace fuel type names with the updated names
            mapped_fuel_type = fuel_type_mapping[fuel_type]

            # Determine the node value and inflow reference based on fuel type
            if fuel_type == 'Wind Offshore':
                node = f"{country}_{mapped_fuel_type}"
                inflow_ref = f"wind_{country}"
            elif fuel_type == 'Wind Onshore':
                node = f"{country}_main"
                inflow_ref = f"wind_{country}"
            elif fuel_type == 'Solar':
                node = f"{country}_main"
                inflow_ref = f"solar_{country}"
            elif fuel_type == 'Hydro':
                node = f"{country}_main"
                inflow_ref = f"inflow_{mapped_fuel_type}"
            else:
                node = f"{country}_main"
                inflow_ref = 'const'

            capacity_2030 = capacities.get((country, fuel_type, 2030), 0)
            capacity_2040 = capacities.get((country, fuel_type, 2040), 0)

            if country in ['NL', 'UK'] and mapped_fuel_type == 'wind':
                for i in range(1, 3):
                    row = {
                        'desc': f"{country}_{mapped_fuel_type}",
                        'type': mapped_fuel_type,
                        'node': f"{node}_{i}",
                        'capacity_2030': capacity_2030 / 2,
                        'capacity_2040': (capacity_2040 - capacity_2030) / 2,
                        'expand_2030': 0,
                        'expand_2040': 0,
                        'pmin': 0,
                        'allow_curtailment': 1,
                        'fuelcost': 1,
                        'fuelcost_ref': f"fuel_{mapped_fuel_type}",
                        'pavg': 0,
                        'inflow_fac': 1,
                        'inflow_ref': inflow_ref,
                        'cost_scaling': 1,
                        'p_maxNew': 0,
                        'storage_cap': 0,
                        'storage_price': '',
                        'storage_ini': '',
                        'storval_filling_ref': '',
                        'storval_time_ref': '',
                        'pump_cap': '',
                        'pump_efficiency': '',
                        'pump_deadband': ''
                    }
                    data.append(row)
            else:
                row = {
                    'desc': f"{country}_{mapped_fuel_type}",
                    'type': mapped_fuel_type,
                    'node': node,
                    'capacity_2030': capacity_2030,
                    'capacity_2040': capacity_2040 - capacity_2030,
                    'expand_2030': 0,
                    'expand_2040': 0,
                    'pmin': 0,
                    'allow_curtailment': 1,
                    'fuelcost': 1,
                    'fuelcost_ref': f"fuel_{mapped_fuel_type}",
                    'pavg': 0,
                    'inflow_fac': 1,
                    'inflow_ref': inflow_ref,
                    'cost_scaling': 1,
                    'p_maxNew': 0,
                    'storage_cap': 0,
                    'storage_price': '',
                    'storage_ini': '',
                    'storval_filling_ref': '',
                    'storval_time_ref': '',
                    'pump_cap': '',
                    'pump_efficiency': '',
                    'pump_deadband': ''
                }
                data.append(row)

    results = pd.DataFrame(data)

    print("Finished processing data.")

    return results

df = make_generator_input('National Trends')
df.to_csv('generators_NT_new.csv', index=False)