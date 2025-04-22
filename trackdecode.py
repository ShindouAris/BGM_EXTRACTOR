import os
import subprocess
import argparse
import sys
import tempfile
import shutil
import shlex

# --- Default Configuration ---
DEFAULT_VGMSTREAM_EXE = r".\vgmstream-win64\vgmstream-cli.exe"
DEFAULT_LAME_EXE = r".\Lame\lame.exe"
DEFAULT_LAME_QUALITY = "-V 2"
ACB_EXTENSION = ".acb"
PREFIXES_TO_REMOVE = ["vs_", "af_", "an_", "in_", "se_", "cl_", "collabo_es_"]
# ---------------------------

def find_executable(name, specified_path=None):
    """Finds an executable, checking specified path, PATH, and current dir."""
    if specified_path:
        if os.path.isfile(specified_path):
            return os.path.abspath(specified_path)
        else:
            print(f"Warning: Specified executable path not found: {specified_path}")

    found_path = shutil.which(name)
    if found_path:
        return os.path.abspath(found_path)

    # Check current directory explicitly as fallback
    local_path = os.path.abspath(os.path.join('.', name))
    if os.path.isfile(local_path):
        return local_path

    return None # Not found

def process_acb_file(acb_path, final_output_dir, vgmstream_exe, lame_exe, lame_opts_list, keep_wav=False, dry_run=False):
    """
    Converts a single ACB file to MP3 tracks. Conditionally appends track number
    and removes known prefixes (e.g., 'vs_', 'an_') from output filename if present.

    Args:
        acb_path (str): Full path to the input .acb file.
        final_output_dir (str): The specific directory where the output MP3s for THIS acb should go.
        vgmstream_exe (str): Path to vgmstream-cli.exe.
        lame_exe (str): Path to lame.exe.
        lame_opts_list (list): List of arguments for LAME quality settings.
        keep_wav (bool): If True, keeps intermediate WAV files.
        dry_run (bool): If True, only print commands, don't execute.

    Returns:
        bool: True if successful (or dry run), False otherwise.
    """
    print(f"---\nProcessing: {acb_path}")
    acb_filename = os.path.basename(acb_path)
    acb_basename, _ = os.path.splitext(acb_filename)

    output_dir = final_output_dir
    print(f"Output Dir: {output_dir}")
    try:
        # Ensure the specific output directory exists
        if not dry_run:
            os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"  [!] Error creating output directory '{output_dir}': {e}")
        return False

    temp_wav_dir = None
    success = True
    wav_files_to_process = []

    try:
        temp_wav_dir = tempfile.mkdtemp(prefix=f"{acb_basename}_wav_")
        print(f"  Temp WAV Dir: {temp_wav_dir}")

        wav_output_pattern = os.path.join(temp_wav_dir, f"{acb_basename}_%s.wav")
        vgmstream_command = [vgmstream_exe, "-o", wav_output_pattern, acb_path]

        print(f"  Running VGMStream: {' '.join(shlex.quote(str(p)) for p in vgmstream_command)}")
        if not dry_run:
            try:
                result_vgm = subprocess.run(vgmstream_command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
                print(f"  VGMStream Output:\n{result_vgm.stdout}")
                if result_vgm.stderr:
                    print(f"  VGMStream Error Output:\n{result_vgm.stderr}")
                wav_files_to_process = [f for f in os.listdir(temp_wav_dir) if f.lower().endswith(".wav")]
            except FileNotFoundError:
                print(f"  [!] Error: vgmstream-cli not found at '{vgmstream_exe}'.")
                success = False
            except subprocess.CalledProcessError as e:
                print(f"  [!] Error running vgmstream-cli (Return Code: {e.returncode}):")
                print(f"  Command: {' '.join(shlex.quote(str(p)) for p in e.cmd)}")
                print(f"  VGMStream Stdout:\n{e.stdout}")
                print(f"  VGMStream Stderr:\n{e.stderr}")
                success = False
            except Exception as e:
                print(f"  [!] Unexpected error during vgmstream execution: {e}")
                success = False
        else: # Dry Run simulation
            print(f"  (Dry Run) Simulating vgmstream outputting WAV files like '{os.path.basename(wav_output_pattern).replace('%s','N')}'")
            test_basename = acb_basename
            # Simulate multi-track if name contains '_multi_' OR if length is even (simple test pattern)
            if "_multi_" in test_basename or len(test_basename.split('_')[0]) % 2 != 0 : # Adjust simulation logic slightly
                wav_files_to_process = [f"{test_basename}_0.wav", f"{test_basename}_1.wav"]
                print("  (Dry Run) Simulating MULTIPLE tracks found.")
            else:
                wav_files_to_process = [f"{test_basename}_0.wav"]
                print("  (Dry Run) Simulating SINGLE track found.")

        if not success and not dry_run:
            return False

        # --- Step 2: Convert generated WAV files to MP3 using LAME ---
        print(f"  Found {len(wav_files_to_process)} WAV file(s) to process.")

        if not wav_files_to_process:
            print(f"  [!] No WAV files found after vgmstream process for {acb_filename}. Skipping LAME.")
            if not dry_run: success = False

        is_single_track = (len(wav_files_to_process) == 1)

        for wav_filename in wav_files_to_process:
            temp_wav_path = os.path.join(temp_wav_dir, wav_filename)

            # Decide the initial MP3 base name
            if is_single_track:
                mp3_base_to_modify = acb_basename
                print(f"    (Single track detected, using original name: {mp3_base_to_modify})")
            else:
                wav_basename, _ = os.path.splitext(wav_filename)
                mp3_base_to_modify = wav_basename
                print(f"    (Multi-track detected, using numbered name: {mp3_base_to_modify})")

            final_mp3_basename = mp3_base_to_modify
            prefix_removed = False
            for prefix in PREFIXES_TO_REMOVE:
                if final_mp3_basename.lower().startswith(prefix.lower()):
                    final_mp3_basename = final_mp3_basename[len(prefix):]
                    print(f"    Removed '{prefix}' prefix, final base name: {final_mp3_basename}")
                    prefix_removed = True
                    break # Stop checking once a prefix is removed
            if not prefix_removed:
                print(f"    (No known prefix found, using base name: {final_mp3_basename})")
            final_mp3_path = os.path.join(output_dir, f"{final_mp3_basename}.mp3")

            lame_command = [lame_exe] + lame_opts_list + [temp_wav_path, final_mp3_path]

            print(f"    Running LAME: {' '.join(shlex.quote(str(p)) for p in lame_command)}")
            if not dry_run:
                lame_success = True
                try:
                    result_lame = subprocess.run(lame_command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
                    if result_lame.stderr:
                        print(f"    LAME Output (Stderr):\n{result_lame.stderr}")
                except FileNotFoundError:
                    print(f"    [!] Error: LAME not found at '{lame_exe}'.")
                    lame_success = False
                    success = False
                except subprocess.CalledProcessError as e:
                    print(f"    [!] Error running LAME (Return Code: {e.returncode}):")
                    print(f"    Command: {' '.join(shlex.quote(str(p)) for p in e.cmd)}")
                    print(f"    LAME Stdout:\n{e.stdout}")
                    print(f"    LAME Stderr:\n{e.stderr}")
                    lame_success = False
                    success = False
                except Exception as e:
                    print(f"  [!] Unexpected error during LAME execution: {e}")
                    lame_success = False
                    success = False

                # --- Step 3: Clean up intermediate WAV file ---
                if lame_success and not keep_wav:
                    try:
                        os.remove(temp_wav_path)
                        print(f"    Removed temp WAV: {wav_filename}")
                    except OSError as e:
                        print(f"    [!] Warning: Could not remove temp WAV '{temp_wav_path}': {e}")
                elif not lame_success:
                    print(f"    Keeping failed WAV: {temp_wav_path}")

    except Exception as e:
        print(f"  [!] An unexpected error occurred processing {acb_path}: {e}")
        import traceback
        traceback.print_exc()
        success = False
    finally:
        # --- Step 4: Clean up temporary directory ---
        if temp_wav_dir and os.path.exists(temp_wav_dir):
            if not keep_wav and success:
                try:
                    shutil.rmtree(temp_wav_dir)
                    print(f"  Removed temp dir: {temp_wav_dir}")
                except OSError as e:
                    print(f"  [!] Warning: Could not remove temp directory '{temp_wav_dir}': {e}")
            elif not success:
                print(f"  Keeping failed temp dir for inspection: {temp_wav_dir}")
            else:
                print(f"  Keeping temp WAV dir as requested: {temp_wav_dir}")

    return success or dry_run

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Batch convert {ACB_EXTENSION} files to MP3 using vgmstream and LAME.")

    parser.add_argument(
        "source_dir",
        help="The root directory containing the .acb files (will be searched recursively)."
    )
    parser.add_argument(
        "output_dir",
        help="The root directory where the converted MP3 files will be saved (structure will be mirrored)."
    )
    parser.add_argument(
        "--vgmstream-path",
        default=DEFAULT_VGMSTREAM_EXE,
        help=f"Path to vgmstream-cli executable. Defaults to checking PATH for '{DEFAULT_VGMSTREAM_EXE}'."
    )
    parser.add_argument(
        "--lame-path",
        default=DEFAULT_LAME_EXE,
        help=f"Path to LAME executable. Defaults to checking PATH for '{DEFAULT_LAME_EXE}'."
    )
    parser.add_argument(
        "--lame-quality",
        default=DEFAULT_LAME_QUALITY,
        help=f"Quality/options string for LAME (e.g., '-V 2', '-b 320'). Default: '{DEFAULT_LAME_QUALITY}'."
    )
    parser.add_argument(
        "--keep-wav",
        action="store_true",
        help="Keep the intermediate WAV files (useful for debugging)."
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show commands that would be executed without running them."
    )

    args = parser.parse_args()

    source_dir_abs = os.path.abspath(args.source_dir)
    output_dir_abs = os.path.abspath(args.output_dir)

    if not os.path.isdir(source_dir_abs):
        print(f"Error: Source directory not found: {source_dir_abs}")
        sys.exit(1)

    vgmstream_exe_path = find_executable(DEFAULT_VGMSTREAM_EXE, args.vgmstream_path)
    if not vgmstream_exe_path:
        print(f"Error: Could not find vgmstream-cli executable ('{DEFAULT_VGMSTREAM_EXE}').")
        print(f"Please ensure it's in your system PATH or specify its location using --vgmstream-path.")
        sys.exit(1)
    print(f"Using vgmstream-cli: {vgmstream_exe_path}")

    lame_exe_path = find_executable(DEFAULT_LAME_EXE, args.lame_path)
    if not lame_exe_path:
        print(f"Error: Could not find LAME executable ('{DEFAULT_LAME_EXE}').")
        print(f"Please ensure it's in your system PATH or specify its location using --lame-path.")
        sys.exit(1)
    print(f"Using LAME: {lame_exe_path}")

    try:
        lame_options_list = shlex.split(args.lame_quality)
        print(f"Using LAME options: {lame_options_list}")
    except ValueError as e:
        print(f"Error: Invalid LAME quality string '{args.lame_quality}': {e}")
        sys.exit(1)


    if not args.dry_run:
        try:
            os.makedirs(output_dir_abs, exist_ok=True)
            print(f"Ensured output directory exists: {output_dir_abs}")
        except OSError as e:
            print(f"Error: Could not create output directory '{output_dir_abs}': {e}")
            sys.exit(1)
    else:
        print("--- DRY RUN MODE: No files will be created or converted. ---")

    acb_count = 0
    success_count = 0
    fail_count = 0

    for root, _, filenames in os.walk(source_dir_abs):
        for filename in filenames:
            if filename.lower().endswith(ACB_EXTENSION):
                acb_count += 1
                full_acb_path = os.path.join(root, filename)
                # Calculate output base dir relative to the initial source_dir argument
                # This ensures structure is mirrored correctly from the root specified
                relative_path_from_source = os.path.relpath(root, source_dir_abs)
                current_output_base = os.path.join(output_dir_abs, relative_path_from_source)

                if process_acb_file(full_acb_path, current_output_base, vgmstream_exe_path, lame_exe_path, lame_options_list, args.keep_wav, args.dry_run):
                    if not args.dry_run: success_count += 1
                else:
                    if not args.dry_run: fail_count += 1


    print("\n--- Conversion Summary ---")
    if args.dry_run:
         print(f"Dry run complete. Would have attempted to process {acb_count} {ACB_EXTENSION} files.")
    else:
        print(f"Attempted processing {acb_count} {ACB_EXTENSION} files.")
        print(f"Successful conversions (all tracks within ACB): {success_count}")
        print(f"Failed conversions (at least one error within ACB): {fail_count}")
        if args.keep_wav:
            print("Intermediate WAV files were kept.")
        if fail_count > 0:
             print("Check logs above for specific errors. Failed temporary directories might have been kept for inspection.")