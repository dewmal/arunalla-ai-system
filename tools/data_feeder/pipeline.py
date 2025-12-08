"""
RAG Data Pipeline Module
Complete pipeline for downloading, extracting, validating, and processing PDF documents.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .pdf_extractor import (
    extract_text_from_pdf,
    extract_text_from_pdf_async,
    get_pdf_info,
    validate_pdf_path,
    PDFSecurityError,
    MAX_TEXT_LENGTH
)
from .downloader import (
    download,
    download_async,
    validate_url,
    is_folder_url,
    DownloadSecurityError
)


@dataclass
class DocumentMetadata:
    """Metadata for a processed document"""
    file_name: str
    file_path: str
    file_size_mb: float
    page_count: int
    text_length: int
    has_sinhala: bool
    has_tamil: bool
    has_english: bool
    is_legacy_font: bool
    unicode_status: str
    source_url: Optional[str] = None
    processed_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Result of pipeline processing"""
    success: bool
    file_path: Optional[str]
    text: Optional[str]
    metadata: Optional[DocumentMetadata]
    error: Optional[str] = None


class RAGPipeline:
    """
    RAG Data Processing Pipeline
    
    Provides a complete workflow for:
    1. Downloading PDFs from Google Drive
    2. Extracting text with Unicode support
    3. Detecting language (Sinhala, Tamil, English)
    4. Validating Unicode vs legacy fonts
    5. Saving processed data for RAG systems
    """
    
    def __init__(
        self,
        output_dir: str = "processed",
        downloads_dir: str = "downloads",
        max_text_length: int = MAX_TEXT_LENGTH
    ):
        self.output_dir = Path(output_dir)
        self.downloads_dir = Path(downloads_dir)
        self.max_text_length = max_text_length
        self.results: List[PipelineResult] = []
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.downloads_dir.mkdir(exist_ok=True)
    
    def detect_languages(self, text: str) -> Dict[str, bool]:
        """Detect which languages are present in text"""
        has_sinhala = any('\u0D80' <= char <= '\u0DFF' for char in text)
        has_tamil = any('\u0B80' <= char <= '\u0BFF' for char in text)
        has_english = any(char.isascii() and char.isalpha() for char in text)
        
        return {
            "has_sinhala": has_sinhala,
            "has_tamil": has_tamil,
            "has_english": has_english
        }
    
    def detect_legacy_font(self, text: str) -> bool:
        """Detect if text uses legacy Sinhala fonts (FM, DL, etc.)"""
        if not text or len(text) < 20:
            return False
        
        # If it has real Sinhala Unicode, it's not legacy
        if any('\u0D80' <= char <= '\u0DFF' for char in text):
            return False
        
        # Legacy font indicators
        total_chars = len(text)
        semicolon_ratio = text.count(';') / total_chars if total_chars > 0 else 0
        
        # FM font patterns
        fm_patterns = [';a', ';s', ';j', ';d', ';l', ';k', 'WIaK', 'fld', 'fjk']
        fm_count = sum(1 for p in fm_patterns if p in text)
        
        return semicolon_ratio > 0.03 or fm_count >= 3
    
    def get_unicode_status(self, languages: Dict[str, bool], is_legacy: bool) -> str:
        """Get human-readable Unicode status"""
        if is_legacy:
            return "INVALID (Legacy Font)"
        if languages["has_sinhala"]:
            return "VALID (Sinhala Unicode)"
        if languages["has_tamil"]:
            return "VALID (Tamil Unicode)"
        if languages["has_english"]:
            return "VALID (English)"
        return "UNKNOWN"
    
    def process_pdf(
        self,
        pdf_path: str,
        source_url: Optional[str] = None
    ) -> PipelineResult:
        """
        Process a single PDF file through the pipeline.
        
        Args:
            pdf_path: Path to PDF file
            source_url: Optional source URL
            
        Returns:
            PipelineResult with extracted text and metadata
        """
        try:
            # Validate path
            validated_path = validate_pdf_path(pdf_path)
            
            # Get PDF info
            info = get_pdf_info(str(validated_path))
            
            if not info.get("is_valid"):
                return PipelineResult(
                    success=False,
                    file_path=str(validated_path),
                    text=None,
                    metadata=None,
                    error=info.get("error", "Invalid PDF")
                )
            
            # Extract text
            text = extract_text_from_pdf(str(validated_path), max_length=self.max_text_length)
            
            if text.startswith("Error"):
                return PipelineResult(
                    success=False,
                    file_path=str(validated_path),
                    text=None,
                    metadata=None,
                    error=text
                )
            
            # Detect languages and legacy fonts
            languages = self.detect_languages(text)
            is_legacy = self.detect_legacy_font(text)
            unicode_status = self.get_unicode_status(languages, is_legacy)
            
            # Create metadata
            metadata = DocumentMetadata(
                file_name=validated_path.name,
                file_path=str(validated_path),
                file_size_mb=info.get("file_size_mb", 0),
                page_count=info.get("page_count", 0),
                text_length=len(text),
                has_sinhala=languages["has_sinhala"],
                has_tamil=languages["has_tamil"],
                has_english=languages["has_english"],
                is_legacy_font=is_legacy,
                unicode_status=unicode_status,
                source_url=source_url,
                processed_at=datetime.now().isoformat()
            )
            
            result = PipelineResult(
                success=True,
                file_path=str(validated_path),
                text=text,
                metadata=metadata
            )
            
            self.results.append(result)
            return result
            
        except PDFSecurityError as e:
            return PipelineResult(
                success=False,
                file_path=pdf_path,
                text=None,
                metadata=None,
                error=f"Security Error: {e}"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                file_path=pdf_path,
                text=None,
                metadata=None,
                error=f"Error: {e}"
            )
    
    def download_and_process(self, url: str) -> PipelineResult:
        """
        Download a PDF from Google Drive and process it.
        
        Args:
            url: Google Drive URL
            
        Returns:
            PipelineResult with extracted text and metadata
        """
        try:
            # Validate URL
            validated_url = validate_url(url)
            
            # Download
            success = download(validated_url, str(self.downloads_dir))
            
            if not success:
                return PipelineResult(
                    success=False,
                    file_path=None,
                    text=None,
                    metadata=None,
                    error="Download failed"
                )
            
            # Find the downloaded file (most recent PDF in downloads)
            pdf_files = list(self.downloads_dir.glob("*.pdf"))
            if not pdf_files:
                return PipelineResult(
                    success=False,
                    file_path=None,
                    text=None,
                    metadata=None,
                    error="No PDF file found after download"
                )
            
            latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
            
            # Process the downloaded PDF
            return self.process_pdf(str(latest_pdf), source_url=url)
            
        except DownloadSecurityError as e:
            return PipelineResult(
                success=False,
                file_path=None,
                text=None,
                metadata=None,
                error=f"Security Error: {e}"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                file_path=None,
                text=None,
                metadata=None,
                error=f"Error: {e}"
            )
    
    async def process_pdf_async(
        self,
        pdf_path: str,
        source_url: Optional[str] = None
    ) -> PipelineResult:
        """Async version of process_pdf"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.process_pdf(pdf_path, source_url)
            )
        return result
    
    async def download_and_process_async(self, url: str) -> PipelineResult:
        """Async version of download_and_process"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.download_and_process(url)
            )
        return result
    
    async def batch_process_async(
        self,
        urls: List[str],
        max_concurrent: int = 3
    ) -> List[PipelineResult]:
        """
        Process multiple URLs concurrently.
        
        Args:
            urls: List of Google Drive URLs
            max_concurrent: Max concurrent downloads
            
        Returns:
            List of PipelineResults
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit(url: str) -> PipelineResult:
            async with semaphore:
                return await self.download_and_process_async(url)
        
        tasks = [process_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(PipelineResult(
                    success=False,
                    file_path=None,
                    text=None,
                    metadata=None,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def save_result(
        self,
        result: PipelineResult,
        save_text: bool = True,
        save_metadata: bool = True
    ) -> Dict[str, str]:
        """
        Save pipeline result to files.
        
        Args:
            result: PipelineResult to save
            save_text: Whether to save extracted text
            save_metadata: Whether to save metadata JSON
            
        Returns:
            Dict with paths to saved files
        """
        saved_files = {}
        
        if not result.success or not result.metadata:
            return saved_files
        
        base_name = Path(result.metadata.file_name).stem
        
        if save_text and result.text:
            text_path = self.output_dir / f"{base_name}_text.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"# File: {result.metadata.file_name}\n")
                f.write(f"# Pages: {result.metadata.page_count}\n")
                f.write(f"# Unicode: {result.metadata.unicode_status}\n")
                f.write(f"# Processed: {result.metadata.processed_at}\n")
                f.write("#" + "=" * 50 + "\n\n")
                f.write(result.text)
            saved_files["text"] = str(text_path)
        
        if save_metadata:
            meta_path = self.output_dir / f"{base_name}_metadata.json"
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(result.metadata), f, indent=2, ensure_ascii=False)
            saved_files["metadata"] = str(meta_path)
        
        return saved_files
    
    def save_all_results(self) -> str:
        """
        Save all results to a summary JSON file.
        
        Returns:
            Path to summary file
        """
        summary = {
            "processed_at": datetime.now().isoformat(),
            "total_files": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "results": []
        }
        
        for result in self.results:
            if result.metadata:
                summary["results"].append(asdict(result.metadata))
            else:
                summary["results"].append({
                    "file_path": result.file_path,
                    "success": False,
                    "error": result.error
                })
        
        summary_path = self.output_dir / "pipeline_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(summary_path)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline processing statistics"""
        successful = [r for r in self.results if r.success]
        
        return {
            "total_processed": len(self.results),
            "successful": len(successful),
            "failed": len(self.results) - len(successful),
            "total_pages": sum(r.metadata.page_count for r in successful if r.metadata),
            "total_text_chars": sum(r.metadata.text_length for r in successful if r.metadata),
            "with_sinhala": sum(1 for r in successful if r.metadata and r.metadata.has_sinhala),
            "with_tamil": sum(1 for r in successful if r.metadata and r.metadata.has_tamil),
            "legacy_fonts": sum(1 for r in successful if r.metadata and r.metadata.is_legacy_font)
        }


def run_pipeline(
    urls: Optional[List[str]] = None,
    files: Optional[List[str]] = None,
    output_dir: str = "processed"
) -> Dict[str, Any]:
    """
    Convenience function to run the pipeline.
    
    Args:
        urls: List of Google Drive URLs to download and process
        files: List of local PDF files to process
        output_dir: Output directory for results
        
    Returns:
        Dict with processing summary
    """
    pipeline = RAGPipeline(output_dir=output_dir)
    
    # Process URLs
    if urls:
        for url in urls:
            print(f"Processing URL: {url[:50]}...")
            result = pipeline.download_and_process(url)
            if result.success:
                pipeline.save_result(result)
                print(f"  ✅ Success: {result.metadata.file_name}")
            else:
                print(f"  ❌ Failed: {result.error}")
    
    # Process local files
    if files:
        for file_path in files:
            print(f"Processing file: {file_path}...")
            result = pipeline.process_pdf(file_path)
            if result.success:
                pipeline.save_result(result)
                print(f"  ✅ Success: {result.metadata.file_name}")
            else:
                print(f"  ❌ Failed: {result.error}")
    
    # Save summary
    summary_path = pipeline.save_all_results()
    stats = pipeline.get_stats()
    
    print("\n" + "=" * 50)
    print("Pipeline Summary")
    print("=" * 50)
    print(f"Total processed: {stats['total_processed']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total pages: {stats['total_pages']}")
    print(f"With Sinhala: {stats['with_sinhala']}")
    print(f"With Tamil: {stats['with_tamil']}")
    print(f"Legacy fonts: {stats['legacy_fonts']}")
    print(f"Summary saved to: {summary_path}")
    
    return {
        "stats": stats,
        "summary_path": summary_path,
        "results": pipeline.results
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m tools.data_feeder.pipeline --url <google_drive_url>")
        print("  python -m tools.data_feeder.pipeline --file <pdf_path>")
        print("  python -m tools.data_feeder.pipeline --batch <url1> <url2> ...")
        sys.exit(1)
    
    mode = sys.argv[1]
    args = sys.argv[2:]
    
    if mode == "--url" and args:
        run_pipeline(urls=args)
    elif mode == "--file" and args:
        run_pipeline(files=args)
    elif mode == "--batch" and args:
        run_pipeline(urls=args)
    else:
        print("Invalid arguments")
        sys.exit(1)
