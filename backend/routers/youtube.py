from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
# Model import
from models import youtubeModel
# Database imports
from firebase_admin import db
# Datetime imports
from datetime import datetime
from dateutil.relativedelta import relativedelta
# Additional imports
import google.oauth2.credentials
import googleapiclient.discovery
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

router = APIRouter()

# Database reference
ref = db.reference("/youtube")

# Temporary import of tokens to backend
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


# Youtube Calls Dev purposes

@router.get("/youtube/basic-metrics")
async def getBasicMetrics(startDate: str, endDate: str):
    """ Aggregated metrics for owner's claimed content """
    """ Testing Functions inputs """
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

# ETL Calls


@router.post("/youtube/basic-metrics")
async def storeBasicMetrics(num_months: int):
    """ Storing basic metrics for x number of months """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        startDate = (datetime.today() + relativedelta(months=-num_months)
                     ).strftime('%Y-%m-%d')
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,estimatedMinutesWatched,averageViewDuration',
            dimensions='day',
            sort='day')

        ref = db.reference("/youtube/basic_metrics")

        # print(response['rows'][0][0])
        for i in response['rows']:
            ref.child(i[0]).set({
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "estimatedMinutesWatched": i[5],
                "averageViewDuration": i[6]
            })
        return response

    except Exception as err:
        raise err


@router.get("/youtube/basic-metrics/views")
async def get_views(date: str):
    """ Get views by date """
    try:
        ref = db.reference("/youtube/basic_metrics/" + date + "/views")
        return ref.get()
    except Exception as err:
        raise err

# class EngagementMetrics(BaseModel):
#         Comments: int
#         Likes: int
#         Dislikes: int
#         Shares: int

# class ReachMetrics(BaseModel):
#         TotalViews: int
#         estimatedWatchTime: float
#         averageViewDuration: float

# @router.get("/youtube/basic-metrics-by-channel")
# async def getMetricsByChannel(startDate: str, endDate: str, metrics: str, sort: str | None=None):
#     """ Aggregated metrics for owner's claimed content (dimension set as channel) """
#     try:
#         response = execute_api_request(
#             youtubeAnalytics.reports().query,
#             ids='channel==MINE',
#             startDate=startDate,
#             endDate=endDate,
#             metrics=metrics,
#             dimensions='channel',
#             sort= sort
#             )

#         #Transformation of data
#         queried_data = response['rows'][0][1:]
#         dataset = {}
#         metric_fields = metrics.split(",")
#         index = 0
#         for metrics in metric_fields:
#             dataset[metrics] = queried_data[index]
#             index+=1
#         return dataset

#     except Exception as err:
#         raise err

# @router.get("/youtube/basic-metrics-by-day")
# async def getMetricsByDay(startDate: str, endDate: str, metrics: str):
#     """ Aggregated metrics for owner's claimed content (dimension set as day) """
#     try:
#         response = execute_api_request(
#             youtubeAnalytics.reports().query,
#             ids='channel==MINE',
#             startDate=startDate,
#             endDate=endDate,
#             metrics=metrics,
#             dimensions='day',
#             sort="day"
#             )
#         return response["rows"]

#     except Exception as err:
#         raise err

# @router.get("/youtube/basic-metrics-by-month")
# async def getMetricsByMonth(startDate: str, endDate: str, metrics: str):
#     """ Aggregated metrics for owner's claimed content (dimension set as month) """
#     try:
#         response = execute_api_request(
#             youtubeAnalytics.reports().query,
#             ids='channel==MINE',
#             startDate=startDate,
#             endDate=endDate,
#             metrics=metrics,
#             dimensions= 'month',
#             sort='month'
#             )
#         return response

#     except Exception as err:
#         raise err

# @router.post("/youtube/storeReachMetrics")
# async def storeChannelReachMetrics(reachMetrics: ReachMetrics):
#     ref = db.reference("/Youtube/Reach")
#     ref.update({"TotalViews": reachMetrics.TotalViews,
#                 "estimatedWatchTime": reachMetrics.estimatedWatchTime,
#                 "averageViewDuration": reachMetrics.averageViewDuration})
#     return "data is updated"

# @router.post("/youtube/storeEngagementMetrics")
# async def storeChannelEngagementMetrics(engagementMetrics: EngagementMetrics):
#     ref = db.reference("/Youtube/Engagement")
#     ref.update({"Comments": engagementMetrics.Comments,
#                 "Likes": engagementMetrics.Likes,
#                 "Dislikes": engagementMetrics.Dislikes,
#                 "Share": engagementMetrics.Shares})
#     return "data is updated"
