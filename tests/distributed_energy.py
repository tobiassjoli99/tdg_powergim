from pathlib import Path
from plots_map2 import plot_map2
import pandas as pd
import pyomo.environ as pyo
import powergim as pgim

TEST_DATA_ROOT_PATH = Path(__file__).parent / "test_own_data"


def optimize_nsog():
    # Read in input data
    parameter_data = pgim.file_io.read_parameters(TEST_DATA_ROOT_PATH / "parameters.yaml")
    grid_data = pgim.file_io.read_grid(
        investment_years=parameter_data["parameters"]["investment_years"],
        nodes=TEST_DATA_ROOT_PATH / "nodes.csv",
        branches=TEST_DATA_ROOT_PATH / "branches_wo_2050.csv",
        generators=TEST_DATA_ROOT_PATH / "generators_DE_wo_2050.csv",
        consumers=TEST_DATA_ROOT_PATH / "consumers.csv",
    )
    file_timeseries_sample = TEST_DATA_ROOT_PATH / "time_series_sample.csv"
    grid_data.profiles = pgim.file_io.read_profiles(filename=file_timeseries_sample)

    # TODO: Set temporarily to reproduce previous result:
    grid_data.branch.loc[:, "max_newCap"] = 5000

    grid_data.branch = grid_data.branch.dropna()
    print(grid_data.branch)
    print(grid_data)

    # Create the PowerGIM model object
    model = pgim.SipModel(grid_data=grid_data, parameter_data=parameter_data)
    grid_data.branch["dist_computed"] = grid_data.compute_branch_distances()

    # Assuming the model object is named "model"
    for i in model.c_operating_costs:
        print(i)

    # Solve the model using the GLPK solver
    solver = pyo.SolverFactory('glpk')
    results = solver.solve(model,
                           tee=False,
                           keepfiles=False,
                           symbolic_solver_labels=True,
                           )

    # Optimal variable values
    all_var_values = model.extract_all_variable_values()

    # Check results are as expected
    print(f"Objective = {pyo.value(model.OBJ)}")
    print("Investment cost for 2030: ", all_var_values["v_investment_cost"][2030])
    print("Investment cost for 2040: ", all_var_values["v_investment_cost"][2040])

    print(all_var_values)

    # Create an Excel writer object
    writer = pd.ExcelWriter('results.xlsx')

    # Loop through keys of dictionary
    for key, values in all_var_values.items():
        # Convert value to DataFrame
        df = pd.DataFrame(values.items(), columns=[key, values])
        # Write DataFrame to new sheet with key as sheet name
        df.to_excel(writer, sheet_name=key, index=False)

    # Save Excel file
    writer.close()

    # Plot map
    plot_map2(grid_data, years=[2030, 2040],
              shapefile_path='/Users/tobiassjoli/PycharmProjects/tdg_powergim/tests'
                             '/test_own_data/kart_nsog', ax=None,
              include_zero_capacity=False,
              width_col=None, node_options=None)


if __name__ == "__main__":
    optimize_nsog()
