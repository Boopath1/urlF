# URLF - URL Filter Tool v2.4

<div align="center">

```
 █    █ ██████  █       █████
 █    █ █    █  █       █    
 █    █ █████   █       █████
 █    █ █    █  █       █    
 ██████ █    █  ██████  █    
```

**A powerful Python tool for filtering and deduplicating URLs based on domain and query parameter names.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.4-orange.svg)](https://github.com/Boopath1/urlf)

*Created by 0xBobby*

</div>

## 🚀 Features

- **Smart Deduplication**: Removes duplicate URLs based on domain + parameter names (not values)
- **Parameter Order Agnostic**: `?id=1&name=test` = `?name=test&id=1`
- **Value Independent**: `?id=1` = `?id=2` = `?id=999` (all treated as duplicates)
- **High Performance**: Multithreaded processing with configurable worker count
- **Memory Efficient**: Chunk-based processing for large files
- **Progress Tracking**: Real-time progress bar with processing statistics
- **Multiple Output Formats**: Plain text, JSON, and detailed reports
- **Comprehensive Statistics**: Domain analysis, parameter frequency, and filtering accuracy
- **Colored Output**: Beautiful colored terminal output for better readability

## 📋 Requirements

- Python 3.8 or higher
- Required packages (install via `pip install -r requirements.txt`):
  ```
  art
  colorlog
  tqdm
  colorama
  ```

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Boopath1/urlF.git
   cd urlf
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make it executable:**
   ```bash
   chmod +x urlf.py
   ```

## 📖 Usage

### Basic Usage
```bash
python3 urlf.py input.txt output.txt
```

### Advanced Usage
```bash
# With verbose output and JSON export
python3 urlf.py input.txt output.txt -v -j

# Generate detailed report with custom thread count
python3 urlf.py input.txt output.txt -r -w 20

# Sequential processing (no multithreading)
python3 urlf.py input.txt output.txt -s

# Full featured run with all options
python3 urlf.py input.txt output.txt -v -j -r -w 15 --debug
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output showing duplicate parameter sets |
| `-j, --json` | Save output as JSON without prompting |
| `-r, --report` | Generate a detailed statistics report |
| `-s, --sequential` | Disable multithreading for sequential processing |
| `-d, --debug` | Enable debug logging |
| `-w, --workers` | Number of worker threads (default: 10) |
| `--version` | Show version information |
| `-h, --help` | Show help message with usage examples |

## 🔧 How It Works

### Deduplication Logic

The tool uses a sophisticated deduplication algorithm:

1. **URL Parsing**: Each URL is parsed to extract domain and query parameters
2. **Parameter Name Extraction**: Only parameter names are considered, values are ignored
3. **Unique Key Generation**: Creates a unique key using `(domain, frozenset(parameter_names))`
4. **Duplicate Detection**: URLs with identical keys are marked as duplicates
5. **First Occurrence Wins**: The first URL encountered with a unique key is kept

### Example Processing

**Input URLs:**
```
https://example.com/page?id=1&name=test
https://example.com/page?name=test&id=1
https://example.com/page?id=2&name=demo
https://google.com/search?q=python
https://google.com/search?q=java
https://google.com/search?query=different
https://facebook.com/profile
https://facebook.com/profile?tab=about
```

**Processing Steps:**
```
✅ https://example.com/page?id=1&name=test     → UNIQUE (domain: example.com, params: {id, name})
❌ https://example.com/page?name=test&id=1     → DUPLICATE (same domain + same params)
❌ https://example.com/page?id=2&name=demo     → DUPLICATE (same domain + same params)
✅ https://google.com/search?q=python          → UNIQUE (domain: google.com, params: {q})
❌ https://google.com/search?q=java            → DUPLICATE (same domain + same params)
✅ https://google.com/search?query=different   → UNIQUE (domain: google.com, params: {query})
✅ https://facebook.com/profile                → UNIQUE (domain: facebook.com, params: {})
✅ https://facebook.com/profile?tab=about      → UNIQUE (domain: facebook.com, params: {tab})
```

**Output:**
```
https://example.com/page?id=1&name=test
https://google.com/search?q=python
https://google.com/search?query=different
https://facebook.com/profile
https://facebook.com/profile?tab=about
```

## 📊 Output Files

### 1. Main Output File (`output.txt`)
Plain text file containing unique URLs, one per line.

### 2. JSON Export (`output.json`)
Structured data with URLs and statistics:
```json
{
    "unique_urls": [
        "https://example.com/page?id=1&name=test",
        "https://google.com/search?q=python"
    ],
    "statistics": {
        "total": 8,
        "unique": 5,
        "duplicates": 2,
        "invalid": 1
    }
}
```

### 3. Detailed Report (`output_report.txt`)
Comprehensive analysis including:
- Processing statistics
- Top domains by frequency
- Most common parameters
- Filtering accuracy percentage

## 🔍 Performance

- **Memory Efficient**: Processes files in 1000-URL chunks
- **Multithreaded**: Uses ThreadPoolExecutor for parallel processing
- **Scalable**: Handles files with millions of URLs
- **Progress Tracking**: Real-time progress updates with ETA

### Benchmarks
| File Size | URLs | Processing Time | Memory Usage |
|-----------|------|----------------|--------------|
| 1 MB | 10K URLs | ~2 seconds | <50 MB |
| 10 MB | 100K URLs | ~15 seconds | <100 MB |
| 100 MB | 1M URLs | ~2 minutes | <200 MB |

## 🚨 Error Handling

The tool gracefully handles:
- **Invalid URLs**: Skipped and counted in statistics
- **Empty files**: Warning message with graceful exit
- **Large files**: Chunk-based processing prevents memory issues
- **Network interruptions**: Ctrl+C handling for clean exit
- **File permissions**: Clear error messages for access issues

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🎉 Acknowledgments

- Built with ❤️ for the bug bounty and security testing community

---

<div align="center">
<b>Happy Hacking! \(^-^)/</b>
</div>
