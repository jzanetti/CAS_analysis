
from os.path import join

from matplotlib.pyplot import (close, colorbar, figure, legend, savefig,
                               subplots, title)
from mpl_toolkits.basemap import Basemap
from numpy import array, asarray, float16, sum
from pandas import DataFrame

from data_process import (ANALYSIS_FILEDS_KEY, LAT_KEY, LON_KEY, MAP_CFG,
                          RECORDS_KEY, REGION_KEY, SPATIAL_FILENAME,
                          TIMESERIES_FILENAME, YEAR_KEY)
from data_process.temporal import obtain_temporal_trend


def create_title_str(analysis_fields_cfg: dict, field_name: str) -> str:
    """Create the plots title

    Args:
        analysis_fields_cfg (dict): analysis field configuration
        field_name (str): field name, e.g., field name 1

    Returns:
        str: title to be used
    """

    proc_analysis_field_cfg = analysis_fields_cfg[field_name]

    major_key_name = list(proc_analysis_field_cfg.keys())[0]

    if proc_analysis_field_cfg[major_key_name] is None:
        return major_key_name

    constrains = ""
    for constrain_key in proc_analysis_field_cfg[major_key_name]:
        constrains += ", {constrain_key}: {constrain_value}".format(
            constrain_key=constrain_key,
            constrain_value=proc_analysis_field_cfg[major_key_name][constrain_key],
        )


    return major_key_name + f"{constrains}"


def rank_region_by_crashes(timeseries_data: dict, cfg: dict) -> dict:
    """Rank regions by the number of crashes

    Args:
        timeseries_data (dict): timeseries data
        cfg (dict): timeseries configuration

    Returns:
        dict: the dict contains the ranked regions
    """
    ranked_regions = {}
    total_crash = {}
    for proc_field_name in timeseries_data:
        total_crash[proc_field_name] = {}
        for proc_region in cfg[REGION_KEY]:
            proc_timeseries = timeseries_data[proc_field_name][proc_region]
            # if cfg[GRADIENT_KEY]:
            #    proc_timeseries = proc_timeseries / max(proc_timeseries)
            #    proc_timeseries = gradient(proc_timeseries)

            total_crash[proc_field_name][proc_region] = sum(proc_timeseries)

        ranked_regions[proc_field_name] = sorted(
            total_crash[proc_field_name], key=total_crash[proc_field_name].get, reverse=True
        )

    return ranked_regions


def temporal_vis(work_dir: str, cfg: dict, timeseries_data: dict):
    """Temporal analysis visualization

    Args:
        work_dir (str): working directory, e.g., where to save the figures
        cfg (dict): temporal analysis configuration
        timeseries_data (dict): produced time series data
    """
    ranked_regions = rank_region_by_crashes(timeseries_data, cfg)

    for proc_field_name in timeseries_data:

        ts_data = []
        for proc_region in ranked_regions[proc_field_name]:

            proc_ts_data = array(timeseries_data[proc_field_name][proc_region])

            ts_data.append(proc_ts_data)

        ts_data = asarray(ts_data)
        ts_data_trend = obtain_temporal_trend(ts_data)
        _, ax = subplots(1, 1, figsize=(12, 10))

        cb = ax.pcolor(ts_data.astype(float16), cmap="jet")

        ax.set_title(
            create_title_str(cfg[ANALYSIS_FILEDS_KEY], proc_field_name)
        )
        ax.set_xticks(range(0, ts_data.shape[1]))
        ax.set_xticklabels(cfg[YEAR_KEY], rotation=90)
        ax.set_xlabel(YEAR_KEY)

        ax.set_yticks(range(0, ts_data.shape[0]))
        ax.set_yticklabels(ranked_regions[proc_field_name], rotation=45)
        ax.set_ylabel(REGION_KEY)

        cbar = colorbar(cb, fraction=0.03, pad=0.1)
        cbar.set_label("Crash number", rotation=270)



        ax2 = ax.twinx()
        ax2.set_ylabel("total crashes", color="r")  # we already handled the x-label with ax1
        ax2.plot(ts_data_trend["x_regres"], ts_data_trend["y_regres"], color="r")
        ax2.scatter(ts_data_trend["x"], ts_data_trend["y"], color="r", s=50)
        ax2.tick_params(axis='y', labelcolor="r")

        filename = TIMESERIES_FILENAME.format(field_name=proc_field_name)

        savefig(join(work_dir, filename), bbox_inches="tight")

        close()


def plot_spatial(work_dir: str, spatial_data: dict, latlon: DataFrame, vis_scatter_factor: float, per_capita: bool):
    """Plot spatial data

    Args:
        work_dir (str): working directory
        spatial_data (dict): spatial data to be plotted
        latlon (DataFrame): lat and lon for different regions
    """

    for field_name in spatial_data:
        proc_spatial_data = spatial_data[field_name]

        for field in proc_spatial_data:

            figure(figsize=(12, 10))
            map_obj = generate_map()

            scatter_objs = []
            scatter_values = []
            for region_name in proc_spatial_data[field]:
                region_lat = latlon.loc[latlon[REGION_KEY.capitalize()]==region_name].to_dict(RECORDS_KEY)[0][LAT_KEY]
                region_lon = latlon.loc[latlon[REGION_KEY.capitalize()]==region_name].to_dict(RECORDS_KEY)[0][LON_KEY]
                x, y = map_obj(region_lon, region_lat)

                for proc_year in proc_spatial_data[field][region_name]:
                    
                    proc_value = proc_spatial_data[field][region_name][proc_year]
                    if per_capita:
                        proc_value *= 100000.0

                    scatter_objs.append(map_obj.scatter(x, y, proc_value**vis_scatter_factor, marker='o', edgecolors=None, color='Red', alpha=0.3))
                    scatter_values.append(proc_value)

            index = [i[0] for i in sorted(enumerate(scatter_values), key=lambda x:x[1])]
            scatter_objs_sorted = [scatter_objs[i] for i in index][::5]
            scatter_values_sorted = [round(scatter_values[i],3) for i in index][::5]

            title_str = f"Crashes, {field}, {proc_year}"
            if per_capita:
                tag = ",Crashes/100,000 person"
                title_str += tag
            else:
                tag = ",Total crashes"
                title_str += tag

            legend(scatter_objs_sorted, scatter_values_sorted, ncol=4, frameon=True, fontsize=12,
                handlelength=2, loc = 8, borderpad = 1.8,
                handletextpad=1, title=tag, scatterpoints = 1)

            title(title_str)
            
            filename = SPATIAL_FILENAME.format(field_name=field_name)
            savefig(join(work_dir, filename), bbox_inches="tight")
            close()

def generate_map() -> dict:
    """Generates basemap object.

    Returns:
        a dict contains the map ionformation
    """

    map_obj = Basemap(
        projection="mill",
        llcrnrlon=MAP_CFG["llcrnrlon"],
        urcrnrlon=MAP_CFG["urcrnrlon"],
        llcrnrlat=MAP_CFG["llcrnrlat"],
        urcrnrlat=MAP_CFG["urcrnrlat"],
        resolution=MAP_CFG["resolution"],
    )


    # x, y = map_obj(lon, lat)

    map_obj.drawcoastlines()

    map_obj.drawmapboundary()

    map_obj.drawrivers()

    return map_obj

    return {"map_obj": map_obj, "x": x, "y": y}
