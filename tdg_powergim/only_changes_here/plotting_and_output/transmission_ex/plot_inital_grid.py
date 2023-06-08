import geopandas
import matplotlib.pyplot as plt
import shapely
from matplotlib import cm

import powergim as pgim
import os
import numpy as np
import pandas as pd

from powergim.grid_data import GridData


def plot_initial(
    years,
    shapefile_path: str,
    ax=None,
    include_zero_capacity=False,
    width_col=None,
    node_options=None,
    capacities_2030=None,
    **kwargs
):
    """Plot grid using geopandas (for print)"""

    try:
        land = geopandas.read_file(f"{shapefile_path}/ne_50m_land.zip")
        lakes = geopandas.read_file(f"{shapefile_path}/ne_50m_lakes.zip")
        coastline = geopandas.read_file(f"{shapefile_path}/ne_50m_coastline.zip")
        borders = geopandas.read_file(f"{shapefile_path}/ne_50m_admin_0_boundary_lines_land.zip")
    except Exception as ex:
        print(
            ex,
            ">> Missing shape file. Download from https://www.naturalearthdata.com/downloads/",
        )
        return
    try:
        borders_sea = geopandas.read_file(f"{shapefile_path}/World_maritime_Boundaries.zip")
    except Exception as ex:
        print(
            ex,
            ">> Missing shape file. Download from https://hub.arcgis.com/datasets/nga::world-maritime-boundaries/",
        )
        return

    # Make paths
    INPUT_DATA_PATH = '/only_changes_here/run_optimization/nodes'

    case = 'case3'
    scenario = 'scenario3'

    parameter_data = pgim.file_io.read_parameters(
        '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/parameters.yaml')
    grid_data = pgim.file_io.read_grid(
        investment_years=parameter_data["parameters"]["investment_years"],
        nodes=os.path.join(INPUT_DATA_PATH, case, f"nodes_{case}_{scenario}.csv"),
        branches=os.path.join(INPUT_DATA_PATH, case, f"branches_{case}_{scenario}.csv"),
        generators=f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/generation/generators_DE_new.csv",
        consumers=f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/DE_time_series/consumers_DE_new.csv",
    )

    if ax is None:
        plt.figure(figsize=(8, 10))
        ax = plt.gca()
    ax.set_facecolor("white")
    lakes.plot(ax=ax, color="white")
    land.plot(ax=ax, color="lightgray")
    coastline.plot(ax=ax, color="darkgray")
    borders.plot(ax=ax, color="darkgray")
    borders_sea.plot(ax=ax, color="darkgray")

    branch = grid_data.branch.copy()
    node = grid_data.node.copy()
    branch["capacity"] = branch["capacity_2030"]

    if not include_zero_capacity:
        branch = branch[branch["capacity"] > 0]

    gdf_nodes = geopandas.GeoDataFrame(
        grid_data.node,
        geometry=geopandas.points_from_xy(grid_data.node["lon"], grid_data.node["lat"]),
        crs="EPSG:4326",
    )

    # Color nodes with name containing 'PLI' in blue
    gdf_nodes.loc[gdf_nodes['id'].str.contains('PLI'), 'color'] = 'red'
    gdf_nodes.loc[gdf_nodes['color'].isna(), 'color'] = 'black'

    node_options = node_options or {}
    node_options['color'] = gdf_nodes['color']

    branch["index"] = branch.index
    gdf_edges = branch.merge(
        gdf_nodes[["lat", "lon", "geometry"]],
        how="left",
        left_on="node_from",
        right_index=True,
    ).merge(
        gdf_nodes[["lat", "lon", "geometry"]],
        how="left",
        left_on="node_to",
        right_index=True,
    )

    # Compute unique capacities and create color map
    unique_capacities = np.unique(branch["capacity"])
    color_map = cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=unique_capacities.min(), vmax=unique_capacities.max()))
    colors = [color_map.to_rgba(capacity) if capacity > 0 else 'black' for capacity in branch["capacity"]]

    # TODO: This gives shapely deprecation warning (issue 13)
    gdf_edges_geometry = gdf_edges.apply(
        lambda x: shapely.geometry.LineString([x["geometry_x"], x["geometry_y"]]),
        axis=1
    )

    gdf_edges = geopandas.GeoDataFrame(gdf_edges, geometry=gdf_edges_geometry, crs="EPSG:4326")

    # Change colors
    if width_col is not None:
        kwargs["linewidth"] = (gdf_edges[width_col[0]] / width_col[1]).clip(upper=width_col[2])
    gdf_edges.plot(ax=ax, color=colors, **kwargs)

    # Plot nodes
    if node_options is None:
        node_options = {}
    gdf_nodes.plot(ax=ax, **node_options)

    """
    # Add labels to nodes
    for x, y, label in zip(gdf_nodes.geometry.x, gdf_nodes.geometry.y, gdf_nodes['id']):
        ax.text(x, y-0.1, label, ha='center', va='top', fontsize=8)
    """

    ax.set_xlim(grid_data.node["lon"].min() - 1, grid_data.node["lon"].max() + 1)
    ax.set_ylim(grid_data.node["lat"].min() - 1, grid_data.node["lat"].max() + 1)
    ax.set(xlabel=None, ylabel=None)

    # Add color legend
    cbar = plt.colorbar(color_map, ax=ax, fraction=0.05, pad=0.02)
    cbar.ax.yaxis.set_ticks_position('right')
    cbar.ax.yaxis.set_label_position('right')
    cbar.ax.spines['right'].set_visible(True)

    plt.show()

    return


def plot_nodes(
    shapefile_path: str,
    ax=None,
    node_options=None,
):
    """Plot grid using geopandas (for print)"""

    try:
        land = geopandas.read_file(f"{shapefile_path}/ne_50m_land.zip")
        lakes = geopandas.read_file(f"{shapefile_path}/ne_50m_lakes.zip")
        coastline = geopandas.read_file(f"{shapefile_path}/ne_50m_coastline.zip")
        borders = geopandas.read_file(f"{shapefile_path}/ne_50m_admin_0_boundary_lines_land.zip")
    except Exception as ex:
        print(
            ex,
            ">> Missing shape file. Download from https://www.naturalearthdata.com/downloads/",
        )
        return
    try:
        borders_sea = geopandas.read_file(f"{shapefile_path}/World_maritime_Boundaries.zip")
    except Exception as ex:
        print(
            ex,
            ">> Missing shape file. Download from https://hub.arcgis.com/datasets/nga::world-maritime-boundaries/",
        )
        return

    # Make paths
    INPUT_DATA_PATH = '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/branches'

    case = 'case1'
    scenario = 'scenario1'

    parameter_data = pgim.file_io.read_parameters(
        '/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/parameters.yaml')
    grid_data = pgim.file_io.read_grid(
        investment_years=parameter_data["parameters"]["investment_years"],
        nodes='/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/nodes/case3/nodes_case3_scenario3.csv',
        branches=os.path.join(INPUT_DATA_PATH, case, f"branches_{case}_{scenario}.csv"),
        generators=f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/generation/generators_DE_new.csv",
        consumers=f"/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/DE_time_series/consumers_DE_new.csv",
    )

    if ax is None:
        plt.figure(figsize=(8, 10))
        ax = plt.gca()
    ax.set_facecolor("white")
    lakes.plot(ax=ax, color="white")
    land.plot(ax=ax, color="lightgray")
    coastline.plot(ax=ax, color="darkgray")
    borders.plot(ax=ax, color="darkgray")
    borders_sea.plot(ax=ax, color="darkgray")

    gdf_nodes = geopandas.GeoDataFrame(
        grid_data.node,
        geometry=geopandas.points_from_xy(grid_data.node["lon"], grid_data.node["lat"]),
        crs="EPSG:4326",
    )

    # Color nodes with name containing 'PLI' in blue
    gdf_nodes.loc[gdf_nodes['id'].str.contains('PLI'), 'color'] = 'red'
    gdf_nodes.loc[gdf_nodes['color'].isna(), 'color'] = 'black'

    node_options = node_options or {}
    node_options['color'] = gdf_nodes['color']

    # Plot nodes
    if node_options is None:
        node_options = {}
    gdf_nodes.plot(ax=ax, **node_options)

    # Add labels to nodes containing 'PLI' in their IDs
    for x, y, label in zip(gdf_nodes.geometry.x, gdf_nodes.geometry.y, gdf_nodes['id']):
        if 'PLI_' in label:
            # split label at underscore and take the second part
            number = label.split('_')[1]
            ax.text(x, y - 0.1, number, ha='center', va='top', fontsize=10, color='red')
        else:
            label = label.replace('wind', 'w').replace('coast', 'c').replace('main', 'm')
            ax.text(x, y - 0.1, label, ha='center', va='top', fontsize=10)  # Move label below node

    ax.set_xlim(grid_data.node["lon"].min() - 1, grid_data.node["lon"].max() + 1)
    ax.set_ylim(grid_data.node["lat"].min() - 1, grid_data.node["lat"].max() + 1)
    ax.set(xlabel=None, ylabel=None)

    plt.show()

    return


plot_nodes(shapefile_path='/Users/tobiassjoli/PycharmProjects/tdg_powergim/tests/test_own_data/kart_nsog')