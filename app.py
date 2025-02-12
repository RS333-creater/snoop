from fastapi import FastAPI, HTTPException
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
import logging

app = FastAPI()

# Google Analytics クライアントをグローバル変数として定義
client = BetaAnalyticsDataClient()

GA4_PROPERTY_ID = "1600198309"  # テストデータ用のGA4プロパティID

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/analytics/impressions")
def get_impressions():
    try:
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            metrics=[Metric(name="impressions")],
            dimensions=[Dimension(name="date")]
        )
        response = client.run_report(request)
        data = [{"date": row.dimension_values[0].value, "impressions": row.metric_values[0].value} for row in response.rows]
        return {"impression_data": data}
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
