# Url's - Filter by - Parameters

`urlF.py` is a Python script designed to remove duplicate URLs based on both the base URL (including path) and their query parameters. The script processes a list of URLs from an input file, filters out duplicates based on their query parameters, and writes the unique URLs to an output file.

---

## 🚀 Installation

You can install `urlF.py` using **GitHub** or **PyPI**.

### **Option 1: Install from GitHub**
> **Step 1: Clone the Repository**
```sh
git clone https://github.com/Boopath1/urlF.py
```
or

```sh
git clone --depth 1 https://github.com/Boopath1/urlF.py
```

Install the required dependencies:
> Step 2
```sh
pip3 install -r requirements.txt  # or pip install -r requirements.txt
```

### **Option 2: Install from PyPI**
> **Step 1: Install via pip**
```sh
pip install urlf  # Standard installation
```

Alternative: If Facing System Restrictions
```sh
pip install urlf --break-system-packages  # For some restricted environments
```

## Usage
> Step 1
```sh
python3 -m urlf <input_file> <output_file>
```

- `<input_file>`: Path to the input file containing the list of URLs.
- `<output_file>`: Path to the output file where unique URLs will be written.


Basic usage:
> Step 2
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

## 📊 Comparison with Other Tools

| Tool           | Functionality | Limitation |
|---------------|--------------|------------|
| **`sort`**        | Orders URLs alphabetically | Does not filter based on query parameters |
| **`urldedupe`**   | Removes exact duplicate URLs | Cannot analyze query parameter uniqueness |
| **`uro`**         | Normalizes and deduplicates URLs | Does not focus on parameter-based filtering |
| **`urlF.py`**     | Filter URLs based on both the base URL (including path) and their query parameters | Provides better query-based filtering and cleanup |


## Sample POC

The timing is also mentioned on the right side. You can verify that this script takes little time compared to other tools.

![image](https://github.com/user-attachments/assets/eec38c30-b47e-4729-a25d-f00cbc3761e0)

## **🔹 Why Run This After paramspider?**
- When running `paramspider`, you’ll often get duplicate parameters.
- Instead of scanning the same parameter multiple times, use urlF.py to filter results efficiently.

![image](https://github.com/user-attachments/assets/1f9bdbab-016d-4f53-91fa-dcc5e2d80143)

![image](https://github.com/user-attachments/assets/8a552bb2-d3bb-4860-8ed8-02b345acc28a)

- Almost 2K URLs 😱

## **💡 Contributing**

Contributions are welcome! If you have suggestions or feature improvements, feel free to:
- Fork the repository and create a pull request.
- Open an issue if you encounter any bugs.

## **🎯 Final Thoughts**

- After enumerating all the URLs using tools like `waybackurls`, `gau`, `katana`, and others, use `urlF.py` to get unique URLs along with their parameters.
- This ensures efficient filtering, reduces redundant requests, and helps in better targeted testing.
- Optimized for security researchers and penetration testers to streamline the URL analysis process.

Happy Hacking! 🎯 🚀
