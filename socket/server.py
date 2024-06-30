import socket
import select
import time

def main():
    # 创建一个TCP/IP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 绑定到指定的地址和端口
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)

    # 监听传入的连接
    server_socket.listen(5)

    # 设置为非阻塞模式
    server_socket.setblocking(False)

    # 用于存储已连接的客户端套接字列表
    client_sockets = []
    client_statues = {}

    while True:
        # 使用select来检查是否有新的连接或数据到达
        read_sockets, _, _ = select.select([server_socket] + client_sockets, [], [],0)

        for sock in read_sockets:
            if sock is server_socket:
                # 新连接到达
                client_socket, client_address = server_socket.accept()
                print('New connection from', client_address)
                client_socket.setblocking(False)  # 也设置为非阻塞
                client_sockets.append(client_socket)
                client_statues[client_socket]='init'
            else:
                # 现有连接有数据到达
                data = sock.recv(1024)
                if data:
                    # 处理接收到的数据
                    print(f'Received data {sock}:', data.decode())
                    print('Statue:', client_statues[sock])
                    # 发送响应给客户端（可选）
                    sock.send(b'Echo: ' + data)
                else:
                    # 如果没有数据，则可能是客户端断开了连接
                    print('Client disconnected', sock.getpeername())
                    client_sockets.remove(sock)
                    del client_statues[sock]
                    sock.close()
        #time.sleep(1)
        #print(time.time)
    # 注意：通常情况下，服务器不会退出这个循环，除非发生错误或手动停止

if __name__=='__main__':
    main()