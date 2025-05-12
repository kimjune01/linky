from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("linky")


@mcp.tool()
async def ping() -> str:
    """Ping the Linky server"""
    return "Pong!"


if __name__ == "__main__":
    mcp.run()
