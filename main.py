import asyncio
import json
import psutil
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# Allow both ports and any origin for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


async def system_stats_generator(request: Request):
    # Prime psutil's per-core sampler
    psutil.cpu_percent(percpu=True)

    while True:
        if await request.is_disconnected():
            print("Client disconnected.")
            break

        memory_info = psutil.virtual_memory()

        stats = {
            "cpu_percent": psutil.cpu_percent(),
            "cpu_per_core": psutil.cpu_percent(percpu=True),
            "memory_percent": memory_info.percent,
            "memory_used_mb": round(memory_info.used / (1024 ** 2), 2),
            "memory_total_mb": round(memory_info.total / (1024 ** 2), 2),
        }

        yield f"data: {json.dumps(stats)}\n\n"
        await asyncio.sleep(2)


@app.get("/system-stats")
async def stream_system_stats(request: Request):
    return StreamingResponse(
        system_stats_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
