import pytest
import asyncio
from unittest.mock import patch
from server import scrape_multiple_linkedin_profiles


@pytest.mark.asyncio
async def test_scrape_multiple_linkedin_profiles_parallelism(monkeypatch):
    handles = ["alice", "bob", "carol"]
    delays = {"alice": 2, "bob": 3, "carol": 1}
    results_content = {h: f"Profile for {h}\n" * 20 for h in handles}

    # Mock webbrowser.open_new to do nothing
    monkeypatch.setattr("webbrowser.open_new", lambda url: None)

    async def fake_wait_for_profile_file(handle):
        await asyncio.sleep(delays[handle])
        return handle, results_content[handle]

    with patch("server.wait_for_profile_file", side_effect=fake_wait_for_profile_file):
        import time

        start = time.time()
        await scrape_multiple_linkedin_profiles(handles)
        elapsed = time.time() - start
        # The max delay is 3, so the function should finish in just over 3 seconds if parallel
        assert elapsed < 3.5, (
            f"Function took too long: {elapsed} seconds (should be parallel)"
        )
