# connect.py
import socket
import json
import select
import time

from SporeBG_Engine.base import GameE

server_ipot=('localhost',12345)
server_maxuser=6
VERSION=1010
class ClientObj():#a class for server to manage client
	def __init__(self,socket):
		self.socket=socket
		self.id=None
		self.name='Unknown'
		self.statue='init'
		self.game=None
	def login(self,iden:str):
		self.id=iden
	def sockName(self):
		return self.socket.getpeername()
	def new_wantGame(self,setting:dict)->None:
		self.statue='wantGame'
		self.wantGame_setting=setting
	def send(self,jdata:dict):
		self.socket.send(json.dumps(jdata).encode())
	def onGame(self,game):#game:GameOnS
		self.statue='onGame'
		self.game = game
	def showObj(self):
		return {'id':self.id,'statue':self.statue,'sockName':self.sockName()}
class ClientObjs(list):
	def __init__(self,*args,**kwrgs):
		list.__init__(self,*args,**kwrgs)
	def sockets(self):
		return [client.socket for client in self]
	def removeBySocket(self,socketObj):
		for i in self:
			if i.socket is socketObj:
				self.remove(i)
	def objBySocket(self,socketObj):
		for i in self:
			if i.socket is socketObj:
				return i
		return ClientObj(socketObj)
	def wantGame(self,setting:dict)->ClientObj:#对用户进行匹配查找
		for i in self:
			if i.statue=='wantGame' and \
			i.wantGame_setting['gameMode']==setting['gameMode']:
				return i
		return None


		
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
	def __init__(self,player1:ClientObj,player2:ClientObj):
		self.p1,self.p2=player1,player2
		player1.onGame(self)#向玩家的客户端对象注册该对局
		player2.onGame(self)
		self.g=GameE((7,7))
	def showObj(self)->dict:
		return {'player_1':self.p1.showObj(),'player_2':self.p2.showObj()}
class GameOnS_s(list):#用来统筹管理所有的Server对局
	def __init__(self,*args,**kwrgs):
		list.__init__(self,*args,**kwrgs)
	def removeByPlayer(self,cobj:ClientObj):
		for i in self:
			if i.p1 is cobj or i.p2 is cobj:
				self.remove(i)
class UsersOnS():# 用于服务端账号管理的类数据库接口
	FILEPATH='userData.ons'
	def __init__(self):
		self.jdata=self.readFile()
	def __str__(self):
		return f'<database obj work on file {self.FILEPATH}>'
	def readFile(self)->dict:
		try:
			with open(self.FILEPATH,'r') as f:
				jmsg = json.loads(f.read())
			return jmsg
		except FileNotFoundError:
			print('不存在数据库文件 创建新数据库')
			return self.newFile()
		print('数据库文件异常')
		return {}
	def newFile(self)->dict:#创建新的数据文件
		jmsg = {'version':VERSION,
		'data':[{'id':'admin','pw':'admin','goal':10},
			{'id':'1001','pw':'password','goal':0}]}
		with open(self.FILEPATH,'w') as f:
			f.write(json.dumps(jmsg))
		return jmsg
	def jobj(self)->dict:#获取数据库中json数据
		return self.jdata
	def newUser(self,iden:str,pw:str)->dict:
		self.jdata['data'].append({'id':iden,'pw':pw,'goal':0})
		return self.jdata
	def login(self,iden:str,pw:str)->bool:
		for i in self.jdata['data']:
			if i['id']==iden and i['pw']==pw:
				return True
		return False


class Server():#用于实现底层的非阻塞服务端框架
	def __init__(self,ipot=server_ipot,maxuser=server_maxuser):#ipot means (ip_address,port)
		self.ipot=ipot
		self.maxuser=maxuser
	def process(self,sock:socket,data:str):
		'''
		Server收到已连接客户端发来的数据时调用 在其中编写服务端更高层次的回应方法
		'''
		#留出的端口 具体实现应该在子类上 所以下面 is a 'helloWorld'
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
					cobj = self.clients.objBySocket(sock)#通过socket获取对应ClientObj对象
					self.process(cobj,data.decode())
				else:
					# 如果没有数据，则可能是客户端断开了连接
					print('Client disconnected', sock.getpeername())
					#self.client_sockets.remove(sock)
					#del self.client_statues[sock]
					self.games.removeByPlayer(self.clients.objBySocket(sock))
					self.clients.removeBySocket(sock)
					sock.close()
	@classmethod
	def verSpportIf(cls,version:int):# 用于服务端判定 是否能够为客户端提供版本支持
		return version==VERSION
class BGServer(Server):# with the SporeBG
	def __init__(self,*args,**kwrgs):
		Server.__init__(self,*args,**kwrgs)
		self.games=[]
	def start(self):#在Server的基础上 添加数据库初始连接 和对局管理
		Server.start(self)
		print('服务端启动，版本号',VERSION)
		self.db = UsersOnS()#database
		print('连接数据库',self.db)
		self.games=GameOnS_s()
	def process(self,cobj:ClientObj,data:str):
		jmsg=json.loads(data)
		mode = jmsg['mode']
		def send(jdata:dict):
			cobj.socket.send(json.dumps(jdata).encode())
		if mode=='versionCheck':
			send(self.versionCheck(jdata=jmsg))
		elif mode=='login':
			send(self.login(cobj=cobj,jdata=jmsg))
		elif mode=='wantGame':
			send(self.wantGame(cobj=cobj,jdata=jmsg))
		elif mode=='onlineUsers':
			send(self.onlineUsers())
		elif mode=='onlineGames':
			send(self.onlineGames())
		else:
			send({'mode':'Err','msg':'不支持的请求模式 请确认服务端支持该版本'})
	def versionCheck(self,jdata:dict) -> dict:
		version=jdata['version']
		msg = {
			'mode':'versionCheck',
			'version':VERSION,
			'verResult':self.verSpportIf(version)}
		return msg
	def login(self,cobj:ClientObj,jdata:dict)->dict:
		iden = jdata['id']
		pw = jdata['pw']
		result = self.db.login(iden,pw)#交给数据库校验账号密码是否正确
		if result:
			cobj.login(iden)#向ClientObj提交已登录信息，将其绑定到账户
			print('用户登录',iden,cobj.sockName())
		return {'mode':'login','loginResult':result}
	def wantGame(self,cobj:ClientObj,jdata:dict)->dict:
		setting = jdata['setting']
		aimCobj = self.clients.wantGame(setting)#查找已正等待匹配的客户端
		if aimCobj:#直接匹配成功
			aimCobj.send({'mode':'wantGame',#通知先等待的玩家
				'setting':setting,
				'wantGameResult':\
				cobj.id if cobj.id else 'Unknown'})#返回对方用户名
			new_game = GameOnS(aimCobj,cobj)#为二人创建在Server上的对局
			self.games.append(new_game)
			return {'mode':'wantGame',
			'setting':setting,
			'wantGameResult':\
			aimCobj.id if aimCobj.id else 'Unknown'}#若未登录则返回默认名Unknown
		cobj.new_wantGame(setting)#注册新的匹配等待 使当前客户端进入匹配等待状态
		return {'mode':'wantGame',
		'setting':setting,
		'wantGameResult':''}
	def onlineUsers(self):
		l = []
		for i in self.clients:
			if i.id:
				l.append(i.showObj())
		return {'mode':'onlineUsers','onlineUsersResult':l}
	def onlineGames(self):
		return {'mode':'onlineGames','onlineGamesResult':[i.showObj() for i in self.games]}





		
		







class Client():
	def __init__(self,ipot=server_ipot):
		self.ipot=ipot
		self.statue='init'
	def act(self,data:str)->str:#阻塞式向服务器发送数据并等待回应
		self.client_socket.send(data.encode())
		return self.waitReact()
	def waitReact(self):#等待服务端回应
		return self.client_socket.recv(1024).decode()
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
		self.id=None
	def actJson(self,j:dict)->dict:# 和self.act相似 但接受并返回字典(通过json)数据
		return json.loads(self.act(json.dumps(j)))
	def waitReactJson(self):
		return json.loads(self.waitReact())
	def start(self,ipot=None):#入口
		Client.start(self,ipot)
		self.versionCheck()
		#self.login(iden='admin',pw='admin')
	def login(self,iden:str,pw:str)->bool:
		print('正在登陆',iden)
		react = self.actJson({'mode':'login','id':iden,'pw':pw})
		result = react['loginResult']
		if result:
			self.id=iden
			print('成功登陆',iden)
		else:
			print('登陆失败')
		return result
	def versionCheck(self)->None:
		sendjson={'mode':'versionCheck', 'version':VERSION}
		#msg = json.dumps(sendjson)
		#react = json.loads(self.act(msg))
		react = self.actJson(sendjson)
		print('服务器版本号',react['version'])
		if react['verResult']:
			print('服务器支持该版本')
	def wantGame(self)->None:#阻塞式等待服务器提供可加入的游戏
		sendjson={'mode':'wantGame','setting':{'gameMode':'amuse','boardSize':[7,7]}}
		print('尝试匹配...')
		react = self.actJson(sendjson)#进入匹配模式
		result = react['wantGameResult']
		if not result:
			print('正在匹配中 请稍候...')
			react = self.waitReactJson()
			result = react['wantGameResult']
		print('匹配成功 对手',result)
		self.game = GameE(react['setting']['boardSize'])
	def onlineUsers(self)->list[dict]:#查询服务器上都有哪些用户已登录
		react = self.actJson({'mode':'onlineUsers'})
		return react['onlineUsersResult']
	def onlineGames(self)->list[dict]:#查询服务器上注册的对局
		react = self.actJson({'mode':'onlineGames'})
		return react['onlineGamesResult']


if __name__=='__main__':
	s=BGServer()
	s.start()
	while True:
		s.run()#调试用 不拦截报错
		'''
		try:#真正运行时使用 拦截报错继续运行并输出
			s.run()
		except Exception as e:
			print(e)
		'''