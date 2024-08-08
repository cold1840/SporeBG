# connect.py
import socket
import json
import select
import time

server_ipot=('localhost',12345)
server_maxuser=6
VERSION=1010
class ClientObj():#a class for server to manage client
	def __init__(self,socket):
		self.socket=socket
		self.id=None
		self.name='Unknown'
		self.statue='init'
	def fileno(self,*args,**kwrgs):
		return self.socket.fileno()
class ClientObjs(list):
	def __init__(self,*args,**kwrgs):
		list.__init__(self,*args,**kwrgs)
	def sockets(self):
		return [client.socket for client in self]
	def removeBySocket(self,socketObj):
		for i in self:
			if i.socket is socketObj:
				self.remove(i)


		
'''
the statue of ClientObj:
init		waiting for client to send its version data
-initA		after check version, client is ready for build a connect of SporeBG
-initB		it's sorry that the server can't provide anything cause' the version
			if client get this statue, the server will still hold the socket 
			connection but only response Err message back until the client close 
			the socket itself
initReady	the SporeBG perparetion is done and it's ready for anything
holdGame	client is holding its game and wait anyone else to join
findGame	client is trying to find game, the server will return game list
waitGame	client is glad to join any game avaliable, give it
'''
class GameOnS():# game on server, 
	def __init__(self,player1,player2):
		self.p1,self.p2=player1,player2

class Server():
	def __init__(self,ipot=server_ipot,maxuser=server_maxuser):#ipot means (ip_address,port)
		self.ipot=ipot
		self.maxuser=maxuser
	def process(self,sock:socket,data:str):#a 'helloWorld'
		# 处理接收到的数据
		print(f'Received data {sock}:', data)
		print('Statue:', self.client_statues[sock])
		# 发送响应给客户端（可选）
		sock.send(b'Echo: ' + data.encode)
	def start(self,ipot=None):
		if ipot==None:
			ipot=self.ipot
		# 创建一个TCP/IP套接字 to create a TCP/IP socket
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# 绑定到指定的地址和端口 bind to a chosen address and port
		self.server_socket.bind(ipot)

		# 监听传入的连接
		self.server_socket.listen(self.maxuser)

		# 设置为非阻塞模式
		self.server_socket.setblocking(False)

		# 用于存储已连接的客户端对象的列表
		self.clients = ClientObjs()
		self.client_sockets = []
		#self.client_statues = {}
	def run(self):#非阻塞循环中进程
		# 使用select来检查是否有新的连接或数据到达
		read_sockets, _, _ = select.select([self.server_socket] + self.clients.sockets(), [], [],0)

		for sock in read_sockets:
			if sock is self.server_socket:
				# 新连接到达
				client_socket, client_address = self.server_socket.accept()
				print('New connection from', client_address)
				client_socket.setblocking(False)  # 也设置为非阻塞
				self.clients.append(ClientObj(client_socket))
				# 服务器向客户端发送版本信息
				#client_socket.send(str(VERSION).encode())
			else:
				# 现有连接有数据到达
				data = sock.recv(1024)
				if data:
					self.process(sock,data.decode())
				else:
					# 如果没有数据，则可能是客户端断开了连接
					print('Client disconnected', sock.getpeername())
					#self.client_sockets.remove(sock)
					#del self.client_statues[sock]
					self.clients.removeBySocket(sock)
					sock.close()
	@classmethod
	def verSpportIf(cls,version):# version is int
		return version==VERSION
class BGServer(Server):# with the SporeBG
	def __init__(self,*args,**kwrgs):
		Server.__init__(self,*args,**kwrgs)
		self.games=[]
	def process(self,sock:socket,data:str):
		sock.send(self.versionCheck(data).encode())
		
	def versionCheck(self,data:str) -> str:
		version=json.loads(data)['version']
		msg = json.dumps({
			'mode':'versionCheck',
			'version':VERSION,
			'verResult':self.verSpportIf(version)})
		return msg

class Client():
	def __init__(self,ipot=server_ipot):
		self.ipot=ipot
		self.statue='init'
	def act(self,data:str):#阻塞式向服务器发送数据并等待回应
		self.client_socket.send(data.encode())
		return self.client_socket.recv(1024)
	def start(self,ipot=None):
		if ipot==None:
			ipot=self.ipot
		print('客户端启动，版本号',VERSION)
		# 创建一个TCP/IP套接字
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# 连接到服务器
		self.client_socket.connect(ipot)
class BGClient(Client):
	def __init__(self,*args,**kwrgs):
		Client.__init__(self,*args,**kwrgs)
	def go(self,ipot=None):#入口
		self.start(ipot)
		self.versionCheck()
	def actJson(self,j:dict)->dict:
		return json.loads(self.act(json.dumps(j)).decode())
	def versionCheck(self):
		sendjson={'mode':'versionCheck', 'version':VERSION}
		#msg = json.dumps(sendjson)
		#react = json.loads(self.act(msg).decode())
		react = self.actJson(sendjson)
		print('服务器版本号',react['version'])
		if react['verResult']:
			print('服务器支持该版本')

if __name__=='__main__':
	s=BGServer()
	s.start()
	while True:
		s.run()