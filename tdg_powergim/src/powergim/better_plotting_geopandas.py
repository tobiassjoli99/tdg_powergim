import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import shapely
import numpy as np
import matplotlib.cm as cm

from powergim.grid_data import GridData


def plot_map2(
    grid_data: GridData,
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

    # TODO: Make it more general
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

    if ax is None:
        plt.figure(figsize=(10, 10))
        ax = plt.gca()
    ax.set_facecolor("white")
    lakes.plot(ax=ax, color="white")
    land.plot(ax=ax, color="lightgray")
    coastline.plot(ax=ax, color="darkgray")
    borders.plot(ax=ax, color="darkgray")
    borders_sea.plot(ax=ax, color="darkgray")

    branch = grid_data.branch.copy()
    node = grid_data.node.copy()
    # generator = grid_data.generator.copy()
    # consumer = grid_data.consumer.copy()
    df_capacities = pd.read_csv(capacities_2030)
    # Make a dataframe from the input capacities for 2030

    # Finally its working! Fuck! Its not working after all.... Workin;)
    if years == [2030]:
        if years is not None:
            branch["capacity"] = branch["capacity_2030"] - df_capacities['capacity_2030']
            # generator["capacity"] = generator[[f"capacity_{p}" for p in years]].sum(axis=1)
            node["capacity"] = node[[f"capacity_{p}" for p in years if f"capacity_{p}" in node]].sum(axis=1)
        if not include_zero_capacity:
            branch = branch[branch["capacity"] > 0]
            node = node[node["capacity"] > 0]
    else:
        print('Give a valid year!')

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
    num_colors = len(unique_capacities)
    color_map = cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=unique_capacities.min(), vmax=unique_capacities.max()))
    colors = [color_map.to_rgba(capacity) if capacity > 0 else 'black' for capacity in branch["capacity"]]

    # TODO: This gives shapely deprecation warning (issue 13)
    gdf_edges_geometry = gdf_edges.apply(
        lambda x: shapely.geometry.LineString([x["geometry_x"], x["geometry_y"]]),
        axis=1
    )

    gdf_edges = geopandas.GeoDataFrame(gdf_edges, geometry=gdf_edges_geometry, crs="EPSG:4326")

    # Hide branches that are built
    gdf_edges = gdf_edges[gdf_edges['expand_2030'] == 1]

    # Change colors
    if width_col is not None:
        kwargs["linewidth"] = (gdf_edges[width_col[0]] / width_col[1]).clip(upper=width_col[2])
    gdf_edges.plot(ax=ax, color=colors, zorder=1, **kwargs)

    # Plot nodes
    if node_options is None:
        node_options = {}
    node_options['zorder'] = 2  # Set zorder to 2 for nodes so they appear on top of branches
    gdf_nodes.plot(ax=ax, **node_options)


    # Add labels to nodes containing 'PLI' in their IDs
    for x, y, label in zip(gdf_nodes.geometry.x, gdf_nodes.geometry.y, gdf_nodes['id']):
        if 'PLI_' in label:
            # split label at underscore and take the second part
            number = label.split('_')[1]
            ax.text(x, y + 0.1, number, ha='center', va='bottom', fontsize=10, color='red')



    ax.set_xlim(grid_data.node["lon"].min() - 1, grid_data.node["lon"].max() + 1)
    ax.set_ylim(grid_data.node["lat"].min() - 1, grid_data.node["lat"].max() + 1)
    ax.set(xlabel=None, ylabel=None)

    # Add color legend
    cbar = plt.colorbar(color_map, ax=ax, fraction=0.05, pad=0.02)
    cbar.ax.yaxis.set_ticks_position('right')
    cbar.ax.yaxis.set_label_position('right')
    cbar.ax.spines['right'].set_visible(True)

    # Set the position
    ax.set_position([0.1, 0.1, 0.5, 0.5])  # Adjust the position as needed

    return
