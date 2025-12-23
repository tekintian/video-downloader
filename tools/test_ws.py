import asyncio
import traceback
import websockets

async def test():
    try:
        print('trying to connect')
        
        # try common host variants
        hosts = ['127.0.0.1', 'localhost', '[::1]']
        ws = None
        last_exc = None
        for h in hosts:
            try:
                uri = f"ws://{h}:8000/ws"
                print('trying', uri)
                ws = await asyncio.wait_for(websockets.connect(uri), timeout=3)
                print('connected to', uri)
                break
            except Exception as exc:
                print('connect to', h, 'failed:', type(exc).__name__, exc)
                last_exc = exc
        if ws is None:
            raise last_exc
        print('connected')
        try:
            await asyncio.wait_for(ws.send('ping'), timeout=2)
            print('sent ping')
            res = await asyncio.wait_for(ws.recv(), timeout=5)
            print('recv', res)
        finally:
            await ws.close()
    except Exception:
        print('EXCEPTION:')
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test())
