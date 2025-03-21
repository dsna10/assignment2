#!/usr/bin/env python3

import sys
import os
import subprocess
import argparse

'''
OPS445 Assignment 2 - Winter 2025
Program: duim.py 
Author: "dsna10"
The python code in this file (duim.py) is original work written by
"dsna10". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or online resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script mimics the functionality of `du`, displaying disk usage
with a bar graph representing space usage in a directory.

Date: 3/21/2025
'''

def parse_command_args():
    """Set up argparse to parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 2022"
    )
    parser.add_argument(
        "-l", "--length", type=int, default=20,
        help="Specify the length of the graph. Default is 20."
    )
    parser.add_argument(
        "-H", "--human-readable", action="store_true",
        help="Print sizes in human readable format (e.g., 1K 23M 2G)."
    )
    parser.add_argument(
        "target", nargs="?", default=os.getcwd(),
        help="The directory to scan. Default is the current directory."
    )

    return parser.parse_args()

def percent_to_graph(percent, total_chars):
    """Returns a string representing a bar graph of percentage."""
    if not (0 <= percent <= 100):
        raise ValueError("Percent must be between 0 and 100")

    filled_chars = round((percent / 100) * total_chars)
    return "=" * filled_chars + " " * (total_chars - filled_chars)

def call_du_sub(location):
    """Runs `du -d 1 <location>` and returns the output as a list of strings."""
    try:
        process = subprocess.Popen(
            ["du", "-d", "1", location],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        # Filter out permission errors and warnings
        error_lines = stderr.strip().split("\n")
        filtered_errors = [line for line in error_lines if "Permission denied" not in line]

        # Print only important errors, ignore permission issues
        if filtered_errors:
            print("\n".join(filtered_errors), file=sys.stderr)

        return stdout.strip().split("\n")
    
    except FileNotFoundError:
        print("Error: `du` command not found. Ensure it's installed on your system.", file=sys.stderr)
        sys.exit(1)

def create_dir_dict(alist):
    """Converts a list of du output lines into a dictionary {dir: size}."""
    dir_dict = {}
    for line in alist:
        parts = line.split("\t")  # `du` output is tab-separated
        if len(parts) == 2:
            size, directory = parts
            dir_dict[directory] = int(size)
    return dir_dict

# 🔴 **THIS IS WHERE YOU PASTE THE MAIN PROGRAM LOGIC** 🔴
if __name__ == "__main__":
    # Step 1: Parse Arguments
    args = parse_command_args()

    # Step 2: Ensure the target directory exists
    if not os.path.isdir(args.target):
        print(f"Error: '{args.target}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Step 3: Call `du` and get disk usage info
    du_output = call_du_sub(args.target)
    dir_dict = create_dir_dict(du_output)

    # Step 4: Calculate total size of the target directory
    total_size = dir_dict.get(args.target, sum(dir_dict.values()))

    # Step 5: Generate Output
    print("\nDisk Usage Report:")
    for directory, size in sorted(dir_dict.items(), key=lambda x: x[1], reverse=True):
        percent = (size / total_size) * 100 if total_size > 0 else 0
        bar = percent_to_graph(percent, args.length)

        # Convert size to human-readable format if -H flag is used
        size_str = f"{size} B"
        if args.human_readable:
            for unit in ["B", "K", "M", "G", "T"]:
                if size < 1024:
                    break
                size /= 1024
            size_str = f"{size:.1f} {unit}"

        print(f"{percent:5.1f}% [{bar}] {size_str}  {directory}")

    # Convert total size to human-readable format if -H flag is used
    total_size_str = f"{total_size} B"
    if args.human_readable:
        total_size_float = float(total_size)
        for unit in ["B", "K", "M", "G", "T"]:
            if total_size_float < 1024:
                break
            total_size_float /= 1024
        total_size_str = f"{total_size_float:.1f} {unit}"

    print(f"\nTotal: {total_size_str}  {args.target}")

