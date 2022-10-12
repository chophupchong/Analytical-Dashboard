from fastapi import APIRouter
from firebase_admin import db

# Additional imports
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

router = APIRouter()

# Database reference

ref = db.reference("/facebookpage")
f = open('./facebookPageAccessTokens.json')
data = json.load(f)

# Define Parameters Dictionary
params = dict()
params['graph_domain'] = 'https://graph.facebook.com'
params['graph_version'] = 'v14.0'
params['endpoint_base'] = params['graph_domain'] + '/' + params['graph_version'] + '/'
params['facebook_page_id'] = data["page_id"]
params['access_token'] = data["access_token"]
"""
@router.get('/facebookPage')
async def getBasicPageMetrics():
    x = requests.get("https://graph.facebook.com/v14.0/514523281960829/insights/page_impressions?access_token=EAAF8MV19jIkBAONjhXDE7HZCEdsKqPZBtJHb5rwTUZBiItHrvsCQcwZBgllGt0zJIa743GsxTzkq64JFCqd0TW321oYjMctAj0iQjtZAVb5VazZCM3q2lyudFwSECkv53FPnB6wLXUMhZAi1zRcASerNBgkZBWj2WK7myZCV8On8tc1fnlGZAr00JxdyINSNx7ZBCOafdRWxCyZBbSgU9ovq7aZAf")
    print(x.json())
"""

@router.get('/facebookPage/basic-page-metrics')
async def getBasicPageMetrics():
    url = params['endpoint_base'] + \
        params['facebook_page_id'] + "/insights?metric="
    endpointParams = dict()
    endpointParams['fields'] = 'page_impressions'
    endpointParams['access_token'] = params['access_token']

    try:
        data = requests.get(url , endpointParams)
        #data = requests.get(url + "page_impressions/day?access_token=" +params['access_token'])
        data_insight = json.loads(data.content)

        ref = db.reference("/facebookPage/basic-page-metrics")
        '''
        ref.child('facebook-page').set({
            "page_impressions": data_insight['page_impressions']
        })
        '''
        return data_insight
    except requests.HTTPError as e:
        print(f"[!] Exception caught: {e}")
