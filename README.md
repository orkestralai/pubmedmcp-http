# PubMed MCP - HTTP Streamable Server

A **Model Context Protocol (MCP) server** that provides HTTP-streamable access to PubMed data. This server implements the **StreamableHTTP transport** in stateless mode, making it ideal for web-based applications and distributed deployments.

PubMed is a database of over 35 million citations for biomedical literature from MEDLINE, life science journals, and online books.

This MCP server relies on the [pubmedclient](https://github.com/grll/pubmedclient) Python package to perform the search and fetch operations.

## 🏢 About OrkestralAI

[OrkestralAI](https://www.orkestralai.com) empowers users to build, deploy, and manage trustworthy AI agents with ease. Our platform enables anyone to design complex AI workflows visually, integrate third-party services, and automate tasks—no coding required. We believe in ubiquitous, portable AI agents that adapt to your needs, freeing you to focus on what matters most.

## 🚀 Quick Start

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/orkestralai/pubmedmcp-http)

Or deploy manually:

```bash
# Clone the repository
git clone https://github.com/orkestralai/pubmedmcp-http.git
cd pubmedmcp-http

# Install dependencies
uv sync

# Run locally
uv run pubmedmcp --port 3000
```

## 🚀 Key Features

- **HTTP-Streamable MCP**: Uses the StreamableHTTP transport instead of stdio
- **Stateless Architecture**: No session state maintained between requests
- **Web-Ready**: Perfect for browser-based clients and web applications
- **Scalable**: Suitable for deployment in multi-node environments
- **RESTful API**: Standard HTTP methods (GET, POST, DELETE) for MCP operations
- **CORS Support**: Ready for cross-origin requests from web browsers

## 📖 Usage

### Local Development

Start the HTTP-streamable MCP server:

```bash
# Using default port 3000
uv run pubmedmcp

# Using custom port
uv run pubmedmcp --port 8080

# Custom logging level
uv run pubmedmcp --log-level DEBUG

# Enable JSON responses instead of SSE streams
uv run pubmedmcp --json-response
```

### Client Configuration

For HTTP-based MCP clients, connect to the server at:
- **Base URL**: `http://127.0.0.1:3000/mcp`
- **HTTP Methods**: GET, POST, DELETE
- **Headers**: Include `Mcp-Session-Id` header for session management
- **Content-Type**: `application/json` for POST requests

### Example HTTP Client Usage

```bash
# List available tools
curl -X GET http://127.0.0.1:3000/mcp \
  -H "Mcp-Session-Id: test-session-123"

# Search PubMed abstracts
curl -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: test-session-123" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "search_abstracts",
      "arguments": {
        "term": "asthma treatment",
        "retmax": 5
      }
    }
  }'
```

### Tools Available

The server exposes a tool named "search_abstracts" that accepts the following arguments:

- `term` (required): Entrez text query for searching PubMed
- `retmax` (optional): Number of UIDs to return (default=20, max=10000)
- `sort` (optional): Sort method (pub_date, Author, JournalName, relevance)
- `field` (optional): Search field to limit entire search
- `datetype` (optional): Type of date (mdat, pdat, edat)
- `reldate` (optional): Items within the last n days
- `mindate` (optional): Start date for date range (YYYY/MM/DD format)
- `maxdate` (optional): End date for date range (YYYY/MM/DD format)

## 🚀 Deployment

### Vercel Deployment (Recommended)

This project is configured for easy deployment to Vercel:

1. **Quick Deploy**: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/orkestralai/pubmedmcp-http)

2. **Manual Deploy**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel
   ```

3. **Environment Variables** (optional):
   - `LOG_LEVEL`: Set logging level (default: INFO)

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed deployment instructions.

### Other Deployment Options

- **Docker**: Create a Dockerfile for containerized deployment
- **Railway**: Deploy as a web service
- **Heroku**: Deploy as a web dyno
- **AWS Lambda**: Use serverless framework

## 🧪 Testing

You can test the server using:

1. **HTTP clients** (curl, Postman, etc.) - see examples above
2. **[MCP Inspector](https://github.com/modelcontextprotocol/inspector)** - for interactive testing
3. **Web browsers** - the server supports CORS for browser-based clients

### Live Demo

Once deployed to Vercel, your server will be available at:
- **Production URL**: `https://your-project-name.vercel.app/mcp`
- **Test with curl**: See examples in the usage section above

### Example Usage

```bash
# List available tools
curl -X GET https://your-project-name.vercel.app/mcp \
  -H "Mcp-Session-Id: test-session-123"

# Search PubMed abstracts
curl -X POST https://your-project-name.vercel.app/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: test-session-123" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "search_abstracts",
      "arguments": {
        "term": "asthma treatment",
        "retmax": 5
      }
    }
  }'
```

## 🔧 Development

### Project Structure

```
pubmedmcp-http/
├── api/
│   └── index.py             # Vercel serverless function handler
├── src/pubmedmcp/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   └── server.py            # HTTP-streamable MCP server
├── pyproject.toml           # Project configuration
├── requirements.txt         # Python dependencies for Vercel
├── vercel.json             # Vercel deployment configuration
├── README.md               # This file
└── LICENSE                 # MIT License
```

### Dependencies

- **mcp**: Model Context Protocol implementation
- **pubmedclient**: PubMed API client
- **starlette**: ASGI web framework
- **uvicorn**: ASGI server
- **anyio**: Async I/O utilities
- **click**: CLI framework
- **httpx**: HTTP client

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.