from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

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
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

router = APIRouter()

# Database reference
ref = db.reference("/youtube")
f = open('./googleAdConfig.json')
tokenData = json.load(f)
refreshToken = tokenData['refresh_token']
developerToken = tokenData['developer_token']
accountNames = tokenData['account_name']
clientID = tokenData['client_id']
clientSecret = tokenData['client_secret']
managerCustomerId = tokenData['login_customer_id']
clientCustomerId = tokenData['client_customer_id']
protoPlus = tokenData['use_proto_plus']
credentials = {
    "developer_token": developerToken,
    "refresh_token": refreshToken,
    "client_id": clientID,
    "client_secret": clientSecret,
    "login_customer_id": managerCustomerId,
    "use_proto_plus": protoPlus
}

client = GoogleAdsClient.load_from_dict(credentials)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


@router.put('/youtube/store-basic-ad-metrics/aggregated/{days}',  tags=["youtube-ads"])
def storeAggregatedBasicAdMetricsByDay(days: int):
    try:
        #will change in future
        accountNameEdited = accountNames.copy()
        if accountNameEdited[0] == 'Chop Hup Chong':
            accountNameEdited[0] = 'Hup Chong' 

        for token in range(len(accountNames)):
            credentials = {
                "developer_token": developerToken,
                "refresh_token": refreshToken,
                "client_id": clientID,
                "client_secret": clientSecret,
                "login_customer_id": managerCustomerId,
                "use_proto_plus": protoPlus
            }   
            client = GoogleAdsClient.load_from_dict(credentials)       
            ga_service = client.get_service("GoogleAdsService")
            endDate = datetime.today().strftime('%Y-%m-%d')
            startDate = (datetime.today() + relativedelta(months=-days)
                        ).strftime('%Y-%m-%d')

            aggregatedBasicAdMetrics = f"""
                    SELECT  
                        campaign.name,
                        metrics.impressions, 
                        metrics.ctr, 
                        metrics.clicks,
                        metrics.engagements, 
                        metrics.interactions, 
                        metrics.average_cost 
                        FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}' AND campaign.name LIKE '%{accountNameEdited[token]}%' 
                    """
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = clientCustomerId
            search_request.query = aggregatedBasicAdMetrics
            results = ga_service.search(request=search_request)
            # add dates into the dictionary if necessary
            dataset = {
                'impressions': 0,
                'spend': 0,
                'engagements': 0,
                'ctr': 0,
                'clicks': 0,
                'interactions': 0
            }

            test = ""
            for row in results:
                dataset['impressions'] += row.metrics.impressions
                dataset['ctr'] += row.metrics.ctr
                dataset['clicks'] += row.metrics.clicks
                dataset['engagements'] += row.metrics.engagements
                dataset['interactions'] += row.metrics.interactions
                dataset['spend'] += row.metrics.average_cost * \
                    row.metrics.interactions
                test += f"{row.campaign.name}, "

            ref = db.reference(f"/youtube/{accountNames[token]}/basic-ad-metrics/aggregated/{days}")
            ref.set(dataset)
        return test

    except Exception as err:
        raise err


@router.put('/youtube/store-basic-ad-metrics/{days}', tags=["youtube-ads"])
def storeDailyBasicAdMetrics(days: int):
    try:
        accountNameEdited = accountNames.copy()
        if accountNameEdited[0] == 'Chop Hup Chong':
            accountNameEdited[0] = 'Hup Chong' 

        for token in range(len(accountNames)):
            credentials = {
                "developer_token": developerToken,
                "refresh_token": refreshToken,
                "client_id": clientID,
                "client_secret": clientSecret,
                "login_customer_id": managerCustomerId,
                "use_proto_plus": protoPlus
            }   
            client = GoogleAdsClient.load_from_dict(credentials)   
            ga_service = client.get_service("GoogleAdsService")
            endDate = datetime.today().strftime('%Y-%m-%d')
            startDate = (datetime.today() + relativedelta(days=-days)
                        ).strftime('%Y-%m-%d')

            # cannot develop further because test account returns empty metrics.
            dailyBasicAdMetrics = f"""
                SELECT  
                    metrics.impressions, 
                    metrics.ctr, 
                    metrics.clicks,
                    metrics.engagements, 
                    metrics.interactions, 
                    metrics.average_cost,
                    segments.date
                    FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}' AND campaign.name LIKE '%{accountNameEdited[token]}%'
                
                """
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = clientCustomerId
            search_request.query = dailyBasicAdMetrics
            results = ga_service.search(request=search_request)
            # add dates into the dictionary if necessary
            dataset = {}
            now = datetime.now()
            since = now - timedelta(days=days)
            for single_date in daterange(since, now):
                curr_date = single_date.strftime("%Y-%m-%d")
                prev_date = (single_date - timedelta(days=1)).strftime("%Y-%m-%d")
                dataset[curr_date] = {
                    'impressions': 0,
                    'spend': 0,
                    'engagements': 0,
                    'ctr': 0,
                    'clicks': 0,
                    'interactions': 0,
                    "date_start": prev_date,
                    "date_stop": curr_date
                }
            for row in results:
                dataset[f"{row.segments.date}"]['impressions'] += row.metrics.impressions
                dataset[f"{row.segments.date}"]['ctr'] += row.metrics.ctr
                dataset[f"{row.segments.date}"]['clicks'] += row.metrics.clicks
                dataset[f"{row.segments.date}"]['engagements'] += row.metrics.engagements
                dataset[f"{row.segments.date}"]['interactions'] += row.metrics.interactions
                dataset[f"{row.segments.date}"]['spend'] += row.metrics.average_cost * \
                    row.metrics.interactions

            ref = db.reference(f"/youtube/{accountNames[token]}/basic-ad-metrics/daily")
            ref.set(dataset)
        return dataset

    except Exception as err:
        raise err

### get requests for daily basic metrics ###


@router.get("/youtube/basic-ad-metrics/aggregated/{days}", tags=["youtube-ads"])
async def getAggregatedBasicAdMetrics(days: int):
    try:
        dataset = {}
        for token in range(len(accountNames)):
            ref = db.reference(f"/youtube/{accountNames[token]}/basic-ad-metrics/aggregated/{days}")
            dataset[accountNames[token]] = ref.get()
        
        return dataset
    except Exception as err:
        raise err


@router.get("/youtube/basic-ad-metrics/daily/{days}",  tags=["youtube-ads"])
async def getDailyBasicAdMetrics(days: int = 30):
    try:
        if days < 0:
            days = 30
        now = datetime.now()
        since = now - timedelta(days=days)
        dataset = {}
        for token in range(len(accountNames)):
            dataset[accountNames[token]] = {}
            ref = db.reference(f"/youtube/{accountNames[token]}/basic-ad-metrics/daily")
            metrics = ref.get()
            for single_date in daterange(since, now):
                curr_date = single_date.strftime("%Y-%m-%d")
                # only retrieves if the current daily date is already stored in db.
                if curr_date in metrics:
                    dataset[accountNames[token]][curr_date] = {}
                    for key, value in metrics[curr_date].items():
                        dataset[accountNames[token]][curr_date][key] = value
        return dataset

    except Exception as err:
        raise err