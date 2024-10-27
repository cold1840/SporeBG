# SporeBG.py
# 完整的程序入口



from SporeBG_Engine.base import GameEG,germs_inclu,count
from SporeBG_Engine.cons import *
from SporeBG_pygame import GameEG_pygame_port as GamePageObj

import pygame



class PageBase:
	def __init__(self):
		pass
	def render(self,sur):
		pass
	def eventer(self,event):
		pass
class MenuPage(PageBase):
	def __init__(self):
		pass
	def render(self,sur):
		sur.fill('#fae3d9')
		sur.blit(pygame.font.SysFont('SimHei', 100).render('SporeBG',True,(255,255,255)),(220,40))
		sur.blit(pygame.font.SysFont('SimHei', 60).render('new game',True,(255,255,255)),(280,240))
	def eventer(self,event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			posi=event.pos
			mx,my=posi
			if 240<my and my<300:
				return GamePage()
				print(1)


class GamePage(PageBase):
	def __init__(self):
		self.g=GamePageObj((7,7),(180,10,420,420),None)
	def render(self,sur):
		self.g.scr=sur
		self.g.draw()
	def eventer(self,event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			posi=event.pos
			mx,my=posi
			self.g.click(posi)
def main():
	pygame.init()
	scr=pygame.display.set_mode((800,600))
	page=MenuPage()
	# g=GamePageObj((7,7),(180,10,420,420),scr)
	# g.player1Unable()
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
			rt = page.eventer(event)
			if rt!=None:
				page=rt
		page.render(scr)
		pygame.display.update()



if __name__=='__main__':
	main()