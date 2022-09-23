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


@router.post("/youtube/storeBasicmetrics")
async def storeBasicChannelMetrics(num_months: int):
    """ Storing basic metrics by channel for x number of months """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        startDate = (datetime.today() + relativedelta(months=-num_months)
                     ).strftime('%Y-%m-%d')
        responseChannel = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='channel',
        )

        responseDay = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='day',
            sort="day"
        )

        # reponse is for subscriber count
        youtubeDataResponse = execute_api_request(
            youtube.channels().list,
            part="statistics",
            mine=True
        )

        ref = db.reference("/youtube/total")

        # print(response['rows'][0][0])
        for i in responseChannel['rows']:
            ref.set({
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "shares": i[5],
                "estimatedMinutesWatched": i[6],
                "averageViewDuration": i[7],
                "engagement": i[2] + i[3] + i[4] + i[5],
                "subscribers": youtubeDataResponse['items'][0]['statistics']['subscriberCount'],
                "subscriberChange": i[8] - i[9]
            })

        ref = db.reference("youtube/day")

        for i in responseDay['rows']:
            ref.child(i[0]).set({
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "shares": i[5],
                "estimatedMinutesWatched": i[6],
                "averageViewDuration": i[7],
                "engagement": i[2] + i[3] + i[4] + i[5],
                "subscribers": youtubeDataResponse['items'][0]['statistics']['subscriberCount'],
                "subscriberChange": i[8] - i[9]
            })

        responseChannelAudienceMetrics = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate="2015-01-01",
            endDate=endDate,
            metrics='viewerPercentage',
            sort="gender,ageGroup",
            dimensions='ageGroup,gender',
        )

        ref = db.reference("/youtube/total")

        # print(response['rows'][0][0])
        for i in responseChannelAudienceMetrics['rows']:
            if i[1] == "male":
                ref.child("maleViewerPercentage").update({
                    i[0].split("age")[1]: i[2]
                })
            elif i[1] == "female":
                ref.child("femaleViewerPercentage").update({
                    i[0].split("age")[1]: i[2]
                })


        return (responseChannel, responseDay, youtubeDataResponse, responseChannelAudienceMetrics)
        return (responseChannel, responseDay, youtubeDataResponse, responseChannelAudienceMetrics)

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

@router.get("/youtube/total/femaleViewerPercentage")
async def get_channel_female_view_percentage():
    """ Get total viewer percentages for female """
    try:
        ref = db.reference("/youtube/total/" + "/female")
        return ref.get()
    except Exception as err:
        raise err

@router.get("/youtube/total/maleViewerPercentage")
async def get_channel_male_view_percentage():
    """ Get total viewer percentages for male """
    try:
        ref = db.reference("/youtube/total/" + "/male")
        return ref.get()
    except Exception as err:
        raise err
@router.get("/youtube/total/views")
async def get_total_views():
    """ Get total views for channel """
    try:
        ref = db.reference("/youtube/total/" + "/views")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/likes")
async def get_total_likes():
    """ Get get total likes for channel """
    try:
        ref = db.reference("/youtube/total/" + "/likes")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/dislikes")
async def get_total_dislikes():
    """ Get total dislikes for channel """
    try:
        ref = db.reference("/youtube/total/" + "/dislikes")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/comments")
async def get_total_comments():
    """ Get total comments for channel """
    try:
        ref = db.reference("/youtube/total/" + "/comments")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/shares")
async def get_total_shares():
    """ Get total shares for channel """
    try:
        ref = db.reference("/youtube/total/" + "/shares")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/engagement")
async def get_total_engagements():
    """ Get total engagements for channel """
    try:
        ref = db.reference("/youtube/total/" + "/engagement")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/estimatedMinutesWatched")
async def get_total_estimatedMinutesWatched():
    """ Get total estimated minutes watched for channel """
    try:
        ref = db.reference("/youtube/total/" +
                           "/estimatedMinutesWatched")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/averageViewDuration")
async def get_total_averageViewDuration():
    """ Get total average view duration for channel """
    try:
        ref = db.reference(
            "/youtube/total/" + "/averageViewDuration")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/subscribers")
async def get_total_subscribers():
    """ Get total subscribers for channel """
    try:
        ref = db.reference(
            "/youtube/total/" + "/subscribers")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/total/subscriberChange")
async def get_total_subscriberChange():
    """ Get total change in subscribers for channel """
    try:
        ref = db.reference(
            "/youtube/total/" + "/subscriberChange")
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
