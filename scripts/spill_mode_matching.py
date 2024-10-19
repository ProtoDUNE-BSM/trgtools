import trgtools
from trgtools.plot import PDFPlotter # type: ignore

import numpy as np # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse

# Constants
spill_duration = 4.8 # seconds
TICK_TO_SEC_SCALE = 16e-9  # seconds per tick

def parse():
    """
    Parses CLI input arguments.
    """
    parser = argparse.ArgumentParser(
        description="Display time distribution of TPs related to beam spill extractions."
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
        "--output", '-o',
        help="Output file to store TP time distribution accounting for beam spill extractions. Default: TP_Spill_time_distribution.pdf.",
        default="spill_trg_records.csv"
    )

    return parser.parse_args()

def spill_mode_matching(spill_file: str, trg_records_file: str) -> pd:
    # Process Arguments & Data
    # args = parse()
    # spill_file = args.spill_filename
    # trg_records_file = args.trg_records_filename

    # Read the data from the files
    spill_df = pd.read_csv(spill_file)
    trig_Records = pd.read_csv(trg_records_file)

    # Extract the start time from the specified column
    time_spill = (spill_df['Clock'])/1000
    
    # Convert the timestamp from DTS to seconds
    trig_Records['Timestamp'] = trig_Records['Timestamp']*TICK_TO_SEC_SCALE
    
    # Assign the spill mode to the TPs
    trig_Records['spill_mode'] = 'OFF' # OFF is the default mode
    for time_ON in time_spill:
        assign_tps_spill_ON(time_ON, trig_Records)
    print("Trigger Records were assigned to spill mode.")

    return trig_Records

# Function to assign TPs the spill ON tag
def assign_tps_spill_ON(time_ON: float, df_trig_record: pd) -> None:
    df_trig_record.loc[(df_trig_record['Timestamp'] >= time_ON) & (df_trig_record['Timestamp'] <= time_ON + spill_duration), 'spill_mode'] = 'ON'

# Main function to plot the TP distribution
if __name__ == "__main__":
    args = parse()
    output_file = args.output
    trig_Records = spill_mode_matching()
    
    # Save DataFrame into a CSV file
    trig_Records.to_csv(output_file, index=False)