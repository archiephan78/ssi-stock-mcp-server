# SSI Stock MCP Server

A Message Control Protocol (MCP) server for SSI Stock integration.

## Introduction

SSI Stock MCP Server is a server that uses the Message Control Protocol (MCP) to integrate and communicate with the SSI Stock system. This project allows you to securely and easily retrieve stock data (include intraday data) from SSI via API.

## System Requirements

- Python >= 3.8
- pip >= 20.0
- Operating System: Linux, macOS, or Windows

## Installation

1. Clone the repository:
    ```bash
    git clone <repo-url>
    cd mcp-ssi-stock-server
    ```
2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install .
    ```

## Configuration

The server requires the following environment variables:

- `SSI_API_URL`: The URL of the SSI Stock API server
- `SSI_API_KEY`: Your SSI Stock API key

You can create a `.env` file in the project root with the following content:
```
SSI_API_URL=https://api.ssi.com.vn/stock
SSI_API_KEY=your_api_key_here
```

## Usage

To run the server:
```bash
ssi-stock-mcp-server
```

Example requests/responses or API endpoints will be added if detailed API documentation is available.

## Development

1. Install development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```
2. Run tests:
    ```bash
    pytest
    ```
3. Check code style:
    ```bash
    flake8
    ```

Contributions are welcome! Please open a pull request or an issue on GitHub.

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Contact / Support

- Please open an issue on GitHub if you encounter any problems or need support.
- Email: your.email@example.com
