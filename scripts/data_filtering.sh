#!/bin/bash

# Author: Hamza Amar Es-sghir
# Institution: IFIC-Valencia
# Date: 2024-10-16
# Description: This script processes raw HDF5 files listed in a given text file and extracts trigger records of type 8, kSupernova. This to remove ground shake events from the data.
#              The output is saved in a CSV file with the following columns: Run, Subrun, Trigger_Record, Timestamp.

# Function to find the next available output file name
find_next_available_filename() {
  local base_name=$1
  local counter=1
  local output_file="${base_name}.csv"

  while [ -f "$output_file" ]; do
    output_file="${base_name}${counter}.csv"
    ((counter++))
  done

  echo "$output_file"
}

# Function to process a single file
process_file() {
  local file_path="$1"
  local output_file="$2"
  # Extract run and subrun numbers from the file name
  local run_number=$(echo "$file_path" | grep -oP 'run\K\d+' | head -n 1)
  local subrun_number=$(echo "$file_path" | grep -oP '_\K\d+(?=_dataflow)')

  # Process the file and filter for trigger_type: 8, then extract the trigger record ID and timestamp
  HDF5LIBS_TestDumpRecord "$file_path" | grep "trigger_type: 8" | awk -F', ' '{
    for(i=1; i<=NF; i++) {
      if ($i ~ /trigger_number:/) {
        split($i, arr, ": ");
        trigger_id = arr[2];
      } else if ($i ~ /trigger_timestamp:/) {
        split($i, arr, ": ");
        timestamp = arr[2];
      }
    }
    print trigger_id, timestamp
  }' | while read -r trigger_id timestamp; do
    echo "$run_number,$subrun_number,$trigger_id,$timestamp" >> "$output_file"
  done
}

# Initialize variables
output_file=""
target_path=""

# Function to display help
show_help() {
    echo "Usage: $0 -p <path_to_text_file> [-o output_file]"
    echo "  -p  Specify the path to a text file containing paths to raw HDF5 files."
    echo "  -o  Specify the output CSV file name (Optional). If not provided, a default name is generated."
    echo "  -h  Display this help message."
}

# Parse command-line options
while getopts ":hp:o:" opt; do
    case ${opt} in
        h )
            show_help
            exit 0
            ;;
        p )
            target_path=$OPTARG
            ;;
        o )
            output_file=$OPTARG
            ;;
        \? )
            echo "Invalid option: $OPTARG" 1>&2
            show_help
            exit 1
            ;;
        : )
            echo "Invalid option: $OPTARG requires an argument" 1>&2
            show_help
            exit 1
            ;;
    esac
done
shift $((OPTIND -1))

# Check if target path is provided
if [ -z "$target_path" ]; then
    echo "Target path is mandatory."
    show_help
    exit 1
fi

# If output file is not provided, generate a default name
if [ -z "$output_file" ]; then
    output_file=$(find_next_available_filename 'output')
fi

# Check if the output file already exists, if not, add the header
if [ ! -f "$output_file" ]; then
    echo "Run,Subrun,Trigger_Record,Timestamp" > "$output_file"
fi

# Check if the specified path is a valid file
if [ -f "$target_path" ]; then
    # Read each line in the file as a path to a raw HDF5 file
    while IFS= read -r file_path; do
        if [ -f "$file_path" ]; then
            process_file "$file_path" "$output_file"
        else
            echo "Warning: File '$file_path' not found."
        fi
    done < "$target_path"
else
    echo "The specified path does not exist or is not a valid file."
    exit 1
fi