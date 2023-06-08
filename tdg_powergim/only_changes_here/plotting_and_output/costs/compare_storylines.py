import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def billions_formatter(x, pos):
    """Formatter function to divide the y-axis labels by 1e9 (1,000,000,000)"""
    return f'{x / 1e9:.0f}'


def compare_costs_storylines(case, scenario):
    # This function makes a csv file with costs for all scenarios
    output_directory = "/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/plotting_and_output/costs"
    file_paths = {
        "Distributed Energy": f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/Distributed Energy/{case}/{scenario}/results_{case}_{scenario}.xlsx",
        "Global Ambition": f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/Global Ambition/{case}/{scenario}/results_{case}_{scenario}.xlsx",
        "National Trends": f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/National Trends/{case}/{scenario}/results_{case}_{scenario}.xlsx"
    }
    data = []

    for storyline_name, file_path in file_paths.items():
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=None)

        # Extract investment cost and operational cost
        investment = df['v_investment_cost'].loc[0, 'value']
        operational = df['v_operating_cost'].loc[0, 'value']

        # Append the data to the list
        data.append([investment, operational, investment + operational])  # added total cost

    # Create a DataFrame from the data, with storyline names as columns
    df_output = pd.DataFrame(data, columns=['investment_2030', 'operational_2030', 'total_2030'], index=file_paths.keys())

    # Transpose the DataFrame so that storylines become column names and costs become indices
    df_output = df_output.transpose()

    # Create the output file path
    output_file = os.path.join(output_directory, case, f"costs_{scenario}.csv")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save the DataFrame to a CSV file
    df_output.to_csv(output_file)

    print(f"Successfully saved the costs for {case}, {scenario}")

    return output_file


def latex_table_obj_costs(case, scenario):
    scenario_map = {
        ('case1', 'scenario1'): 'Scenario A',
        ('case1', 'scenario2'): 'Scenario B',
        ('case1', 'scenario3'): 'Scenario C',
        ('case2', 'scenario1'): 'Scenario D',
        ('case2', 'scenario2'): 'Scenario E',
        ('case2', 'scenario3'): 'Scenario F',
        ('case3', 'scenario1'): 'Scenario G',
        ('case3', 'scenario2'): 'Scenario H',
        ('case3', 'scenario3'): 'Scenario I',
    }

    input_csv_path = compare_costs_storylines(case, scenario)
    output_tex_path = f"/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Costs_tables/latex_{case}_{scenario}.tex"

    df = pd.read_csv(input_csv_path, index_col=0)
    df = df / 1e9
    df = df.round(2)

    df.index = df.index.map({
        "investment_2030": "Investment cost",
        "operational_2030": "Operational cost",
        "total_2030": "Total cost"
    })

    scenario_name = scenario_map.get((case, scenario), 'Unknown Scenario')

    table = df.to_latex(header=[r'\textbf{DE [Bn \euro]}', r'\textbf{GA [Bn \euro]}', r'\textbf{NT [Bn \euro]}'],
                        bold_rows=True, escape=False)

    table = '\\begin{table}\n' + \
            '    \\centering\n' + \
            f'    \\caption{{Investment, operational, and total costs for {scenario_name}}}\n' + \
            f'    \\label{{tab:costs_{case}_{scenario}}}\n' + \
            table + \
            '\\end{table}\n'

    with open(output_tex_path, 'w') as f:
        f.write(table)


def plot_costs(case, scenario):
    # This function runs the compare_costs_storylines and plot the costs
    # Read the CSV file
    csv_file = compare_costs_storylines(case, scenario)
    df = pd.read_csv(csv_file)

    # Extract the scenario names and cost values
    scenarios = df['storyline']
    investment = df['investment_2030']
    operational = df['operational_2030']

    # Set the width of the bars
    bar_width = 0.3

    # Set the x positions for the bars
    x = range(len(scenarios))

    # Plot the results
    fig, ax = plt.subplots(figsize=(10, 4))

    in_color = 'blue'
    op_color = 'darkorange'

    # 2030 bars
    ax.bar(x - np.array(bar_width)/10, investment, width=bar_width, label='Investment cost', color=in_color)
    ax.bar(x - np.array(bar_width)/10, operational, width=bar_width, bottom=investment, label='Operational cost', color=op_color)

    ax.set_xlabel('')
    ax.set_ylabel('Cost [Bn €]')
    ax.set_title(f"Total project costs for {scenario}")
    ax.set_xticks([i + bar_width / 2 for i in x])
    ax.set_xticklabels(scenarios)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4), ncol=len(scenarios))

    # Add legends for the cost types
    leg1 = plt.Rectangle((0, 0), 1, 1, color=in_color, label='Investment cost')
    leg2 = plt.Rectangle((0, 0), 1, 1, color=op_color, label='Operational cost')
    ax.legend(handles=[leg1, leg2], loc='upper right', title='')

    # Format y-axis labels as billions
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(billions_formatter))

    # Show the plot
    # plt.show()

    # Save the figure
    figure_path = "/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Costs_plot"
    fig.savefig(f"{figure_path}/costs_{case}_{scenario}.png")

    print(f"Successfully saved the plot for {case}, {scenario}")

