#!/usr/bin/env python

"""
Author: Hamza Amar Es-sghir
Institution: IFIC-Valencia
Date: 2024-10-17
Description: This script provides an event display for readout windows for TPs at the collection plane (except APA1) when beam spill mode is ON. 
             It includes functionalities for plotting start time vs channel for each APA, finding and saving output names, reading file paths, and extracting run and subrun numbers. 
             It supports both single file and file list inputs, with optional verbosity and overwrite capabilities.
"""

import trgtools
from trgtools.plot import PDFPlotter

import numpy as np
import matplotlib.colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import os
import re
import argparse
import spill_mode_matching as spill

# Constants
TICK_TO_SEC_SCALE = 16e-9  # s per tick

def find_save_name(run_id: int, subrun_id: int, trg_record_id: int, overwrite: bool) -> str:
    """
    Find a new save name or overwrite an existing one.

    Parameters:
        run_id (int): The run number for the read file.
        subrun_id (int): The subrun of the read file.
        trg_record_id (int): The trigger record ID.
        overwrite (bool): Overwrite the 0th plot directory of the same naming.

    Returns:
        (str): Save name to write as.

    This is missing the file extension. It's the job of the save/write command
    to append the extension.
    """
    # Try to find a new name.
    save_name = f"Run{run_id}-Subrun{subrun_id:04}-TriggerRecord{trg_record_id}"

    # Outputs will always create a PDF, so use that as the comparison.
    while not overwrite and os.path.exists(save_name + ".pdf"):
        save_name = f"Run{run_id}-Subrun{subrun_id:04}-TriggerRecord{trg_record_id}-zoom"
    print(f"Saving outputs to ./{save_name}.*")

    return save_name

def plot_pdf_start_time_vs_channel_per_apa(tp_data: np.ndarray, pdf: PdfPages) -> None:
    """
    Plot the start time vs channel for each APA.
    
    Parameters:
        tp_data (np.ndarray): Array of TP data.
        pdf (PdfPages): PDF file to save the plots.
        
    Returns:
        None
    """
    # Define APA limits
    apa_limits = [
        (800, 1600),   # APA 1
        (7200, 7680),  # APA 2
        (4160, 4640),  # APA 3
        (9280, 9760)   # APA 4
    ]
    
    for start, end in apa_limits:
        # Filter data for the current APA
        mask = (tp_data['channel'] >= start) & (tp_data['channel'] <= end)
        filtered_data = tp_data[mask]

        # Check if filtered_data is empty
        if filtered_data.size == 0:
            print(f"No data for APA range {start}-{end}. Skipping plot.")
            continue

        plt.figure(figsize=(6, 4), dpi=200)
        times = filtered_data['time_start'] - np.min(filtered_data['time_start'])
        channel = filtered_data['channel']
        plt.scatter(channel, times, c=filtered_data['adc_integral'], s=2, norm=matplotlib.colors.LogNorm())
        plt.colorbar(ax=plt.gca(), cmap='viridis', label='ADC integral', format='%d')  # format='%.0e' for scientific notation

        plt.title(f"TP Start Time vs Channel for APA {apa_limits.index((start, end)) + 1}")
        plt.xlabel("Channel")
        plt.ylabel("Relative Start Time (ticks)")
        plt.xlim(start, end)
        # plt.ylim(0, 80000)  # Uncomment if a fixed y-axis range is desired

        plt.tight_layout()
        pdf.savefig()
        plt.close()


def read_file_paths(filelist_path: str) -> list:
    """
    Reads file paths from a given file.

    Parameters:
        filelist_path (str): Path to the file containing the list of file paths.

    Returns:
        (list): List of file paths.
    """
    with open(filelist_path, 'r') as file:
        paths = file.read().splitlines()
    return paths

def extract_run_subrun(file_path):
    """
    Extracts the run and subrun numbers from the file path.

    Parameters:
        file_path (str): The path to the file.
    
    Returns:
        (str, str): Run number, Subrun number
    """
    match = re.search(r"run(\d{6})_(\d{4})", file_path)
    if match:
        return match.group(1), match.group(2)  # Run number, Subrun number
    return None, None

def select_file_paths(filelist, desired_run, desired_subrun):
    """
    Selects file paths from a file list based on the desired run and subrun numbers.
    
    Parameters:
        filelist (list): list containing the file paths.
        desired_run (str): Desired run number.
        desired_subrun (str): Desired subrun number.
    
    Returns:
        (list): List of file paths.
    """
    filtered_paths = []
    for file_path in filelist:
        try:
            run, subrun = extract_run_subrun(file_path)
            # Ensure run and subrun are strings for comparison
            run, subrun = int(run), int(subrun)
            if run == desired_run and subrun == desired_subrun:
                filtered_paths.append(file_path)
        except Exception as e:
            # Handle or log the error as appropriate
            print(f"Error extracting run and subrun from {file_path}: {e}")
    return filtered_paths

def parse():
    """
    Parse command line arguments.
    
    Returns:
        (argparse.Namespace): Arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description="Display TP events recorded by each collection plane for a given raw file."
    )
    parser.add_argument(
        "--filename",
        help="Absolute path to raw file to display."
    )
    parser.add_argument(
        "--filelist",
        help="Absolute path to a file containing a list of raw files to display."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        help="Increment the verbose level (errors, warnings, all)."
        "Default: 0.",
        default=0
    )
    parser.add_argument(
        "--spill_filename",
        help="Absolute path to the csv file with time spill information."
    )
    parser.add_argument(
        "--trg_records_filename",
        help="Absolute path to the csv file with trigger records information."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite old outputs. Default: False."
    )

    args = parser.parse_args()

    # Check for mutual exclusivity and at least one option provided
    if args.filename and args.filelist:
        parser.error("The --filename and --filelist options are mutually exclusive. Please specify only one.")
    elif not args.filename and not args.filelist:
        parser.error("Please specify at least one option: --filename or --filelist.")

    return args

def main():
    """
    Drives the processing and plotting.
    """
    # Process Arguments & Data
    args = parse()
    filename = args.filename
    filelist = args.filelist
    spill_file = args.spill_filename
    trg_records_file = args.trg_records_filename
    verbosity = args.verbose
    overwrite = args.overwrite

    # Read the file paths from the file list
    if filelist:
        file_paths = read_file_paths(filelist)
    else:
        file_paths = [filename]
    # Process the spill mode matching to get values when spill mode is ON
    df_trg_records = spill.spill_mode_matching(spill_file, trg_records_file)
    df_spillON = df_trg_records[df_trg_records['spill_mode'] == 'ON']
    runs = df_spillON['Run'].unique()

    for run in runs:
        subruns = df_spillON[df_spillON['Run'] == run]['Subrun'].unique()
        for subrun in subruns:
            print(f"Processing Run {run}, Subrun {subrun}")
            trg_records = df_spillON[(df_spillON['Run'] == run) & (df_spillON['Subrun'] == subrun)]['Trigger_Record'].unique()
            # Filter and read the data from the filtered file list. This will contain files with different dataflow numbering
            for file_path in select_file_paths(file_paths, run, subrun):
                print(f"File: {file_path}")

                # Determine if we are dealing with even or odd trigger records based on the file path. This must be modified in case of further dataflows
                if "dataflow0" in file_path:
                    filtered_trg_records = [trgID for trgID in trg_records if trgID % 2 == 0]  # Even trigger records: dataflow0
                else:
                    filtered_trg_records = [trgID for trgID in trg_records if trgID % 2 != 0]  # Odd trigger records: dataflow1
                
                for trg_record in filtered_trg_records:
                    print(f"Processing Trigger Record {trg_record}")
                    data = trgtools.TPReader(file_path, trg_record, verbosity)
                    # Load all TP fragments for the corresponding Trigger Record
                    data.read_all_fragments()
                    # Find a new save name or overwrite an old one.
                    save_name = find_save_name(data.run_id, data.file_index, trg_record, overwrite)
                    # Enforcing output for a useful metric
                    print(f"Number of TPs: {data.tp_data.shape[0]}")
                    # Plotting
                    pdf_plotter = PDFPlotter(save_name)
                    pdf = pdf_plotter.get_pdf()
                    # === Start Time vs Channel ===
                    plot_pdf_start_time_vs_channel_per_apa(data.tp_data, pdf)
                    # ========================================
    return None

if __name__ == "__main__":
    main()
