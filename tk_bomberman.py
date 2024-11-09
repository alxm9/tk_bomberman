from tkinter import *
import random
import threading
import time
import os

map_pattern = [ # 0-Nothing, 1-Indestructible, 2-Destructible
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
	[1,0,0,2,2,2,2,2,2,2,0,0,0,0,1],
	[1,0,1,0,1,2,1,2,1,0,1,0,1,0,1],
	[1,2,2,2,2,2,2,2,0,0,0,0,0,0,1],
	[1,2,1,0,1,0,1,2,1,0,1,0,1,0,1],
	[1,2,0,0,2,2,2,2,2,2,2,2,2,0,1],
	[1,0,1,0,1,2,1,2,1,0,1,0,1,0,1],
	[1,0,2,0,2,2,2,2,2,0,0,0,2,0,1],
	[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
	[1,0,0,2,0,2,2,2,2,2,2,0,2,0,1],
	[1,0,1,0,1,0,1,2,1,0,1,0,1,0,1],
	[1,0,0,0,0,0,2,2,2,0,0,0,0,0,1],
	[1,0,1,0,1,0,1,2,1,0,1,0,1,0,1],
	[1,0,0,2,2,0,2,2,2,2,0,0,0,0,1],
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
tile_dict = {}
item_dict = {}

class App():
	graphics = {} # Don't'. Find another way
	interface = Tk()
	interface.geometry("600x600")
	canvas = Canvas(interface, bg = "green", width = 600, height = 600)
	canvas.pack()
	
	def __init__(self):
		self.populate_tiles()
		self.populate_creatures()
		self.interface.bind("<Key>", lambda event: self.bindings(event))
		self.worker = threading.Thread(target=self.gameloop)
		self.worker.start()
		self.interface.mainloop()
		
	def gameloop(self):
		while True:
			time.sleep(1)
			print("test")

	def populate_tiles(self): # Draws map based on map_pattern
		color_list = ["grey","#3d4a38"]
		
		for row in range(15): # Adds some variety to the floor
			for column in range(15):
				if (column%2) == 1 and (row%2)==1:
					self.canvas.create_rectangle(0+(40*row),0+(40*column),40+(40*row),40+(40*column), fill="#439229", width=0)
		
		for row_index, row in enumerate(map_pattern): # Adds tiles
			for column_index, column in enumerate(row):
				if row[column_index] == 0:
					continue
				location = f"{row_index+1}_{column_index+1}"
				x0,y0,x1,y1 = 0+(40*row_index),0+(40*column_index),40+(40*row_index),40+(40*column_index)
				color = color_list[row[column_index]%2]
				self.graphics[(row_index,column_index)] = self.canvas.create_rectangle(x0,y0,x1,y1, fill=color, width=2)
				tile = Tile((row_index,column_index),True if color==color_list[0] else False,self.graphics[(row_index,column_index)])
		
	def bindings(self,event):
		player = Creature.creatures["player"]
		binds = {
		"x" : self.debug_destroy_random,
		"Down" : lambda: player.move("Down"),
		"Up" : lambda: player.move("Up"),
		"Left" : lambda: player.move("Left"),
		"Right" : lambda: player.move("Right")
		}
		# print(event)
		if event.keysym in binds:
			binds[event.keysym]()
			

	def populate_creatures(self):
		entity = Creature((1,1),"player")
		for entity in Creature.creatures:
			self.canvas.create_image(60,40,image=Creature.creatures[entity].shape)

	def debug_destroy_random(self):
		key = random.choice(list(tile_dict))
		if tile_dict[key].destructible == True:
			self.canvas.delete(tile_dict[key].shape)
			del tile_dict[key]
			
class Creature():
	creatures = {}
	
	def __init__(self,location, kind):
		self.location = location
		self.kind = "player"
		self.speed = 2
		self.passable = True # When running passable check, enemy AI can walk towards you
		self.destructible = True
		self.moving = False # can't move if you're already moving
		self.shape_giver()
		self.creatures[self.kind] = self

	def shape_giver(self):
		match self.kind:
			case "player":
				self.shape = PhotoImage(file="sprites/stand.png")

	def passable_check(self,direction):
		dx_dy = {"Down":(0,1), "Up":(0,-1),"Left":(-1,0),"Right":(1,0)}[direction]
		proposed_loc = (self.location[0]+dx_dy[0],self.location[1]+dx_dy[1])
		return Tile.find_by_location(proposed_loc)
				
	def move(self, direction):
		if self.passable_check(direction) == True:
			return # Space occupied
		for step in range(40):
			pass
			

	@classmethod
	def find_by_location(self, location):
		return location in self.creatures

class Bomb():
	def __init__(self):
		pass

class Item():
	def __init__(self):
		self.passable = True
		self.destructible = True

class Tile(): # Cannot pass through tiles
	tiles = {}
	
	def __init__(self, location, destructible, shape):
		self.location = location
		self.destructible = destructible
		self.shape = shape
		self.tiles[location] = self

	def destroy(self): # If destructible tile, gets destroyed when touched by explosion
		pass
		# Play destruction animation
		# Canvas delete
		# Random chance to place item at self.position
		# Delete self

	def assign_item(self):
		pass
		# Random chance to assign an item upon

	@classmethod
	def find_by_location(self, location):
		return location in self.tiles

app = App()
