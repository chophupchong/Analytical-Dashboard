def sample(app):
    from fastapi import FastAPI, Depends
    import json
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adsinsights import AdsInsights
    from facebook_business.api import FacebookAdsApi

    f = open('./facebookAccessTokens.json')
    data = json.load(f)
    access_token = data["access_token"]
    ad_account_id = data["ad_account_id"]
    app_secret = data["app_secret"]
    app_id = data["app_id"]
    #print(access_token)
    @app.get("/facebook")
    async def root():
        FacebookAdsApi.init(access_token=access_token)
        dataset = {}
        fields = [
            'reach',
            'impressions',
            'spend',
            #'quality_score_ecvr',
            #'quality_score_ectr',
            #'actions:page_engagement',
            #'actions:like',
        ]
        params = {
            'time_range': {'since':'2022-08-16','until':'2022-09-15'},
            'filtering': [],
            'level': 'account',
            #'breakdowns': ['ad_name'],
        }
        result = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
        )
        
        for record in result:
            #print(dir(record))
            for metric_name in record:
                #print(metric_name + ": " + record[metric_name])
                dataset[metric_name] = record[metric_name]
        return json.dumps(dataset)
