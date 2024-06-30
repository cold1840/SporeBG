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
		tr=pygame.font.SysFont('arial', 100).render(mode_str(g.step_mode),True,(255,255,255))
		scr.blit(tr,(200,430))
		scr.blit(pygame.font.SysFont('arial', 36).render(f'{len(g.germs_u)} g',True,(255,255,255)),(10,20))
		scr.blit(pygame.font.SysFont('arial', 36).render(f'{count(g.germs_u)} b',True,(255,255,255)),(10,60))
		scr.blit(pygame.font.SysFont('arial', 36).render(f'{len(g.germs_e)} g',True,(255,255,255)),(630,330))
		scr.blit(pygame.font.SysFont('arial', 36).render(f'{count(g.germs_e)} b',True,(255,255,255)),(630,370))
		scr.blit(pygame.font.SysFont('arial', 36).render(t,True,(255,255,255)),(10,160))
		pygame.display.update()

if __name__=='__main__':
	main()