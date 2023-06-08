import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter


def latex_table_costs_storylines():
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']
    storylines = ["Distributed Energy", "Global Ambition", "National Trends"]

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

    for storyline in storylines:
        data = []
        for case in cases:
            for scenario in scenarios:
                file_path = f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{storyline}/{case}/{scenario}/results_{case}_{scenario}.xlsx"
                df = pd.read_excel(file_path, sheet_name=None)
                investment = df['v_investment_cost'].loc[0, 'value']
                operational = df['v_operating_cost'].loc[0, 'value']
                total = investment + operational
                data.append(
                    [scenario_mapping.get((case, scenario), 'Unknown Scenario'), total / 1e9])  # total cost in Bn Euro

        df_output = pd.DataFrame(data, columns=['Scenario', 'Total Cost [Bn Euro]'])

        # Calculate and add "Difference from Scenario A" column
        scenario_a_cost = df_output.loc[df_output['Scenario'] == 'Scenario A', 'Total Cost [Bn Euro]'].values[0]
        df_output['Difference from Scenario A'] = df_output['Total Cost [Bn Euro]'] - scenario_a_cost

        df_output = df_output.round(2)

        output_tex_path = f"/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Total_costs_scenarios_latex/latex_total_costs_{storyline}.tex"

        table = df_output.to_latex(index=False, header=[r'\textbf{Scenario}', r'\textbf{Total Cost [Bn \euro]}',
                                                        r'\textbf{Difference from Scenario A}'],
                                   bold_rows=True, escape=False)

        table = '\\begin{table}\n' + \
                '    \\centering\n' + \
                f'    \\caption{{Total costs for {storyline}}}\n' + \
                f'    \\label{{tab:total_costs_{storyline}}}\n' + \
                table + \
                '\\end{table}\n'

        with open(output_tex_path, 'w') as f:
            f.write(table)

        print(f"Successfully created LaTeX table for {storyline}")


latex_table_costs_storylines()


