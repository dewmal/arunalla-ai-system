"""
Data Feeder module for RAG Data Curator Tool.
Provides PDF extraction and Google Drive download functionality.
Includes security validation, context length limits, and async support.
"""

from .pdf_extractor import (
    extract_text_from_pdf,
    extract_text_from_pdf_async,
    get_pdf_info,
    validate_pdf_path,
    truncate_text,
    PDFSecurityError,
    PDFExtractionError,
    MAX_TEXT_LENGTH,
    MAX_PAGES,
    MAX_FILE_SIZE_MB
)
from .downloader import (
    download,
    download_async,
    download_file,
    download_folder,
    is_folder_url,
    validate_url,
    validate_output_path,
    DownloadSecurityError
)
from .pipeline import (
    RAGPipeline,
    PipelineResult,
    DocumentMetadata,
    run_pipeline
)

__all__ = [
    # PDF Extractor
    "extract_text_from_pdf",
    "extract_text_from_pdf_async",
    "get_pdf_info",
    "validate_pdf_path",
    "truncate_text",
    "PDFSecurityError",
    "PDFExtractionError",
    "MAX_TEXT_LENGTH",
    "MAX_PAGES",
    "MAX_FILE_SIZE_MB",
    # Downloader
    "download",
    "download_async",
    "download_file",
    "download_folder",
    "is_folder_url",
    "validate_url",
    "validate_output_path",
    "DownloadSecurityError",
    # Pipeline
    "RAGPipeline",
    "PipelineResult",
    "DocumentMetadata",
    "run_pipeline"
]
