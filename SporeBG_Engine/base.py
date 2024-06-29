from typing import Tuple

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
		self.germs_pick()
		self.player_now=2 if self.player_now==1 else 1
		self.germs_left=self.germs_now().copy()
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
			if len(self.germs_left)==0:
				self.roll()
		return check
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
	g.go(GROW,(6,6),(5,6))
	g.show()
	print('germs_left',g.germs_left)



if __name__=='__main__':
	main()