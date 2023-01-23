import uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from datetime import datetime, timedelta

from api_utils import disable_security
from database import Database
from inverter import Inverter
from model import AppConfig

app_config = AppConfig()

db = Database(app_config.db_ip)
inverter = Inverter(app_config.inverter_ip)
api = FastAPI()
disable_security(api)


@api.on_event("startup")
@repeat_every(seconds=1)
def scheduler():
    inverter_data = {
        '_id': datetime.now(),
        'ac': inverter.get_ac_data(),
        'dc': inverter.get_dc_data(),
        'meter': inverter.get_meter_data()
    }
    db.insert('inverter_data', [inverter_data])


@api.get("/ac-usage", tags=["power"])
async def ac_usage():
    now = datetime.now()
    x = list(db.get_by_query('inverter_data', {'_id': {'$gte': now - timedelta(days=1)}}))
    return x[:10]


if __name__ == "__main__":
    uvicorn.run("power:api", host="0.0.0.0", port=8001, reload=True)
