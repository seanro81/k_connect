import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from contextlib import asynccontextmanager

from adapters.pg import SimpleORM
from adapters.kafka import consumer
from utils.promethius import json_to_prometheus

from settings.config import logging,APP_PORT

app = FastAPI()


@app.get("/metrics")
async def metrics():
    try:
        orm = SimpleORM()
        data_json = await orm.metrics_get(metric_id='all')
        output = await json_to_prometheus(json_str=data_json)
    except Exception as e:
        msg = f"/metrics: Ошибка выполнения: {str(e)}"
        logging.error(msg)
        return Response(content=msg, status_code=500, media_type="application/xml")
    return Response(content=output, status_code=200, media_type="application/xml")


@app.on_event("startup")
async def startup():
    orm = SimpleORM()
    await orm.migration()
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(consumer(), loop)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
