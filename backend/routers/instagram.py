from fastapi import APIRouter
from firebase_admin import db

# Additional imports
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

router = APIRouter()

# Database reference
ref = db.reference("/instagram")

# Define Parameters Dictionary
params = dict()
params['graph_domain'] = 'https://graph.facebook.com'
params['graph_version'] = 'v14.0'
params['endpoint_base'] = params['graph_domain'] + \
    '/' + params['graph_version'] + '/'
# need to dynamically get ig-user-id
params['instagram_account_id'] = '17841403562665103'
f = open('./instagramAccessTokens.json')
data = json.load(f)
params['access_token'] = data["access_token"]


@router.post('/instagram/basic-page-metrics')
async def getBasicPageMetrics():
    url = params['endpoint_base'] + \
        params['instagram_account_id']
    endpointParams = dict()
    endpointParams['fields'] = 'followers_count, media_count'
    endpointParams['access_token'] = params['access_token']

    try:
        data = requests.get(url, endpointParams)
        data_insight = json.loads(data.content)

        ref = db.reference("/instagram/basic-page-metrics")

        ref.child('ig-page').set({
            "followers_count": data_insight['followers_count'],
            "media_count": data_insight['media_count'],
        })

        return data_insight
    except requests.HTTPError as e:
        print(f"[!] Exception caught: {e}")


# (follower_count) metric only supports querying data for the last 30 days excluding the current day
@router.post('/instagram/daily-follower-count')
async def getDailyFollowerCount():
    url = params['endpoint_base'] + \
        params['instagram_account_id'] + '/insights'
    endpointParams = dict()
    endpointParams['metric'] = 'follower_count'
    endpointParams['period'] = 'day'
    endpointParams['since'] = ''
    endpointParams['until'] = ''
    endpointParams['access_token'] = params['access_token']
    endDate = datetime.today()
    startDate = (endDate + relativedelta(days=-30))
    endpointParams['since'] = startDate.strftime('%Y-%m-%d')
    endpointParams['until'] = endDate.strftime('%Y-%m-%d')
    try:
        data = requests.get(url, endpointParams)
        data_insight = json.loads(data.content)

        data_dict = dict()
        data_dict['daily-new-followers'] = data_insight['data'][0]['values']

        ref = db.reference("/instagram/daily-new-followers")
        for i in range(0, len(list(data_dict.values())[0])):
            d = datetime.strptime(data_dict['daily-new-followers'][i]['end_time'], "%Y-%m-%dT%H:%M:%S%z").strftime(
                '%Y-%m-%d')
            ref.child(d).set({
                "daily-new-followers": data_dict['daily-new-followers'][i]['value']
            })

        return data_insight
    except requests.HTTPError as e:
        print(f"[!] Exception caught: {e}")


@router.post('/instagram/daily-basic-metrics')
async def getDailyBasicMetrics(num_months: int):

    url = params['endpoint_base'] + \
        params['instagram_account_id'] + '/insights'
    endpointParams = dict()
    endpointParams['metric'] = 'impressions, reach, profile_views, website_clicks'
    endpointParams['period'] = 'day'
    endpointParams['since'] = ''
    endpointParams['until'] = ''
    endpointParams['access_token'] = params['access_token']

    try:
        data_dict = dict()
        endDate = datetime.today()
        # instagram graph api only returns a maximum of 30 days worth of data
        for j in range(0, num_months):
            startDate = (endDate + relativedelta(days=-30))
            endpointParams['since'] = startDate.strftime('%Y-%m-%d')
            endpointParams['until'] = endDate.strftime('%Y-%m-%d')
            endDate = startDate

            data = requests.get(url, endpointParams)
            data_insight = json.loads(data.content)

            for i in range(0, len(data_insight['data'])):
                if j == 0:
                    data_dict[(data_insight['data'][i]['name'])
                              ] = data_insight['data'][i]['values']
                else:
                    data_dict[(data_insight['data'][i]['name'])
                              ] += (data_insight['data'][i]['values'])

        ref = db.reference("/instagram/daily-basic-metrics")
        for i in range(0, len(list(data_dict.values())[0])):
            d = datetime.strptime(data_dict['reach'][i]['end_time'], "%Y-%m-%dT%H:%M:%S%z").strftime(
                '%Y-%m-%d')
            ref.child(d).set({
                "reach": data_dict['reach'][i]['value'],
                "impressions": data_dict['impressions'][i]['value'],
                "profile_views": data_dict['profile_views'][i]['value'],
                "website_clicks": data_dict['website_clicks'][i]['value']
            })

        return data_insight['data']
    except requests.HTTPError as e:
        print(f"[!] Exception caught: {e}")


@router.post('/instagram/media-metrics')
async def getMediaMetrics():
    url = params['endpoint_base'] + \
        params['instagram_account_id'] + '/media'
    endpointParams = dict()
    endpointParams['fields'] = 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,like_count,comments_count'
    endpointParams['access_token'] = params['access_token']

    try:
        data = requests.get(url, endpointParams)
        data_insight = dict()
        data_insight = json.loads(data.content)

        metrics_dict = dict()
        metrics_dict['IMAGE'] = 'engagement,impressions,reach,saved'
        metrics_dict['VIDEO'] = 'engagement,impressions,reach,saved,video_views'
        metrics_dict['CAROUSEL_ALBUM'] = 'carousel_album_engagement,carousel_album_impressions,carousel_album_reach,carousel_album_saved,carousel_album_video_views'

        endpointParams = dict()
        endpointParams['access_token'] = params['access_token']

        # count = 0
        ref = db.reference("/instagram/ig_media_metrics")

        for i in data_insight['data']:  # gotta add in engagement stats of posts later
            # url = params['endpoint_base'] + i['id'] + '/insights'
            # if i['media_type'] == 'IMAGE':
            #     endpointParams['metric'] = metrics_dict['IMAGE']
            # elif i['media_type'] == 'VIDEO':
            #     endpointParams['metric'] = metrics_dict['VIDEO']
            # elif i['media_type'] == 'CAROUSEL_ALBUM':
            #     endpointParams['metric'] = metrics_dict['CAROUSEL_ALBUM']
            # else:
            #     endpointParams['metric'] = metrics_dict['IMAGE']
            # data = requests.get(url, endpointParams)
            # metrics_insights = json.loads(data.content)

            ref.child(i['id']).set({
                "media_type": i['media_type'],
                "media_url": i['media_url'],
                "permalink": i['permalink'],
                # "thumbnail_url": i['thumbnail_url'],
                "timestamp": i['timestamp'],
                "username": i['username'],
                "like_count": i['like_count'],
                "comments_count": i['comments_count']
            })

        return data_insight['data']
    except requests.HTTPError as e:
        print(f"[!] Exception caught: {e}")


### get requests for daily basic metrics (impressions, reach, profile_views, website_clicks) ###
@router.get("/instagram/daily-basic-metrics/impressions")
async def get_impressions(date: str):
    """ Get impressions by date """
    try:
        ref = db.reference(
            "/instagram/daily-basic-metrics/" + date + "/impressions")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/instagram/daily-basic-metrics/reach")
async def get_reach(date: str):
    """ Get reach by date """
    try:
        ref = db.reference(
            "/instagram/daily-basic-metrics/" + date + "/reach")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/instagram/daily-basic-metrics/profile_views")
async def get_profile_views(date: str):
    """ Get profile_views by date """
    try:
        ref = db.reference(
            "/instagram/daily-basic-metrics/" + date + "/profile_views")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/instagram/daily-basic-metrics/website_clicks")
async def get_website_clicks(date: str):
    """ Get website_clicks by date """
    try:
        ref = db.reference(
            "/instagram/daily-basic-metrics/" + date + "/website_clicks")
        return ref.get()
    except Exception as err:
        raise err


### get requests for basic channel metrics ###
@router.get("/instagram/basic-page-metrics/followers_count")
async def get_followers_count():
    """ Get followers_count by date """
    try:
        ref = db.reference(
            "/instagram/basic-page-metrics/" + "ig-page" + "/followers_count")
        return ref.get()
    except Exception as err:
        raise err


@router.get("/instagram/basic-page-metrics/media_count")
async def get_media_count():
    """ Get media_count by date """
    try:
        ref = db.reference(
            "/instagram/basic-page-metrics/" + "ig-page" + "/media_count")
        return ref.get()
    except Exception as err:
        raise err

### get requests for daily-follower-count metrics ###


@router.get("/instagram/daily-follower-count/daily-new-followers")
async def get_daily_new_followers(date: str):
    """ Get daily-new-followers by date """
    try:
        ref = db.reference(
            "/instagram/daily-new-followers/" + date + "/daily-new-followers")
        return ref.get()
    except Exception as err:
        raise err

### get requests for daily basic metrics ###


# @router.get('/instagram/basic-metrics')
# async def getImpressionReach():
#     url = params['endpoint_base'] + \
#         params['instagram_account_id'] + '/insights'
#     endpointParams = dict()
#     endpointParams['metric'] = 'impressions, reach, profile_views'
#     endpointParams['period'] = 'day'
#     endpointParams['since'] = '2022-08-21'
#     endpointParams['until'] = '2022-08-23'
#     endpointParams['access_token'] = params['access_token']

#     try:
#         data = requests.get(url, endpointParams)
#         data_insight = json.loads(data.content)
#         data_dict = dict()

#         metrics_arr = []

#         for i in range(len(data_insight['data'])):
#             metrics_arr.append((data_insight['data'][i]['name']))
#             print("hi")
#             # print([[a, x] for a, x in b.items()) for b in data_insight['data'][i]['values']])
#             print(data_insight['data'][i]['values'])
#             data_dict[metrics_arr[i]] = data_insight['data'][i]['values']

#         response_data = [
#             {"date": datetime.strptime(x['end_time'], "%Y-%m-%dT%H:%M:%S%z").strftime(
#                 '%Y-%m-%d'), "data": {'name': k, 'value': x['value']}}
#             for k, v in data_dict.items() for x in v
#         ]
#         # print(response_data)
#         print(response_data[0])
#         print(data_dict['reach'])
#         print(len(list(data_dict.values())[0]))
#         ref = db.reference("/instagram/basic-metrics")
#         for i in range(0, len(list(data_dict.values())[0])):
#             d = datetime.strptime(data_dict['reach'][i]['end_time'], "%Y-%m-%dT%H:%M:%S%z").strftime(
#                 '%Y-%m-%d')
#             ref.child(d).set({
#                 "reach": data_dict['reach'][i]['value'],
#                 "impressions": data_dict['impressions'][i]['value'],
#                 "profile_views": data_dict['profile_views'][i]['value']
#             })
#         # for i in range(list(data_dict.keys())):  # [0, 3]

#         # for k, v1, v2 in data_dict.items():
#         #     print(k, v1, v2)

#         return data_insight['data']
#     except requests.HTTPError as e:
#         print(f"[!] Exception caught: {e}")


# # f = open('/Users/roopa/Documents/NUS/Semesters/Y3S1/Capstone/dev/Analytical-Dashboard/backend/instagramAccessTokens.json')
# # data = json.load(f)
# # access_token = data["access_token"]
# # ig_page_id = data["ig_page_id"]


# # // 'https://graph.facebook.com/v14.0/{}/?access_token={}&fields=followers_count',
# url_list = [

#     'https://graph.facebook.com/v14.0/{}/insights/?access_token={}&metric=impressions,reach,profile_views&period=day'
# ]


# async def get_event(session):
#     return [await (await session.get(url_list[0].format(ig_page_id, access_token), ssl=False)).json()]


# # async def get_event(session):
# #     return [await (await session.get(url_list[0].format(ig_page_id, access_token), ssl=False)).json(), await (await session.get(url_list[1].format(ig_page_id, access_token), ssl=False)).json()]


# async def get_api_data():
#     async with aiohttp.ClientSession() as session:
#         return await asyncio.gather(get_event(session))
