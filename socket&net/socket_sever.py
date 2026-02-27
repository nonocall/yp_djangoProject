# coding:utf-8

import socket

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'

body = '''Hello,world! <h1> from yp Gjango 实战</h1>'''
response_params = [
    'HTTP/1.0 200 OK',
    'Date: Fri, 01 Jan 2000 00:00:00 GMT',
    'Content-Type: text/plain; charset=utf-8',
    'Content-Length: {}\r\n'.format(len(body.encode())),
    body,
]
response = '\r\n'.join(response_params)

def handle_connection(connection,address):
    print('oh new conn', connection,address)
    import time
    time.sleep(100)
    request = b""
    while EOL1 not in request and EOL2 not in request:
        request += connection.recv(1024)
    print(request)
    connection.send(response.encode())  # 转化为bytes后输出
    connection.close()

def main():
    # socket.AF_INET 用于服务器与服务器之间的网络通信
    # socket.SOCK_STREAM 用于基于TCP的流式 socket 通信
    serversoctet = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 设置端口可复用，保证我们每次按ctrl+c 组合键之后，快速启动
    serversoctet.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversoctet.bind(('127.0.0.1',8000))
    serversoctet.listen(5)
    # 设置backlog--socket 连接最大排队数量

    print('http://127.0.0.1:8000')

    try:
        while True:
            connection, address = serversoctet.accept()
            handle_connection(connection, address)
    finally:
        serversoctet.close()

if __name__ == '__main__':
    main()