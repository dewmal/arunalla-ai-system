#!/usr/bin/env python3
"""
Data Feeder CLI - Command line interface for PDF extraction and Google Drive downloads.
Part of RAG Data Curator Tool.

Usage:
    python -m tools.data_feeder.app extract <pdf_file>
    python -m tools.data_feeder.app download <google_drive_url> [output_folder]
    python -m tools.data_feeder.app info <pdf_file>
"""

import sys
import os

from .pdf_extractor import extract_text_from_pdf, get_pdf_info
from .downloader import download


def print_usage():
    print(__doc__)


def cmd_extract(args):
    if not args:
        print("Error: Please provide a PDF file path")
        return 1
    
    pdf_path = args[0]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return 1
    
    print(f"Extracting text from: {pdf_path}")
    print("=" * 50)
    result = extract_text_from_pdf(pdf_path)
    print(result)
    return 0


def cmd_download(args):
    if not args:
        print("Error: Please provide a Google Drive URL")
        return 1
    
    url = args[0]
    output_folder = args[1] if len(args) > 1 else "downloads"
    
    print(f"Downloading from: {url}")
    print(f"Output folder: {output_folder}")
    print("=" * 50)
    
    success = download(url, output_folder)
    return 0 if success else 1


def cmd_info(args):
    if not args:
        print("Error: Please provide a PDF file path")
        return 1
    
    pdf_path = args[0]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return 1
    
    info = get_pdf_info(pdf_path)
    print(f"PDF Info: {pdf_path}")
    print("=" * 50)
    print(f"  Pages: {info['page_count']}")
    print(f"  Title: {info['title'] or 'N/A'}")
    print(f"  Author: {info['author'] or 'N/A'}")
    print(f"  Subject: {info['subject'] or 'N/A'}")
    print(f"  Creator: {info['creator'] or 'N/A'}")
    return 0


def main():
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        "extract": cmd_extract,
        "download": cmd_download,
        "info": cmd_info,
        "help": lambda _: (print_usage(), 0)[1],
        "-h": lambda _: (print_usage(), 0)[1],
        "--help": lambda _: (print_usage(), 0)[1]
    }
    
    if command in commands:
        return commands[command](args)
    else:
        print(f"Unknown command: {command}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
