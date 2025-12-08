# RAG Data Curator Tool

A tool for preparing Sri Lankan A/L and O/L exam materials for RAG (Retrieval-Augmented Generation) systems. It downloads PDFs from Google Drive, extracts text with proper Unicode support for Sinhala and Tamil, and outputs structured data ready for AI pipelines.

Website: https://arunalla.help/

## What it does

- Downloads files and folders from Google Drive
- Extracts text from PDFs (supports Sinhala, Tamil, and English)
- Detects whether text is proper Unicode or legacy fonts (like FM Abhaya)
- Validates and processes documents through a pipeline
- Outputs JSON metadata and extracted text files

## Quick start

Install dependencies:

```
pip install -r requirements.txt
```

Run the GUI app:

```
python app.py
```

Or use the command line tools:

```
# Extract text from a PDF
python -m tools.data_feeder.app extract your_file.pdf

# Download from Google Drive
python -m tools.data_feeder.app download "https://drive.google.com/..."

# Run the full pipeline
python -m tools.data_feeder.pipeline --url "https://drive.google.com/..."
python -m tools.data_feeder.pipeline --file file1.pdf file2.pdf
```

## Project structure

```
app.py                  - Main GUI application
tools/
  data_feeder/
    app.py              - CLI tool
    downloader.py       - Google Drive downloader
    pdf_extractor.py    - PDF text extraction
    pipeline.py         - Full processing pipeline
```

## Output

The pipeline creates:

- `processed/` folder with extracted text and metadata
- `pipeline_summary.json` with processing stats
- Individual `_text.txt` and `_metadata.json` files per document

Sample metadata:

```json
{
  "file_name": "example.pdf",
  "page_count": 5,
  "has_sinhala": true,
  "has_tamil": false,
  "unicode_status": "VALID (Sinhala Unicode)"
}
```

## Security

- URL validation (only Google Drive allowed)
- Path traversal protection
- File size limits (100MB max)
- Input sanitization

## Dependencies

- PyMuPDF - PDF rendering
- pdfplumber - Text extraction
- gdown - Google Drive downloads
- Pillow - Image handling

## License

See LICENSE file.
