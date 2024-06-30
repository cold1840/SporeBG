from typing import Tuple
import json # for saving games

GROW=1
MOVE=2
SPORE=3


def around(pos):
	x,y=pos
	return [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
def germs_inclu(pos,germs):#检索pos是否在germs中存在
	o=0
	for i in germs:
		if pos in i:
			return (o,i.index(pos))
		o+=1
	return None

def count(germs):
	c=0
	for i in germs:
		c+=len(i)
	return c

def new_field(W,H):
	field=[]
	for i in range(H):
		field.append([])
		for ii in range(W):
			field[i].append(0)
	field[0][0]=1
	field[0][2]=1
	field[-1][-1]=2
	field[-2][-2]=2
	return field

class GameE():#GameEngine 负责游戏规则和存档处理
	def __init__(self,GShape:Tuple[int,int]):
		self.W,self.H=GShape
		self.field=new_field(self.W,self.H)
		self.germs_e=[]
		self.germs_u=[]
		self.player_now=1
		self.germs_left=[]
		self.history={'InitField':self.field,'InitGShape':GShape,\
			'InitPlayer':1,\
			'AllSteps':[]}
		self.step_step=[]
		self.roll()
	def fieldset(self,pos,aim):
		x,y=pos
		self.field[y][x]=aim
	def fieldget(self,pos):
		x,y=pos
		if y<0 or y>=len(self.field):
			return None
		l=self.field[y]
		if x<0 or x>=len(l):
			return None
		return l[x]
	def germs_pick(self):
		self.germs_e,self.germs_u=[],[]
		for fy in range(self.H):
			for fx in range(self.W):
				fn=self.fieldget((fx,fy))
				pos=(fx,fy)
				if fn==1:
					germs=self.germs_u
				elif fn==2:
					germs=self.germs_e
				else:
					continue
				germ_a=None
				for i in around(pos):
					g=germs_inclu(i, germs)
					#print(g)
					if g:
						germs[g[0]].append(pos)
						if germ_a and germ_a[0]!=g[0]:
							ggg=germs[germ_a[0]].copy()
							germs[g[0]]+=ggg
							del(germs[germ_a[0]])
						germ_a=g
						#break
				if not germ_a:
					germs.append([pos])
	def germs_now(self):
		if self.player_now==1:
			return self.germs_u
		return self.germs_e
	def roll(self):
		if self.step_step!=[]:
			self.history['AllSteps'].append(self.step_step)
		self.step_step=[]
		print(self.history)
		self.germs_pick()
		self.player_now=2 if self.player_now==1 else 1
		self.germs_left=self.germs_now().copy()
		#self.save_as_file('save.json')
	def show(self):
		for i in self.field:
			print(i)
	def check(self,mode,f_pos,t_pos):
		if mode!=GROW and mode!=MOVE and mode!=SPORE:
			return False,100 #操作模式无效
		if self.fieldget(f_pos)==None:
			return False,101 #操作棋子无效
		if self.fieldget(t_pos)==None:
			return False,102 #落子位置无效
		if self.fieldget(f_pos)!=self.player_now:
			return False,300 #操作的棋子不属于当前执子者
		if germs_inclu(f_pos,self.germs_left)==None:
			return False,301 #操作的棋子已无行动力
		if t_pos not in self.allow_pick(mode,f_pos):
			return False,302 #落子不符合游戏规则
		return True,200
	def go(self,mode,f_pos,t_pos):
		check=self.check(mode,f_pos,t_pos)
		if check[0]:
			if mode==MOVE or mode==SPORE:
				self.fieldset(f_pos,0)
			self.fieldset(t_pos,self.player_now)
			del self.germs_left[germs_inclu(f_pos,self.germs_left)[0]]
			self.step_step.append([mode,f_pos,t_pos])
			if len(self.germs_left)==0:
				self.roll()
		return check
	def go_step(self,step):
		mode,f_pos,t_pos=step
		return self.go(mode,f_pos,t_pos)
	def go_steps(self,steps):
		field_copy=self.field # 备份棋盘
		o=0
		for step in steps:
			check = self.go_step(step)
			if not check[0]:
				self.field=field_copy # 还原棋盘
				return False,o,check
			o+=1
		return True,o,200
	def allow_pick_base(self,germ,aim=0):
		allow=[]
		g=germ.copy()
		for i in g:
			for ii in around(i):
				if self.fieldget(ii)==aim and ii not in allow:
					allow.append(ii)
		return allow
	def allow_pick_grow(self,f_pos):
		germs=self.germs_now()
		i=germs_inclu(f_pos,germs)
		if i==None:
			return []
		return self.allow_pick_base(germs[i[0]])
	def allow_pick_move(self,f_pos):
		germs=self.germs_now()
		i=germs_inclu(f_pos,germs)
		if i==None:
			return []
		return self.allow_pick_base(germs[i[0]])+\
			self.allow_pick_base(germs[i[0]],1 if self.player_now==2 else 2)
	def allow_pick_spore(self,f_pos):
		a1=self.allow_pick_base([f_pos])
		return a1+self.allow_pick_base(a1)
	def allow_pick(self,mode,f_pos):
		if self.fieldget(f_pos)==self.player_now:
			if mode==GROW:
				return self.allow_pick_grow(f_pos)
			elif mode==MOVE:
				return self.allow_pick_move(f_pos)
			elif mode==SPORE:
				return self.allow_pick_spore(f_pos)
		return []
	def save_as_file(self,filename):#将存档写入json文件
		try:
			with open(filename,'w') as f:
				json.dump(self.history,f)
			return True,200
		except BaseException as e:
			return False,e
	def load_fr_history(self,history):#从合法的history字典中加载游戏
		self.W,self.H=history['InitGShape']
		self.field=history['InitField']
		self.player_now=history['InitPlayer']
		self.history=history
		self.step_step=[]
		self.roll()
		for i in history['AllSteps']:
			go_steps(i)
	def load_fr_file(self,filename):#从json文件中加载存档
		try:
			with open(filename,'r') as f:
				history=json.loads(f.read())
			return self.load_fr_history(history)
		except BaseException as e:
			return False,e
class GameEG(GameE):#GameEngineGraph 扩展原始的图形计算工具
	def __init__(self,GShape:Tuple[int,int],ScrRect:Tuple[int,int,int,int]):
		GameE.__init__(self,GShape)
		self.set_scrRect(ScrRect)
	def blockpos(self,posi):#由图形坐标得到网格坐标
		x,y=posi
		return (int(x/self.SW*self.W),int(y/self.SH*self.H))
	def blockposi_LT(self,pos):
		x,y=pos
		return (int(self.SW/self.W*x),int(self.SH/self.H*y))
	def set_scrRect(self,ScrRect):
		self.SX,self.SY,self.SW,self.SH=ScrRect
		self.BW=int(self.SW/self.W)
		self.BH=int(self.SH/self.H)
	def ScrRect(self):
		return (self.SX,self.SY,self.SW,self.SW)

def main():
	g=GameE((7,7))
	g.show()
	print('player_now',g.player_now)
	print('germs_left',g.germs_left)
	print('check',g.check(GROW,(6,6),(5,6)))
	g.go_steps([[1, (6, 6), (5, 6)], [1, (5, 5), (6, 5)]])
	g.show()
	g.go(GROW,(0,0),(0,1))
	g.show()
	print('germs_left',g.germs_left)
	g.go(GROW,(2,0),(2,1))
	g.go(SPORE,(5,6),(3,6))
	g.show()
	g.save_as_file('save.json')
	print('player_now',g.player_now)



if __name__=='__main__':
	g=GameE((7,7))
	print(g.load_fr_file('save.json'))
	g.show()
	#main()