import os

import redis
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (DateRange, Dimension, Filter,
                                                FilterExpression,
                                                FilterExpressionList, Metric,
                                                RunReportRequest)

from app.config import settings

# credential.json環境変数に保存 app.gaがapp.mainによって読み込まれる時に実行
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'app/ga-credential.json'

def ga_api_request_screenpageview(start_date:str,page_path:str,end_date:str):
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{settings.ga_property_id}",
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="pagePath",
                    string_filter=Filter.StringFilter(value=page_path),
                )
            )
    )
    response = client.run_report(request)
    screenpageview:int=0
    if len(response.rows) != 0 and len(response.rows[0].metric_values) != 0:
        screenpageview = int(response.rows[0].metric_values[0].value)
    return screenpageview
def ga_screenpageview(start_date:str,page_path:str,end_date:str):
    try:
        redis_conn = redis.Redis(host=settings.redis_host, port=6379, db=0,decode_responses=True)
        screenpageview_cache=redis_conn.get("ga-screenpageview-"+start_date+end_date+page_path)
        if screenpageview_cache:
            return int(screenpageview_cache)
        else:
            screenpageview = ga_api_request_screenpageview(start_date,page_path,end_date)
            redis_conn.set("ga-screenpageview-"+start_date+end_date+page_path,screenpageview,ex=60) # expire 1min
            return screenpageview
    except: # Redisへの接続に失敗
        screenpageview = ga_api_request_screenpageview(start_date,page_path,end_date)
        return screenpageview


