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

ref = db.reference("/meta")

f = open('./facebookAccessTokens.json') #tobeupdated
data = json.load(f)
access_token = data["access_token"]
ad_account_ids = data["ad_account_ids"].split(" ")
app_secret = data["app_secret"]
app_id = data["app_id"]

#helper method
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + datetime.timedelta(n)

#helper method
def actions_dictionary(actions_list):
    actions_dict = {
        "rsvp": 0, #events_responses
        "post_engagement": 0, #post_engagements
        "onsite_conversion.messaging_conversation_started_7d": 0, #messaging_conversations_started
        "link_click": 0, #link_clicks
    }
    for action in actions_list:
        if action["action_type"] in actions_dict:
            actions_dict[action["action_type"]] = int(action["value"])
    return actions_dict

#ETL
@router.put("/meta/store/ad-metrics/gender/aggregated/{days}")
async def updateAggregatedBasicAdMetricsByDays(days: int = 30):
    if days <= 0:
        days = 1
    if days > 550:
        days = 550
    FacebookAdsApi.init(access_token=access_token)
    dataset = {}
    fields = [
        'reach',
        'impressions',
        'spend',
        'actions', #ad objective metrics
        # 'quality_score_ecvr',
        # 'quality_score_ectr',
        # 'actions:page_engagement',
        # 'actions:like',
        
    ] #https://developers.facebook.com/docs/marketing-api/insights/parameters/v15.0
    
    #current period dates
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    now_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    since = now - datetime.timedelta(days=days-1) #days-1 since days = 1 will be today and ytd
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
    
    prev_since = prev_now - datetime.timedelta(days=days-1)
    year = '{:02d}'.format(prev_since.year)
    month = '{:02d}'.format(prev_since.month)
    day = '{:02d}'.format(prev_since.day)
    prev_since_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    params = {
        'time_range': {'since': since_day_month_year, 'until': now_day_month_year},
        'filtering': [], #https://developers.facebook.com/docs/marketing-api/ad-rules/overview/evaluation-spec
        'level': 'account',
        'breakdowns': ['gender'], #https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    }
    genders = ["male", "female", "unknown"]
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        for gender in genders:
            dataset[ad_account_id][gender] = {
                "reach": 0,
                "impressions": 0,
                "spend": 0.00,
                "events_responses": 0,
                "post_engagements": 0,
                "messaging_conversations_started": 0,
                "link_clicks": 0,
                "avg_cost_per_ad_obj": 0,
                "date_start": since_day_month_year,
                "date_stop": now_day_month_year,
                "previous_period": {
                    "reach": 0,
                    "impressions": 0,
                    "spend": 0.00,
                    "events_responses": 0,
                    "post_engagements": 0,
                    "messaging_conversations_started": 0,
                    "link_clicks": 0,
                    "avg_cost_per_ad_obj": 0,
                    "date_start": prev_since_day_month_year,
                    "date_stop": prev_now_day_month_year,
                }
            }
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )

        for record in result:
            curr_gender = record["gender"]
            actions_list = []
            if "actions" in record:
                actions_list = record["actions"]
            actions_dict = actions_dictionary(actions_list)
            dataset[ad_account_id][curr_gender]["reach"] += int(record["reach"])
            dataset[ad_account_id][curr_gender]["impressions"] += int(record["impressions"])
            dataset[ad_account_id][curr_gender]["spend"] += float(record["spend"])
            dataset[ad_account_id][curr_gender]["impressions"] += int(record["impressions"])
            dataset[ad_account_id][curr_gender]["events_responses"] += actions_dict["rsvp"]
            dataset[ad_account_id][curr_gender]["post_engagements"] += actions_dict["post_engagement"]
            dataset[ad_account_id][curr_gender]["messaging_conversations_started"] += actions_dict["onsite_conversion.messaging_conversation_started_7d"]
            dataset[ad_account_id][curr_gender]["link_clicks"] += actions_dict["link_click"]
        for gender in genders:
            ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/aggregated/{days}/gender/{gender}")
            if dataset[ad_account_id][gender]["spend"] > 0:
                dataset[ad_account_id][gender]["avg_cost_per_ad_obj"] = (dataset[ad_account_id][gender]["events_responses"] 
                + dataset[ad_account_id][gender]["post_engagements"]
                + dataset[ad_account_id][gender]["messaging_conversations_started"] 
                + dataset[ad_account_id][gender]["link_clicks"]) / dataset[ad_account_id][gender]["spend"]
            ref.update({
                "reach": dataset[ad_account_id][gender]["reach"],
                "impressions": dataset[ad_account_id][gender]["impressions"],
                "spend": dataset[ad_account_id][gender]["spend"],
                "events_responses": dataset[ad_account_id][gender]["events_responses"],
                "post_engagements": dataset[ad_account_id][gender]["post_engagements"],
                "messaging_conversations_started": dataset[ad_account_id][gender]["messaging_conversations_started"],
                "link_clicks": dataset[ad_account_id][gender]["link_clicks"],
                "date_start": dataset[ad_account_id][gender]["date_start"],
                "date_stop": dataset[ad_account_id][gender]["date_stop"],
                "avg_cost_per_ad_obj": dataset[ad_account_id][gender]["avg_cost_per_ad_obj"]
            })
            
    #now to get and store previous period data.
    params = {
        'time_range': {'since': prev_since_day_month_year, 'until': prev_now_day_month_year}, #prev period dates
        'filtering': [], #https://developers.facebook.com/docs/marketing-api/ad-rules/overview/evaluation-spec
        'level': 'account',
        'breakdowns': ['gender'], #https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    }
    for ad_account_id in ad_account_ids:
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )

        for record in result:
            curr_gender = record["gender"]
            actions_list = []
            if "actions" in record:
                actions_list = record["actions"]
            actions_dict = actions_dictionary(actions_list)
            dataset[ad_account_id][curr_gender]["previous_period"]["reach"] += int(record["reach"])
            dataset[ad_account_id][curr_gender]["previous_period"]["impressions"] += int(record["impressions"])
            dataset[ad_account_id][curr_gender]["previous_period"]["spend"] += float(record["spend"])
            dataset[ad_account_id][curr_gender]["previous_period"]["events_responses"] += actions_dict["rsvp"]
            dataset[ad_account_id][curr_gender]["previous_period"]["post_engagements"] += actions_dict["post_engagement"]
            dataset[ad_account_id][curr_gender]["previous_period"]["messaging_conversations_started"] += actions_dict["onsite_conversion.messaging_conversation_started_7d"]
            dataset[ad_account_id][curr_gender]["previous_period"]["link_clicks"] += actions_dict["link_click"]
        for gender in genders:
            ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/aggregated/{days}/gender/{gender}/previous_period")
            if dataset[ad_account_id][gender]["previous_period"]["spend"] > 0:
                dataset[ad_account_id][gender]["previous_period"]["avg_cost_per_ad_obj"] = (dataset[ad_account_id][gender]["previous_period"]["events_responses"] 
                + dataset[ad_account_id][gender]["previous_period"]["post_engagements"]
                + dataset[ad_account_id][gender]["previous_period"]["messaging_conversations_started"] 
                + dataset[ad_account_id][gender]["previous_period"]["link_clicks"]) / dataset[ad_account_id][gender]["previous_period"]["spend"]
            ref.update({
                "reach": dataset[ad_account_id][gender]["previous_period"]["reach"],
                "impressions": dataset[ad_account_id][gender]["previous_period"]["impressions"],
                "spend": dataset[ad_account_id][gender]["previous_period"]["spend"],
                "events_responses": dataset[ad_account_id][gender]["previous_period"]["events_responses"],
                "post_engagements": dataset[ad_account_id][gender]["previous_period"]["post_engagements"],
                "messaging_conversations_started": dataset[ad_account_id][gender]["previous_period"]["messaging_conversations_started"],
                "link_clicks": dataset[ad_account_id][gender]["previous_period"]["link_clicks"],
                "date_start": dataset[ad_account_id][gender]["previous_period"]["date_start"],
                "date_stop": dataset[ad_account_id][gender]["previous_period"]["date_stop"],
                "avg_cost_per_ad_obj": dataset[ad_account_id][gender]["previous_period"]["avg_cost_per_ad_obj"]
            })
    return json.dumps(dataset)

#reading from db
@router.get("/meta/ad-metrics/gender/aggregated/{days}")
async def getAggregatedBasicAdMetrics(days: int = 30):
    if days <= 0:
        days = 1
    if days > 1110:
        days = 1110
    dataset = {}
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/aggregated/{days}/gender")
        metrics = ref.get()
        for key, value in metrics.items():
            dataset[ad_account_id][key] = value
    return json.dumps(dataset)
   
   
#ETL
@router.put("/meta/store/ad-metrics/gender/daily/{days}") 
#max days is 1110
#"message": "(#3018) The start date of the time range cannot be beyond 37 months from the current date",
async def updateDailyBasicAdMetrics(days: int = 30):
    if days <= 0:
        days = 1
    if days > 1110:
        days = 1110
    FacebookAdsApi.init(access_token=access_token)
    dataset = {}
    fields = [
        'reach',
        'impressions',
        'spend',
        'actions',
    ]
    
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    now_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    since = now - datetime.timedelta(days=days-1)
    year = '{:02d}'.format(since.year)
    month = '{:02d}'.format(since.month)
    day = '{:02d}'.format(since.day)
    since_day_month_year = '{}-{}-{}'.format(year, month, day)
    params = {
        'time_range': {'since': since_day_month_year, 'until': now_day_month_year},
        'filtering': [],
        'level': 'account',
        'breakdowns': ['gender'],
        "time_increment": 1, #to get daily increment https://developers.facebook.com/docs/marketing-api/insights/parameters/v15.0
    }
    genders = ["male", "female", "unknown"]
    for ad_account_id in ad_account_ids:
        dataset[ad_account_id] = {}
        for single_date in daterange(since, now):
            curr_date = single_date.strftime("%Y-%m-%d")
            dataset[ad_account_id][curr_date] = {}
            for gender in genders:
                dataset[ad_account_id][curr_date][gender] = {
                    "reach": 0,
                    "impressions": 0,
                    "spend": 0.00,
                    "events_responses": 0,
                    "post_engagements": 0,
                    "messaging_conversations_started": 0,
                    "link_clicks": 0,
                    "avg_cost_per_ad_obj": 0,
                    "date_start": curr_date,
                    "date_stop": curr_date
                }
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )
        for record in result:
            curr_gender = record["gender"]
            actions_list = []
            if "actions" in record:
                actions_list = record["actions"]
            actions_dict = actions_dictionary(actions_list)
            dataset[ad_account_id][record["date_stop"]][curr_gender]["reach"] += int(record["reach"])
            dataset[ad_account_id][record["date_stop"]][curr_gender]["impressions"] += int(record["impressions"])
            dataset[ad_account_id][record["date_stop"]][curr_gender]["spend"] += float(record["spend"])
            dataset[ad_account_id][record["date_stop"]][curr_gender]["events_responses"] += actions_dict["rsvp"]
            dataset[ad_account_id][record["date_stop"]][curr_gender]["post_engagements"] += actions_dict["post_engagement"]
            dataset[ad_account_id][record["date_stop"]][curr_gender]["messaging_conversations_started"] += actions_dict["onsite_conversion.messaging_conversation_started_7d"]
            dataset[ad_account_id][record["date_stop"]][curr_gender]["link_clicks"] += actions_dict["link_click"]
            if dataset[ad_account_id][record["date_stop"]][curr_gender]["spend"] > 0:
                dataset[ad_account_id][record["date_stop"]][curr_gender]["avg_cost_per_ad_obj"] = (dataset[ad_account_id][record["date_stop"]][curr_gender]["events_responses"] 
                + dataset[ad_account_id][record["date_stop"]][curr_gender]["post_engagements"]
                + dataset[ad_account_id][record["date_stop"]][curr_gender]["messaging_conversations_started"] 
                + dataset[ad_account_id][record["date_stop"]][curr_gender]["link_clicks"]) / dataset[ad_account_id][record["date_stop"]][curr_gender]["spend"]
        ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/daily/gender/")
        for curr_date_key in dataset[ad_account_id]:
            for gender in genders:
                ref.child(curr_date_key).update({gender:{
                    "reach": dataset[ad_account_id][curr_date_key][gender]["reach"],
                    "impressions": dataset[ad_account_id][curr_date_key][gender]["impressions"],
                    "spend": dataset[ad_account_id][curr_date_key][gender]["spend"],
                    "events_responses": dataset[ad_account_id][curr_date_key][gender]["events_responses"],
                    "post_engagements": dataset[ad_account_id][curr_date_key][gender]["post_engagements"],
                    "messaging_conversations_started": dataset[ad_account_id][curr_date_key][gender]["messaging_conversations_started"],
                    "link_clicks": dataset[ad_account_id][curr_date_key][gender]["link_clicks"],
                    "date_start": dataset[ad_account_id][curr_date_key][gender]["date_start"],
                    "date_stop": dataset[ad_account_id][curr_date_key][gender]["date_stop"],
                    "avg_cost_per_ad_obj": dataset[ad_account_id][curr_date_key][gender]["avg_cost_per_ad_obj"]
                }})
        #update last updated date
        ref.child("last_updated_date").update({
            "date": now_day_month_year
        })
    return json.dumps(dataset) 


#ETL the main daily call since we dont want to call all the way to history everytime we want the "latest" data since the last time we called it
@router.put("/meta/storead-metrics/gender/latest-daily/") 
#max days is 1110
#"message": "(#3018) The start date of the time range cannot be beyond 37 months from the current date",
async def updateDailyBasicAdMetrics():
    FacebookAdsApi.init(access_token=access_token)
    dataset = {}
    fields = [
        'reach',
        'impressions',
        'spend',
        'actions',
    ]
    
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    now_day_month_year = '{}-{}-{}'.format(year, month, day)
    
    genders = ["male", "female", "unknown"]
    for ad_account_id in ad_account_ids:
        ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/daily/gender/last_updated_date")
        since_day_month_year_date = ref.get()
        if since_day_month_year_date == None:
            since = now - datetime.timedelta(days=1110)
            year = '{:02d}'.format(since.year)
            month = '{:02d}'.format(since.month)
            day = '{:02d}'.format(since.day)
            since_day_month_year = '{}-{}-{}'.format(year, month, day)
        else:
            since_day_month_year = since_day_month_year_date["date"]
            since = datetime.datetime.strptime(since_day_month_year, "%Y-%m-%d")
        dataset[ad_account_id] = {}
        for single_date in daterange(since, now):
            curr_date = single_date.strftime("%Y-%m-%d")
            dataset[ad_account_id][curr_date] = {}
            for gender in genders:
                dataset[ad_account_id][curr_date][gender] = {
                    "reach": 0,
                    "impressions": 0,
                    "spend": 0.00,
                    "events_responses": 0,
                    "post_engagements": 0,
                    "messaging_conversations_started": 0,
                    "link_clicks": 0,
                    "avg_cost_per_ad_obj": 0,
                    "date_start": curr_date,
                    "date_stop": curr_date
                }
        params = {
            'time_range': {'since': since_day_month_year, 'until': now_day_month_year},
            'filtering': [],
            'level': 'account',
            'breakdowns': ['gender'],
            "time_increment": 1, #to get daily increment https://developers.facebook.com/docs/marketing-api/insights/parameters/v15.0
        }
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )
        for record in result:
            curr_gender = record["gender"]
            actions_list = []
            if "actions" in record:
                actions_list = record["actions"]
            actions_dict = actions_dictionary(actions_list)
            dataset[ad_account_id][record["date_stop"]][curr_gender]["reach"] += int(record["reach"])
            dataset[ad_account_id][record["date_stop"]][curr_gender]["impressions"] += int(record["impressions"])
            dataset[ad_account_id][record["date_stop"]][curr_gender]["spend"] += float(record["spend"])
            dataset[ad_account_id][record["date_stop"]][curr_gender]["events_responses"] += actions_dict["rsvp"]
            dataset[ad_account_id][record["date_stop"]][curr_gender]["post_engagements"] += actions_dict["post_engagement"]
            dataset[ad_account_id][record["date_stop"]][curr_gender]["messaging_conversations_started"] += actions_dict["onsite_conversion.messaging_conversation_started_7d"]
            dataset[ad_account_id][record["date_stop"]][curr_gender]["link_clicks"] += actions_dict["link_click"]
            if dataset[ad_account_id][record["date_stop"]][curr_gender]["spend"] > 0:
                dataset[ad_account_id][record["date_stop"]][curr_gender]["avg_cost_per_ad_obj"] = (dataset[ad_account_id][record["date_stop"]][curr_gender]["events_responses"] 
                + dataset[ad_account_id][record["date_stop"]][curr_gender]["post_engagements"]
                + dataset[ad_account_id][record["date_stop"]][curr_gender]["messaging_conversations_started"] 
                + dataset[ad_account_id][record["date_stop"]][curr_gender]["link_clicks"]) / dataset[ad_account_id][record["date_stop"]][curr_gender]["spend"]
        ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/daily/gender/")
        for curr_date_key in dataset[ad_account_id]:
            for gender in genders:
                ref.child(curr_date_key).update({gender:{
                    "reach": dataset[ad_account_id][curr_date_key][gender]["reach"],
                    "impressions": dataset[ad_account_id][curr_date_key][gender]["impressions"],
                    "spend": dataset[ad_account_id][curr_date_key][gender]["spend"],
                    "events_responses": dataset[ad_account_id][curr_date_key][gender]["events_responses"],
                    "post_engagements": dataset[ad_account_id][curr_date_key][gender]["post_engagements"],
                    "messaging_conversations_started": dataset[ad_account_id][curr_date_key][gender]["messaging_conversations_started"],
                    "link_clicks": dataset[ad_account_id][curr_date_key][gender]["link_clicks"],
                    "date_start": dataset[ad_account_id][curr_date_key][gender]["date_start"],
                    "date_stop": dataset[ad_account_id][curr_date_key][gender]["date_stop"],
                    "avg_cost_per_ad_obj": dataset[ad_account_id][curr_date_key][gender]["avg_cost_per_ad_obj"]
                }})
        #update last updated date
        ref.child("last_updated_date").update({
            "date": now_day_month_year
        })
    return json.dumps(dataset) 

#reading from db
@router.get("/meta/ad-metrics/gender/daily/{days}")
async def getDailyBasicAdMetrics(days: int = 30):
    try:
        if days < 0:
            days = 1
        if days > 1110:
            days = 1110
        now = datetime.datetime.now()
        since = now - datetime.timedelta(days=days-1) #days-1 since if we want 1 day then its just today's data
        dataset = {}
        for ad_account_id in ad_account_ids:
            dataset[ad_account_id] = {}
            ref = db.reference(f"/meta/{ad_account_id}/breakdown-ad-metrics/daily/gender/")
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