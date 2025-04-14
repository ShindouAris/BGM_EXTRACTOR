import os
import argparse
import sys

# --- Configuration ---
OLD_EXTENSION = ".bytes"
NEW_EXTENSION = ".acb"
# -------------------

def rename_files(target_dir, recursive=False, dry_run=False):
    """
    Renames files ending with OLD_EXTENSION to NEW_EXTENSION in the target_dir.

    Args:
        target_dir (str): The directory to search for files.
        recursive (bool): If True, search subdirectories recursively.
        dry_run (bool): If True, only print what would be renamed, don't actually rename.
    """
    rename_count = 0
    error_count = 0

    print(f"--- Starting Renamer ---")
    print(f"Target Directory: {os.path.abspath(target_dir)}")
    print(f"Searching Recursively: {recursive}")
    print(f"Dry Run (No changes will be made): {dry_run}")
    print(f"Renaming files ending with '{OLD_EXTENSION}' to '{NEW_EXTENSION}'")
    print("-" * 25)

    if not os.path.isdir(target_dir):
        print(f"Error: Target directory '{target_dir}' not found or is not a directory.")
        sys.exit(1)

    if recursive:
        # os.walk yields (directory_path, subdirectories, filenames)
        walker = os.walk(target_dir)
    else:

        try:
            items = os.listdir(target_dir)
            files = [f for f in items if os.path.isfile(os.path.join(target_dir, f))]
            walker = [(target_dir, [], files)]
        except OSError as e:
             print(f"Error accessing directory '{target_dir}': {e}")
             sys.exit(1)


    # Process files
    for root_dir, _, filenames in walker:
        for filename in filenames:
            if filename.lower().endswith(OLD_EXTENSION.lower()):
                base_name = filename[:-len(OLD_EXTENSION)] # Remove old extension
                new_filename = base_name
                old_path = os.path.join(root_dir, filename)
                new_path = os.path.join(root_dir, new_filename)

                print(f"Found: '{old_path}'")

                if os.path.exists(new_path):
                    print(f"  [!] Skipping: Target file '{new_path}' already exists.")
                    error_count += 1
                    continue

                action_prefix = "[DRY RUN] Would rename" if dry_run else "Renaming"
                print(f"  -> {action_prefix} to '{new_path}'")

                if not dry_run:
                    try:
                        os.rename(old_path, new_path)
                        rename_count += 1
                    except OSError as e:
                        print(f"  [!] Error renaming '{old_path}': {e}")
                        error_count += 1

    print("-" * 25)
    action_suffix = "(Dry Run)" if dry_run else ""
    print(f"--- Finished {action_suffix} ---")
    if not dry_run:
        print(f"Successfully renamed: {rename_count} file(s).")
    else:
         print(f"Files that would be renamed: {rename_count}") # In dry run, count potential renames
    if error_count > 0:
        print(f"Skipped/Errors: {error_count} file(s).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Rename files ending with {OLD_EXTENSION} to {NEW_EXTENSION}.")

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help=f"The target directory containing the {OLD_EXTENSION} files. Defaults to the current directory."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Search for files recursively in subdirectories."
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show which files would be renamed without actually renaming them."
    )

    args = parser.parse_args()

    rename_files(args.directory, args.recursive, args.dry_run)