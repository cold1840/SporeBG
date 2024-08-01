# client.py
from connect import *


if __name__=='__main__':
	c=Client()
	c.start()
	while True:
		c.run()