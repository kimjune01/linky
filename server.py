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
    """
    Simple health check tool for the Linky server.
    """
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
    """
    Scrapes a new browser window for the given LinkedIn handle, with the help of a browser addon.

    This tool opens the LinkedIn profile page for the specified handle in a new browser window. It then waits for a file to appear in the ~/Desktop/temp directory, which is expected to be created by a browser addon that scrapes the profile data. The tool checks if the file exists and contains at least 20 lines before returning its content. If the file is not found or is incomplete after 10 seconds, an error message is returned.

    Args:
        handle (str): The LinkedIn handle (username) of the profile to scrape.

    Returns:
        str: The content of the scraped profile file, or an error message if the file is not found or incomplete.

    Caveats:
        - Relies on a browser addon to create the file in the expected location.
        - The file must contain at least 20 lines to be considered complete.
        - The tool will open a new browser window if the file is missing or incomplete.
    """
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
async def search_linkedin_people(query: str, page: int = 1) -> str:
    """
    Open a new browser window for a LinkedIn people search with the given query and page number.

    This tool URL-encodes the provided search query, checks if a corresponding .txt file exists in the ~/Desktop/temp directory (using the pattern: <encoded_query>_page<page>.txt), and returns its content if it contains at least 2 lines. If not, it opens a new browser window with the LinkedIn people search URL and waits for the file to be created and populated by a browser addon.

    The 'page' query parameter is included in the LinkedIn search URL only if page > 1. For page 1, it is omitted.

    Args:
        query (str): The search query to use for finding people on LinkedIn.
        page (int, optional): The page number of the search results. Defaults to 1.

    Returns:
        str: The content of the search result file, or an error message if the file is not found or incomplete after 20 seconds.

    Caveats:
        - Relies on a browser addon to create the file in the expected location.
        - The file must contain at least 2 lines to be considered complete.
        - The tool will open a new browser window if the file is missing or incomplete.
        - The filename follows the pattern: <encoded_query>_page<page>.txt
        - The 'page' query parameter is only included in the URL if page > 1.
    """
    encoded_query = urllib.parse.quote(query)
    filename = f"{encoded_query}_page{page}.txt" if query else "search.txt"
    file_path = os.path.expanduser(f"~/Desktop/temp/{filename}")
    # Check for file before opening the URL
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            result = f.read()
            if len(result.strip().splitlines()) >= 2:
                return result
    base_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}&sid=qAl"
    if page > 1:
        url = f"{base_url}&page={page}"
    else:
        url = base_url
    webbrowser.open_new(url)
    return await wait_for_file(file_path, min_lines=2, max_wait=20)


@mcp.tool()
async def clear_temp_cache() -> str:
    """
    Delete all files in the ~/Desktop/temp directory, to refresh LinkedIn searches and profiles.

    This tool removes all files in the ~/Desktop/temp directory. It is useful for clearing cached LinkedIn search and profile results, ensuring that subsequent operations fetch fresh data.

    Returns:
        str: A message indicating how many files were deleted from the temp directory.

    Caveats:
        - Only files in the ~/Desktop/temp directory are deleted; subdirectories are not affected.
        - Any cached data in this directory will be lost after running this tool.
    """
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


@mcp.tool()
async def list_linkedin_search_queries(page: int = 1, page_size: int = 10) -> list[str]:
    """
    Return a paginated list of queries of previous LinkedIn people searches based on .txt files in the temp dir.

    This tool scans the ~/Desktop/temp directory for files ending with .txt, which are assumed to be the cached results of LinkedIn people searches.
    It extracts the base filename (removing the .txt extension), URL-decodes it to recover the original search query, and returns a paginated list of all such queries.

    Args:
        page (int, optional): The page number to return (1-based). Defaults to 1.
        page_size (int, optional): The number of queries per page. Defaults to 10.

    Returns:
        list[str]: A paginated list of search queries (as strings) that have been previously used for LinkedIn people searches and cached as .txt files.

    Caveats:
        - Only files ending in .txt are considered, and the filename (before .txt) is expected to be a URL-encoded query string.
        - If a filename cannot be URL-decoded, it is skipped.
        - The tool does not check the contents of the files, only their names.
        - The returned queries are not sorted or deduplicated.
        - Pagination is 1-based; if the page is out of range, an empty list is returned.
    """
    temp_dir = os.path.expanduser("~/Desktop/temp")
    txt_files = glob.glob(os.path.join(temp_dir, "*.txt"))
    queries = []
    for f in txt_files:
        base = os.path.basename(f)
        if base.endswith(".txt"):
            encoded_query = base[:-4]
            try:
                query = urllib.parse.unquote(encoded_query)
                queries.append(query)
            except Exception:
                pass
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    return queries[start:end]


if __name__ == "__main__":
    mcp.run()
