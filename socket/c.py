import socket

# 创建一个TCP/IP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 设置服务器地址和端口
server_address = ('localhost', 12345)

# 连接到服务器
client_socket.connect(server_address)
while True:
    od=input('>>> ')
    if od=='q':
        break
    print('Sending:', od)
    client_socket.send(od.encode())
    data = client_socket.recv(1024)
    print('Received:', data.decode())


'''
try:
    # 发送数据到服务器
    message = 'Hello, Server!'
    print('Sending:', message)

    # 接收服务器的响应
    data = client_socket.recv(1024)
    print('Received:', data.decode())
finally:
    # 关闭连接
    print('Closing socket')
    client_socket.close()
'''