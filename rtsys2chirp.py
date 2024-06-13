#!/usr/bin/env python3

"""
This requires python 3.10 or later as I figured I'd try a map/case in lieu of if/elif.
This will convert an exported csv file from rt systems radio programming software to a format 
that can be ingested by chirp.
"""

import csv
import argparse


# Define the column mapping from rtsystems to chirp
column_mapping = {
    "Name": "Name",
    "Receive Frequency": "Frequency",
    "Offset Frequency": "Offset",
    "Offset Direction": "Duplex",
    "Tone Mode": "Tone",
    "Operating Mode": "Mode",
    "Step": "TStep",
    "Skip": "Skip",
    "TX Power": "Power",
    "Comment": "Comment",
}

# some mapping for valid values from rt->chirp
mode_mapping = {
    "WFM": "WFM",
    "FM": "FM",
    "FM Narrow": "NFM",
    "AM": "AM",
    "NAM": "NAM",
    "DN": "DIG",
    "USB": "USB",
    "LSB": "LSB",
    "CW": "CW",
    "RTTY": "RTTY",
    "DIG": "DIG",
    "PKT": "PKT",
}

duplex_mapping = {"Simplex": "off", "Minus": "-", "Plus": "+"}

tone_mapping = {
    "Tone": "Tone",
    "T Sql": "TSQL",
    "DCS": "DTCS",
    "Rev CTCSS": "DTCS-R",
}

skip_mapping = {"Skip": "S", "Scan": "P", "P Scan": "P"}

# Additional fields that need to be manually handled
additional_fields = ["rToneFreq", "cToneFreq", "DtcsCode", "RxDtcsCode"]


def convert_csv(input_file, output_file):
    # Read the input CSV file in rtsystems format
    with open(input_file, mode="r") as infile:
        # Read the header row explicitly
        header = infile.readline().strip().split(",")

        # Create DictReader with explicit fieldnames
        reader = csv.DictReader(infile, fieldnames=header)
        fieldnames = reader.fieldnames

        # Prepare the fieldnames for the chirp output
        chirp_fieldnames = (
            ["Location"]
            + [
                column_mapping[field]
                for field in fieldnames[1:]
                if field in column_mapping
            ]
            + additional_fields
        )
        # Write to the output CSV file in chirp format
        with open(output_file, mode="w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=chirp_fieldnames)
            writer.writeheader()

            for idx, row in enumerate(reader, start=1):
                # skip empty rows, but increment the index.
                if not row["Receive Frequency"]:
                    continue
                chirp_row = {
                    "Location": idx
                }  # Set the location field to the row number
                for field, value in row.items():
                    match field:
                        case "Operating Mode":
                            chirp_row["Mode"] = mode_mapping.get(value, "")
                        case "Offset Direction":
                            chirp_row["Duplex"] = duplex_mapping.get(value, "")
                        case "Tone Mode":
                            chirp_row["Tone"] = tone_mapping.get(value, "")
                        case "Skip":
                            chirp_row["Skip"] = skip_mapping.get(value, "")
                        # convert step to float
                        case "Step":
                            step_str = value
                            step_str = step_str.replace("kHz", "").strip()
                            chirp_row["TStep"] = float(step_str)
                        case "Comment":
                            match value:
                                case "":
                                    chirp_row[field] = row.get("Name")
                                case _:
                                    chirp_row[column_mapping[field]] = value
                        case _:
                            if field in column_mapping:
                                chirp_row[column_mapping[field]] = value
                # Handle CTCSS separately
                chirp_row["rToneFreq"] = row.get("CTCSS", "")
                chirp_row["cToneFreq"] = row.get("CTCSS", "")

                # Handle DCS separately
                chirp_row["DtcsCode"] = row.get("DCS", "")
                chirp_row["RxDtcsCode"] = row.get("DCS", "")
                writer.writerow(chirp_row)

    print("Conversion from rtsystems to chirp format completed successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Convert rtsystems CSV format to chirp CSV format."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Input CSV file in rtsystems format",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        help="Output CSV file in chirp format",
    )

    args = parser.parse_args()
    convert_csv(args.input, args.output)


if __name__ == "__main__":
    main()
