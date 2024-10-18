#!/bin/bash

# Author: Hamza Amar Es-sghir
# Institution: IFIC-Valencia
# Date: 2024-10-16
# Description: This script sorts ProtoDUNE HD raw data files based on the run number provided by the user.
#              It allows specifying an output file name and provides a help message for usage guidance.

# Function to display help
show_help() {
    echo "Usage: $0 -r <run_number> [-o <output_file>] [-h]"
    echo "  -r, --run       Specify the run number for the raw data file."
    echo "  -o, --output    Specify the output file name (default is sorted_run<run_number>)."
    echo "  -h, --help      Display this help message and exit."
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) show_help; exit 0 ;;
        -r|--run) run_number="$2"; shift ;;
        -o|--output) output_file="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; show_help; exit 1 ;;
    esac
    shift
done

# Validate run number
if [ -z "$run_number" ]; then
    echo "Error: Run number is required."
    show_help
    exit 1
fi

# Default output file name if not provided
if [ -z "$output_file" ]; then
    output_file="sorted_run${run_number}"
fi

# Find all files matching the run number and dump into a temporary file
temp_file=$(mktemp)
find /eos/experiment/neutplatform/protodune/dune/hd-protodune/ -type f -name "np04hd_raw_run${run_number}_*" > "$temp_file"

# Sort files considering both the run number and the dataflow number, then write to the output file
awk -F'[_/.]' '{print $(NF-1), $0}' "$input_file" | sort -k1,1n | cut -d' ' -f2- > "$output_file"

# Clean up
rm "$temp_file"

echo "Sorted files have been written to $output_file."