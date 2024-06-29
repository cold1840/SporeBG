GROW=1
MOVE=2
SPORE=3
def mode_str(mode):
	if mode==GROW:
		return 'GROW'
	elif mode==MOVE:
		return 'MOVE'
	elif mode==SPORE:
		return 'SPORE'
	return
def mode_str_ch(mode):
	if mode==GROW:
		return '生长'
	elif mode==MOVE:
		return '移动'
	elif mode==SPORE:
		return '孢子'
	return