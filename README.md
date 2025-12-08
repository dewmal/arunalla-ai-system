# RAG Data Curator Tool

A desktop GUI application for preparing Sri Lankan A/L & O/L exam materials for a Retrieval-Augmented Generation (RAG) pipeline.

> **Website:** <https://arunalla.help/>

## Features

- 📁 **File Browser** - Browse and navigate PDF files in any folder
- 👁️ **PDF Preview** - View PDF pages with navigation controls
- 📥 **Google Drive Download** - Download files/folders directly from Google Drive URLs
- 📝 **Text Extraction** - Extract text from PDFs (quick 3-page or full extraction)
- 🔤 **Unicode Detection** - Detect Sinhala, Tamil, English text and legacy font encoding
- 🏷️ **Metadata Tagging** - Tag files with subject, year, exam level, paper type
- 💾 **Export** - Save metadata to JSON and export to CSV for Google Sheets

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/AdhiDevX369/arunalla-ai-system.git
   cd arunalla-ai-system
   ```

1. Create a virtual environment (recommended):

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Application

Run the main application:

```bash
python app.py
```

### CLI Tools

The data feeder module provides command-line tools:

```bash
# Extract text from a PDF
python -m tools.data_feeder.app extract <pdf_file>

# Download from Google Drive
python -m tools.data_feeder.app download <google_drive_url> [output_folder]

# Get PDF info
python -m tools.data_feeder.app info <pdf_file>
```

### Standalone Downloader

Run the interactive Google Drive downloader:

```bash
python tools/data_feeder/downloader.py
```

## Project Structure

```text
arunalla-ai-system/
├── app.py                      # Main GUI application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # License file
├── .gitignore                  # Git ignore rules
└── tools/
    └── data_feeder/
        ├── __init__.py         # Package exports
        ├── app.py              # CLI entry point
        ├── downloader.py       # Google Drive downloader
        └── pdf_extractor.py    # PDF text extraction
```

## Dependencies

| Package | Purpose |
|---------|---------|
| PyMuPDF | PDF rendering and quick text extraction |
| Pillow | Image processing for preview |
| pdfplumber | Full text extraction (better accuracy) |
| PyPDF2 | Fallback PDF text extraction |
| gdown | Google Drive downloads |
| requests | HTTP requests |
| beautifulsoup4 | HTML parsing |

## Supported Content

- **Exam Levels:** A/L (Advanced Level), O/L (Ordinary Level)
- **Languages:** Sinhala (Unicode), Tamil (Unicode), English
- **Paper Types:** Past Papers, Model Papers, Notes, Tutorials, Marking Schemes, Syllabi

## Unicode Detection

The tool detects:

- ✅ Valid Sinhala Unicode (U+0D80 to U+0DFF)
- ✅ Valid Tamil Unicode (U+0B80 to U+0BFF)
- ✅ English/Latin text
- ❌ Legacy Sinhala fonts (FM, DL, Kaputa) - These are NOT usable for RAG

## License

See [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
