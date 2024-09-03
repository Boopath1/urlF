# Url's - Filter by - Parameters
`urlF.py` is a Python script designed to remove duplicate URLs based on their query parameters. The script processes a list of URLs from an input file, filters out duplicates based on their query parameters, and writes the unique URLs to an output file.

## Installation

> Step 1
```sh
git clone https://github.com/Boopath1/urlF.py
```

Install the required dependencies:
> Step 2
```sh
pip3 install -r requirements.txt / or pip install -r requirements.txt
```

## Usage
```sh
python3 urlF.py <input_file> <output_file>
```

- `<input_file>`: Path to the input file containing the list of URLs.
- `<output_file>`: Path to the output file where unique URLs will be written.

Basic usage:
> Step 3
```sh
python3 urlF.py duplicate-params.txt filtered_urls.txt
```
`urlF.py`: The main script file. It processes URLs from an input file, removes duplicates based on query parameters, and writes the results to an output file.

## Example
The input file `duplicate-params.txt` might look like this:
<pre>
https://example.com/page?fileGuid=DPg868kv89HJtQ8q
https://example.com/page?fileGuid=DPg868kv89HJtQ8q&anotherParam=123
https://example.com/page?anotherParam=123
https://example.com/page?fileGuid=aAqwe868kv89HJtQ8q
https://example.com/page?fileGuid=DPg868kv89HJtQ8q&extraParam=xyz
https://example.com/page?extraParam=xyz
https://example.com/page?extraParam=xyz_Aqw
https://example.com/page?fileGuid=DifferentGuid
</pre>

The output file `filtered_urls.txt` will contain:
<pre>
https://example.com/page?fileGuid=DPg868kv89HJtQ8q
https://example.com/page?fileGuid=DPg868kv89HJtQ8q&anotherParam=123
https://example.com/page?anotherParam=123
https://example.com/page?fileGuid=DPg868kv89HJtQ8q&extraParam=xyz
https://example.com/page?extraParam=xyz
</pre>


## Features
If you're doing a mass scan, `urlF.py` can save you a lot of time. Even if you're using other tools like `sort`, `urldedupe`, or `uro`, this script has some extra filtering by query parameters that can make the results easier to work with and speed up the process.

## Comparison with Other Tools

### `sort`

- **Function**: Orders URLs alphabetically.
- **Limitation**: Does not remove duplicates based on query parameters or other content.

### `urldedupe`

- **Function**: Removes duplicate URLs by checking the full URL.
- **Limitation**: This may not handle complex query parameters or URL structures as effectively as a dedicated script.

### `uro`

- **Function**: URL normalization and deduplication.
- **Limitation**: Focuses on normalization which might not be sufficient for complex query parameter deduplication.

### `urlF.py`

- **Function**: Specifically designed to remove duplicates based on query parameters while preserving the structure of unique URLs.
- **Advantage**: Provides an additional layer of filtering by analyzing query parameters, which can be more precise and tailored for specific needs. Outputs a clear and concise list of unique URLs with minimized redundancy.

## Sample POC

The timing is also mentioned on the right side. You can verify that this script takes little time compared to other tools.

![image](https://github.com/user-attachments/assets/eec38c30-b47e-4729-a25d-f00cbc3761e0)

- Even if you ran `paramspider` you will get most of the duplicate parameters.
- What is the purpose of running multiple scans on the same parameter? I’m not criticizing any tools here. However, after running paramspider, using my tool next can help you save a significant amount of time.

![image](https://github.com/user-attachments/assets/1f9bdbab-016d-4f53-91fa-dcc5e2d80143)

## Contributing

If you have suggestions or improvements, you can create a pull request or open an issue.
