import contextlib
import logging
import os
from collections.abc import AsyncIterator
from typing import Any, Literal, Optional

import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pubmedclient.models import Db, EFetchRequest, ESearchRequest
from pubmedclient.sdk import efetch, esearch, pubmedclient_client
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)


class SearchAbstractsRequest(BaseModel):
    """
    Request parameters for NCBI ESearch API for searching abstracts on the PubMed database.

    Functions:
        - Provides a list of abstracts matching a text query

    Examples:
        >>> # Basic search in PubMed for 'asthma' articles abstracts
        >>> SearchAbstractsRequest(term="asthma")

        >>> # Search with publication date range
        >>> ESearchRequest(
        ...     term="asthma",
        ...     mindate="2020/01/01",
        ...     maxdate="2020/12/31",
        ...     datetype="pdat"
        ... )

        >>> # Search with field restriction
        >>> ESearchRequest(term="asthma[title]")
        >>> # Or equivalently:
        >>> ESearchRequest(term="asthma", field="title")

        >>> # Search with proximity operator
        >>> ESearchRequest(term='"asthma treatment"[Title:~3]')

        >>> # Sort results by publication date
        >>> ESearchRequest(
        ...     term="asthma",
        ...     sort="pub_date"
        ... )
    """

    term: str = Field(
        ...,
        description="""Entrez text query. All special characters must be URL encoded. 
        Spaces may be replaced by '+' signs. For very long queries (more than several 
        hundred characters), consider using an HTTP POST call. See PubMed or Entrez 
        help for information about search field descriptions and tags. Search fields 
        and tags are database specific.""",
    )

    retmax: Optional[int] = Field(
        20,
        description="""Number of UIDs to return (default=20, max=10000).""",
    )

    sort: Optional[str] = Field(
        None,
        description="""Sort method for results. PubMed values:
        - pub_date: descending sort by publication date
        - Author: ascending sort by first author
        - JournalName: ascending sort by journal name
        - relevance: default sort order ("Best Match")""",
    )
    field: Optional[str] = Field(
        None,
        description="""Search field to limit entire search. Equivalent to adding [field] 
        to term.""",
    )
    datetype: Optional[Literal["mdat", "pdat", "edat"]] = Field(
        None,
        description="""Type of date used to limit search:
        - mdat: modification date
        - pdat: publication date
        - edat: Entrez date
        Generally databases have only two allowed values.""",
    )
    reldate: Optional[int] = Field(
        None,
        description="""When set to n, returns items with datetype within the last n 
        days.""",
    )
    mindate: Optional[str] = Field(
        None,
        description="""Start date for date range. Format: YYYY/MM/DD, YYYY/MM, or YYYY. 
        Must be used with maxdate.""",
    )
    maxdate: Optional[str] = Field(
        None,
        description="""End date for date range. Format: YYYY/MM/DD, YYYY/MM, or YYYY. 
        Must be used with mindate.""",
    )


def create_app(json_response: bool = False) -> Starlette:
    """Create the ASGI application for Vercel deployment."""
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("PubMedMCP")

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[types.ContentBlock]:
        if name == "search_abstracts":
            # Parse the request arguments
            try:
                request = SearchAbstractsRequest(**arguments)
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error parsing request parameters: {str(e)}",
                    )
                ]

            try:
                # Perform the PubMed search
                async with pubmedclient_client() as client:
                    # perform a search and get the ids
                    search_request = ESearchRequest(
                        db=Db.PUBMED, **request.model_dump()
                    )
                    search_response = await esearch(client, search_request)
                    ids = search_response.esearchresult.idlist

                    if not ids:
                        return [
                            types.TextContent(
                                type="text",
                                text="No articles found matching the search criteria.",
                            )
                        ]

                    # get the abstracts of each ids
                    # in practice it returns something like the following:
                    #
                    # 1. Allergy Asthma Proc. 2025 Jan 1;46(1):1-3. doi: 10.2500/aap.2025.46.240102.
                    #
                    # Exploring mast cell disorders: Tryptases, hereditary alpha-tryptasemia, and MCAS
                    # treatment approaches.
                    # Bellanti JA, Settipane RA.
                    # DOI: 10.2500/aap.2025.46.240102
                    # PMID: 39741377
                    #
                    # 2. ...
                    fetch_request = EFetchRequest(
                        db=Db.PUBMED,
                        id=",".join(ids),
                        retmode="text",
                        rettype="abstract",
                    )
                    fetch_response = await efetch(client, fetch_request)

                    return [
                        types.TextContent(
                            type="text",
                            text=fetch_response,
                        )
                    ]
            except Exception as e:
                logger.error(f"Error searching PubMed: {str(e)}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error searching PubMed: {str(e)}",
                    )
                ]
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="search_abstracts",
                description="Search abstracts on PubMed database based on the request parameters. Returns formatted text containing article titles, abstracts, authors, journal names, publication dates, DOIs, and PMIDs.",
                inputSchema={
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
            )
        ]

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("PubMedMCP server started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("PubMedMCP server shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=False,  # Disable debug mode for production
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Wrap ASGI application with CORS middleware to expose Mcp-Session-Id header
    # for browser-based clients (ensures 500 errors get proper CORS headers)
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],  # Allow all origins - adjust as needed for production
        allow_methods=["GET", "POST", "DELETE"],  # MCP streamable HTTP methods
        expose_headers=["Mcp-Session-Id"],
    )

    return starlette_app


@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    """Main function for local development."""
    # Set environment variable for logging
    os.environ["LOG_LEVEL"] = log_level

    # Create the app
    starlette_app = create_app(json_response)

    import uvicorn

    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0
