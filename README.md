# CAS_analysis
This is a reporsitory analyzing the [open data crash statistics](https://opendata-nzta.opendata.arcgis.com/datasets/crash-analysis-system-cas-data-1/explore?location=-20.304565%2C0.000000%2C2.92) from NZTA. The system is created mainly using **_python_**, while some visualizations are presented with **_html_** and **_javascript_**.

There are mainly four components in this reporsitory:
- `cli/cli_preproc.py`: downloading and decoding the dataset, and doing the quality control if it is needed. (Note that for this version, only `csv` can be accepted as the input data format)

- `cli/cli_temporal_analysis.py`: conducting temporal analysis for dataset, e.g.,
    - national wide crash changes over years
    - regional crash changes over years
    - the changes of cross-correlations between crash and other factors (e.g., weather) over years

- `cli/cli_spatial_analysis.py`: conducting spatial analysis for dataset, e.g.,
    - display the map for crashes or crashes per capita

- `cli/cli_feature_analysis.py`: conducting feature analysis for dataset, e.g.,
    - ranking the factors that may contribute to the crashes
    - post event analysis

# How to install the package
The package is managed by _conda_(and _mamba_), and can be installed using the provided `makefile`:

### Install through conda
```
make build_conda_env_from_scratch
```

### Create a docker image
If we need to create a docker image for the system, we can run:
```
make install
```

# How to use the package
### Prepare input data for cas analysis 
```
cli_preproc --workdir <WORK DIR> --input_fmt <INPUT DATA FORMAT>
```

- `<WORK DIR>`: working directory (e.g., where to save the cas analysis input)
- `<INPUT DATA FORMAT>`: input data format (e.g., by default it is _csv_)

### Temporal analysis 
```
cli_temporal_analysis --workdir <WORK DIR> --data_src <CAS DATA PATH> --config_file <CONFIG FILE PATH>
```

- `<WORK DIR>`: working directory (e.g., where to save the temporal analysis output)
- `<CAS DATA PATH>`: where to get the CAS dataset (prepared by `cli_preproc`)
- `<INPUT DATA FORMAT>`: input data format (e.g., by default it is _csv_)

### Feature analysis 
```
cli_feature_analysis --workdir <WORK DIR> --data_src <CAS DATA PATH> --config_file <CONFIG FILE PATH>
```

- `<WORK DIR>`: working directory (e.g., where to save the temporal analysis output)
- `<CAS DATA PATH>`: where to get the CAS dataset (prepared by `cli_preproc`)
- `<INPUT DATA FORMAT>`: input data format (e.g., by default it is _csv_)

# Contact
**Note that this package is not peer reviewed yet, please contact Sijin at zsjzyhzp@gmail.com for any questions**


