# BGM Extractor Toolkit

This repository contains two Python scripts designed to assist with batch processing of audio files for game music extraction and conversion:

1. **`bytestoacb.py`**: A script to rename `.bytes` files to `.acb` format.
2. **`trackdecode.py`**: A script to convert `.acb` files into `.mp3` format using `vgmstream-cli` and `LAME`.

---

## Prerequisites

> **Python 3.11**: Ensure Python is installed on your system.

---

## Scripts Overview

### 1. `bytestoacb.py`

This script renames files with the `.bytes` extension to `.acb`.

#### Usage

```bash
python bytestoacb.py [options] [directory]
```

#### Options
- `directory`: The target directory containing `.bytes` files. Defaults to the current directory.
- `-r`, `--recursive`: Search for files recursively in subdirectories.
- `-d`, `--dry-run`: Show which files would be renamed without actually renaming them.

#### Examples
- Rename `.bytes` to `.acb` in the current directory:
  ```bash
  python bytestoacb.py
  ```
- Rename recursively in a specific directory:
  ```bash
  python bytestoacb.py -r /path/to/files
  ```
- Perform a dry run:
  ```bash
  python bytestoacb.py -d
  ```

---

### 2. `trackdecode.py`

This script converts `.acb` files into `.mp3` format using `vgmstream-cli` and `LAME`.

#### Usage

```bash
python trackdecode.py [options] <source_directory> <output_directory>
```

#### Options
- `--vgmstream-path PATH`: Path to the `vgmstream-cli` executable.
- `--lame-path PATH`: Path to the `LAME` executable.
- `--lame-quality "OPTIONS"`: LAME encoding options (default: `"-V 2"`).
- `--keep-wav`: Keep intermediate `.wav` files.
- `-d`, `--dry-run`: Show commands that would be executed without running them.

#### Examples
- Convert `.acb` files to `.mp3` in a specific directory:
  ```bash
  python trackdecode.py /path/to/acb /path/to/output
  ```
- Specify paths to tools and use CBR 320kbps quality:
  ```bash
  python trackdecode.py --vgmstream-path "C:/tools/vgmstream-cli.exe" --lame-path "/usr/bin/lame" --lame-quality "-b 320" /path/to/acb /path/to/output
  ```
- Perform a dry run:
  ```bash
  python trackdecode.py -d /path/to/acb /path/to/output
  ```

---

## Notes

> [!Warning]
> Ensure you run the `bytestoacb.py` script first to rename `.bytes` files to `.acb` before using `trackdecode.py`. Failure to do so will result in `trackdecode.py` being unable to locate the required `.acb` files.

- ~~Ensure `vgmstream-cli` and `LAME` are accessible via the system `PATH` or specify their paths using the script options.~~
- Both scripts provide detailed output and error reporting to assist with troubleshooting.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.