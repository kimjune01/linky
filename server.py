from mcp.server.fastmcp import FastMCP
import webbrowser
import os
import asyncio
import urllib.parse
import glob

# Initialize FastMCP server
mcp = FastMCP("linky")


@mcp.tool()
async def ping() -> str:
    """Ping the Linky server"""
    return "hello Pong!!!"


async def wait_for_file(file_path: str, min_lines: int, max_wait: int) -> str:
    """Wait for a file to exist and have at least min_lines, up to max_wait seconds."""
    waited = 0
    while waited < max_wait:
        await asyncio.sleep(2)
        waited += 2
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                result = f.read()
                if len(result.strip().splitlines()) < min_lines:
                    continue
                return result
    return (
        f"File not found or incomplete after {max_wait} seconds. file_path: {file_path}"
    )


@mcp.tool()
async def scrape_linkedin_profile(handle: str) -> str:
    """Scrapes a new browser window for the given LinkedIn handle, with the help of a browser addon."""
    file_path = os.path.expanduser(f"~/Desktop/temp/{handle}.md")
    # Check for file before opening the URL
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            result = f.read()
            if len(result.strip().splitlines()) >= 20:
                return result
    url = f"https://www.linkedin.com/in/{handle}"
    webbrowser.open_new(url)
    return await wait_for_file(file_path, min_lines=20, max_wait=10)


@mcp.tool()
async def search_linkedin_people(query: str) -> str:
    """Open a new browser window for a LinkedIn people search with the given query."""
    encoded_query = urllib.parse.quote(query)
    file_path = os.path.expanduser(f"~/Desktop/temp/{encoded_query}.txt")
    # Check for file before opening the URL
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            result = f.read()
            if len(result.strip().splitlines()) >= 2:
                return result
    url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}&sid=qAl"
    webbrowser.open_new(url)
    return await wait_for_file(file_path, min_lines=2, max_wait=20)


@mcp.tool()
async def clear_temp_cache() -> str:
    """Delete all files in the ~/Desktop/temp directory, to refresh linkedin searches and profiles"""
    temp_dir = os.path.expanduser("~/Desktop/temp")
    files = glob.glob(os.path.join(temp_dir, "*"))
    deleted = 0
    for f in files:
        try:
            os.remove(f)
            deleted += 1
        except Exception as e:
            pass
    return f"Deleted {deleted} files from {temp_dir}."


if __name__ == "__main__":
    mcp.run()
