from fastapi import APIRouter, Query
from firebase_admin import db

# Additional imports
import json
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
import datetime
router = APIRouter()

ref = db.reference("/facebook")

f = open('./facebookAccessTokens.json')
data = json.load(f)
access_token = data["access_token"]
ad_account_ids = data["ad_account_ids"].split(" ")
app_secret = data["app_secret"]
app_id = data["app_id"]


@router.get("/facebook/test")
async def root():
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
    ]
    params = {
        'time_range': {'since': '2022-08-16', 'until': '2022-09-15'},
        'filtering': [],
        'level': 'account',
        # 'breakdowns': ['ad_name'],
    }
    result = AdAccount(ad_account_id).get_insights(
        fields=fields,
        params=params,
    )

    for record in result:
        # print(dir(record))
        for metric_name in record:
            #print(metric_name + ": " + record[metric_name])
            dataset[metric_name] = record[metric_name]
    return json.dumps(dataset)

@router.put("/facebook/basic-ad-metrics")
async def getBasicAdMetrics(days: int = 30):
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
    }
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics")
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )

        for record in result:
            # print(dir(record))
            for metric_name in record:
                #print(metric_name + ": " + record[metric_name])
                dataset[ad_account_id][metric_name] = record[metric_name]
                ref.update({
                    metric_name: record[metric_name],
                })
    
    return json.dumps(dataset)

@router.get("/facebook/basic-ad-metrics")
async def getBasicAdMetrics():
    dataset = {}
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        ref = db.reference(f"/facebook/{ad_account_id}/basic-ad-metrics/")
        metrics = ref.get()
        for key, value in metrics.items():
            dataset[ad_account_id][key] = value
    return json.dumps(dataset)
    