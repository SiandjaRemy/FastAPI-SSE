import asyncio
import json
import psutil
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


async def system_stats_generator(request: Request):
    while True:
        if await request.is_disconnected():
            print("Client disconnected.")
            break

        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()

        stats = {
            "cpu_percent": cpu_usage,
            "memory_percent": memory_info.percent,
            "memory_used_mb": round(memory_info.used / (1024 * 1024), 2),
            "memory_total_mb": round(memory_info.total / (1024 * 1024), 2)
        }

        yield f"data: {json.dumps(stats)}\n\n"
        await asyncio.sleep(2)


@app.get("/system-stats")
async def stream_system_stats(request: Request):
    return StreamingResponse(system_stats_generator(request), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
