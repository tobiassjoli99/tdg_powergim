from pathlib import Path

import mpi4py
import mpisppy.utils.sputils
import pandas as pd
import pyomo.environ as pyo

import powergim as pgim

TEST_DATA_ROOT_PATH = Path(__file__).absolute().parent / "data"
NUMERIC_THRESHOLD = 1e-3

NUM_SCENARIOS = 4


def my_scenario_creator(scenario_name, grid_data, parameter_data):
    """Create a scenario."""
    print("Scenario {}".format(scenario_name))

    # Read input data
    sip = pgim.SipModel()
    dict_data = sip.createModelData(grid_data, parameter_data, maxNewBranchNum=5, maxNewBranchCap=5000)

    # Adjust data according to scenario name
    num_scenarios = NUM_SCENARIOS
    probabilities = {f"scen{k}": 1 / num_scenarios for k in range(num_scenarios)}
    # probabilities = {"scen0": 0.3334, "scen1": 0.3333, "scen2": 0.3333,"scen"}
    if scenario_name == "scen0":
        pass
    elif scenario_name == "scen1":
        # Less wind at SN2
        dict_data["powergim"]["genCapacity2"][4] = 1400  # SN phase 2 1.4 GW instead of 7 GW
    elif scenario_name == "scen2":
        # More wind and SN2
        dict_data["powergim"]["genCapacity2"][4] = 10000  # SN2 phase 2 10 GW instead of 7 GW
        dict_data["powergim"]["genCapacity2"][3] = 10000  # Dog 10 GW instad of 7 GW
    elif scenario_name == "scen3":
        # More wind, more demand
        dict_data["powergim"]["genCapacity2"][4] = 8000
    elif scenario_name == "scen4":
        dict_data["powergim"]["genCapacity2"][4] = 9000
    elif scenario_name == "scen5":
        dict_data["powergim"]["genCapacity2"][4] = 10000
    else:
        raise ValueError("Invalid scenario name")

    # Create stochastic model:
    model = sip.scenario_creator(scenario_name, dict_data=dict_data, probability=probabilities[scenario_name])
    return model


def my_scenario_denouement(rank, scenario_name, scenario):
    print(f"DENOUEMENT scenario={scenario_name} OBJ={pyo.value(scenario.OBJ)}")
    sip = pgim.SipModel()
    all_var_values_dict = sip.extract_all_variable_values(scenario)
    dfs = []
    for varname, data in all_var_values_dict.items():
        df = pd.DataFrame(data).reset_index()
        df["variable"] = varname
        dfs.append(df)
    pd.concat(dfs).to_csv(f"ph_res_ALL_{scenario_name}.csv")


def solve_ph(solver_name):
    # Read input data
    grid_data = pgim.file_io.read_grid(
        nodes=TEST_DATA_ROOT_PATH / "nodes.csv",
        branches=TEST_DATA_ROOT_PATH / "branches.csv",
        generators=TEST_DATA_ROOT_PATH / "generators.csv",
        consumers=TEST_DATA_ROOT_PATH / "consumers.csv",
    )
    parameter_data = pgim.file_io.read_parameters(TEST_DATA_ROOT_PATH / "parameters.yaml")
    file_timeseries_sample = TEST_DATA_ROOT_PATH / "time_series_sample.csv"
    grid_data.profiles = pgim.file_io.read_profiles(filename=file_timeseries_sample)

    # Scenarios
    scenario_creator_kwargs = {"grid_data": grid_data, "parameter_data": parameter_data}
    # scenario_names = ["scen0", "scen1", "scen2", "scen3", "scen4", "scen5"]
    scenario_names = [f"scen{k}" for k in range(NUM_SCENARIOS)]

    # Solve via progressive hedging (PH)
    options = {
        "solvername": solver_name,
        "PHIterLimit": 5,
        "defaultPHrho": 10,
        "convthresh": 1e-7,
        "verbose": False,
        "display_progress": False,
        "display_timing": False,
        # "linearize_binary_proximal_terms": True,  # HGS (linearise only binary terms)
        # the below gives error unless "create_cut" is change to "add_cut" in mpisppy code:
        # mpisppy\utils\prox_approx.py", line 176, in _create_initial_cuts
        # ...but that creates new error because y_pnt is 'NoneType'
        # mpisppy\utils\prox_approx.py", line 89, in check_tol_add_cut
        "linearize_proximal_terms": True,  # True gives error (bug in mpisppy code)
        "proximal_linearization_tolerance ": 0.1,  # default =1e-1
        "initial_proximal_cut_count": 2,  # default = 2
        "iter0_solver_options": {"mipgap": 0.01},  # dict(),
        "iterk_solver_options": {"mipgap": 0.005},  # dict(),
    }
    ph = mpisppy.opt.ph.PH(
        options,
        scenario_names,
        scenario_creator=my_scenario_creator,
        scenario_denouement=my_scenario_denouement,  # post-processing and reporting
        scenario_creator_kwargs=scenario_creator_kwargs,
    )

    # solve
    conv, obj, tbound = ph.ph_main()

    rank = mpi4py.MPI.COMM_WORLD.Get_rank()
    # These values are not very useful:
    # print(f"{rank}: conv = {conv}")
    # print(f"{rank}: obj = {obj}")
    # print(f"{rank}: tbound= {tbound}")

    # Extract results:
    res_ph = []
    variables = ph.gather_var_values_to_rank0()
    if variables is not None:
        # this is true when rank is zero.
        for (scenario_name, variable_name) in variables:
            variable_value = variables[scenario_name, variable_name]
            res_ph.append({"scen": scenario_name, "var": variable_name, "value": variable_value})
        df_res = pd.DataFrame(data=res_ph)
        print(f"{rank}: Saving to file...ph_res_rank0.csv")
        df_res.to_csv("ph_res_rank0.csv")
    return ph


if __name__ == "__main__":
    main_ph = solve_ph(solver_name="cbc")