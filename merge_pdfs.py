#!/usr/bin/env python3
"""Merge PDFs from the local input directory in natural filename order."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Sequence

from pypdf import PdfWriter
from pypdf.errors import FileNotDecryptedError, PdfReadError
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.prompt import Confirm
from rich.table import Table


APP_NAME = "PDF Name Merger"
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
DEFAULT_OUTPUT = BASE_DIR / "merged.pdf"
NUMBER_PARTS = re.compile(r"(\d+)")

console = Console()
logging.getLogger("pypdf").setLevel(logging.ERROR)


class MergeError(Exception):
    """A user-friendly error raised while preparing or merging PDFs."""


def natural_sort_key(path: Path) -> tuple[tuple[int, int | str], ...]:
    """Return a case-insensitive natural key (2.pdf sorts before 10.pdf)."""

    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.casefold())
        for part in NUMBER_PARTS.split(path.name)
        if part
    )


def find_input_pdfs(input_dir: Path) -> list[Path]:
    """Find PDF files directly inside input_dir and return them sorted."""

    input_dir.mkdir(exist_ok=True)
    return sorted(
        (
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix.casefold() == ".pdf"
        ),
        key=lambda path: (natural_sort_key(path), path.name.casefold(), path.name),
    )


def display_header() -> None:
    """Print the application banner."""

    console.print(
        Panel.fit(
            "[bold bright_cyan]PDF NAME MERGER[/]\n"
            "[dim]Clean, ordered PDF merging from your terminal[/]",
            border_style="bright_cyan",
            padding=(1, 4),
        )
    )


def display_file_order(files: Sequence[Path]) -> None:
    """Show the exact order that will be used for the merge."""

    table = Table(
        title=f"[bold]Merge order ({len(files)} files)[/]",
        border_style="cyan",
        header_style="bold bright_cyan",
        show_lines=False,
    )
    table.add_column("#", justify="right", style="dim", width=5)
    table.add_column("PDF file", overflow="fold")

    for index, pdf_path in enumerate(files, start=1):
        table.add_row(str(index), escape(pdf_path.name))

    console.print(table)


def merge_pdfs(files: Sequence[Path], output_path: Path) -> int:
    """Merge files into output_path and return the total number of pages."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_name(f".{output_path.stem}.tmp.pdf")
    temporary_output.unlink(missing_ok=True)

    writer = PdfWriter()
    total_pages = 0

    progress = Progress(
        SpinnerColumn(style="bright_cyan"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="grey37", complete_style="bright_cyan"),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TextColumn("[dim]{task.fields[current_file]}[/]"),
        console=console,
        expand=True,
    )

    try:
        with progress:
            task_id = progress.add_task(
                "Merging",
                total=len(files),
                current_file="Preparing...",
            )

            for pdf_path in files:
                progress.update(task_id, current_file=escape(pdf_path.name))
                pages_before = len(writer.pages)

                try:
                    writer.append(str(pdf_path))
                except FileNotDecryptedError as error:
                    raise MergeError(
                        f"'{pdf_path.name}' is password-protected and cannot be merged."
                    ) from error
                except (PdfReadError, OSError, ValueError) as error:
                    raise MergeError(
                        f"Could not read '{pdf_path.name}': {error}"
                    ) from error
                except Exception as error:
                    raise MergeError(
                        f"Could not merge '{pdf_path.name}': {error}"
                    ) from error

                total_pages += len(writer.pages) - pages_before
                progress.advance(task_id)

            progress.update(task_id, description="Writing", current_file=output_path.name)
            try:
                with temporary_output.open("wb") as output_stream:
                    writer.write(output_stream)
                temporary_output.replace(output_path)
            except OSError as error:
                raise MergeError(f"Could not write the output file: {error}") from error
    finally:
        temporary_output.unlink(missing_ok=True)
        writer.close()

    return total_pages


def resolve_output_path(raw_output: str) -> Path:
    """Resolve relative output paths from the project directory."""

    output_path = Path(raw_output).expanduser()
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path
    return output_path.resolve()


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Merge every PDF in the input folder using natural filename order."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT),
        metavar="FILE",
        help="output PDF path (default: merged.pdf beside this script)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite an existing output file without asking",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Run the terminal application and return its exit code."""

    args = build_parser().parse_args(argv)
    display_header()

    try:
        output_path = resolve_output_path(args.output)
        if output_path.suffix.casefold() != ".pdf":
            raise MergeError("The output filename must end with .pdf.")

        files = find_input_pdfs(INPUT_DIR)
        if not files:
            raise MergeError(
                f"No PDF files were found. Add PDFs to: {INPUT_DIR}"
            )

        if output_path in (path.resolve() for path in files):
            raise MergeError("The output file cannot also be an input file.")

        display_file_order(files)

        if output_path.exists() and not args.force:
            if not sys.stdin.isatty():
                raise MergeError(
                    f"'{output_path.name}' already exists. Use --force to overwrite it."
                )
            if not Confirm.ask(
                f"[yellow]'{escape(output_path.name)}' already exists. Overwrite it?[/]",
                default=False,
                console=console,
            ):
                console.print("[yellow]Cancelled. No files were changed.[/]")
                return 0

        total_pages = merge_pdfs(files, output_path)
    except MergeError as error:
        console.print(Panel(str(error), title="[bold red]Merge failed[/]", border_style="red"))
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled. No output file was created.[/]")
        return 130

    console.print(
        Panel(
            f"[bold green]Merge complete![/]\n\n"
            f"[bold]{len(files)}[/] files  [dim]•[/]  "
            f"[bold]{total_pages}[/] pages\n"
            f"[dim]Saved to[/] [cyan]{escape(str(output_path))}[/]",
            border_style="green",
            title="[bold green]Success[/]",
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
