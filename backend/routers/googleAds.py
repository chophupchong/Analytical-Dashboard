from cgi import test
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
    "client_customer_id": clientCustomerId,
    "use_proto_plus": protoPlus
}

client = GoogleAdsClient.load_from_dict(credentials)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


@router.put('/youtube/store-basic-ad-metrics/aggregated/{days}',  tags=["youtube-ads"])
def storeAggregatedBasicAdMetricsByDay(days: int):
    try:
        accountNameEdited = accountNames.copy()
        for token in range(len(accountNames)):
            credentials = {
                "developer_token": developerToken,
                "refresh_token": refreshToken,
                "client_id": clientID,
                "client_secret": clientSecret,
                "login_customer_id": managerCustomerId,
                "client_customer_id": clientCustomerId,
                "use_proto_plus": protoPlus
            }   
            client = GoogleAdsClient.load_from_dict(credentials)       
            ga_service = client.get_service("GoogleAdsService")
            endDate = datetime.today().strftime('%Y-%m-%d')
            startDate = (datetime.today() + relativedelta(days=-days)
                        ).strftime('%Y-%m-%d')
            prevPeriodStartDate = (datetime.today() + relativedelta(days=- 2 * days)
                        ).strftime('%Y-%m-%d')
            prevPeriodEndDate = startDate

            aggregatedBasicAdMetrics = f"""
                    SELECT  
                        campaign.name,
                        metrics.impressions, 
                        metrics.ctr, 
                        metrics.clicks,
                        metrics.engagements, 
                        metrics.interactions, 
                        metrics.average_cpm 
                        FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}'"""
            
            prevPeriodAggregatedBasicAdMetrics = f"""
                    SELECT  
                        campaign.name,
                        metrics.impressions, 
                        metrics.ctr, 
                        metrics.clicks,
                        metrics.engagements, 
                        metrics.interactions, 
                        metrics.average_cpm 
                        FROM campaign WHERE segments.date BETWEEN '{prevPeriodStartDate}' AND '{prevPeriodEndDate}'"""
            
            aggregateHourlyBasicAdMetrics = f"""
                    SELECT  
                        campaign.name,
                        metrics.impressions, 
                        metrics.ctr, 
                        metrics.clicks,
                        metrics.engagements, 
                        metrics.interactions, 
                        metrics.average_cpm,
                        segments.hour
                        FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}'"""

            aggregateWeeklyAndHourlyBasicAdMetrics = f"""
                    SELECT  
                        campaign.name,
                        metrics.impressions, 
                        metrics.ctr, 
                        metrics.clicks,
                        metrics.engagements, 
                        metrics.interactions, 
                        metrics.average_cpm,
                        segments.day_of_week,
                        segments.hour
                        FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}'"""
            
            #code to find respective account data from the same ad account.
            for word in accountNameEdited[token].split(" "):
                if word =='Chop':
                    continue
                else:
                    aggregatedBasicAdMetrics += f" AND campaign.name LIKE '%{word}%'"
                    prevPeriodAggregatedBasicAdMetrics += f" AND campaign.name LIKE '%{word}%'"
                    aggregateHourlyBasicAdMetrics += f" AND campaign.name LIKE '%{word}%'"
                    aggregateWeeklyAndHourlyBasicAdMetrics += f" AND campaign.name LIKE '%{word}%'"

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
                'interactions': 0,
            }

            prevPeriodDataset = {
                'impressions': 0,
                'spend': 0,
                'engagements': 0,
                'ctr': 0,
                'clicks': 0,
                'interactions': 0
            }
            
            #all average etc must be divided by 1 million. (intended calculation by google)
            for row in results:
                dataset['impressions'] += row.metrics.impressions
                dataset['ctr'] += row.metrics.ctr
                dataset['clicks'] += row.metrics.clicks
                dataset['engagements'] += row.metrics.engagements
                dataset['interactions'] += row.metrics.interactions
                dataset['spend'] += (row.metrics.average_cpm /1000000) * (row.metrics.impressions / 1000)

            prev_period_search_request = client.get_type("SearchGoogleAdsRequest")
            prev_period_search_request.customer_id = clientCustomerId
            prev_period_search_request.query = prevPeriodAggregatedBasicAdMetrics
            prev_period_results = ga_service.search(request=prev_period_search_request)

            for row in prev_period_results:
                prevPeriodDataset['impressions'] += row.metrics.impressions
                prevPeriodDataset['ctr'] += row.metrics.ctr
                prevPeriodDataset['clicks'] += row.metrics.clicks
                prevPeriodDataset['engagements'] += row.metrics.engagements
                prevPeriodDataset['interactions'] += row.metrics.interactions
                prevPeriodDataset['spend'] += (row.metrics.average_cpm /1000000) * (row.metrics.impressions / 1000)


            #code to get aggregated hourly metrics 
            hourly_search_request = client.get_type("SearchGoogleAdsRequest")
            hourly_search_request.customer_id = clientCustomerId
            hourly_search_request.query = aggregateHourlyBasicAdMetrics
            hourly_results = ga_service.search(request=hourly_search_request)
            hourlyDataset = {}
            for hour in range(0,24):
                if hour not in hourlyDataset:
                    hourlyDataset[hour] = {
                        'impressions': 0,
                        'spend': 0,
                        'engagements': 0,
                        'ctr': 0,
                        'clicks': 0,
                        'interactions': 0
                        }
                    
            for row in hourly_results:
                hourlyDataset[row.segments.hour]['impressions'] += row.metrics.impressions
                hourlyDataset[row.segments.hour]['spend'] +=  (row.metrics.average_cpm /1000000) * (row.metrics.impressions / 1000)
                hourlyDataset[row.segments.hour]['engagements'] += row.metrics.engagements
                hourlyDataset[row.segments.hour]['ctr'] += row.metrics.ctr
                hourlyDataset[row.segments.hour]['clicks'] += row.metrics.clicks
                hourlyDataset[row.segments.hour]['interactions'] += row.metrics.interactions
            

            #code to get aggregated weekly & hourly metrics 
            weekly_search_request = client.get_type("SearchGoogleAdsRequest")
            weekly_search_request.customer_id = clientCustomerId
            weekly_search_request.query = aggregateWeeklyAndHourlyBasicAdMetrics
            weekly_results = ga_service.search(request=weekly_search_request)
            week = {2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6:"Friday", 7:"Saturday", 8:"Sunday"}
            weeklyDataset = {}

            for day in week.values():
                if day not in weeklyDataset:
                    weeklyDataset[day] = {}
                for hour in range(0,24):
                    if hour not in weeklyDataset:
                        weeklyDataset[day][hour] = {
                            'impressions': 0,
                            'spend': 0,
                            'engagements': 0,
                            'ctr': 0,
                            'clicks': 0,
                            'interactions': 0
                            }

            for row in weekly_results:
                weeklyDataset[week[row.segments.day_of_week]][row.segments.hour]['impressions'] += row.metrics.impressions
                weeklyDataset[week[row.segments.day_of_week]][row.segments.hour]['spend'] +=  (row.metrics.average_cpm /1000000) * (row.metrics.impressions / 1000)
                weeklyDataset[week[row.segments.day_of_week]][row.segments.hour]['engagements'] += row.metrics.engagements
                weeklyDataset[week[row.segments.day_of_week]][row.segments.hour]['ctr'] += row.metrics.ctr
                weeklyDataset[week[row.segments.day_of_week]][row.segments.hour]['clicks'] += row.metrics.clicks
                weeklyDataset[week[row.segments.day_of_week]][row.segments.hour]['interactions'] += row.metrics.interactions
            
               
            ref = db.reference(f"/youtube/{accountNames[token]}/basic-ad-metrics/aggregated/{days}")
            #store aggregated basic ad metrics
            ref.set(dataset)

            #prevent errors caused by denominator zero for metrics percentage change.
            for key, value in dataset.items():
                if value == 0:
                    dataset[key] = dataset[key] + 1
                    prevPeriodDataset[key] = prevPeriodDataset[key] + 1
            
            for key, value in prevPeriodDataset.items():
                if value == 0:
                    prevPeriodDataset[key] = prevPeriodDataset[key] + 1
                    dataset[key] = dataset[key] + 1

            #store percentage changes for ad metrics
            ref.child("metricsPercentageChange").update({
                "impressionsPercentChange": ((dataset['impressions'] - prevPeriodDataset['impressions']) / dataset['impressions']) * 100,
                "ctrPercentChange": ((dataset['ctr'] - prevPeriodDataset['ctr']) / dataset['ctr']) * 100,
                "clicksPercentChange": ((dataset['clicks'] - prevPeriodDataset['clicks']) / dataset['clicks']) * 100,
                "engagementsPercentChange": ((dataset['engagements'] - prevPeriodDataset['engagements']) / dataset['engagements']) * 100,
                "interactionsPercentChange": ((dataset['interactions'] - prevPeriodDataset['interactions']) / dataset['interactions']) * 100,
                "spendPercentChange": ((dataset['spend'] - prevPeriodDataset['spend']) / dataset['spend']) * 100,
            })

            #store aggregated hourly ad metrics 
            ref.child("hourly").update(hourlyDataset)

            #store aggregated weekly-hourly ad metrics
            ref.child("weeklyHourly").update(weeklyDataset)


        return weeklyDataset

    except Exception as err:
        raise err


@router.put('/youtube/store-basic-ad-metrics/{days}', tags=["youtube-ads"])
def storeDailyBasicAdMetrics(days: int):
    try:
        accountNameEdited = accountNames.copy()
        for token in range(len(accountNames)):
            credentials = {
                "developer_token": developerToken,
                "refresh_token": refreshToken,
                "client_id": clientID,
                "client_secret": clientSecret,
                "login_customer_id": managerCustomerId,
                "client_customer_id": clientCustomerId,
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
                    metrics.average_cpm,
                    segments.date
                    FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}'"""
            
            for word in accountNameEdited[token].split(" "):
                if word =='Chop':
                    continue
                else:
                    dailyBasicAdMetrics += f" AND campaign.name LIKE '%{word}%'"
                
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
                dataset[f"{row.segments.date}"]['spend'] += (row.metrics.average_cpm /1000000) * (row.metrics.impressions / 1000)

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