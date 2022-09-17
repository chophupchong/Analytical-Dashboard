from fastapi import APIRouter

# Additional imports
import asyncio
import aiohttp
import json
from pydantic import BaseModel

router = APIRouter()


f = open('/Users/roopa/Documents/NUS/Semesters/Y3S1/Capstone/dev/Analytical-Dashboard/backend/instagramAccessTokens.json')
data = json.load(f)
access_token = data["access_token"]
ig_page_id = data["ig_page_id"]

url_list = [
    'https://graph.facebook.com/v14.0/{}/?access_token={}&fields=followers_count',
    'https://graph.facebook.com/v14.0/{}/insights/?access_token={}&metric=impressions,reach,profile_views&period=day'
]


async def get_event(session):
    return [await (await session.get(url_list[0].format(ig_page_id, access_token), ssl=False)).json(), await (await session.get(url_list[1].format(ig_page_id, access_token), ssl=False)).json()]


async def get_api_data():
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(get_event(session))


@router.get('/instagram')
async def instagram():
    results = await get_api_data()
    # print(results2[0])
    return results[0]
