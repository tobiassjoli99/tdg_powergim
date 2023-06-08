from pathlib import Path
import pandas as pd
import pyomo.environ as pyo
import powergim as pgim
from only_changes_here.plotting_and_output.allocation_costs.allocation_costs import allocation_costs_to_latex
from only_changes_here.plotting_and_output.costs.compare_storylines import latex_table_obj_costs
from only_changes_here.plotting_and_output.power_flow.find_power_flow import plot_PLI_flow
from only_changes_here.plotting_and_output.transmission_ex.maps_three_storylines import plot_maps_scenarios
import joblib
import os

from powergim import const


def optimize_nsog(story_name, case, scenario):
    # Set names for storylines
    if story_name == 'Distributed Energy':
        story_ini = 'DE'
    elif story_name == 'Global Ambition':
        story_ini = 'GA'
    elif story_name == 'National Trends':
        story_ini = 'NT'
    else:
        print('Give valid storyline')

    # Make paths
    TEST_DATA_ROOT_PATH = f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{story_name}/{case}/{scenario}/"
    GRID_DATA_RESULTS_PATH = os.path.join(TEST_DATA_ROOT_PATH, "grid_data_results.joblib")
    ALL_VAR_VALUES_PATH = os.path.join(TEST_DATA_ROOT_PATH, "all_var_values_results.joblib")
    DUAL_VALUES_PATH = os.path.join(TEST_DATA_ROOT_PATH, "dual_values.joblib")
    BRANCH_COSTS = os.path.join(TEST_DATA_ROOT_PATH, f"costs.csv")
    INPUT_DATA_PATH = '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data'

    # Read in input data
    parameter_data = pgim.file_io.read_parameters(
        '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/parameters.yaml')
    grid_data = pgim.file_io.read_grid(
        investment_years=parameter_data["parameters"]["investment_years"],
        nodes=os.path.join(INPUT_DATA_PATH, 'nodes', case, f"nodes_{case}_{scenario}.csv"),
        branches=os.path.join(INPUT_DATA_PATH, 'branches', case, f"branches_{case}_{scenario}.csv"),
        generators=f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/generation/generators_{story_ini}_new.csv",
        consumers=f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/{story_ini}_time_series/consumers_{story_ini}_new.csv",
    )
    file_timeseries_sample = f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/{story_ini}_time_series/time_series_sample_{story_ini}.csv"
    grid_data.profiles = pgim.file_io.read_profiles(filename=file_timeseries_sample)

    # Set maximum branch
    grid_data.branch.loc[:, "max_newCap"] = 20000

    # Set the correct PLI capacity
    if case == 'case2':
        if scenario == 'scenario1':
            pgim.const.MAX_NODE_NEW_CAPACITY = 10000
        elif scenario == 'scenario2':
            pgim.const.MAX_NODE_NEW_CAPACITY = 20000
        elif scenario == 'scenario3':
            pgim.const.MAX_NODE_NEW_CAPACITY = 50000

    # Set the correct PLI capacity
    if case == 'case3':
        pgim.const.MAX_NODE_NEW_CAPACITY = 10000

    # Create the PowerGIM model object
    model = pgim.SipModel(grid_data=grid_data, parameter_data=parameter_data)

    # Compute the branch distances
    grid_data.branch["dist_computed"] = grid_data.compute_branch_distances()

    # Solve the model using the Gurobi solver
    solver = pyo.SolverFactory('gurobi')
    results = solver.solve(model,
                           tee=False,
                           keepfiles=False,
                           symbolic_solver_labels=True,
                           )

    # Optimal variable values
    all_var_values = model.extract_all_variable_values()
    joblib.dump(all_var_values, ALL_VAR_VALUES_PATH)

    # Save the result grid data for optimization results
    grid_data_result = model.grid_data_result(all_var_values)
    joblib.dump(grid_data_result, GRID_DATA_RESULTS_PATH)

    # Save the costs
    df_branch_cost = pd.DataFrame()
    for branch in model.s_branch:
        for period in model.s_period:
            investment = pyo.value(model.costBranch(branch, 2030))
            df_branch_cost.loc[branch, period] = model.npvInvestment(period, investment)
    df_branch_cost.to_csv(BRANCH_COSTS)

    # Create an Excel writer object
    writer = pd.ExcelWriter(os.path.join(TEST_DATA_ROOT_PATH, f"results_{case}_{scenario}.xlsx"))

    # Loop through keys of dictionary
    for key, values in all_var_values.items():
        # Convert value to DataFrame
        if values is not None:
            df = pd.DataFrame(values.items(), columns=[key, 'value'])
            # Write DataFrame to new sheet with key as sheet name
            df.to_excel(writer, sheet_name=key, index=False)

    # Save Excel file
    writer.close()

    print(f"Optimization finito for: {story_name}: {case}: {scenario}")

    return


def choose_optimizations(what, case):
    storylines = ['Distributed Energy', 'Global Ambition', 'National Trends']
    scenarios = ['scenario1', 'scenario2', 'scenario3']

    """
    optimize_nsog(storyline, case, scenario)
    allocation_costs_to_latex(case, scenario)
    latex_table_obj_costs(case, scenario)
    plot_PLI_flow(case, scenario)
    plot_maps_scenarios(case, scenario)
    """

    if what == 'optimize_case':
        for scenario in scenarios:
            for storyline in storylines:
                optimize_nsog(storyline, case, scenario)
    elif what == 'optimize_and_make':
        for scenario in scenarios:
            for storyline in storylines:
                optimize_nsog(storyline, case, scenario)
            plot_maps_scenarios(case, scenario)
            allocation_costs_to_latex(case, scenario)
            latex_table_obj_costs(case, scenario)
            plot_PLI_flow(case, scenario)


choose_optimizations('optimize_and_make', 'case1')

choose_optimizations('optimize_and_make', 'case2')

choose_optimizations('optimize_and_make', 'case3')












