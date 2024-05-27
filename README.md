# The Diversity We Breath: Community Diversity and Gas Leak Management

This repository contains the code and final datasets to replicate the empirical analysis in "The Diversity We Breath: Community Diversity and Gas Leak Management".

We encourage researchers to make use of the code and data in this repository, but we kindly ask to please cite the paper in any publication as:

[SUGGESTED CITATION]

## Instructions
To reproduce the **final results**:
- Run scripts in the scripts/analysis directory in alphabetic order. The names of scripts refer to the table/figure they create, which are saved in the results directory.
- For Python scripts, make sure to set you working directory to the root of this repository. All paths are relative to the root and the scripts should run smootly.
- Fort Stata scripts, please change the global variable defined at the begining of each code to the root of the directory in your system before running the scripts. All paths are relative to the root and the scripts should run smootly after this change.

To reproduce **data constuction**:
- Run scrits/create_data/A_directoryStructure.py to create local directory structure.
- Contact corresponding author to obtain raw data, and copy it in data/raw
- Run scripts in scripts/data_processing directory from root directory.
- Note that, to georeference leaks, you will need to provide the path to your Google API in the scripts/create_data/B-geocodeLeaks.py, line 25, where the local variable PATH_TO_KEY is defined. The scrtucture of the file is quite simple, just one line where you replace [API_KEY] for your key: GOOGLE_GEOREF_API_KEY=[API_KEY].

## Software requiremets
The data processing is run entirely on Python. The following packages are required:
- GeoPandas
- Pandas
- BeautifulSoup
- Numpy
- SciPy

The scripts that run the final analysis are run in Python and Stata. For Python, the following packages are required
- GeoPandas
- Pandas

Please do not hessitate to contact should you find any difficulty running the scripts.


Felipe Jordán, 2024 - felipe.jordan@uc.cl
