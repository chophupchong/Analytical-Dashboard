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
credentials = google.oauth2.credentials.Credentials(token=accessToken,
                                                    refresh_token=refreshToken,
                                                    token_uri=tokenURI,
                                                    client_id=clientID,
                                                    client_secret=clientSecret,
                                                    scopes=scope,
                                                    )

youtubeAnalytics = googleapiclient.discovery.build(
    'youtubeAnalytics', 'v2', credentials=credentials)

youtube = googleapiclient.discovery.build(
    'youtube', 'v3', credentials=credentials)

def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()


# Youtube Calls Dev purposes

@router.get("/youtube/basic-channel-metrics")
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
            sort='day'
        )

        return response
    except Exception as err:
        raise err

# ETL Calls

@router.post("/youtube/basic-channel-metrics")
async def storeBasicChannelMetrics(num_months: int):
    """ Storing basic metrics by channel for x number of months """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        startDate = (datetime.today() + relativedelta(months=-num_months)
                     ).strftime('%Y-%m-%d')
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration',
            dimensions='channel',
        )

        #reponse is for subscriber count
        youtubeDataResponse = execute_api_request(
            youtube.channels().list,
            part="statistics",
            mine=True
            )
        

        ref = db.reference("/youtube/basic_channel_metrics")

        # print(response['rows'][0][0])
        for i in response['rows']:
            ref.child('channel').set({
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "shares": i[5],
                "estimatedMinutesWatched": i[6],
                "averageViewDuration": i[7],
                "engagement": i[2] + i[3] + i[4] + i[5],
                "subscribers": youtubeDataResponse['items'][0]['statistics']['subscriberCount']
            })
        return response

    except Exception as err:
        raise err

@router.post("/youtube/daily-basic-metrics")
async def storeDailyBasicMetrics(num_months: int):
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
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration',
            dimensions='day',
            sort='day')


        ref = db.reference("/youtube/daily_basic_metrics")

        # print(response['rows'][0][0])
        for i in response['rows']:
            ref.child(i[0]).set({
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "shares": i[5],
                "estimatedMinutesWatched": i[6],
                "averageViewDuration": i[7],
                "engagement": i[2] + i[3] + i[4] + i[5]
            })
        return response

    except Exception as err:
        raise err



### get requests for daily basic metrics ###

@router.get("/youtube/daily_basic_metrics/views")
async def get_views(date: str):
    """ Get views by date """
    try:
        ref = db.reference("/youtube/daily_basic_metrics/" + date + "/views")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/daily_basic_metrics/engagement")
async def get_engagement(date: str):
    """ Get engagement by date """
    try:
        ref = db.reference("/youtube/daily_basic_metrics/" + date + "/engagement")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/daily_basic_metrics/estimatedMinsWatched")
async def get_views(date: str):
    """ Get estimatedMinsWatched by date """
    try:
        ref = db.reference("/youtube/daily_basic_metrics/" + date + "/estimatedMinsWatched")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/daily_basic_metrics/averageViewDuration")
async def get_views(date: str):
    """ Get averageViewDuration by date """
    try:
        ref = db.reference("/youtube/daily_basic_metrics/" + date + "/averageViewDuration")
        return ref.get()
    except Exception as err:
        raise err

### get requests for basic channel metrics ###

@router.get("/youtube/basic_channel_metrics/views")
async def get_channel_views():
    """ Get total views for channel """
    try:
        ref = db.reference("/youtube/daily_basic_metrics/" + "channel" + "/views")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/basic_channel_metrics/likes")
async def get_channel_likes():
    """ Get get total likes for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/likes")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/basic_channel_metrics/dislikes")
async def get_channel_dislikes():
    """ Get total dislikes for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/dislikes")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/basic_channel_metrics/comments")
async def get_channel_comments():
    """ Get total comments for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/comments")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/basic_channel_metrics/shares")
async def get_channel_shares():
    """ Get total shares for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/shares")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/basic_channel_metrics/engagement")
async def get_channel_engagements():
    """ Get total engagements for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/engagement")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/basic_channel_metrics/estimatedMinutesWatched")
async def get_channel_estimatedMinutesWatched():
    """ Get total estimated minutes watched for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/estimatedMinutesWatched")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/basic_channel_metrics/averageViewDuration")
async def get_channel_averageViewDuration():
    """ Get average view duration for channel """
    try:
        ref = db.reference("/youtube/basic_channel_metrics/" + "channel" + "/averageViewDuration")
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
