# api/index.py
"""
Vercel serverless function handler for PubMed MCP HTTP-streamable server.

This module provides a simple HTTP handler that implements the MCP protocol
for PubMed database searches using NCBI E-utilities API.
"""

import json
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """HTTP request handler for PubMed MCP server on Vercel."""

    def do_GET(self):
        """Handle GET requests"""
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = {
                "name": "PubMed MCP Server",
                "version": "1.0.0",
                "status": "running",
                "tools": 1,
                "description": "PubMed search MCP server for Vercel",
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            if post_data:
                try:
                    request_data = json.loads(post_data.decode("utf-8"))
                    response = handle_mcp_request(request_data)
                except json.JSONDecodeError as e:
                    response = create_error_response(-32700, f"Parse error: {str(e)}")
                except Exception as e:
                    response = create_error_response(
                        -32603, f"Internal error: {str(e)}"
                    )
            else:
                response = create_error_response(
                    -32600, "Invalid Request: No data received"
                )

            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key"
        )
        self.end_headers()


def handle_mcp_request(request_data):
    """Handle MCP protocol requests"""
    # Validate request structure
    if not isinstance(request_data, dict):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error: Invalid JSON"},
        }

    if "jsonrpc" not in request_data or request_data.get("jsonrpc") != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {
                "code": -32600,
                "message": "Invalid Request: Missing or invalid jsonrpc field",
            },
        }

    method = request_data.get("method")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {
                    "name": "PubMed MCP Server",
                    "version": "1.0.0",
                    "description": "HTTP-streamable MCP server for PubMed database searches",
                },
            },
        }

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": request_data.get("id"), "result": {}}

    elif method == "tools/list":
        tools = [
            {
                "name": "search_abstracts",
                "description": "Search abstracts on PubMed database based on the request parameters. Returns formatted text containing article titles, abstracts, authors, journal names, publication dates, DOIs, and PMIDs.",
                "inputSchema": {
                    "type": "object",
                    "required": ["term"],
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": "Entrez text query. All special characters must be URL encoded. Spaces may be replaced by '+' signs.",
                        },
                        "retmax": {
                            "type": "integer",
                            "description": "Number of UIDs to return (default=20, max=10000).",
                            "default": 20,
                        },
                        "sort": {
                            "type": "string",
                            "description": "Sort method for results. Options: pub_date, Author, JournalName, relevance",
                            "enum": ["pub_date", "Author", "JournalName", "relevance"],
                        },
                        "field": {
                            "type": "string",
                            "description": "Search field to limit entire search. Equivalent to adding [field] to term.",
                        },
                        "datetype": {
                            "type": "string",
                            "description": "Type of date used to limit search: mdat (modification date), pdat (publication date), edat (Entrez date)",
                            "enum": ["mdat", "pdat", "edat"],
                        },
                        "reldate": {
                            "type": "integer",
                            "description": "When set to n, returns items with datetype within the last n days.",
                        },
                        "mindate": {
                            "type": "string",
                            "description": "Start date for date range. Format: YYYY/MM/DD, YYYY/MM, or YYYY. Must be used with maxdate.",
                        },
                        "maxdate": {
                            "type": "string",
                            "description": "End date for date range. Format: YYYY/MM/DD, YYYY/MM, or YYYY. Must be used with mindate.",
                        },
                    },
                },
            }
        ]
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {"tools": tools},
        }

    elif method == "tools/call":
        params = request_data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "search_abstracts":
            try:
                result = search_pubmed_abstracts(arguments)
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"PubMed search error: {str(e)}",
                    },
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {"content": [{"type": "text", "text": result}]},
        }

    elif method == "resources/list":
        resources = [
            {
                "uri": "config://server",
                "name": "Server Configuration",
                "description": "PubMed MCP server configuration and status information",
                "mimeType": "application/json",
            },
            {
                "uri": "help://pubmed",
                "name": "PubMed Search Help",
                "description": "Documentation for PubMed search parameters and usage",
                "mimeType": "text/plain",
            },
        ]
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {"resources": resources},
        }

    elif method == "resources/templates/list":
        templates = [
            {
                "uri": "template://pubmed-search",
                "name": "PubMed Search Template",
                "description": "Template for common PubMed search patterns",
                "mimeType": "application/json",
            },
            {
                "uri": "template://recent-articles",
                "name": "Recent Articles Template",
                "description": "Template for finding recent articles on a topic",
                "mimeType": "application/json",
            },
        ]
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {"templates": templates},
        }

    elif method == "resources/read":
        params = request_data.get("params", {})
        uri = params.get("uri")

        if uri == "config://server":
            config = {
                "name": "PubMed MCP Server",
                "version": "1.0.0",
                "description": "HTTP-streamable MCP server for PubMed database searches",
                "capabilities": {
                    "tools": ["search_abstracts"],
                    "resources": ["config://server", "help://pubmed"],
                },
                "environment": "vercel",
                "features": ["pubmed_search", "abstract_retrieval", "ncbi_api"],
            }
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(config, indent=2),
                        }
                    ]
                },
            }
        elif uri == "help://pubmed":
            help_text = """PubMed MCP Server - Search Help

Available Tools:
- search_abstracts: Search PubMed database for research abstracts

Search Parameters:
- term (required): Search query string
- retmax (optional): Number of results to return (default: 20, max: 10000)
- sort (optional): Sort method - pub_date, Author, JournalName, relevance
- field (optional): Search field to limit entire search
- datetype (optional): Date type - mdat, pdat, edat
- reldate (optional): Return items from last N days
- mindate (optional): Start date (YYYY/MM/DD format)
- maxdate (optional): End date (YYYY/MM/DD format)

Examples:
- Search for "cancer" articles: {"term": "cancer"}
- Recent articles: {"term": "diabetes", "reldate": 30}
- Date range: {"term": "covid", "mindate": "2023/01/01", "maxdate": "2023/12/31"}
- Sort by date: {"term": "machine learning", "sort": "pub_date"}

The server uses NCBI E-utilities API for PubMed searches."""
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
                    "contents": [
                        {"uri": uri, "mimeType": "text/plain", "text": help_text}
                    ]
                },
            }
        elif uri == "template://pubmed-search":
            template = {
                "name": "PubMed Search Template",
                "description": "Template for common PubMed search patterns",
                "arguments": {
                    "term": {
                        "type": "string",
                        "description": "Search term for PubMed",
                        "required": True,
                    },
                    "retmax": {
                        "type": "integer",
                        "description": "Number of results (default: 20)",
                        "default": 20,
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort method",
                        "enum": ["pub_date", "Author", "JournalName", "relevance"],
                        "default": "relevance",
                    },
                },
                "examples": [
                    {
                        "name": "Basic Search",
                        "arguments": {"term": "cancer treatment", "retmax": 10},
                    },
                    {
                        "name": "Recent Articles",
                        "arguments": {
                            "term": "machine learning",
                            "sort": "pub_date",
                            "retmax": 5,
                        },
                    },
                ],
            }
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(template, indent=2),
                        }
                    ]
                },
            }
        elif uri == "template://recent-articles":
            template = {
                "name": "Recent Articles Template",
                "description": "Template for finding recent articles on a topic",
                "arguments": {
                    "term": {
                        "type": "string",
                        "description": "Search term for recent articles",
                        "required": True,
                    },
                    "reldate": {
                        "type": "integer",
                        "description": "Days back to search (default: 30)",
                        "default": 30,
                    },
                    "retmax": {
                        "type": "integer",
                        "description": "Number of results (default: 10)",
                        "default": 10,
                    },
                },
                "examples": [
                    {
                        "name": "Last 7 Days",
                        "arguments": {"term": "covid-19", "reldate": 7, "retmax": 5},
                    },
                    {
                        "name": "Last Month",
                        "arguments": {
                            "term": "artificial intelligence",
                            "reldate": 30,
                            "retmax": 20,
                        },
                    },
                ],
            }
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(template, indent=2),
                        }
                    ]
                },
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": f"Resource not found: {uri}"},
            }

    else:
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


def create_error_response(code, message, request_id=None):
    """Create a properly formatted JSON-RPC error response"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def search_pubmed_abstracts(arguments):
    """Search PubMed abstracts using NCBI E-utilities API"""
    try:
        # Extract parameters
        term = arguments.get("term", "")
        retmax = arguments.get("retmax", 20)
        sort = arguments.get("sort", "")
        field = arguments.get("field", "")
        datetype = arguments.get("datetype", "")
        reldate = arguments.get("reldate", "")
        mindate = arguments.get("mindate", "")
        maxdate = arguments.get("maxdate", "")

        if not term:
            return "Error: Search term is required"

        # Build ESearch URL
        esearch_params = {
            "db": "pubmed",
            "term": term,
            "retmax": retmax,
            "retmode": "json",
            "usehistory": "y",
        }

        if sort:
            esearch_params["sort"] = sort
        if field:
            esearch_params["field"] = field
        if datetype:
            esearch_params["datetype"] = datetype
        if reldate:
            esearch_params["reldate"] = reldate
        if mindate:
            esearch_params["mindate"] = mindate
        if maxdate:
            esearch_params["maxdate"] = maxdate

        esearch_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
            + urllib.parse.urlencode(esearch_params)
        )

        # Perform search
        with urllib.request.urlopen(esearch_url) as response:
            esearch_data = json.loads(response.read().decode())

        if (
            "esearchresult" not in esearch_data
            or "idlist" not in esearch_data["esearchresult"]
        ):
            return "No articles found matching the search criteria."

        ids = esearch_data["esearchresult"]["idlist"]
        if not ids:
            return "No articles found matching the search criteria."

        # Build EFetch URL
        efetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "text",
            "rettype": "abstract",
        }

        efetch_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
            + urllib.parse.urlencode(efetch_params)
        )

        # Fetch abstracts
        with urllib.request.urlopen(efetch_url) as response:
            abstracts = response.read().decode()

        return abstracts

    except Exception as e:
        return f"Error searching PubMed: {str(e)}"
