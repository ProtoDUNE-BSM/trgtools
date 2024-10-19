# TP Event Display Tools for ProtoDUNE-BSM

This document provides an overview and usage guide for a set of tools developed for data processing and event display within the DAQ framework. These tools, located in `sourcecode/trgtools/scripts`, include `find_run.sh`, `data_filtering.sh`, and `event_display_trigger_records.py`, with the latter depending on `spill_mode_matching.py` for its operation.

## Set up the np-04 development area in `lxplus` virtual machine

To get event display tools working while accessing directly to raw data files stored in the eos (`/eos/experiment/neutplatform/protodune/dune/hd-protodune/`), you need to set up the `np04` development area in the `lxplus` virtual machine. The following bash script will guide you through the process:

```bash
#!/bin/bash

# Set the development area name
DIRECTORY=ProtoDUNE-BSM
# Set up the dunedaq environment
source /cvmfs/dunedaq.opensciencegrid.org/setup_dunedaq.sh
# Set up the dbt with the latest version
setup_dbt latest
# Create the development area
dbt-create -n last_fddaq ${DIRECTORY}
# Move to the development area
cd ${DIRECTORY}
# Source the environment
source env.sh
```

Once you have set up the `np04` development area, one must clone the `trgtools` repository. To do so, access the `sourcecode` directory and clone the repository:

```bash
git clone https://github.com/ProtoDUNE-BSM/trgtools.git
```

Bear in mind using `pip install -r requirements.txt` in `trgtools` directory to install all Python packages necessary to run the `event_display_trigger_records.py` script. 

Once completed the cloning process, one can proceed to build the `trgtools` repository. Just execute the command `dbt-build`. If the build process is successful, it is time to create a work directoy within the `build` directory. This directory will be used to run the following tools.

## find_run.sh

`find_run.sh` is a shell script that facilitates the search and listing of runs based on specific criteria. It is particularly useful for identifying runs that match certain parameters or conditions, streamlining the process of data selection for analysis.

The output text file will contain the sorted raw data files according to the subrun number. For dataflows that sort is not needed.

It is worth mentioning that the script is designed to work with raw data files from ProtoDUNE-HD runs.

---

To use `find_run.sh`, navigate to the directory containing the script and execute it with desired options:

```bash
./find_run.sh -r <run_number> [-o <output_file>]
```

Options include `-r` for specifying the run number and `-o` for defining the output file name where the sorted runs will be saved.

## data_filtering.sh

`data_filtering.sh` is a script designed to process raw data files, applying filters and extracting relevant information for further analysis. It plays a crucial role in preparing the data for visualization and detailed study for SPS beam spill time coincidence.

---

Execute the script from the command line, providing the path to the input file and the desired output file name with CSV extension to be later used by `event_display_trigger_records.py` as a DataFrame object:

```bash
./data_filtering.sh -p <path_to_text_file> [-o output_file]
```

The CSV output file will contain the following columns: `Run,Subrun,Trigger_Record,Timestamp`.

## event_display_trigger_records.py

`event_display_trigger_records.py` is a Python script used for generating visual representations of readout windows for TPs (Trigger Primitives) at the collection plane when the beam spill mode is ON. It relies on `spill_mode_matching.py` to match spill modes (ON/OFF) taken by the user from the [Fermilab IF Beam Data Server](#get-beam-spill-timestamps-from-the-fermilab-if-beam-data-server), in CSV format, and filter data accordingly.

---

Before running `event_display_trigger_records.py`, ensure that `spill_mode_matching.py` is accessible in your environment as it is a dependency for data filtering based on spill mode.

To run `event_display_trigger_records.py`, use the following command:

```bash
python event_display_trigger_records.py --filelist <input_file_list> -o <output_file> --spill_filename <spill_mode_file> --trg_records_filename <trg_records_file> [options]
```

This macro is ready to process a list of raw data files, in txt format, that were already filtered by `data_filtering.sh` with the proper spill timestamps, both in CSV format.

Options include parameters for specifying a single input file, verbosity levels, and whether to overwrite existing output files. Consult the script for additional details on available options.

The output is a set of pdf files showing the TP readout windows for each event in the filtered data, with the spill mode ON.

---

**Caveat**: The output directory would be the same as the one where running the script. The user could change the output directory by modifying the script.

## spill_mode_matching.py

`spill_mode_matching.py` is a utility script used by `event_display_trigger_records.py` to filter data based on the spill mode. It identifies trigger record timestamps when the beam spill mode is ON and selects the corresponding data for visualization.

---

This script is typically not run independently but is invoked by `event_display_trigger_records.py`. Ensure that it is located in the same directory or in the Python path to be successfully imported.

---

These tools collectively support the processing, analysis, and visualization of TP data within the ProtoDUNE-BSM project, facilitating a deeper understanding of the experimental results.

## Get beam spill timestamps from the Fermilab IF Beam Data Server

To get the beam spill timestamps, access the [Fermilab IF Beam Data Server](https://dbweb8.fnal.gov:8443/ifbeam/app/Browser/?) and select the following parameters:

1. **Event**: z,pdune
2. **Name**: dip/acc/SPS/Timing/Cycle/StartExtractionEvent:cycleStamp[]
3. **From**: YYYY-MM-DDTHH:MM:SS+00:00
4. **To**: YYYY-MM-DDTHH:MM:SS+00:00
5. **Format**: CSV
6. **Show times in time time zone**: UTC

When cliking on the *Show device* button, the server will display the beam spill timestamps in CSV format. Save the file and use it as input for the `spill_mode_matching.py` script. The column of interest is `Clock`, which containts timestamps for the beginning of spill extractions in milliseconds (ms).

---

**Caveat**: There is one defect in the output CSV file. The user must add this column header to the file: `Event,Variable,Clock,Units,Value1,Value2`. This is necessary for the `spill_mode_matching.py` script to work properly.

**Caveat**: The beam spill timestamps are in UTC time zone. Beam data has timestamps related to that time region. However, if one wants to compare with an event from DQM tools during a shift, keep in mind that the timestamps are in CERN local time, +02:00.
