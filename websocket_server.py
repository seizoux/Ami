import asyncio
import logging
from os import name
from typing import Mapping, Optional

import aiohttp
from aiohttp import web

logging.basicConfig(level=logging.INFO)

app = web.Application()

class WsWrapper:
    def __init__(self, ws: web.WebSocketResponse) -> None:
        self.ws = ws
        self.waiter: Optional[asyncio.Future] = None
        pass

websockets: Mapping[str, WsWrapper] = {}

async def websocket_callback(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    logging.info('websocket opened')
    try:
        cluster = await ws.receive_str(timeout=10)
    except asyncio.TimeoutError:
        logging.warning("timed out waiting for cluster to identify")
        await ws.close(code=4000)
        return ws

    logging.info(f'got connection from cluster {cluster}')

    wrapper = websockets[cluster] = WsWrapper(ws)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()
                command = data.get("cmd")
                if command is None:
                    if wrapper.waiter is not None:
                        wrapper.waiter.set_result({"cluster": cluster, "data": data})
                    continue
                elif command == "close":
                    logging.info("gracefully closing connection to {}")
                elif command == "connected_clusters":
                    await ws.send_json({"data": list(websockets.keys())})
                elif command == "broadcast":
                    payload = data['data'].get('payload')
                    timeout = data['data'].get('timeout', 10)
                    if not payload:
                        continue
                    futures: list[asyncio.Future] = []
                    slf = None
                    for clust, websocket in websockets.items():
                        if clust == cluster:
                            await ws.send_json(payload)
                            slf = await ws.receive_json(timeout=timeout)
                            continue
                        await websocket.ws.send_json(payload)
                        waiter = websocket.waiter = asyncio.Future()
                        futures.append(waiter)
                    try:
                        resps, not_done = await asyncio.wait(futures, timeout=timeout)
                        # resps = []
                        rsps = [await r for r in resps]
                        rsps.append({'cluster': cluster, 'data': slf})
                        await ws.send_json({'data': {'responses': rsps, 'not_done': len(not_done)}})
                    except asyncio.TimeoutError:
                        await ws.send_json({'error': 'timeout', 'success': True})
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.error(
                    f"ws connection to {cluster} closed with exception {ws.exception()}"
                )
            else:
                logging.error(f'incorrect message type {msg.type}')
                return
    finally:
        websockets.pop(cluster)

    logging.info(f"websocket connection closed to {cluster}")

    return ws


app.add_routes([web.get("/ws", websocket_callback)])

web.run_app(app, port='42069')
