<div align="center">

# PDF Name Merger

**A tiny, friendly terminal app that merges PDFs in filename order.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Windows-Terminal-0078D4?logo=windows&logoColor=white)
![Style](https://img.shields.io/badge/UI-Rich-13B5EA)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

Drop your PDF files into `input/`, run one command, and get one clean
`merged.pdf`. The app shows the exact merge order before it starts and displays
a live graphical progress bar while it works.

## Highlights

- **Natural filename sorting** - `2.pdf` comes before `10.pdf`.
- **Case-insensitive discovery** - both `.pdf` and `.PDF` are accepted.
- **Polished terminal UI** - clear file table, progress bar, and result summary.
- **Safe output** - the result is written to a temporary file first; source PDFs
  are never modified.
- **Windows-friendly** - works in Windows Terminal, PowerShell, and Command
  Prompt.
- **Simple by design** - only two small dependencies and no configuration file.

## Project structure

```text
pdf-name-merger/
├── input/
│   └── .gitkeep
├── merge_pdfs.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Quick start on Windows

1. Install [Python 3.10 or newer](https://www.python.org/downloads/). During
   installation, enable **Add Python to PATH**.
2. Open PowerShell in the project folder.
3. Create a virtual environment and install the dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

4. Copy your PDF files into the `input` folder.
5. Run the merger:

   ```powershell
   python merge_pdfs.py
   ```

The finished file will be created as `merged.pdf` beside the Python script.

<details>
<summary><strong>Using Command Prompt instead?</strong></summary>

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python merge_pdfs.py
```

</details>

## Filename order

Files are sorted using **natural, case-insensitive order**. For example, these
input files:

```text
10-appendix.pdf
2-method.pdf
01-cover.pdf
Chapter-3.PDF
```

are merged in this order:

```text
01-cover.pdf
2-method.pdf
10-appendix.pdf
Chapter-3.PDF
```

For the clearest and most predictable order, use numbered names such as
`01-cover.pdf`, `02-introduction.pdf`, and `03-results.pdf`.

## Command options

### Choose a different output name

```powershell
python merge_pdfs.py --output complete-book.pdf
```

Relative output paths are resolved from the project folder. Absolute paths are
also supported.

### Overwrite without confirmation

```powershell
python merge_pdfs.py --force
```

This is useful in scripts or automated workflows. Without `--force`, the app
asks before replacing an existing output in an interactive terminal and stops
safely in a non-interactive terminal.

### Show all options

```powershell
python merge_pdfs.py --help
```

## What the terminal looks like

```text
╭────────────────────────────────────╮
│          PDF NAME MERGER           │
│ Clean, ordered PDF merging from    │
│ your terminal                      │
╰────────────────────────────────────╯

      Merge order (3 files)
┌─────┬──────────────────────┐
│   # │ PDF file             │
├─────┼──────────────────────┤
│   1 │ 01-cover.pdf         │
│   2 │ 02-chapter.pdf       │
│   3 │ 03-appendix.pdf      │
└─────┴──────────────────────┘

⠹ Merging ━━━━━━━━━━━━━━━━━━━ 67% 2/3 03-appendix.pdf
```

## How it works

1. The script looks only at PDF files directly inside `input/`.
2. It sorts their names naturally and shows the planned order.
3. [`pypdf`](https://pypdf.readthedocs.io/en/latest/user/merging-pdfs.html)
   appends every PDF to a single writer.
4. [`Rich`](https://rich.readthedocs.io/en/latest/progress.html) renders the
   table, progress bar, and status panels.
5. The completed document is atomically moved into its final location.

## Usage

Run the application locally to merge PDF files.

## Notes and troubleshooting

- **No files found:** confirm the PDFs are directly inside `input/`, not in a
  nested folder.
- **Output already exists:** approve the prompt or run with `--force`.
- **Password-protected PDF:** unlock it first, then place the unlocked copy in
  `input/`.
- **PowerShell blocks activation:** run
  `Set-ExecutionPolicy -Scope Process Bypass`, then activate the environment
  again. This changes the policy only for the current PowerShell window.
- **Colors or animation look limited:** use the current
  [Windows Terminal](https://aka.ms/terminal) for the best display.

The app runs locally. It does not upload your documents or require an internet
connection after the dependencies have been installed.

## Requirements

- Python 3.10+
- `pypdf`
- `rich`

Install everything with:

```powershell
python -m pip install -r requirements.txt
```

## License

Released under the [MIT License](LICENSE).

---

<div align="center">
Made for quick, predictable, no-fuss PDF merging.
</div>
