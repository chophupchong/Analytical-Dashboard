from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

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
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

router = APIRouter()

# Database reference
ref = db.reference("/youtube")
f = open('./googleAdConfig.json')
tokenData = json.load(f)
refreshToken = tokenData['refresh_token']
developerToken = tokenData['developer_token']
clientID = tokenData['client_id']
clientSecret = tokenData['client_secret']
managerCustomerId = tokenData['login_customer_id']
clientCustomerId = tokenData['client_customer_id']
protoPlus = tokenData['use_proto_plus']
credentials = {
    "developer_token" : developerToken,
    "refresh_token": refreshToken,
    "client_id": clientID,
    "client_secret": clientSecret,
    "login_customer_id": managerCustomerId,
    "use_proto_plus": protoPlus
}
                                                    
client = GoogleAdsClient.load_from_dict(credentials)

@router.post('/youtube/basic-ad-metrics')
def storeBasicAdMetrics(num_months: int):
    ga_service = client.get_service("GoogleAdsService")
    endDate = datetime.today().strftime('%Y-%m-%d')
    startDate = (datetime.today() + relativedelta(months=-num_months)
                ).strftime('%Y-%m-%d')
    
    totalBasicAdMetrics = f"""
            SELECT 
                campaign.name, 
                metrics.impressions, 
                metrics.ctr, 
                metrics.clicks,
                metrics.engagements, 
                metrics.interactions, 
                metrics.average_cost 
                FROM campaign WHERE segments.date BETWEEN '{startDate}' AND '{endDate}'
            """
    search_request = client.get_type("SearchGoogleAdsRequest")
    search_request.customer_id = clientCustomerId
    search_request.query = totalBasicAdMetrics
    results = ga_service.search(request=search_request)
    #add dates into the dictionary if necessary
    basicAdMetrics = { 
        'impressions': 0,
        'spend' : 0,
        'engagements' : 0,
        'ctr' : 0,
        'clicks' : 0,
        'interactions' : 0,
    }
    
    for row in results: 
        basicAdMetrics['impressions'] += row.metrics.impressions
        basicAdMetrics['ctr'] += row.metrics.ctr
        basicAdMetrics['clicks'] += row.metrics.clicks
        basicAdMetrics['engagements'] += row.metrics.engagements
        basicAdMetrics['interactions'] += row.metrics.interactions
        basicAdMetrics['spend'] += row.metrics.average_cost * row.metrics.interactions

    ref = db.reference("/youtube/basic-ad-metrics/total")
    ref.update(basicAdMetrics)
    return basicAdMetrics
