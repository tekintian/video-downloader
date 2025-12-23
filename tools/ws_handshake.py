import socket, base64
s = socket.create_connection(('127.0.0.1', 8000), timeout=3)
key = base64.b64encode(b'testkey123').decode()
req = (
    'GET /ws HTTP/1.1\r\n'
    'Host: 127.0.0.1:8000\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    f'Sec-WebSocket-Key: {key}\r\n'
    'Sec-WebSocket-Version: 13\r\n'
    '\r\n'
)
print('sending...')
s.send(req.encode())
res = s.recv(4096)
print('response:')
print(res.decode(errors='ignore'))
s.close()
