from fastapi import APIRouter

# Additional imports
import google.oauth2.credentials
import googleapiclient.discovery
import json
from pydantic import BaseModel

router = APIRouter()

f = open('./youtubeAccessTokens.json')
tokenData = json.load(f)
accessToken = tokenData['token']
refreshToken = tokenData['refresh_token']
tokenURI = tokenData['token_uri']
clientID = tokenData['client_id']
clientSecret = tokenData['client_secret']
scope = tokenData['scopes']
API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
credentials = google.oauth2.credentials.Credentials(token=accessToken,
                                                    refresh_token=refreshToken,
                                                    token_uri=tokenURI,
                                                    client_id=clientID,
                                                    client_secret=clientSecret,
                                                    scopes=scope,
                                                    )

youtubeAnalytics = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, credentials=credentials)


def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()


@router.get("/youtube/basic-metrics")
async def getBasicMetrics(startDate: str, endDate: str):
    """ Aggregated metrics for owner's claimed content """
    try:
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,estimatedMinutesWatched,averageViewDuration',
            dimensions='day',
            sort='day')
        return response
    except Exception as err:
        raise err
