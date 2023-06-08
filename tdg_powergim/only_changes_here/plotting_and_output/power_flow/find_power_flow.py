import pandas as pd
import joblib
import powergim as pgim
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

def get_PLI_flow(storyline, case, scenario):

    # Load excel file
    xls = pd.ExcelFile(f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/run_optimization/{storyline}/{case}/{scenario}/results_{case}_{scenario}.xlsx")

    # Load the branch names
    branch_names = pd.read_csv(
        f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/branches/{case}/branches_{case}_{scenario}.csv",
        index_col=False)
    branch_names = branch_names[['node_from', 'node_to']]

    # Filter out the branch names that contain 'PLI'
    pli_branch_flows = branch_names[
        branch_names['node_from'].str.contains('PLI') | branch_names['node_to'].str.contains('PLI')]

    pli_branch_flows = pli_branch_flows.reset_index()

    # Read 'v_branch_new_capacity' sheet and add capacity to pli_branch_flows
    v_branch_new_capacity = pd.read_excel(xls, sheet_name='v_branch_new_capacity')
    v_branch_new_capacity['branch_index'] = v_branch_new_capacity['v_branch_new_capacity'].apply(lambda x: int(x.split(',')[0][1:]))

    pli_branch_flows = pli_branch_flows.merge(v_branch_new_capacity, left_on='index', right_on='branch_index', how='left')
    pli_branch_flows = pli_branch_flows.rename(columns={'value': 'capacity'})
    pli_branch_flows = pli_branch_flows.drop('branch_index', axis=1)

    # Function to calculate mean flow
    def calculate_mean_flow(sheet_name, flow_column_name):
        flow_df = pd.read_excel(xls, sheet_name=sheet_name)
        flow_df['branch_index'] = flow_df[sheet_name].apply(lambda x: int(x.split(',')[0][1:]))
        mean_flow = flow_df.groupby('branch_index')['value'].mean().reset_index()
        mean_flow = mean_flow.rename(columns={'value': flow_column_name})
        return mean_flow

    # Calculate mean flow_in and flow_out
    mean_flow_in = calculate_mean_flow('v_branch_flow12', 'flow_in')
    mean_flow_out = calculate_mean_flow('v_branch_flow21', 'flow_out')

    # Add mean flow_in and flow_out to pli_branch_flows
    pli_branch_flows = pli_branch_flows.merge(mean_flow_in, left_on='index', right_on='branch_index', how='left')
    pli_branch_flows = pli_branch_flows.drop('branch_index', axis=1)
    pli_branch_flows = pli_branch_flows.merge(mean_flow_out, left_on='index', right_on='branch_index', how='left')
    pli_branch_flows = pli_branch_flows.drop('branch_index', axis=1)

    # Delete all branches where the capacity is zero
    pli_branch_flows = pli_branch_flows.loc[pli_branch_flows['capacity'] > 1]

    return pli_branch_flows


def plot_PLI_flow(case, scenario):
    storylines = ['Distributed Energy', 'Global Ambition', 'National Trends']
    pli_data_per_storyline = {}

    # First gather all data per storyline, this avoids multiple calls to get_PLI_flow()
    for storyline in storylines:
        pli_data_per_storyline[storyline] = get_PLI_flow(storyline, case, scenario)

    # Identify unique PLIs in all storylines
    pli_set = set()
    for pli_data in pli_data_per_storyline.values():
        pli_set.update(pli_data['node_from'].unique())

    for pli_name in pli_set:
        pli_storylines = []  # storylines that contain this PLI
        pli_branch_flows_dict = {}  # dictionary to hold pli_branch_flows for each storyline

        for storyline, pli_data in pli_data_per_storyline.items():
            pli_flow = pli_data[pli_data['node_from'] == pli_name]

            if not pli_flow.empty:
                pli_storylines.append(storyline)
                pli_branch_flows_dict[storyline] = pli_flow

        # Only generate a figure if this PLI is in at least one storyline
        if pli_storylines:
            fig, axes = plt.subplots(1, len(pli_storylines), figsize=(len(pli_storylines)*7, 8))  # Adjust the figure size as needed
            if len(pli_storylines) == 1:
                axes = [axes]  # Ensure axes is always a list
            fig.tight_layout(pad=10.0)  # Add space between subplots
            fig.suptitle(pli_name, fontsize=16, y=0.88)  # Add a main title above the legends of the subplots

            for i, storyline in enumerate(pli_storylines):
                ax = axes[i]
                pli_flow = pli_branch_flows_dict[storyline]

                # Plotting flow_in and capacity on left side of vertical line
                ax.barh(pli_flow['node_to'], -pli_flow['flow_in'], color='#008000')
                ax.barh(pli_flow['node_to'], -pli_flow['capacity'], color='#808080', alpha=0.5)

                # Adding a vertical line at x=0
                ax.axvline(0, color='k')

                # Plotting flow_out and capacity on right side of vertical line
                ax.barh(pli_flow['node_to'], pli_flow['flow_out'], color='#ff0000')
                ax.barh(pli_flow['node_to'], pli_flow['capacity'], color='#808080', alpha=0.5)

                # Adjusting legend and grid
                legend_elements = [Patch(facecolor='#008000', label='Flow in'),
                                   Patch(facecolor='#808080', label='Line capacity'),
                                   Patch(facecolor='#ff0000', label='Flow out')]

                # Moving the legend to the bottom center under the plot
                ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

                # Adjusting xticks to be in intervals of 1500, and they should go in both directions from the vertical line
                max_abs_value = max(max(abs(pli_flow['flow_in'])), max(abs(pli_flow['flow_out'])),
                                    max(abs(pli_flow['capacity'])))
                xticks = np.linspace(0, int(max_abs_value),
                                     num=5)  # Adjust num as needed for number of x-axis labels
                ax.set_xticks(list(xticks) + [-x for x in xticks])

                # Apply absolute value to labels
                ax.set_xticklabels([abs(int(x)) for x in ax.get_xticks()], rotation='vertical')

                # Removing labels and adjusting title
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.set_title(storyline)

                for ax in plt.gcf().axes:
                    # Change x-axis label size
                    ax.tick_params(axis='x', labelsize=12)  # Change the text size here

                    # Change y-axis label (bar name) size
                    ax.tick_params(axis='y', labelsize=12)  # Change the text size here

                    legend = ax.get_legend()
                    # If a legend exists in this axes
                    if legend:
                        for text in legend.get_texts():
                            text.set_fontsize(12)  # Change the text size here

            # Save the figure
            figure_path = "/Users/tobiassjoli/Documents/Master/Bilder_figurer/Results/Power_flow_plot/"
            fig.savefig(f"{figure_path}/{pli_name}_{case}_{scenario}.png")

            print('Successfully saved the powerflow')

    # plt.show()


def make_all_flow_plots():
    cases = ['case1', 'case2', 'case3']
    scenarios = ['scenario1', 'scenario2', 'scenario3']

    for case in cases:
        for scenario in scenarios:
            plot_PLI_flow(case, scenario)

