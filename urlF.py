#!/usr/bin/env python3
import urllib.parse
import argparse
import art
import logging
import colorlog
from tqdm import tqdm
import os
import sys
import random
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from colorama import Fore, Style, init
from typing import Dict, List, Set, Tuple, FrozenSet, Optional, Iterator, Any, Union

# Initialize colorama
init(autoreset=True)


class Config:
    """Configuration settings for the URL Filtering Tool."""
    TOOL_NAME = "URLF"
    VERSION = "2.0"
    AUTHOR = "0xBobby"
    COLORS = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN
    ]
    MAX_WORKERS = 10  # Maximum number of threads for parallel processing
    CHUNK_SIZE = 1000  # Number of URLs to process in each chunk
    DEFAULT_LOG_LEVEL = logging.INFO


class Logger:
    """Handles all logging functionality with colored output."""
    
    @staticmethod
    def setup(log_level: int = Config.DEFAULT_LOG_LEVEL) -> logging.Logger:
        """Configure and return a colored logger instance."""
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s: %(message)s"))
        logger = colorlog.getLogger()
        logger.handlers = []  # Clear existing handlers
        logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger


class URLValidator:
    """Handles URL validation and parameter extraction."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if a string is a valid URL."""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def extract_parameters(url: str) -> FrozenSet[str]:
        """Extract parameters from a URL into a frozenset for comparison."""
        try:
            if not URLValidator.is_valid_url(url):
                return frozenset(["Invalid URL"])
                
            parsed_url = urllib.parse.urlparse(url.lower())
            query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            return frozenset(query_params.keys()) if query_params else frozenset(["No parameters"])
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            return frozenset(["Error extracting parameters"])


class Display:
    """Handles all display and UI elements."""
    
    @staticmethod
    def random_color() -> str:
        """Return a random color from the COLORS list."""
        return random.choice(Config.COLORS)
    
    @staticmethod
    def generate_ascii_header(text: str, font: str = 'digital') -> str:
        """Generate ASCII art header text."""
        try:
            return art.text2art(text, font=font)
        except Exception as e:
            logger.error(f"Error generating ASCII art header: {e}")
            return f"Error: {e}"
    
    @staticmethod
    def show_banner() -> None:
        """Display the tool banner with randomly colored version and author information."""
        header = Display.generate_ascii_header(Config.TOOL_NAME, font='digital')
        tool_color, version_color, author_color = (
            Display.random_color(), 
            Display.random_color(), 
            Display.random_color()
        )
        
        header_colored = "".join([
            tool_color + line + Style.RESET_ALL + "\n" 
            for line in header.split('\n')
        ])
        
        additional_lines = (
            f"\n{version_color}Version {Config.VERSION}{Style.RESET_ALL} by "
            f"{author_color}{Config.AUTHOR}{Style.RESET_ALL}\n"
            f"Happy hacking \\(^-^)/ \n"
        )
        
        print(header_colored + additional_lines)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
    
    @staticmethod
    def print_stats(stats: Dict[str, Any]) -> None:
        """Print statistics about the URL processing."""
        logger.info(f"{Fore.GREEN}Total URLs processed: {stats['total']}{Style.RESET_ALL}")
        logger.info(f"{Fore.RED}Duplicates removed: {stats['duplicates']}{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}Unique URLs remaining: {stats['unique']}{Style.RESET_ALL}")
        logger.info(f"{Fore.RED}Invalid URLs skipped: {stats['invalid']}{Style.RESET_ALL}")
        
        if stats['total'] > 0:
            accuracy = (stats['unique'] / stats['total']) * 100
            logger.info(f"Filtering accuracy: {accuracy:.2f}%")
    
    @staticmethod
    def print_duplicate_samples(duplicate_params: List[FrozenSet[str]], limit: int = 5) -> None:
        """Print sample duplicate parameter sets for verbose output."""
        if duplicate_params:
            logger.info("Sample duplicate parameter sets detected:")
            for dup_params in duplicate_params[:limit]:
                logger.info(f"  - {', '.join(dup_params) if dup_params else 'No parameters'}")


class FileHandler:
    """Handles all file operations."""
    
    @staticmethod
    def ensure_output_directory(output_file: str) -> None:
        """Ensure the output directory exists."""
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

    @staticmethod
    def read_urls_in_chunks(filename: str, chunk_size: int = Config.CHUNK_SIZE) -> Iterator[List[str]]:
        """Read URLs from file in chunks to avoid loading large files into memory."""
        with open(filename, 'r') as f:
            chunk = []
            for i, line in enumerate(f):
                if line.strip():
                    chunk.append(line.strip())
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            if chunk:  # Don't forget the last chunk
                yield chunk
    
    @staticmethod
    def write_urls_to_file(urls: List[str], output_file: str) -> None:
        """Write URLs to output file."""
        FileHandler.ensure_output_directory(output_file)
        with open(output_file, 'w') as f:
            for url in urls:
                f.write(f"{url}\n")
    
    @staticmethod
    def save_as_json(data: Dict[str, Any], output_file: str) -> str:
        """Save data as JSON and return the filename."""
        json_filename = output_file.replace('.txt', '.json')
        if json_filename == output_file:
            json_filename = f"{output_file}.json"
            
        FileHandler.ensure_output_directory(json_filename)
        with open(json_filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return json_filename
    
    @staticmethod
    def save_stats_report(stats: Dict[str, Any], output_file: str) -> str:
        """Save statistics report and return the filename."""
        report_filename = output_file.replace('.txt', '_report.txt')
        if report_filename == output_file:
            report_filename = f"{output_file}_report.txt"
            
        FileHandler.ensure_output_directory(report_filename)
        with open(report_filename, 'w') as report_file:
            report_file.write(f"URL Filtering Report\n")
            report_file.write(f"=================\n")
            report_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            report_file.write(f"Statistics:\n")
            report_file.write(f"  Total URLs processed: {stats['total']}\n")
            report_file.write(f"  Unique URLs: {stats['unique']}\n")
            report_file.write(f"  Duplicates removed: {stats['duplicates']}\n")
            report_file.write(f"  Invalid URLs skipped: {stats['invalid']}\n")
            
            if stats['total'] > 0:
                accuracy = (stats['unique'] / stats['total']) * 100
                report_file.write(f"  Filtering accuracy: {accuracy:.2f}%\n")
            
            report_file.write(f"\nTop domains:\n")
            for domain, count in stats['domains'].most_common(10):
                report_file.write(f"  {domain}: {count} URLs\n")
            
            report_file.write(f"\nCommon parameters:\n")
            for param, count in stats['parameters'].most_common(10):
                report_file.write(f"  {param}: {count} occurrences\n")
                
        return report_filename


class URLProcessor:
    """Main class for URL processing logic."""
    
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance
        self.stats = {
            "total": 0,
            "duplicates": 0,
            "unique": 0,
            "invalid": 0,
            "domains": None,
            "parameters": None
        }
        self.unique_urls = {}  # (domain, param_set) -> url
        self.duplicate_params = []  # Store duplicate parameter sets for verbose mode
    
    def process_url_chunk(self, urls: List[str]) -> Dict[Tuple[str, FrozenSet[str]], str]:
        """Process a chunk of URLs and return unique URLs in that chunk."""
        chunk_unique_urls = {}
        
        for url in urls:
            if not URLValidator.is_valid_url(url):
                self.stats["invalid"] += 1
                continue
                
            parsed_url = urllib.parse.urlparse(url.lower())
            domain = parsed_url.netloc
            param_set = URLValidator.extract_parameters(url)
            url_key = (domain, param_set)
            
            if url_key not in self.unique_urls and url_key not in chunk_unique_urls:
                chunk_unique_urls[url_key] = url
            else:
                self.duplicate_params.append(param_set)
        
        return chunk_unique_urls
    
    def process_file(self, input_file: str, output_file: str, 
                    verbose: bool = False, 
                    use_threads: bool = True,
                    export_json: bool = False,
                    export_report: bool = True) -> Dict[str, Any]:
        """
        Process a file of URLs, removing duplicates based on domain and parameters.
        
        Args:
            input_file: Path to input file containing URLs
            output_file: Path to write unique URLs
            verbose: Whether to show detailed output
            use_threads: Whether to use multithreading
            export_json: Whether to export results as JSON
            export_report: Whether to generate a detailed report
            
        Returns:
            Statistics dictionary with processing results
        """
        from collections import Counter
        
        self.stats["domains"] = Counter()
        self.stats["parameters"] = Counter()
        
        # Check if input file exists
        if not os.path.exists(input_file):
            self.logger.error(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        
        # Count total lines to set up progress bar
        try:
            with open(input_file, 'r') as f:
                total_lines = sum(1 for line in f if line.strip())
            self.stats["total"] = total_lines
        except Exception as e:
            self.logger.error(f"Error counting lines in file: {e}")
            sys.exit(1)
            
        if self.stats["total"] == 0:
            self.logger.warning("Input file is empty. No URLs to process.")
            return self.stats
        
        self.logger.info(f"Processing {self.stats['total']} URLs from {input_file}")
        
        # Process file in chunks
        with tqdm(total=self.stats["total"], desc='Processing URLs', unit=' URLs') as pbar:
            # Use ThreadPoolExecutor for parallel processing if enabled
            if use_threads and self.stats["total"] > Config.CHUNK_SIZE:
                self.logger.info(f"Using multithreading with {Config.MAX_WORKERS} workers")
                with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
                    futures = []
                    
                    for chunk in FileHandler.read_urls_in_chunks(input_file):
                        futures.append(executor.submit(self.process_url_chunk, chunk))
                        pbar.update(len(chunk))
                    
                    for future in futures:
                        chunk_results = future.result()
                        self.unique_urls.update(chunk_results)
            else:
                # Sequential processing
                for chunk in FileHandler.read_urls_in_chunks(input_file):
                    chunk_results = self.process_url_chunk(chunk)
                    self.unique_urls.update(chunk_results)
                    pbar.update(len(chunk))
        
        # Update statistics
        self.stats["unique"] = len(self.unique_urls)
        self.stats["duplicates"] = self.stats["total"] - self.stats["unique"] - self.stats["invalid"]
        
        # Extract domain and parameter statistics
        for (domain, param_set), url in self.unique_urls.items():
            self.stats["domains"][domain] += 1
            for param in param_set:
                if param not in ["No parameters", "Invalid URL", "Error extracting parameters"]:
                    self.stats["parameters"][param] += 1
        
        # Write unique URLs to output file
        FileHandler.write_urls_to_file(list(self.unique_urls.values()), output_file)
        
        # Display statistics
        Display.print_stats(self.stats)
        
        # Display verbose information if requested
        if verbose and self.stats['duplicates'] > 0:
            Display.print_duplicate_samples(self.duplicate_params)
        
        # Export JSON if requested
        if export_json:
            json_data = {
                "unique_urls": list(self.unique_urls.values()),
                "statistics": {
                    "total": self.stats["total"],
                    "unique": self.stats["unique"],
                    "duplicates": self.stats["duplicates"],
                    "invalid": self.stats["invalid"]
                }
            }
            json_filename = FileHandler.save_as_json(json_data, output_file)
            self.logger.info(f"JSON report saved: {json_filename}")
        
        # Export detailed report if requested
        if export_report:
            report_filename = FileHandler.save_stats_report(self.stats, output_file)
            self.logger.info(f"Detailed report saved: {report_filename}")
        
        return self.stats


def parse_arguments() -> argparse.Namespace:
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"{Config.TOOL_NAME} v{Config.VERSION}: A tool to filter and deduplicate URLs based on domain and query parameters."
    )
    parser.add_argument('input_file', help='Path to the input file containing the list of URLs')
    parser.add_argument('output_file', help='Path to the output file where unique URLs will be written')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output showing duplicate URLs')
    parser.add_argument('-j', '--json', action='store_true', help='Save output as JSON without prompting')
    parser.add_argument('-r', '--report', action='store_true', help='Generate a detailed statistics report')
    parser.add_argument('-s', '--sequential', action='store_true', help='Disable multithreading for sequential processing')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--version', action='version', version=f'%(prog)s {Config.VERSION}', help='Show the version of the script')
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the application."""
    # Parse arguments
    args = parse_arguments()
    
    # Show banner for help or normal operation
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        Display.show_banner()
    
    if '--help' not in sys.argv and '-h' not in sys.argv and len(sys.argv) > 1:
        Display.show_banner()
    
    # Configure logging
    global logger
    logger = Logger.setup(logging.DEBUG if args.debug else logging.INFO)
    
    # Initialize processor
    processor = URLProcessor(logger)
    
    # Process file
    processor.process_file(
        args.input_file, 
        args.output_file,
        verbose=args.verbose,
        use_threads=not args.sequential,
        export_json=args.json,
        export_report=args.report
    )
    
    # If JSON export wasn't done via command line, ask interactively
    if not args.json:
        save_json = input("Do you want to save output as JSON? (y/n): ").strip().lower()
        if save_json == 'y':
            json_data = {
                "unique_urls": list(processor.unique_urls.values()),
                "statistics": {
                    "total": processor.stats["total"],
                    "unique": processor.stats["unique"],
                    "duplicates": processor.stats["duplicates"],
                    "invalid": processor.stats["invalid"]
                }
            }
            json_filename = FileHandler.save_as_json(json_data, args.output_file)
            logger.info(f"JSON report saved: {json_filename}")


if __name__ == "__main__":
    main()