#!/usr/bin/env python3
import urllib.parse
import argparse
import logging
import colorlog
from tqdm import tqdm
import random
import pyfiglet
import os
import sys
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from colorama import Fore, Style, init
from typing import Dict, List, Set, Tuple, FrozenSet, Optional, Iterator, Any
import hashlib
import tempfile
import pickle
from pathlib import Path
import time

# Initialize colorama
init(autoreset=True)

class EnhancedConfig:
    """ configuration with better defaults and validation"""
    TOOL_NAME = "URLF"
    VERSION = "2.4"
    AUTHOR = "0xBobby"
    COLORS = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN
    ]
    
    # Performance settings
    MAX_WORKERS = min(32, os.cpu_count() + 4)  # Better default
    CHUNK_SIZE = 5000  # Increased for better performance
    MEMORY_THRESHOLD = 2000000  # 2M URLs threshold
    CHECKPOINT_INTERVAL = 25000  # Less frequent checkpoints
    
    # Validation settings
    VALID_SCHEMES = {'http', 'https', 'ftp', 'ftps', 'file', 'data'}
    MAX_URL_LENGTH = 2048  # RFC 2616 recommendation
    MAX_DOMAIN_LENGTH = 253  # RFC 1035
    
    # File handling
    SUPPORTED_ENCODINGS = ['utf-8', 'latin1', 'cp1252', 'utf-16']
    BATCH_WRITE_SIZE = 10000  # Write in batches for better I/O
    
    @classmethod
    def validate_workers(cls, workers: int) -> int:
        """Validate and adjust worker count"""
        return max(1, min(workers, cls.MAX_WORKERS))

def print_banner() -> None:
    """Print a random styled banner with tool metadata"""
    styles = ['slant', '3-d', 'banner3-D', 'standard', 'isometric1', 'cyberlarge', 'starwars', 'doom']
    chosen_style = random.choice(styles)
    chosen_color = random.choice(EnhancedConfig.COLORS)
    
    ascii_banner = pyfiglet.figlet_format(EnhancedConfig.TOOL_NAME, font=chosen_style)
    print(chosen_color + ascii_banner + Style.RESET_ALL)
    
    print(f"{chosen_color}Author  : {EnhancedConfig.AUTHOR}{Style.RESET_ALL}")
    print(f"{chosen_color}Version : {EnhancedConfig.VERSION}{Style.RESET_ALL}")
    print()

class EnhancedURLValidator:
    """ URL validator with better performance and accuracy"""
    
    # Pre-compiled regex patterns for better performance
    IP_PATTERN = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$')
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """ URL validation with better performance"""
        try:
            # Quick length check
            if len(url) > EnhancedConfig.MAX_URL_LENGTH:
                return False
            
            # Parse URL
            result = urllib.parse.urlparse(url.strip())
            
            # Validate scheme
            if result.scheme.lower() not in EnhancedConfig.VALID_SCHEMES:
                return False
            
            # Validate netloc
            if not result.netloc:
                return False
            
            # Extract host and port
            netloc_parts = result.netloc.split(':')
            host = netloc_parts[0].lower()
            
            # Validate host length
            if len(host) > EnhancedConfig.MAX_DOMAIN_LENGTH:
                return False
            
            # Validate port if present
            if len(netloc_parts) > 1:
                try:
                    port = int(netloc_parts[1])
                    if not (1 <= port <= 65535):
                        return False
                except ValueError:
                    return False
            
            # Validate host format
            if not (cls._is_valid_domain(host) or cls._is_valid_ip(host) or host == 'localhost'):
                return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def _is_valid_ip(cls, host: str) -> bool:
        """ IP address validation"""
        return bool(cls.IP_PATTERN.match(host))
    
    @classmethod
    def _is_valid_domain(cls, host: str) -> bool:
        """ domain validation"""
        if not host or host.startswith('.') or host.endswith('.'):
            return False
        return bool(cls.DOMAIN_PATTERN.match(host))
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """ URL normalization with better error handling"""
        try:
            url = url.strip()
            parsed = urllib.parse.urlparse(url)
            
            # Normalize components
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            
            # Normalize path
            path = parsed.path
            if path and path != '/':
                path = path.rstrip('/')
            elif not path:
                path = '/'
            
            # Normalize query parameters
            query = ''
            if parsed.query:
                try:
                    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                    sorted_params = sorted(params.items())
                    query = urllib.parse.urlencode(sorted_params, doseq=True)
                except Exception:
                    query = parsed.query  # Keep original if parsing fails
            
            # Reconstruct URL
            return urllib.parse.urlunparse((
                scheme, netloc, path, parsed.params, query, ''
            ))
            
        except Exception:
            return url  # Return original if normalization fails
    
    @classmethod
    def extract_parameters(cls, url: str) -> FrozenSet[str]:
        """ parameter extraction with better error handling"""
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.query:
                return frozenset()
            
            params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            return frozenset(param.lower() for param in params.keys())
            
        except Exception:
            return frozenset()
    
    @classmethod
    def get_domain(cls, url: str) -> str:
        """ domain extraction"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower().split(':')[0]  # Remove port if present
        except Exception:
            return ""

class EnhancedFileHandler:
    """ file handling with better encoding support and error recovery"""
    
    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detect file encoding using multiple methods"""
        try:
            # Try each encoding in order of preference
            for encoding in EnhancedConfig.SUPPORTED_ENCODINGS:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1024)  # Read first 1KB to test
                    return encoding
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            # If all fail, use utf-8 with error handling
            return 'utf-8'
            
        except Exception:
            return 'utf-8'
    
    @staticmethod
    def read_urls_safely(file_path: str) -> Iterator[str]:
        """Safely read URLs with automatic encoding detection"""
        encoding = EnhancedFileHandler.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        yield line
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    @staticmethod
    def write_urls_batch(urls: List[str], output_file: str, append: bool = False) -> None:
        """Write URLs in batches for better I/O performance"""
        mode = 'a' if append else 'w'
        
        try:
            # Ensure output directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, mode, encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
                    
        except Exception as e:
            logger.error(f"Error writing to file {output_file}: {e}")
            raise
    
    @staticmethod
    def safe_json_dump(data: Any, file_path: str) -> None:
        """Safely dump JSON with error handling"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            raise

class EnhancedURLProcessor:
    """ URL processor with better performance and reliability"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = EnhancedConfig.validate_workers(max_workers or EnhancedConfig.MAX_WORKERS)
        self.stats = {
            "total": 0,
            "unique": 0,
            "duplicates": 0,
            "invalid": 0,
            "normalized": 0,
            "processing_time": 0.0,
            "urls_per_second": 0.0
        }
        self.unique_urls = {}
        self.duplicate_samples = []
        self.temp_dir = None
        
    def process_url_batch(self, urls: List[str]) -> Tuple[Dict, List[Dict], int, int]:
        """Process a batch of URLs with enhanced error handling"""
        batch_unique = {}
        batch_duplicates = []
        invalid_count = 0
        normalized_count = 0
        
        for url in urls:
            try:
                # Validate original URL
                if not EnhancedURLValidator.is_valid_url(url):
                    invalid_count += 1
                    continue
                
                # Normalize URL
                normalized = EnhancedURLValidator.normalize_url(url)
                if normalized != url:
                    normalized_count += 1
                
                # Extract key components
                domain = EnhancedURLValidator.get_domain(normalized)
                params = EnhancedURLValidator.extract_parameters(normalized)
                
                # Create unique key
                key = (domain, params)
                
                # Check for duplicates
                if key in self.unique_urls:
                    batch_duplicates.append({
                        'original': self.unique_urls[key],
                        'duplicate': url,
                        'domain': domain,
                        'params': list(params)
                    })
                elif key in batch_unique:
                    batch_duplicates.append({
                        'original': batch_unique[key],
                        'duplicate': url,
                        'domain': domain,
                        'params': list(params)
                    })
                else:
                    batch_unique[key] = normalized
                    
            except Exception as e:
                logger.debug(f"Error processing URL {url}: {e}")
                invalid_count += 1
                
        return batch_unique, batch_duplicates, invalid_count, normalized_count
    
    def process_file(self, input_file: str, output_file: str, 
                    verbose: bool = False, use_threads: bool = True) -> Dict[str, Any]:
        """ file processing with better performance monitoring"""
        
        start_time = time.time()
        
        # Count total URLs
        logger.info("Analyzing input file...")
        total_urls = sum(1 for _ in EnhancedFileHandler.read_urls_safely(input_file))
        self.stats["total"] = total_urls
        
        if total_urls == 0:
            logger.warning("No valid URLs found in input file")
            return self.stats
        
        logger.info(f"Processing {total_urls:,} URLs with {self.max_workers} workers")
        
        # Process URLs in batches
        processed_urls = []
        
        with tqdm(total=total_urls, desc="Processing URLs", unit="URL") as pbar:
            if use_threads and total_urls > 1000:
                # Multithreaded processing
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    # Submit batches to executor
                    batch_size = max(100, total_urls // (self.max_workers * 4))
                    futures = []
                    
                    current_batch = []
                    for url in EnhancedFileHandler.read_urls_safely(input_file):
                        current_batch.append(url)
                        if len(current_batch) >= batch_size:
                            future = executor.submit(self.process_url_batch, current_batch)
                            futures.append(future)
                            current_batch = []
                    
                    # Submit remaining URLs
                    if current_batch:
                        future = executor.submit(self.process_url_batch, current_batch)
                        futures.append(future)
                    
                    # Collect results
                    for future in as_completed(futures):
                        try:
                            batch_unique, batch_duplicates, invalid, normalized = future.result()
                            
                            # Update global state
                            self.unique_urls.update(batch_unique)
                            self.duplicate_samples.extend(batch_duplicates[:5])  # Keep samples
                            self.stats["invalid"] += invalid
                            self.stats["normalized"] += normalized
                            
                            # Update progress
                            processed_count = len(batch_unique) + len(batch_duplicates) + invalid
                            pbar.update(processed_count)
                            
                        except Exception as e:
                            logger.error(f"Error processing batch: {e}")
            else:
                # Sequential processing
                batch = []
                for url in EnhancedFileHandler.read_urls_safely(input_file):
                    batch.append(url)
                    if len(batch) >= 1000:
                        self._process_batch_sequential(batch, pbar)
                        batch = []
                
                # Process remaining URLs
                if batch:
                    self._process_batch_sequential(batch, pbar)
        
        # Calculate final statistics
        self.stats["unique"] = len(self.unique_urls)
        self.stats["duplicates"] = total_urls - self.stats["unique"] - self.stats["invalid"]
        self.stats["processing_time"] = time.time() - start_time
        self.stats["urls_per_second"] = total_urls / self.stats["processing_time"]
        
        # Write output
        logger.info("Writing output file...")
        unique_url_list = list(self.unique_urls.values())
        
        # Write in batches for better performance
        batch_size = EnhancedConfig.BATCH_WRITE_SIZE
        for i in range(0, len(unique_url_list), batch_size):
            batch = unique_url_list[i:i + batch_size]
            EnhancedFileHandler.write_urls_batch(batch, output_file, append=i > 0)
        
        # Display results
        self._display_results(verbose)
        
        return self.stats
    
    def _process_batch_sequential(self, batch: List[str], pbar: tqdm) -> None:
        """Process batch sequentially"""
        batch_unique, batch_duplicates, invalid, normalized = self.process_url_batch(batch)
        
        self.unique_urls.update(batch_unique)
        self.duplicate_samples.extend(batch_duplicates[:5])
        self.stats["invalid"] += invalid
        self.stats["normalized"] += normalized
        
        pbar.update(len(batch))
    
    def _display_results(self, verbose: bool) -> None:
        """Display processing results"""
        stats = self.stats
        
        logger.info(f"\n{Fore.GREEN}=== Processing Complete ==={Style.RESET_ALL}")
        logger.info(f"Total URLs processed: {stats['total']:,}")
        logger.info(f"Unique URLs: {stats['unique']:,}")
        logger.info(f"Duplicates removed: {stats['duplicates']:,}")
        logger.info(f"Invalid URLs skipped: {stats['invalid']:,}")
        logger.info(f"URLs normalized: {stats['normalized']:,}")
        logger.info(f"Processing time: {stats['processing_time']:.2f}s")
        logger.info(f"Processing speed: {stats['urls_per_second']:.0f} URLs/sec")
        
        if stats['total'] > 0:
            efficiency = (stats['unique'] / stats['total']) * 100
            logger.info(f"Deduplication efficiency: {efficiency:.1f}%")
        
        if verbose and self.duplicate_samples:
            logger.info(f"\nSample duplicates found:")
            for i, dup in enumerate(self.duplicate_samples[:5], 1):
                logger.info(f"  {i}. {dup['duplicate']}")
                logger.info(f"     -> Duplicate of: {dup['original']}")

def setup_logging(debug: bool = False) -> logging.Logger:
    """Setup enhanced logging"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s]%(reset)s %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    logger = colorlog.getLogger('urlf')
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    return logger

def main():
    """ main function with better error handling"""
    parser = argparse.ArgumentParser(
        description="A tool to filter and deduplicate URLs based on domain and query parameter NAMES only.",
        epilog="""
USAGE EXAMPLES:
  Basic usage:
    python3 urlf.py input.txt output.txt
    
  With verbose output and JSON export:
    python3 urlf.py input.txt output.txt -v -j
    
  Generate detailed report with custom thread count:
    python3 urlf.py input.txt output.txt -r -w 20
    
  Sequential processing (no multithreading):
    python3 urlf.py input.txt output.txt -s
    
  Full featured run with all options:
    python3 urlf.py input.txt output.txt -v -j -r -w 15 --debug

HOW IT WORKS:
  • URLs are deduplicated based on domain + parameter names (not values)
  • Parameter order doesn't matter: ?id=1&name=test = ?name=test&id=1
  • Parameter values don't matter: ?id=1 = ?id=2 = ?id=999 (all duplicates)
  • Different parameter names are unique: ?q=python ≠ ?query=python
  • Invalid URLs are skipped and counted in statistics
  
OUTPUT FILES:
  • Main output: unique URLs in plain text format
  • JSON export (-j): structured data with statistics
  • Detailed report (-r): comprehensive analysis with domain/parameter stats

Note: This tool auto-cleans your input file to remove malformed or non-UTF8 characters.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_file', help='Input file containing URLs')
    parser.add_argument('output_file', help='Output file for unique URLs')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-s', '--sequential', action='store_true', help='Disable multithreading')
    parser.add_argument('-w', '--workers', type=int, default=EnhancedConfig.MAX_WORKERS, help=f'Number of workers (default: {EnhancedConfig.MAX_WORKERS})')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-j', '--json', action='store_true', help='Export results as JSON')
    parser.add_argument('--version', action='version', version=f'%(prog)s {EnhancedConfig.VERSION}', help='Show the version of the script')
    
    args = parser.parse_args()
    
    # Setup logging
    global logger
    logger = setup_logging(args.debug)
    
    try:
        # Validate input file
        if not os.path.exists(args.input_file):
            logger.error(f"Input file not found: {args.input_file}")
            return 1
        
        # Process URLs
        processor = EnhancedURLProcessor(args.workers)
        stats = processor.process_file(
            args.input_file,
            args.output_file,
            verbose=args.verbose,
            use_threads=not args.sequential
        )
        
        # Export JSON if requested
        if args.json:
            json_file = args.output_file.replace('.txt', '.json')
            json_data = {
                'metadata': {
                    'tool': EnhancedConfig.TOOL_NAME,
                    'version': EnhancedConfig.VERSION,
                    'timestamp': datetime.now().isoformat(),
                    'input_file': args.input_file,
                    'output_file': args.output_file
                },
                'statistics': stats,
                'unique_urls': list(processor.unique_urls.values())
            }
            
            EnhancedFileHandler.safe_json_dump(json_data, json_file)
            logger.info(f"JSON export saved: {json_file}")
        
        logger.info(f"Processing complete! Output saved to: {args.output_file}")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    print_banner()
    sys.exit(main())
