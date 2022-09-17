from fastapi import APIRouter

# Additional imports
import google.oauth2.credentials
import googleapiclient.discovery
import json
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

router = APIRouter()
cred = credentials.Certificate("./serviceAccountKey.json")

#Currently Firebase Realtime Database is linked to the bzacapstonechc firebase acc's proj
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://capstone-7caf6-default-rtdb.firebaseio.com/"
})

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

class EngagementMetrics(BaseModel):
        Comments: int
        Likes: int 
        Dislikes: int
        Shares: int

class ReachMetrics(BaseModel):
        TotalViews: int
        estimatedWatchTime: float
        averageViewDuration: float

def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()


@router.get("/youtube/basic-metrics-by-channel")
async def getMetricsByChannel(startDate: str, endDate: str, metrics: str, sort: str):
    """ Aggregated metrics for owner's claimed content (dimension set as channel) """
    try:
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics=metrics,
            dimensions="channel",
            sort= sort
            )
        return response

    except Exception as err:
        raise err
        
@router.get("/youtube/basic-metrics-by-day")
async def getMetricsByDay(startDate: str, endDate: str, metrics: str):
    """ Aggregated metrics for owner's claimed content (dimension set as channel) """
    try:
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics=metrics,
            dimensions="day",
            sort="day"
            )
        return response

    except Exception as err:
        raise err

@router.get("/youtube/basic-metrics-by-month")
async def getMetricsByMonth(startDate: str, endDate: str, metrics: str):
    """ Aggregated metrics for owner's claimed content (dimension set as channel) """
    try:
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics=metrics,
            dimensions= "month",
            sort="month"
            )
        return response

    except Exception as err:
        raise err

@router.post("/youtube/storeReachMetrics")
async def storeChannelReachMetrics(reachMetrics: ReachMetrics):
    ref = db.reference("/Youtube/Reach")
    ref.update({"TotalViews": reachMetrics.TotalViews,
                "estimatedWatchTime": reachMetrics.estimatedWatchTime,
                "averageViewDuration": reachMetrics.averageViewDuration})
    return "data is updated"

@router.post("/youtube/storeEngagementMetrics")
async def storeChannelEngagementMetrics(engagementMetrics: EngagementMetrics):
    ref = db.reference("/Youtube/Engagement")  
    ref.update({"Comments": engagementMetrics.Comments,
                "Likes": engagementMetrics.Likes,
                "Dislikes": engagementMetrics.Dislikes,
                "Share": engagementMetrics.Shares})
    return "data is updated"
