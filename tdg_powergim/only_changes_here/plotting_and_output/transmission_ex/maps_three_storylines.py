import os
import joblib
import matplotlib

matplotlib.use('TkAgg')  # use TkAgg backend
import matplotlib.pyplot as plt
from powergim.better_plotting_geopandas import plot_map2


def plot_maps_scenarios(case, scenario):
    # This function uses the results for the simulations and plot the map for all three storylines, save as well
    # Define the file paths for the scenarios
    file_paths = {
        "Distributed Energy": f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/Distributed Energy/{case}/{scenario}/grid_data_results.joblib",
        "Global Ambition": f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/Global Ambition/{case}/{scenario}/grid_data_results.joblib",
        "National Trends": f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/National Trends/{case}/{scenario}/grid_data_results.joblib"
    }

    # Load the branches data
    branches_data = f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here//make_input_data/branches/{case}/branches_{case}_{scenario}.csv"

    # Create subplots for the three scenarios
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Iterate over the scenarios and plot the maps for 2030
    for i, (scenario_name, file_path) in enumerate(file_paths.items()):
        grid_data_result = joblib.load(file_path)
        plot_map2(grid_data_result, years=[2030],
                  shapefile_path='/Users/tobiassjoli/PycharmProjects/tdg_powergim/tests/test_own_data/kart_nsog',
                  ax=axs[i], include_zero_capacity=False, width_col=None, node_options=None,
                  capacities_2030=branches_data)
        axs[i].set_title(scenario_name)

    # Adjust the layout and merge the legends
    handles, labels = axs[2].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right')

    # Adjust spacing between subplots and center the figures
    plt.subplots_adjust(wspace=0.2, left=0.05, right=0.87)

    # Save the figure
    figure_path = "/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Maps_plot/"
    fig.savefig(f"{figure_path}/{case}_{scenario}.png")

    # Show the plot
    # plt.show()

    print(f"Successfully saved the plot for {case}, {scenario}")


def plot_all_maps():
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']

    for case in cases:
        for scenario in scenarios:
            plot_maps_scenarios(case, scenario)

# Usage:
# plot_all_maps()

