from tracemalloc import start
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
# Model import
from models import youtubeModel
# Database imports
from firebase_admin import db
# Datetime imports
from datetime import datetime
from datetime import timedelta
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

# helper methods


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def execute_api_request(client_library_function, **kwargs):
    return client_library_function(**kwargs).execute()


# Youtube Calls Dev purposes

# @router.get("/youtube/basic-metrics-ignore")
# async def getBasicMetrics(startDate: str, endDate: str):
    """ Aggregated metrics for owner's claimed content """
    """ Testing Functions inputs """
#    try:
#        response = execute_api_request(
#            youtubeAnalytics.reports().query,
#            ids='channel==MINE',
#            startDate=startDate,
#
#
#
#           endDate=endDate,
#           metrics='views,comments,likes,dislikes,estimatedMinutesWatched,averageViewDuration',
#           dimensions='day',
#             sort='day'
#       )

#       return response
 #   except Exception as err:
  #      raise err

# ETL Calls


@router.put("/youtube/store-basic-metrics/aggregated/{days}")
async def storeAggregatedBasicMetricsByDay(days: int):
    """ Storing basic metrics from the last x days """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        startDate = (datetime.today() + relativedelta(days=-days)
                     ).strftime('%Y-%m-%d')

        prevPeriodEndDate = startDate
        prevPeriodStartDate = (datetime.today() + relativedelta(days=-days * 2)
                               ).strftime('%Y-%m-%d')
        # gets aggregated data
        aggregatedDataResponse = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='channel',
        )

        # gets aggregated data from prev period
        prevPeriodAggregatedDataResponse = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=prevPeriodStartDate,
            endDate=prevPeriodEndDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='channel',
        )

        # reponse is for subscriber count (can only get latest subscriber count)
        youtubeDataResponse = execute_api_request(
            youtube.channels().list,
            part="statistics",
            mine=True
        )

        ref = db.reference(f"/youtube/basic-metrics/aggregated/{days}")
        aggregatedData = {}
        prevPeriodAggregatedData = {}
        # print(response['rows'][0][0])

        if len(aggregatedDataResponse['rows']) == 0:
            ref.set({
                "date_start": startDate,
                "date_stop": endDate,
                "views": 0,
                "comments": 0,
                "likes": 0,
                "dislikes": 0,
                "shares": 0,
                "estimatedMinutesWatched": 0,
                "averageViewDuration": 0,
                "engagement": 0,
                "subscribers": youtubeDataResponse['items'][0]['statistics']['subscriberCount'],
            })
        else:
            for i in aggregatedDataResponse['rows']:
                ref.set({
                    "date_start": startDate,
                    "date_stop": endDate,
                    "views": i[1],
                    "comments": i[2],
                    "likes": i[3],
                    "dislikes": i[4],
                    "shares": i[5],
                    "estimatedMinutesWatched": i[6],
                    "averageViewDuration": i[7],
                    "engagement": i[2] + i[3] + i[4] + i[5],
                    "subscribers": youtubeDataResponse['items'][0]['statistics']['subscriberCount'],
                })

            aggregatedData = {
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "shares": i[5],
                "estimatedMinutesWatched": i[6],
                "averageViewDuration": i[7],
                "engagement": i[2] + i[3] + i[4] + i[5],
                "netSubscriberChange": i[8] - i[9]
            }

        for j in prevPeriodAggregatedDataResponse['rows']:
            prevPeriodAggregatedData = {
                "views": j[1],
                "comments": j[2],
                "likes": j[3],
                "dislikes": j[4],
                "shares": j[5],
                "estimatedMinutesWatched": j[6],
                "averageViewDuration": j[7],
                "engagement": j[2] + j[3] + j[4] + j[5],
                "netSubscriberChange": i[8] - i[9]
            }

        if aggregatedData == {}:
            aggregatedData = {
                "views": 1,
                "comments": 1,
                "likes": 1,
                "dislikes": 1,
                "shares": 1,
                "estimatedMinutesWatched": 1,
                "averageViewDuration": 1,
                "engagement": 1,
                "netSubscriberChange": 1
            }

        if prevPeriodAggregatedData == {}:
            prevPeriodAggregatedData = {
                "views": 1,
                "comments": 1,
                "likes": 1,
                "dislikes": 1,
                "shares": 1,
                "estimatedMinutesWatched": 1,
                "averageViewDuration": 1,
                "engagement": 1,
                "netSubscriberChange": 1
            }

        # set zero values to 1.
        for key, value in aggregatedData.items():
            if value == 0:
                aggregatedData[key] = 1

        for key, value in prevPeriodAggregatedData.items():
            if value == 0:
                prevPeriodAggregatedData[key] = 1

        # calculate and store percent change for metrics.
        ref.child("metricsPercentageChange").update({
            "viewsPercentChange": ((aggregatedData['views'] - prevPeriodAggregatedData['views']) / aggregatedData['views']) * 100,
            "commentsPercentChange": ((aggregatedData['comments'] - prevPeriodAggregatedData['comments']) / aggregatedData['comments']) * 100,
            "likesPercentChange": ((aggregatedData['likes'] - prevPeriodAggregatedData['likes']) / aggregatedData['likes']) * 100,
            "dislikesPercentChange": ((aggregatedData['dislikes'] - prevPeriodAggregatedData['dislikes']) / aggregatedData['dislikes']) * 100,
            "sharesPercentChange": ((aggregatedData['shares'] - prevPeriodAggregatedData['shares']) / aggregatedData['shares']) * 100,
            "estimatedMinutesWatchedPercentChange": ((aggregatedData['estimatedMinutesWatched'] - prevPeriodAggregatedData['estimatedMinutesWatched'])
                                                     / aggregatedData['estimatedMinutesWatched']) * 100,
            "averageViewDurationPercentChange": ((aggregatedData['averageViewDuration'] - prevPeriodAggregatedData['averageViewDuration'])
                                                 / aggregatedData['averageViewDuration']) * 100,
            "engagementPercentChange": ((aggregatedData['engagement'] - prevPeriodAggregatedData['engagement'])
                                        / aggregatedData['engagement']) * 100,
            "subscriberPecentChange": ((aggregatedData['netSubscriberChange'] - prevPeriodAggregatedData['netSubscriberChange'])
                                       / aggregatedData['netSubscriberChange']) * 100
        })

        responseChannelAudienceMetrics = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='viewerPercentage',
            sort="gender,ageGroup",
            dimensions='ageGroup,gender',
        )
        # print(response['rows'][0][0])
        for i in responseChannelAudienceMetrics['rows']:
            if i[1] == "male":
                ref.child("maleViewerPercentage").set({
                    i[0].split("age")[1]: i[2]
                })
            elif i[1] == "female":
                ref.child("femaleViewerPercentage").set({
                    i[0].split("age")[1]: i[2]
                })

        return (aggregatedData, prevPeriodAggregatedData)

    except Exception as err:
        raise err


@router.put("/youtube/store-basic-metrics/{days}")
async def storeDailyBasicMetrics(days: int):
    """ Storing basic metrics from the last x days """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        startDate = (datetime.today() + relativedelta(days=-days)
                     ).strftime('%Y-%m-%d')

        responseDay = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate=startDate,
            endDate=endDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='day',
            sort="day"
        )

        # reponse is for subscriber count (can only get latest subscriber count)
        youtubeDataResponse = execute_api_request(
            youtube.channels().list,
            part="statistics",
            mine=True
        )

        ref = db.reference(f"/youtube/basic-metrics/daily")

        currSubscribers = int(
            youtubeDataResponse['items'][0]['statistics']['subscriberCount'])
        for i in reversed(responseDay['rows']):
            ref.child(i[0]).set({
                "views": i[1],
                "comments": i[2],
                "likes": i[3],
                "dislikes": i[4],
                "shares": i[5],
                "estimatedMinutesWatched": i[6],
                "averageViewDuration": i[7],
                "engagement": i[2] + i[3] + i[4] + i[5],
                "subscribers": currSubscribers - (i[8] - i[9]),
                "subscriberChange": i[8] - i[9]
            })
            currSubscribers = currSubscribers - (i[8] - i[9])

        return (responseDay, youtubeDataResponse)

    except Exception as err:
        raise err


@router.put("/youtube/store-basic-metrics/total")
async def storeTotalBasicMetrics():
    """ Storing latest basic channel metrics """
    try:
        endDate = datetime.today().strftime('%Y-%m-%d')
        responseChannel = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate='2015-01-01',
            endDate=endDate,
            metrics='views,comments,likes,dislikes,shares,estimatedMinutesWatched,averageViewDuration',
            dimensions='channel',
        )

        # reponse is for subscriber count (can only get latest subscriber count)
        youtubeDataResponse = execute_api_request(
            youtube.channels().list,
            part="statistics",
            mine=True
        )

        ref = db.reference("/youtube/basic-metrics/total")

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
            })

        responseChannelAudienceMetrics = execute_api_request(
            youtubeAnalytics.reports().query,
            ids='channel==MINE',
            startDate='2015-01-01',
            endDate=endDate,
            metrics='viewerPercentage',
            sort="gender,ageGroup",
            dimensions='ageGroup,gender',
        )
        # print(response['rows'][0][0])
        for i in responseChannelAudienceMetrics['rows']:
            if i[1] == "male":
                ref.child("maleViewerPercentage").set({
                    i[0].split("age")[1]: i[2]
                })
            elif i[1] == "female":
                ref.child("femaleViewerPercentage").set({
                    i[0].split("age")[1]: i[2]
                })

        return (responseChannel, responseChannelAudienceMetrics)

    except Exception as err:
        raise err

### get requests for daily basic metrics ###


@router.get("/youtube/basic-metrics/aggregated/{days}")
async def getAggregatedBasicMetrics(days: int):
    try:
        ref = db.reference(f"/youtube/basic-metrics/aggregated/{days}")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/youtube/basic-metrics/daily/{days}")
async def getDailyBasicMetrics(days: int = 30):
    try:
        if days < 0:
            days = 30
        now = datetime.now()
        since = now - timedelta(days=days)
        dataset = {}
        ref = db.reference("/youtube/basic-metrics/daily")
        metrics = ref.get()
        for single_date in daterange(since, now):
            curr_date = single_date.strftime("%Y-%m-%d")
            # only retrieves if the current daily date is already stored in db.
            if curr_date in metrics:
                dataset[curr_date] = {}
                for key, value in metrics[curr_date].items():
                    dataset[curr_date][key] = value
        return dataset

    except Exception as err:
        raise err
