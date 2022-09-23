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

@router.get("/youtube/basic-metrics-ignore")
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


@router.post("/youtube/audience")
async def storeAudienceMetrics():
    """ Storing audience metrics such as viewer percentage based on gender and age group """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        startDate = (datetime.today() + relativedelta(months=-1)
                     ).strftime('%Y-%m-%d')
        response = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='viewerPercentage',
            sort="gender,ageGroup",
            dimensions='ageGroup,gender',
        )

        ref = db.reference("/youtube/audience")

        # print(response['rows'][0][0])
        if response['rows'] != []:
            for i in response['rows']:
                if i[1] == "male":
                    ref.child("last-30-days").child("male").update({
                        i[0].split("age")[1]: i[2]
                    })
                elif i[1] == "female":
                    ref.child("last-30-days").child("female").update({
                        i[0].split("age")[1]: i[2]
                    })
        else:
            # last 30 days has no viewership for the channel
            ref.child("last-30-days").child("male").update({
                "18-24": 0,
                "25-34": 0,
                "35-44": 0,
                "45-54": 0,
                "55-64": 0,
                "65-": 0,
            })
            ref.child("last-30-days").child("female").update({
                "18-24": 0,
                "25-34": 0,
                "35-44": 0,
                "45-54": 0,
                "55-64": 0,
                "65-": 0,
            })

        responseForLifetime = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate="2015-01-01",
            endDate=endDate,
            metrics='viewerPercentage',
            sort="gender,ageGroup",
            dimensions='ageGroup,gender',
        )

        # print(response['rows'][0][0])
        for i in responseForLifetime['rows']:
            if i[1] == "male":
                ref.child("lifetime").child("male").update({
                    i[0].split("age")[1]: i[2]
                })
            elif i[1] == "female":
                ref.child("lifetime").child("female").update({
                    i[0].split("age")[1]: i[2]
                })

        return response

    except Exception as err:
        raise err


@router.post("/youtube/totalBasicmetrics")
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

        # reponse is for subscriber count
        youtubeDataResponse = execute_api_request(
            youtube.channels().list,
            part="statistics",
            mine=True
        )

        ref = db.reference("/youtube/total")

        # print(response['rows'][0][0])
        for i in response['rows']:
            ref.set({
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


@router.post("/youtube/dayBasicMetrics")
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
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration,subscribersGained, subscribersLost',
            dimensions='day',
            sort='day')

        ref = db.reference("/youtube/day")

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
                "engagement": i[2] + i[3] + i[4] + i[5],
                "subscriberChange": i[8] - i[9]
            })
        return response

    except Exception as err:
        raise err

## get requests for audience metrics ###


@router.get("/youtube/oneMonth/audience/lastMonth")
async def get_viewPercentageFromLast30Days():
    """ Get view percentage from last 30 days """
    try:
        ref = db.reference("/youtube/audience/lastMonth")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/audience/lifetime")
async def get_viewPercentageFromLifetime():
    """ Get channel lifetime view percentage  """
    try:
        ref = db.reference("/youtube/audience/lifetime")
        return ref.get()
    except Exception as err:
        raise err

### get requests for daily basic metrics ###


@router.get("/youtube/day/{date}/views")
async def get_day_views(date: str):
    """ Get views by date """
    try:
        ref = db.reference("/youtube/day/" + date + "/views")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/day/{date}/engagement")
async def get_day_engagement(date: str):
    """ Get engagement by date """
    try:
        ref = db.reference(
            "/youtube/day/" + date + "/engagement")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/day/{date}/estimatedMinsWatched")
async def get_day_views(date: str):
    """ Get estimatedMinsWatched by date """
    try:
        ref = db.reference("/youtube/day/" +
                           date + "/estimatedMinsWatched")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/day/{date}/averageViewDuration")
async def get_day_views(date: str):
    """ Get averageViewDuration by date """
    try:
        ref = db.reference("/youtube/day/" +
                           date + "/averageViewDuration")
        return ref.get()
    except Exception as err:
        raise err

### get requests for basic channel metrics ###


@router.get("/youtube/total/views")
async def get_channel_views():
    """ Get total views for channel """
    try:
        ref = db.reference("/youtube/total/" + "/views")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/likes")
async def get_channel_likes():
    """ Get get total likes for channel """
    try:
        ref = db.reference("/youtube/total/" + "/likes")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/dislikes")
async def get_channel_dislikes():
    """ Get total dislikes for channel """
    try:
        ref = db.reference("/youtube/total/" + "/dislikes")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/comments")
async def get_channel_comments():
    """ Get total comments for channel """
    try:
        ref = db.reference("/youtube/total/" + "/comments")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/shares")
async def get_channel_shares():
    """ Get total shares for channel """
    try:
        ref = db.reference("/youtube/total/" + "/shares")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/engagement")
async def get_channel_engagements():
    """ Get total engagements for channel """
    try:
        ref = db.reference("/youtube/total/" + "/engagement")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/estimatedMinutesWatched")
async def get_channel_estimatedMinutesWatched():
    """ Get total estimated minutes watched for channel """
    try:
        ref = db.reference("/youtube/total/" +
                           "/estimatedMinutesWatched")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/averageViewDuration")
async def get_channel_averageViewDuration():
    """ Get average view duration for channel """
    try:
        ref = db.reference(
            "/youtube/total/" + "/averageViewDuration")
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
