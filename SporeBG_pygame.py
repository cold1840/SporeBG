from SporeBG_Engine.base import GameEG,germs_inclu,count
from SporeBG_Engine.cons import *
import pygame


COLOR_BG='#eaeaea'
COLOR_BGBG='#ffc7c7'
COLOR_PLAYER1='#e3fdfd'
COLOR_PLAYER2='#f38181'#40514e'
class colorPack_1_pink():# colorPackage
	BG='#fae3d9'
	BGBG='#ffc7c7'
	PLAYER1='#ffffff'
	PLAYER2='#f38181'
	ALLOW='#ffc7c7'
	FROM_1='#ffa8b8'
	FROM_2='#c06c84'
class colorPack_2_green():# colorPackage
	BG='#9df3c4'
	BGBG='#62d2a2'
	PLAYER1='#d7fbe8'
	PLAYER2='#1fab89'
	ALLOW='#ffffc2'
	FROM_1='#6ef3d6'
	FROM_2='#10ddc2'

def rectIf(posi,rect):
	x,y=posi
	rx,ry,rw,rh=rect
	return x>=rx and y>=ry and x-rx<=rw and y-ry<=rh

class GameEG_pygame(GameEG):
	def __init__(self,GShape,ScrRect,scr):
		GameEG.__init__(self,GShape,ScrRect)
		self.scr=scr
		self.sur=pygame.Surface((self.SW,self.SH))
		self.colorPackLoad(colorPack_1_pink())
		self.step_from=self.germs_left[0][0]
		self.step_mode=GROW
	def colorPackLoad(self,colorPack):
		self.CP=colorPack
	def drawblock(self,pos,color):
		bx,by=self.blockposi_LT(pos)
		pygame.draw.rect(self.sur,color,[bx,by,self.BW,self.BH])
	def drawallow(self,pos):
		bx,by=self.blockposi_LT(pos)
		pygame.draw.rect(self.sur,self.CP.ALLOW,[bx+self.BW/4,by+self.BH/4,self.BW/2,self.BH/2])
	def draw(self):
		self.sur.fill(self.CP.BG)
		for dy in range(self.H):
			for dx in range(self.W):
				dn=self.fieldget((dx,dy))
				dp=(dx,dy)
				if dn==1:
					if dp==self.step_from:
						self.drawblock(dp,self.CP.FROM_1)
					else:
						self.drawblock(dp,self.CP.PLAYER1)
				if dn==2:
					if dp==self.step_from:
						self.drawblock(dp,self.CP.FROM_2)
					else:
						self.drawblock(dp,self.CP.PLAYER2)
		if self.step_from!=None:
			for i in self.allow_pick(self.step_mode,self.step_from):
				self.drawallow(i)
		self.scr.blit(self.sur,(self.SX,self.SY))
	def click_i(self,posi):
		mx,my=posi
		p=self.blockpos(posi)
		if self.step_from==p:
			if self.step_mode==GROW:
				self.step_mode=MOVE
			elif self.step_mode==MOVE:
				self.step_mode=SPORE
			elif self.step_mode==SPORE:
				self.step_mode=GROW
		if germs_inclu(p,self.germs_left):
			self.step_from=p
		elif p in self.allow_pick(self.step_mode,self.step_from):
			self.go(self.step_mode,self.step_from,p)
			if len(self.germs_left)>0:
				self.step_from=self.germs_left[0][0]
		else:
			self.step_from=self.germs_left[0][0]
			self.step_mode=GROW
	def click(self,posi):
		if not rectIf(posi,self.ScrRect()):
			return
		mx=posi[0]-self.SX
		my=posi[1]-self.SY
		self.click_i((mx,my))


class GameEG_pygame_port(GameEG_pygame):# 外接端口
	def __init__(self,GShape,ScrRect,scr):
		GameEG_pygame.__init__(self,GShape,ScrRect,scr)
		self.player1_able=True
		self.player2_able=True
	def player1Enable(self):
		self.player1_able=True
	def player1Unable(self):
		self.player1_able=False
	def player2Enable(self):
		self.player2_able=True
	def player2Unable(self):
		self.player2_able=False
	def playerAbleIf(self,player=None):
		if player==None:
			player=self.player_now
		if player==1:
			return self.player1_able
		elif player==2:
			return self.player2_able
		return False
	def render(self):# 内部渲染并返回画面(pygame.Surface)
		self.sur.fill(self.CP.BG)
		for dy in range(self.H):
			for dx in range(self.W):
				dn=self.fieldget((dx,dy))
				dp=(dx,dy)
				if dn==1:
					if dp==self.step_from and self.playerAbleIf(1):
						self.drawblock(dp,self.CP.FROM_1)
					else:
						self.drawblock(dp,self.CP.PLAYER1)
				if dn==2:
					if dp==self.step_from and self.playerAbleIf(2):
						self.drawblock(dp,self.CP.FROM_2)
					else:
						self.drawblock(dp,self.CP.PLAYER2)
		if self.step_from!=None:
			for i in self.allow_pick(self.step_mode,self.step_from):
				if self.playerAbleIf():
					self.drawallow(i)
		return self.sur
	def draw(self,sur=None):
		if sur==None:
			sur=self.render()
		self.scr.blit(sur,(self.SX,self.SY))

	def click(self,posi):# 重写click以实现禁用玩家操作
		if not rectIf(posi,self.ScrRect()) or not self.playerAbleIf():
			return
		mx=posi[0]-self.SX
		my=posi[1]-self.SY
		self.click_i((mx,my))


def main():
	pygame.init()
	scr=pygame.display.set_mode((800,600))
	g=GameEG_pygame((7,7),(180,10,420,420),scr)
	#g.colorPackLoad(colorPack_2_green())
	clock = pygame.time.Clock()
	t=''
	done=False
	while not done:
		clock.tick(60)
		# 处理事件
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
			elif event.type == pygame.MOUSEBUTTONDOWN:
				fresh=True
				posi=event.pos
				mx,my=posi
				g.click(posi)
			elif event.type == pygame.MOUSEMOTION:
				t=str(event.pos)
		scr.fill(g.CP.BGBG)
		g.draw()
		tr=pygame.font.SysFont('SimHei', 100).render(mode_str_ch(g.step_mode),True,(255,255,255))
		scr.blit(tr,(200,430))
		scr.blit(pygame.font.SysFont('SimHei', 36).render(f'{len(g.germs_u)} 菌落',True,(255,255,255)),(10,20))
		scr.blit(pygame.font.SysFont('SimHei', 36).render(f'{count(g.germs_u)} 单位',True,(255,255,255)),(10,60))
		scr.blit(pygame.font.SysFont('SimHei', 36).render(f'{len(g.germs_e)} 菌落',True,(255,255,255)),(630,330))
		scr.blit(pygame.font.SysFont('SimHei', 36).render(f'{count(g.germs_e)} 单位',True,(255,255,255)),(630,370))
		scr.blit(pygame.font.SysFont('SimHei', 36).render(f'{g.player_now}',True,(255,255,255)),(630,570))
		scr.blit(pygame.font.SysFont('SimHei', 36).render(t,True,(255,255,255)),(10,160))
		pygame.display.update()

if __name__=='__main__':
	main()