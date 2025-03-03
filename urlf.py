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
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Tool information
TOOL_NAME = "URLF"
VERSION = "1.1"
AUTHOR = "0xBobby"

# Color options for random selection
COLORS = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN
]

# Configure colored logging
def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(message)s"))
    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

def extract_parameters(url: str) -> frozenset:
    try:
        parsed_url = urllib.parse.urlparse(url.lower())
        query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
        return frozenset(query_params.keys())
    except Exception as e:
        logger.error(f"Error extracting parameters: {e}")
        return frozenset()

def generate_ascii_header(text: str, font: str ='digital') -> str:
    try:
        return art.text2art(text, font=font)
    except Exception as e:
        logger.error(f"Error generating ASCII art header: {e}")
        return f"Error: {e}"

def random_color():
    """Return a random color from the COLORS list"""
    return random.choice(COLORS)

def show_banner():
    """Display the tool banner with randomly colored version and author information"""
    header = generate_ascii_header(TOOL_NAME, font='digital')
    
    # Apply random colors to each component
    tool_color = random_color()
    version_color = random_color()
    author_color = random_color()
    
    header_colored = ""
    for line in header.split('\n'):
        header_colored += tool_color + line + Style.RESET_ALL + "\n"
    
    additional_lines = f"\n{version_color}Version {VERSION}{Style.RESET_ALL} by {author_color}{AUTHOR}{Style.RESET_ALL}\nHappy hacking \\(^-^)/ \n"
    
    print(header_colored + additional_lines)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

def process_file(input_file: str, output_file: str, verbose: bool = False) -> None:
    # Use the domain+param_set as the key to avoid filtering across domains
    unique_urls = {}  # (domain, param_set) -> url
    stats = {
        "total": 0,
        "duplicates": 0,
        "unique": 0
    }
    
    logger.info("Starting the URL filtering process...")
    
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            logger.error(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
            
        # Read input lines
        with open(input_file, 'r') as infile:
            lines = [line.strip() for line in infile if line.strip()]
        
        total_lines = len(lines)
        stats["total"] = total_lines
        
        if total_lines == 0:
            logger.warning("Input file is empty. No URLs to process.")
            return
            
        with tqdm(total=total_lines, desc='Processing URLs', unit=' URLs') as pbar:
            for url in lines:
                parsed_url = urllib.parse.urlparse(url.lower())
                domain = parsed_url.netloc
                param_set = extract_parameters(url)
                
                # Create a unique key that includes domain
                url_key = (domain, param_set)
                
                if url_key not in unique_urls:
                    unique_urls[url_key] = url
                    stats["unique"] += 1
                else:
                    stats["duplicates"] += 1
                    if verbose:
                        logger.debug(f"Duplicate found: {url}")
                
                pbar.update(1)
        
        # Write output
        with open(output_file, 'w') as outfile:
            for url in unique_urls.values():
                outfile.write(url + '\n')
        
        # Display statistics
        logger.info(f"Total URLs processed: {stats['total']}")
        logger.info(f"Duplicates removed: {stats['duplicates']}")
        logger.info(f"Unique URLs remaining: {stats['unique']}")
        logger.info(f"Filtering complete. {stats['unique']} unique URLs written to {output_file}.")
        
        # Calculate and display accuracy
        if stats['total'] > 0:
            accuracy = (stats['unique'] / stats['total']) * 100
            logger.info(f"Filtering accuracy: {accuracy:.2f}%")
    
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description=(
            f"{TOOL_NAME} v{VERSION}: A tool to filter and deduplicate URLs based on domain and query parameters."
        )
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input file containing the list of URLs'
    )
    parser.add_argument(
        'output_file',
        help='Path to the output file where unique URLs will be written'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output showing duplicate URLs'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {VERSION}',
        help='Show the version of the script'
    )
    
    # Check if --help or -h flag is passed
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        # Show banner before help
        show_banner()
    
    args = parser.parse_args()
    
    # Only show banner for normal operation (not with --help or -h)
    if '--help' not in sys.argv and '-h' not in sys.argv and len(sys.argv) > 1:
        show_banner()
    
    process_file(args.input_file, args.output_file, args.verbose)

if __name__ == "__main__":
    main()