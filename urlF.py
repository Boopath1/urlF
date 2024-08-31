import urllib.parse
import argparse
import art
import logging
import colorlog
from tqdm import tqdm

# Configure colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(message)s"
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def extract_parameters(url: str) -> frozenset:
    try:
        parsed_url = urllib.parse.urlparse(url.lower())
        query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
        return frozenset(query_params.keys())
    except Exception as e:
        logger.error(f"Error extracting parameters: {e}")
        return None

def generate_ascii_header(text: str, font: str ='standard') -> str:
    try:
        return art.text2art(text, font=font)
    except Exception as e:
        logger.error(f"Error generating ASCII art header: {e}")
        return f"Error: {e}"

def process_file(input_file: str, output_file: str) -> None:
    unique_param_sets = set()
    unique_urls = {}
    logger.info("Starting the URL filtering process...")

    try:
        with open(input_file, 'r') as infile:
            total_lines = sum(1 for line in infile)

        with open(input_file, 'r') as infile, tqdm(total=total_lines, desc='Processing URLs', unit=' URLs') as pbar:
            for line in infile:
                url = line.strip()
                if url:
                    param_set = extract_parameters(url)
                    if param_set and param_set not in unique_param_sets:
                        unique_param_sets.add(param_set)
                        unique_urls[url] = url
                    pbar.update(1)

        logger.info(f"Processed {len(unique_urls)} unique URLs.")

        header = generate_ascii_header("URLF", font='digital')
        additional_lines = "\nby Bobby\nHappy hacking \(^-^)/ \n"
        print(header + additional_lines)

        with open(output_file, 'w') as outfile:
            for url in unique_urls.values():
                outfile.write(url + '\n')

        logger.info(f"Filtering complete. {len(unique_urls)} unique URLs written to {output_file}.")

    except FileNotFoundError:
        logger.error(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        logger.error(f"Error during processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Filter-Query: A script to remove duplicate URLs based on query parameters.\n"
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
        '--version',
        action='version',
        version='%(prog)s 1.0',
        help='Show the version of the script'
    )
    
    args = parser.parse_args()
    
    process_file(args.input_file, args.output_file)
