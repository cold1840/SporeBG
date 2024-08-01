# connect.py
import socket
import select
import time

server_ipot=('localhost',12345)
VERSION=1000
class Server():
	def __init__(self,ipot=server_ipot):
		self.ipot=ipot
	def start(self,ipot=None):
		if ipot==None:
			ipot=self.ipot
		# 创建一个TCP/IP套接字
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# 绑定到指定的地址和端口
		self.server_socket.bind(ipot)

		# 监听传入的连接
		self.server_socket.listen(5)

		# 设置为非阻塞模式
		self.server_socket.setblocking(False)

		# 用于存储已连接的客户端套接字列表
		self.client_sockets = []
		self.client_statues = {}
	def run(self):#非阻塞循环中进程
		# 使用select来检查是否有新的连接或数据到达
		read_sockets, _, _ = select.select([self.server_socket] + self.client_sockets, [], [],0)

		for sock in read_sockets:
			if sock is self.server_socket:
				# 新连接到达
				client_socket, client_address = self.server_socket.accept()
				print('New connection from', client_address)
				client_socket.setblocking(False)  # 也设置为非阻塞
				self.client_sockets.append(client_socket)
				self.client_statues[client_socket]='init'
				# 服务器向客户端发送版本信息
				client_socket.send(str(VERSION).encode())
			else:
				# 现有连接有数据到达
				data = sock.recv(1024)
				if data:
					# 处理接收到的数据
					print(f'Received data {sock}:', data.decode())
					print('Statue:', self.client_statues[sock])
					# 发送响应给客户端（可选）
					sock.send(b'Echo: ' + data)
				else:
					# 如果没有数据，则可能是客户端断开了连接
					print('Client disconnected', sock.getpeername())
					self.client_sockets.remove(sock)
					del self.client_statues[sock]
					sock.close()
			print(self.client_statues)


class Client():
	def __init__(self,ipot=server_ipot):
		self.ipot=ipot
	def start(self,ipot=None):
		if ipot==None:
			ipot=self.ipot
		# 创建一个TCP/IP套接字
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# 连接到服务器
		self.client_socket.connect(ipot)
		# 接听服务器版本信息
		data = self.client_socket.recv(1024)
		print('服务端版本:',data.decode())
		print('客户端版本:',VERSION)
		if int(data.decode())>VERSION:
			print('Please update your client programe.')
	def run(self):#非阻塞循环中进程
		od=input('>>> ')
		print('Sending:', od)
		self.client_socket.send(od.encode())
		data = self.client_socket.recv(1024)
		print('Received:', data.decode())
if __name__=='__main__':
	s=Server()
	s.start()
	while True:
		s.run()