from fastapi import APIRouter

from airembr.system.command.feed.get_rss import get_rss as get_rss_cmd

router = APIRouter()


@router.get("/v1/feed", tags=["v1/feed"])
async def get_rss():
    """
        Fetches and parses RSS feeds, sorts entries by publish date, and returns a list of objects.
    """

    return await get_rss_cmd()
