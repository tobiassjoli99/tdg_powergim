from pathlib import Path
import pytest
import pandas as pd
import pyomo.environ as pyo

import powergim as pgim

TEST_DATA_ROOT_PATH = Path(__file__).parent / "test_own_data"
NUMERIC_THRESHOLD = 1e-3


def test_own_data():
    # Read input data
    parameter_data = pgim.file_io.read_parameters(TEST_DATA_ROOT_PATH / "parameters.yaml")
    grid_data = pgim.file_io.read_grid(
        investment_years=parameter_data["parameters"]["investment_years"],
        nodes=TEST_DATA_ROOT_PATH / "nodes.csv",
        branches=TEST_DATA_ROOT_PATH / "branches.csv",
        generators=TEST_DATA_ROOT_PATH / "generators.csv",
        consumers=TEST_DATA_ROOT_PATH / "consumers.csv",
    )
    file_timeseries_sample = TEST_DATA_ROOT_PATH / "time_series_sample.csv"
    grid_data.profiles = pgim.file_io.read_profiles(filename=file_timeseries_sample)

    # Set the grid data and parameterdata
    grid_data.branch.loc[:, "max_newCap"] = 5000

    sip = pgim.SipModel(grid_data=grid_data, parameter_data=parameter_data)
    grid_data.branch["dist_computed"] = grid_data.compute_branch_distances()

    # Solve the problem using glpk solver
    opt = pyo.SolverFactory("glpk")
    results = opt.solve(
        sip,
        tee=False,
        keepfiles=False,
        symbolic_solver_labels=True,
    )

    # Optimal variable values into the all_var_variables dictionary
    all_var_values = sip.extract_all_variable_values()

    # Print the values
    print(f"Objective = {pyo.value(sip.OBJ)}")
    print(all_var_values.keys())

    # Print the values for 2030 and 2040
    print(all_var_values["v_investment_cost"][2030])
    print(all_var_values["v_investment_cost"][2040])


if __name__ == "__main__":
    test_own_data()

'''
def total_cost_objective_rule(model):
    years = [0, 10, 20]
    number_nodes = 5
    number_timesteps = 2
    grid_data, parameter_data = testcases.create_case_star(years, number_nodes, number_timesteps, base_MW=2000)
    sip = powergim.SipModel(grid_data, parameter_data)
    opt = SolverFactory("glpk")
    model.Total_Cost_Objective = Objective(rule=total_cost_objective_rule, sense=minimize)
    instance = model.clone()
    results = opt.solve(instance,
                        tee=True,  # stream the solver output
                        keepfiles=False,  # print the LP file for examination
                        symbolic_solver_labels=False)  # use human readable names

    instance.solutions.load_from(results)
    print('First stage costs: ', value(instance.FirstStageCost) / 10 ** 9, 'bnEUR')
    print('Second stage costs: ', value(instance.SecondStageCost) / 10 ** 9, 'bnEUR')

    return model.FirstStageCost + model.SecondStageCost
'''
