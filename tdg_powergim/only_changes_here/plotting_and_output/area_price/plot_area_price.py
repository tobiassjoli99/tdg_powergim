import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def get_fuel_costs(story_ini, fuel):
    # Set the price for all fuel types
    fuel_costs = {}

    if story_ini in ['DE', 'GA']:
        fuel_costs = {
            'bio': 51.42853029,
            'gas': 41.34853835,
            'hard_coal': 20.26284093,
            'hydro': 20,
            'lignite': 18.5142709,
            'nuclear': 4.834281847,
            'oil': 95.58939721,
            'solar': 0,
            'onshore_wind': 0,
            'wind': 0,
            'other_non_res': 100,
            'other_res': 0
        }
    elif story_ini == 'NT':
        fuel_costs = {
            'bio': 51.42853029,
            'gas': 64.07994874,
            'hard_coal': 25.50855102,
            'hydro': 30,
            'lignite': 18.5142709,
            'nuclear': 4.834281847,
            'oil': 130.547264,
            'solar': 0,
            'onshore_wind': 0,
            'wind': 0,
            'other_non_res': 100,
            'other_res': 0
        }
    else:
        print("Invalid scenario given. Please use 'DE', 'GA', or 'NT'.")
        return None

    # Get the price for the given fuel
    try:
        fuel_price = fuel_costs[fuel]
    except KeyError:
        print(f"Invalid fuel type '{fuel}' given. Please check your input.")
        return None

    return fuel_price


def get_CO2_cost(fuel):
    # Euro/MWh
    CO2_costs = {
        'coal': 67.119,
        'lignite': 70.2,
        'gas': 32.877,
        'oil': 55.9026,
        'other_non_res': 15.6
    }

    CO2_price = CO2_costs.get(fuel, 0)

    return CO2_price


def get_total_generation(storyline, case, scenario):
    # Set names for storylines
    story_ini_dict = {'Distributed Energy': 'DE', 'Global Ambition': 'GA', 'National Trends': 'NT'}
    story_ini = story_ini_dict.get(storyline, 'Give valid storyline')

    # Read the Excel file and csv file with generator names
    v_gen_df = pd.read_excel(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{storyline}/{case}/{scenario}/results_{case}_{scenario}.xlsx",
        sheet_name='v_generation')
    gen_names_df = pd.read_csv(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/generation/generators_{story_ini}_new.csv",
        index_col=False)

    # Create index column in gen_names_df
    gen_names_df['area'] = gen_names_df['desc'].str[:2]
    gen_names_df['fuel_price'] = gen_names_df['type'].apply(lambda x: get_fuel_costs(story_ini, x))
    gen_names_df['index'] = gen_names_df.index
    gen_names_df = gen_names_df[['index', 'area', 'type', 'fuel_price']]

    # Process the 'v_generation' column to form tuples
    v_gen_df['v_generation'] = v_gen_df['v_generation'].apply(lambda x: tuple(map(int, x.strip('()').split(','))))
    v_gen_df['index'] = v_gen_df['v_generation'].apply(lambda x: x[0])
    v_gen_df['timestep'] = v_gen_df['v_generation'].apply(lambda x: x[2])

    # Filter out rows where value is 0
    v_gen_df = v_gen_df[v_gen_df['value'] != 0]

    # Merge gen_names_df to v_gen_df
    v_gen_df = pd.merge(v_gen_df, gen_names_df, how='left', on='index')

    # A list of areas to calculate total generation for
    areas = ['NO', 'DK', 'DE', 'NL', 'BE', 'UK']

    # Initialize a DataFrame to hold total generation for each area
    total_generation = pd.DataFrame(columns=areas)

    # Calculate total generation for each area
    for area in areas:
        area_data = v_gen_df[v_gen_df['area'] == area]
        total_generation[area] = [area_data['value'].sum()]

    # Set the index name to 'Generation'
    total_generation.index = ['Generation']

    return total_generation


def get_load_shed(storyline, case, scenario):
    excel_results = pd.read_excel(f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{storyline}/{case}/{scenario}/results_{case}_{scenario}.xlsx", sheet_name='v_load_shed')
    areas = {
        'NO': 0,
        'DK': 1,
        'DE': 2,
        'NL': 3,
        'BE': 4,
        'UK': 5
    }

    # Process the 'v_load_shed' column to form tuples
    excel_results['v_load_shed'] = excel_results['v_load_shed'].apply(lambda x: tuple(map(int, x.strip('()').split(','))))
    excel_results['index'] = excel_results['v_load_shed'].apply(lambda x: x[0])
    excel_results['timestep'] = excel_results['v_load_shed'].apply(lambda x: x[2])

    # Initialize a DataFrame to hold average load shedding for each area
    shed_cost_per_country = pd.DataFrame(columns=areas.keys())

    for area, area_index in areas.items():
        area_data = excel_results[excel_results['index'] == area_index]
        shed_cost_per_country[area] = [area_data['value'].mean()]

    total_generation = get_total_generation(storyline, case, scenario)
    load_shed_cost = 10000
    shed_cost_per_country *= load_shed_cost

    # Reset the index before the division
    shed_cost_per_country.reset_index(drop=True, inplace=True)
    total_generation.reset_index(drop=True, inplace=True)

    # Now carry out the division
    shed_cost_per_country = shed_cost_per_country / total_generation

    print(f"Loadshedding for {storyline}, {case}, {scenario}")
    print(shed_cost_per_country)

    return shed_cost_per_country

def print_all_shed():
    storylines = ['Distributed Energy', 'Global Ambition', 'National Trends']
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']


    for case in cases:
        for scenario in scenarios:
            for storyline in storylines:
                get_load_shed(storyline, case, scenario)

print_all_shed()

def get_area_price(storyline, case, scenario):
    # Makes a table with the average power price for each country.
    # Set names for storylines
    story_ini_dict = {'Distributed Energy': 'DE', 'Global Ambition': 'GA', 'National Trends': 'NT'}
    story_ini = story_ini_dict.get(storyline, 'Give valid storyline')

    # Read the Excel file and csv file with generator names
    v_gen_df = pd.read_excel(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{storyline}/{case}/{scenario}/results_{case}_{scenario}.xlsx",
        sheet_name='v_generation')
    gen_names_df = pd.read_csv(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/generation/generators_{story_ini}_new.csv",
        index_col=False)

    # Create index column in gen_names_df
    gen_names_df['area'] = gen_names_df['desc'].str[:2]
    gen_names_df['fuel_price'] = gen_names_df['type'].apply(lambda x: get_fuel_costs(story_ini, x))
    gen_names_df['index'] = gen_names_df.index
    gen_names_df = gen_names_df[['index', 'area', 'type', 'fuel_price']]

    # Process the 'v_generation' column to form tuples
    v_gen_df['v_generation'] = v_gen_df['v_generation'].apply(lambda x: tuple(map(int, x.strip('()').split(','))))
    v_gen_df['index'] = v_gen_df['v_generation'].apply(lambda x: x[0])
    v_gen_df['timestep'] = v_gen_df['v_generation'].apply(lambda x: x[2])

    # Filter out rows where value is 0
    v_gen_df = v_gen_df[v_gen_df['value'] != 0]

    # Merge gen_names_df to v_gen_df
    v_gen_df = pd.merge(v_gen_df, gen_names_df, how='left', on='index')

    # A list of areas to calculate max prices for
    areas = ['NO', 'DK', 'DE', 'NL', 'BE', 'UK']

    # Initialize an empty dataframe
    area_price_all_time = pd.DataFrame(index=range(365), columns=areas)

    # Calculate max_generator for each area and timestep
    for area in areas:
        area_data = v_gen_df[v_gen_df['area'] == area]
        area_price_all_time[area] = area_data.groupby('timestep')['type'].apply(
            lambda x: max(get_fuel_costs(story_ini, t) + get_CO2_cost(t) for t in x))

    # Initialize average dataframe
    avg_area_price = area_price_all_time.mean().rename(storyline).to_frame().T

    # Adding cost for load shedding
    load_shed_cost = get_load_shed(storyline, case, scenario)

    # Reset the index before the division
    avg_area_price.reset_index(drop=True, inplace=True)
    load_shed_cost.reset_index(drop=True, inplace=True)

    avg_area_price += load_shed_cost

    # Set the index value to storyline
    avg_area_price.set_index([pd.Index([storyline])], inplace=True)

    return avg_area_price


def area_price_all_storylines(case, scenario):
    storylines = ['Distributed Energy', 'Global Ambition', 'National Trends']
    price_dataframe = []

    for storyline in storylines:
        price_per_storyline = get_area_price(storyline, case, scenario)
        price_dataframe.append(price_per_storyline)

    price_all_storylines = pd.concat(price_dataframe)

    # Rename the index levels
    price_all_storylines.index.names = ['Storyline']

    price_all_storylines.to_csv(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/plotting_and_output/area_price/{case}/area_prices_{case}_{scenario}")

    return price_all_storylines


### Make a latex table comparing the area price for all scenarios. Makes three tables, one for each storyline
def latex_area_price_compare_scenarios(storyline):
    output_path = f"/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Area_price_compare_scenarios_latex/area_price_{storyline}.tex"
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']

    # Create a mapping dictionary for scenarios
    scenario_mapping = {
        ('case1', 'scenario1'): 'Scenario A',
        ('case1', 'scenario2'): 'Scenario B',
        ('case1', 'scenario3'): 'Scenario C',
        ('case2', 'scenario1'): 'Scenario D',
        ('case2', 'scenario2'): 'Scenario E',
        ('case2', 'scenario3'): 'Scenario F',
        ('case3', 'scenario1'): 'Scenario G',
        ('case3', 'scenario2'): 'Scenario H',
        ('case3', 'scenario3'): 'Scenario I'
    }

    all_area_prices = pd.DataFrame()
    for case in cases:
        for scenario in scenarios:
            area_price_per_case_scenario = get_area_price(storyline, case, scenario)
            total_generation_per_case_scenario = get_total_generation(storyline, case, scenario)
            area_price_per_case_scenario.reset_index(drop=True, inplace=True)  # Remove index
            new_scenario_name = scenario_mapping.get((case, scenario), scenario)
            area_price_per_case_scenario["Scenario"] = new_scenario_name

            # Calculate the weighted average price for each scenario
            area_price_per_case_scenario['Average'] = (area_price_per_case_scenario.loc[:,
                                                       'NO':'UK'].values * total_generation_per_case_scenario.values).sum(
                axis=1) / total_generation_per_case_scenario.values.sum()

            all_area_prices = pd.concat([all_area_prices, area_price_per_case_scenario])

    # Move 'Scenario' column to the first position
    all_area_prices = all_area_prices[
        ['Scenario'] + [col for col in all_area_prices.columns if col != 'Scenario' and col != 'Average'] + ['Average']]

    # Round to two decimals
    all_area_prices = all_area_prices.round(2)

    # Make 'Scenario' column bold
    all_area_prices['Scenario'] = all_area_prices['Scenario'].apply(lambda x: r'\textbf{' + x + '}')

    # Latex table
    table = all_area_prices.to_latex(index=False,  # Do not include index in output
                                     header=[r'\textbf{Scenario}', r'\textbf{NO}', r'\textbf{DK}',
                                             r'\textbf{DE}', r'\textbf{NL}', r'\textbf{BE}', r'\textbf{UK}',
                                             r'\textbf{Average}'],
                                     bold_rows=True, escape=False)

    table = '\\begin{table}\n' + \
            '    \\centering\n' + \
            f'    \\caption{{Area prices [EUR/Mwh] for {storyline}}}\n' + \
            f'    \\label{{tab:area_prices_{storyline}}}\n' + \
            table + \
            '\\end{table}\n'

    with open(output_path, 'w') as f:
        f.write(table)

    all_area_prices.to_csv(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/plotting_and_output/area_price/scenarios_compare/area_prices_{storyline}")

    print(f"Successfully saved the area price table for {storyline}")


### Plotting functions
def plot_area_price(case, scenario):
    df = area_price_all_storylines(case, scenario)

    # Reset index
    df_reset = df.reset_index()

    # Melt the DataFrame over both 'Storyline'
    df_melt = df_reset.melt(id_vars=['Storyline'])

    # Rename columns for clarity
    df_melt.columns = ['Storyline', 'Area', 'Price']

    # Create a mapping dictionary for scenarios
    scenario_mapping = {
        ('case1', 'scenario1'): 'Scenario A',
        ('case1', 'scenario2'): 'Scenario B',
        ('case1', 'scenario3'): 'Scenario C',
        ('case2', 'scenario1'): 'Scenario D',
        ('case2', 'scenario2'): 'Scenario E',
        ('case2', 'scenario3'): 'Scenario F',
        ('case3', 'scenario1'): 'Scenario G',
        ('case3', 'scenario2'): 'Scenario H',
        ('case3', 'scenario3'): 'Scenario I'
    }

    # Get the new scenario name from the mapping
    scenario = scenario_mapping.get((case, scenario), scenario)

    # Plot the data
    plt.figure(figsize=(12, 5))
    sns.barplot(x='Area', y='Price', hue='Storyline', data=df_melt, dodge=10)
    plt.title(f"Average area prices for {scenario}")
    plt.ylabel('Price [EUR/MWh]')
    plt.xlabel('Country')
    plt.xticks(rotation=45)
    plt.legend(title='Storyline')

    # Show the plot
    plt.tight_layout()
    # plt.show()

    # Save the figure
    figure_path = "/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Area_prices_plot/"
    plt.savefig(f"{figure_path}/area_prices_{case}_{scenario}.png")


def plot_all_area_prices():
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']

    for case in cases:
        for scenario in scenarios:
            plot_area_price(case, scenario)
            print(f"Successfully saved the area price for {case}, {scenario}")


# plot_all_area_prices()


def make_all_latex_scenarios():
    storylines = ['Distributed Energy', 'Global Ambition', 'National Trends']
    for storyline in storylines:
        latex_area_price_compare_scenarios(storyline)


# make_all_latex_scenarios()