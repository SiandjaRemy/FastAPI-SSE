# FastAPI SSE — Real-Time System Monitor

A lightweight system monitor that streams live CPU and memory stats to the browser using **Server-Sent Events (SSE)** — no WebSockets, no JavaScript framework, no database.



<video src="https://github.com/user-attachments/assets/92ae748d-5282-4c1d-8057-b6788cd2181e" controls width="100%"></video>

---

## What it does

The FastAPI backend reads CPU and memory metrics from the host machine every 2 seconds using `psutil`, then pushes them down a persistent HTTP connection as a stream of SSE events. The browser receives each event and updates the dashboard in place — no polling, no page reloads.

```
psutil (host metrics)
  └─► FastAPI StreamingResponse
        └─► text/event-stream HTTP connection
              └─► browser EventSource API
                    └─► live dashboard update
```

**Dashboard panels:**
- CPU usage — current, peak (session), and rolling 10-reading average
- Per-core breakdown with load-level colour coding (blue → amber → red)
- CPU history sparkline (last 30 seconds)
- Memory panel — used / free / total with a fill bar

---

## Stack

| Layer    | Technology          |
|----------|---------------------|
| Backend  | Python 3.12, FastAPI, uvicorn |
| Metrics  | psutil              |
| Frontend | Vanilla HTML/CSS/JS |
| Runtime  | uv                  |

---

## Installation

```bash
git clone https://github.com/SiandjaRemy/FastAPI-SSE.git
cd FastAPI-SSE
uv sync
```

---

## Usage

```bash
uv run python main.py
```

Then open [http://localhost:8000](http://localhost:8000).

To adjust the stream cadence, change the `asyncio.sleep(2)` value in `system_stats_generator`. Lower values give smoother updates; keep it above ~0.5s to avoid saturating the CPU measurement itself.

---

## Project structure

```
FastAPI-SSE/
├── main.py            # FastAPI app + SSE generator
├── templates/
│   └── index.html     # Dashboard frontend
├── pyproject.toml
└── README.md
```

---

## How SSE works here

SSE is a native browser API (`EventSource`) built on plain HTTP. The server holds the connection open and writes newline-delimited `data:` blocks. The browser fires an `onmessage` event for each one. No library needed on either side.

```
# What the server writes to the response body:

data: {"cpu_percent": 34.2, "cpu_per_core": [41.0, 28.0, ...], ...}

data: {"cpu_percent": 37.8, "cpu_per_core": [44.1, 31.2, ...], ...}
```

The browser automatically reconnects if the connection drops.

---

## Credits

Inspired by [Thomas Reid's article on SSE in Python](https://towardsdatascience.com/introducing-server-sent-events-in-python/).