from fastapi import APIRouter, Query
from firebase_admin import db

# Additional imports
import json
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
import datetime
import requests
router = APIRouter()

ref = db.reference("/facebook")

f = open('./facebookAccessTokens.json')
data = json.load(f)
access_token = data["access_token"]
ad_account_ids = data["ad_account_ids"].split(" ")
app_secret = data["app_secret"]
app_id = data["app_id"]

#helper method
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

#test
# @router.get("/facebook/test")
# async def root():
#     FacebookAdsApi.init(access_token=access_token)
#     dataset = {}
#     fields = [
#         'reach',
#         'impressions',
#         'spend',
#         # 'quality_score_ecvr',
#         # 'quality_score_ectr',
#         # 'actions:page_engagement',
#         # 'actions:like',
#     ]
#     params = {
#         'time_range': {'since': '2022-08-16', 'until': '2022-09-15'},
#         'filtering': [],
#         'level': 'account',
#         # 'breakdowns': ['ad_name'],
#     }
#     result = AdAccount(ad_account_id).get_insights(
#         fields=fields,
#         params=params,
#     )

#     for record in result:
#         # print(dir(record))
#         for metric_name in record:
#             #print(metric_name + ": " + record[metric_name])
#             dataset[metric_name] = record[metric_name]
#     return json.dumps(dataset)

#ETL
@router.put("/facebook/basic-ad-metrics/aggregated/{days}")
async def getAggregatedBasicAdMetricsByDays(days: int = 30):
    if days < 0:
        days = 30
    FacebookAdsApi.init(access_token=access_token)
    dataset = {}
    fields = [
        'reach',
        'impressions',
        'spend',
        # 'quality_score_ecvr',
        # 'quality_score_ectr',
        # 'actions:page_engagement',
        # 'actions:like',
        #'actions', #most of the info is here
    ] #https://developers.facebook.com/docs/marketing-api/insights/parameters/v15.0
    
    #current period dates
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    now_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    since = now - datetime.timedelta(days=days)
    year = '{:02d}'.format(since.year)
    month = '{:02d}'.format(since.month)
    day = '{:02d}'.format(since.day)
    since_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    #previous period dates
    prev_now = since - datetime.timedelta(days=1)
    year = '{:02d}'.format(prev_now.year)
    month = '{:02d}'.format(prev_now.month)
    day = '{:02d}'.format(prev_now.day)
    prev_now_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    prev_since = prev_now - datetime.timedelta(days=days)
    year = '{:02d}'.format(prev_since.year)
    month = '{:02d}'.format(prev_since.month)
    day = '{:02d}'.format(prev_since.day)
    prev_since_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    params = {
        'time_range': {'since': since_day_month_year, 'until': now_day_month_year},
        'filtering': [], #https://developers.facebook.com/docs/marketing-api/ad-rules/overview/evaluation-spec
        'level': 'account',
        'breakdowns': ['publisher_platform'], #https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    }
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {
            "reach": "0",
            "impressions": "0",
            "spend": "0",
            "date_start": since_day_month_year,
            "date_stop": now_day_month_year,
            "previous_period": {
                "reach": "0",
                "impressions": "0",
                "spend": "0",
                "date_start": prev_since_day_month_year,
                "date_stop": prev_now_day_month_year,
            }
        }
        ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics/aggregated/{days}")
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )

        for record in result:
            # print(dir(record))
            if (record['publisher_platform'] != "facebook"):
                continue
            for metric_name in record:
                #print(metric_name + ": " + record[metric_name])
                dataset[ad_account_id][metric_name] = record[metric_name]
        ref.update({
            "reach": dataset[ad_account_id]["reach"],
            "impressions": dataset[ad_account_id]["impressions"],
            "spend": dataset[ad_account_id]["spend"],
            "date_start": dataset[ad_account_id]["date_start"],
            "date_stop": dataset[ad_account_id]["date_stop"]
        })
        
    #now to get and store previous period data.
    params = {
        'time_range': {'since': prev_since_day_month_year, 'until': prev_now_day_month_year}, #prev period dates
        'filtering': [], #https://developers.facebook.com/docs/marketing-api/ad-rules/overview/evaluation-spec
        'level': 'account',
        'breakdowns': ['publisher_platform'], #https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    }
    for ad_account_id in ad_account_ids:
        ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics/aggregated/{days}/previous_period")
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )

        for record in result:
            if (record['publisher_platform'] != "facebook"):
                continue
            for metric_name in record:
                dataset[ad_account_id]["previous_period"][metric_name] = record[metric_name]
        ref.update({
            "reach": dataset[ad_account_id]["previous_period"]["reach"],
            "impressions": dataset[ad_account_id]["previous_period"]["impressions"],
            "spend": dataset[ad_account_id]["previous_period"]["spend"],
            "date_start": dataset[ad_account_id]["previous_period"]["date_start"],
            "date_stop": dataset[ad_account_id]["previous_period"]["date_stop"]
        })
    return json.dumps(dataset)

#reading from db
@router.get("/facebook/basic-ad-metrics/aggregated/{days}")
async def getAggregatedBasicAdMetrics(days: int = 30):
    if days < 0:
        days = 30
    dataset = {}
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics/aggregated/{days}")
        metrics = ref.get()
        for key, value in metrics.items():
            dataset[ad_account_id][key] = value
    return json.dumps(dataset)
   
   
#ETL
@router.put("/facebook/basic-ad-metrics/daily/{days}")
async def getDailyBasicAdMetrics(days: int = 30):
    if days < 0:
        days = 30
    FacebookAdsApi.init(access_token=access_token)
    dataset = {}
    fields = [
        'reach',
        'impressions',
        'spend',
        # 'quality_score_ecvr',
        # 'quality_score_ectr',
        # 'actions:page_engagement',
        # 'actions:like',
        #'actions', #most of the info is here
    ]
    
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    now_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    since = now - datetime.timedelta(days=days)
    year = '{:02d}'.format(since.year)
    month = '{:02d}'.format(since.month)
    day = '{:02d}'.format(since.day)
    since_day_month_year = '{}-{}-{}'.format(year, month, day)
    params = {
        'time_range': {'since': since_day_month_year, 'until': now_day_month_year},
        'filtering': [],
        'level': 'account',
        #'breakdowns': ['ad_name'],
        'breakdowns': ['publisher_platform'],
        "time_increment": 1, #to get daily increment https://developers.facebook.com/docs/marketing-api/insights/parameters/v15.0
    }
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        for single_date in daterange(since, now):
            curr_date = single_date.strftime("%Y-%m-%d")
            prev_date = (single_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            dataset[ad_account_id][curr_date] = {
                "reach": "0",
                "impressions": "0",
                "spend": "0",
                "date_start": prev_date,
                "date_stop": curr_date
            }
        ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics/daily/")
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )
        print(result)
        for record in result:
            if (record['publisher_platform'] != "facebook"):
                continue
            dataset[ad_account_id][record["date_stop"]] = {
                "reach": record["reach"],
                "impressions": record["impressions"],
                "spend": record["spend"],
                "date_start": record["date_start"],
                "date_stop": record["date_stop"]
            }
        for curr_date_key in dataset[ad_account_id]:
            ref.child(curr_date_key).update({
                "reach": dataset[ad_account_id][curr_date_key]["reach"],
                "impressions": dataset[ad_account_id][curr_date_key]["impressions"],
                "spend": dataset[ad_account_id][curr_date_key]["spend"],
                "date_start": dataset[ad_account_id][curr_date_key]["date_start"],
                "date_stop": dataset[ad_account_id][curr_date_key]["date_stop"]
            })
    
    return json.dumps(dataset) 

#reading from db
@router.get("/facebook/basic-ad-metrics/daily/{days}")
async def getDailyBasicAdMetrics(days: int = 30):
    try:
        if days < 0:
            days = 30
        now = datetime.datetime.now()
        since = now - datetime.timedelta(days=days)
        dataset = {}
        for ad_account_id in ad_account_ids:
            dataset[ad_account_id] = {}
            ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics/daily")
            metrics = ref.get()
            for single_date in daterange(since, now):
                curr_date = single_date.strftime("%Y-%m-%d")
                if curr_date in metrics: #only retrieves if the current daily date is already stored in db.
                    dataset[ad_account_id][curr_date] = {}
                    for key, value in metrics[curr_date].items():
                        dataset[ad_account_id][curr_date][key] = value
        return json.dumps(dataset)
    except requests.HTTPError as e:
        print(f"[!] Exception caught: {e}")