# File Extension Renamer Script

A Python script to batch rename files within a specified directory (and optionally its subdirectories) by changing their file extension. By default, it renames files ending with `.bytes` to `.acb`.

## Features

*   **Targeted Renaming:** Renames files based on a specific existing extension.
*   **Configurable Extensions:** Easily change the `OLD_EXTENSION` and `NEW_EXTENSION` variables within the script.
*   **Directory Specification:** Choose the target directory for renaming. Defaults to the current directory (`.`).
*   **Recursive Search:** Optionally search through all subdirectories within the target directory.
*   **Dry Run Mode:** Preview which files *would* be renamed without making any actual changes.
*   **Safety Check:** Prevents overwriting by skipping renaming if a file with the new name already exists.
*   **Case-Insensitive Match:** Matches the old extension regardless of case (e.g., `.Bytes`, `.BYTES`, `.bytes` will all be matched if `OLD_EXTENSION` is `.bytes`).
*   **Clear Reporting:** Outputs the actions being taken and provides a summary of renamed files and any errors/skips.

## Prerequisites

*   Python 3.x

## Installation

1.  Save the script code to a file named `rename_files.py` (or any other `.py` name you prefer).
2.  No external libraries need to be installed; the script uses standard Python modules (`os`, `argparse`, `sys`).

## Usage

Run the script from your terminal or command prompt.

**Basic Syntax:**

```bash
python rename_files.py [options] [directory]
```

**Arguments and Options:**

*   `directory` (Optional Positional Argument):
    *   The path to the directory containing the files to rename.
    *   If omitted, the script will run in the current working directory (`.`).
*   `-r`, `--recursive` (Optional Flag):
    *   Search for files recursively within the specified directory and all its subdirectories.
*   `-d`, `--dry-run` (Optional Flag):
    *   Perform a simulation. The script will print which files would be renamed but will not actually modify any files.

**Examples:**

1.  **Rename `.bytes` to `.acb` in the current directory:**
    ```bash
    python bytestoacb.py
    ```

2.  **Rename `.bytes` to `.acb` in a specific directory (`/path/to/your/files`):**
    ```bash
    python bytestoacb.py /path/to/your/files
    ```

3.  **Recursively rename `.bytes` to `.acb` in the current directory and subdirectories:**
    ```bash
    python bytestoacb.py -r
    # or
    python bytestoacb.py --recursive .
    ```

4.  **Perform a dry run (show what would happen) in a specific directory:**
    ```bash
    python bytestoacb.py -d /path/to/your/files
    # or
    python bytestoacb.py --dry-run /path/to/your/files
    ```

5.  **Perform a recursive dry run starting from the current directory:**
    ```bash
    python bytestoacb.py -r -d
    # or
    python bytestoacb.py --recursive --dry-run
    ```

## Configuration

The script is pre-configured to rename files from `.bytes` to `.acb`. You can easily change this by editing the following lines near the top of the `rename_files.py` script:

```python
# --- Configuration ---
OLD_EXTENSION = ".bytes"  # Change this to the extension you want to rename FROM
NEW_EXTENSION = ".acb"    # Change this to the extension you want to rename TO
# -------------------
```

**Important:** Remember to include the leading dot (`.`) in the extension names.

## Example Output

**Dry Run Example:**

```
--- Starting Renamer ---
Target Directory: /home/user/my_data
Searching Recursively: False
Dry Run (No changes will be made): True
Renaming files ending with '.bytes' to '.acb'
-------------------------
Found: '/home/user/my_data/file1.bytes'
  -> [DRY RUN] Would rename to '/home/user/my_data/file1.acb'
Found: '/home/user/my_data/file2.BYTES'
  -> [DRY RUN] Would rename to '/home/user/my_data/file2.acb'
Found: '/home/user/my_data/important.bytes'
  [!] Skipping: Target file '/home/user/my_data/important.acb' already exists.
-------------------------
--- Finished (Dry Run) ---
Files that would be renamed: 2
Skipped/Errors: 1 file(s).
```

**Actual Run Example:**

```
--- Starting Renamer ---
Target Directory: /home/user/my_data
Searching Recursively: True
Dry Run (No changes will be made): False
Renaming files ending with '.bytes' to '.acb'
-------------------------
Found: '/home/user/my_data/file1.bytes'
  -> Renaming to '/home/user/my_data/file1.acb'
Found: '/home/user/my_data/subdir/another.bytes'
  -> Renaming to '/home/user/my_data/subdir/another.acb'
Found: '/home/user/my_data/important.bytes'
  [!] Skipping: Target file '/home/user/my_data/important.acb' already exists.
-------------------------
--- Finished ---
Successfully renamed: 2 file(s).
Skipped/Errors: 1 file(s).
```

## Error Handling

*   The script will exit with an error message if the specified `target_dir` does not exist or is not accessible.
*   If a file with the `NEW_EXTENSION` already exists, the script will skip renaming the corresponding `OLD_EXTENSION` file and print a warning message.
*   Any OS-level errors encountered during the actual `os.rename` operation will be caught and reported, incrementing the error count.
