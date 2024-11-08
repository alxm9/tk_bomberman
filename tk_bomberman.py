from tkinter import *
import random
import threading
import time

tile_dict = {}
creature_dict = {}
item_dict = {}

class App():
	def __init__(self):
		self.interface = Tk()
		self.interface.geometry("600x600")
		self.canvas = Canvas(self.interface, bg = "#eeac68", width = 600, height = 600)
		self.canvas.pack()
		self.worker = threading.Thread(target=self.gameloop)
		self.worker.start()
		self.interface.mainloop()
		
	def gameloop(self):
		while True:
			time.sleep(1)
			print("test")

class Creature():
	def __init__(self):
		self.passable = True
		self.destroyable = True 

class Bomb():
	def __init__(self):
		pass

class Item():
	def __init__(self):
		self.passable = True
		self.destroyable = True

class Tile(): # Cannot pass through tiles
	def __init__(self, position, destroyable):
		self.position = position # (row, column)
		self.passable = False
		self.destroyable = destroyable

	def destroy(self): # If destroyable tile, gets destroyed when touched by explosion.
		pass
		# Play destruction animation
		# Canvas delete
		# Random chance to place item at self.position
		# Delete self

	def assign_item(self):
		pass
		# Random chance to assign an item upon

app = App()
