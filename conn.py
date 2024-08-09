#提供网络服务
from connect import *

c=BGClient()
c.start()
iden = input('账号 ')
pw = input('密码 ')
c.login(iden,pw)
done = True
while done:
	cmd=input()
	print(eval('c.'+cmd))