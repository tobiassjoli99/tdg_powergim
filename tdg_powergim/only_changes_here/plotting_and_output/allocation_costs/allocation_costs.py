import pandas as pd


def allocation_costs(case, scenario):
    storylines = ['Distributed Energy', 'Global Ambition', 'National Trends']

    # Initialize the DataFrame to store country costs
    df_country_costs = pd.DataFrame()

    for storyline in storylines:
        # Load the branch costs
        branch_costs = pd.read_csv(
            f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{storyline}/{case}/{scenario}/costs.csv",
            index_col=False)
        branch_costs = branch_costs['2030']

        # Load the branch names
        branch_names = pd.read_csv(
            f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/branches/{case}/branches_{case}_{scenario}.csv",
            index_col=False)

        node_from = branch_names['node_from']
        node_to = branch_names['node_to']

        df_names_costs = pd.DataFrame()
        df_names_costs['node_from'] = node_from
        df_names_costs['node_to'] = node_to
        df_names_costs['country_from'] = df_names_costs['node_from'].str[:2]
        df_names_costs['country_to'] = df_names_costs['node_to'].str[:2]
        df_names_costs['cost'] = branch_costs

        # Initialize country cost dictionary
        country_costs = {}

        # Loop through the DataFrame
        for index, row in df_names_costs.iterrows():
            cost = row['cost']

            # If 'country_from' is 'PL', assign the whole cost to 'country_to'
            if row['country_from'] == 'PL':
                country = row['country_to']
                country_costs[country] = country_costs.get(country, 0) + cost

            # If 'country_from' and 'country_to' are the same, assign the whole cost to the country
            elif row['country_from'] == row['country_to']:
                country = row['country_from']
                country_costs[country] = country_costs.get(country, 0) + cost

            # If 'country_from' and 'country_to' are different, and 'country_from' is not 'PL', split the cost 50/50
            elif row['country_from'] != row['country_to']:
                country1, country2 = row['country_from'], row['country_to']
                country_costs[country1] = country_costs.get(country1, 0) + cost / 2
                country_costs[country2] = country_costs.get(country2, 0) + cost / 2

        # Remove any cost assigned to 'PL'
        if 'PL' in country_costs:
            del country_costs['PL']

        # Convert the dictionary to a DataFrame
        df_storyline_costs = pd.DataFrame(list(country_costs.items()), columns=['country', storyline])

        # Calculate total cost and percent of total cost for each country
        total_cost = df_storyline_costs[storyline].sum()
        df_storyline_costs[storyline] = df_storyline_costs[storyline].apply(
            lambda x: f"{x / 1e9:.3f} ({100 * x / total_cost:.2f})")

        # Merge the DataFrames
        if df_country_costs.empty:
            df_country_costs = df_storyline_costs
        else:
            df_country_costs = pd.merge(df_country_costs, df_storyline_costs, on='country', how='outer')

    # Define the file path
    file_path = f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/plotting_and_output/allocation_costs/{case}/country_costs_{case}_{scenario}.csv"

    # Save the DataFrame to a CSV file
    df_country_costs.to_csv(file_path, index=False)

    return file_path

def allocation_costs_to_latex(case, scenario):
    output_path = f"/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Allocation_costs_tables/allocation_table_{case}_{scenario}.tex"

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

    # Read the CSV file
    df = pd.read_csv(allocation_costs(case, scenario), index_col=None)

    # Rename columns to include the unit [Bn €] and 'Country'
    df.rename(columns={
        'country': 'Country',
        'Distributed Energy': r'DE [Bn \euro]',
        'Global Ambition': r'GA [Bn \euro]',
        'National Trends': r'NT [Bn \euro]'
    }, inplace=True)

    # Get the new scenario name from the mapping
    scenario = scenario_mapping.get((case, scenario), scenario)

    # Formatter for the country column
    formatters = {'Country': lambda x: f"\\textbf{{{x}}}"}

    # Create bold headers
    bold_headers = [f"\\textbf{{{header}}}" for header in df.columns]

    # Format the table in LaTeX
    latex_table = df.to_latex(header=bold_headers, float_format="%.3f", formatters=formatters, index=False, escape=False)

    caption = f"Allocation of transmission investment costs for {scenario}"

    # Add LaTeX table definition, caption, and label
    latex_table = "\\begin{table}\n\\centering" + \
        f"\n\\caption{{Allocation of transmission investments for {scenario} and percent of total transmission cost}}" + \
        f"\n\\label{{tab:allocation_costs_{case}_{scenario}}}" + \
        f"\n{latex_table}\n\\end{{table}}\n"

    # Write the LaTeX string to a .tex file
    with open(output_path, 'w') as f:
        f.write(latex_table)


def make_all_latex_allocation_costs():
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']

    for case in cases:
        for scenario in scenarios:
            allocation_costs_to_latex(case, scenario)

make_all_latex_allocation_costs()