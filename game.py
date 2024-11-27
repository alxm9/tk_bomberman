from tkinter import *
import threading
import random
import time
import os
import platform

from PIL import Image, ImageTk

if platform.system() == "Linux": # Linux handles key presses and releases differently
	os.system("xset r off")

map_pattern = [ # 0-Nothing, 1-Indestructible, 2-Destructible
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
	[1,0,0,0,2,2,2,2,2,2,0,0,0,0,1],
	[1,0,1,0,1,2,1,2,1,0,1,0,1,0,1],
	[1,2,2,0,2,2,2,2,0,0,0,0,0,0,1],
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

keys_held = {
    1: "",
    2: "",
    3: "",
    4: ""
}

class App():
	# graphics = {} # Don't'. Find another way
	interface = Tk()
	width = 600
	height = 600
	interface.geometry("600x600")
	canvas = Canvas(interface, bg = "green", width = 600, height = 600)
	canvas.pack()
	tile_sqpixels = 40
	
	def __init__(self):
		self.window = True
		self.populate_tiles()
		self.populate_creatures()
		# self.interface.bind("<Key>", lambda event: self.bindings(event))
		# self.interface.bind("<x>", lambda _: print(self.keys_pressed))
		self.interface.bind("<KeyPress>", lambda event: self.start_holding(event))
		self.interface.bind("<KeyRelease>", lambda event: self.stop_holding(event))
		self.interface.bind("<Destroy>", lambda event: self.closegame())
		self.interface.bind("<Escape>", lambda event: self.interface.destroy())
		self.player = Creature.creatures["bomberman"]
		self.keys_pressed = [] # keys currently being pressed
		self.worker = threading.Thread(target=self.gameloop)
		self.worker.start()
		self.interface.mainloop()
	
	def gameloop(self):
		self.lock = threading.Lock()
		while self.window:
			self.lock.acquire()
			time.sleep(0.1)
			print(keys_held)
			if keys_held[1] != "":
				self.bindings(keys_held[1])
			# if len(self.keys_pressed) > 0:
			# 	self.bindings(self.keys_pressed[0])
			# if len(self.keys_pressed) == 0:
			# 	pass # restore standing sprite
			# for key, creature in Creature.creatures.items():
			# 	creature.move()
			# print("tick")
			self.lock.release()

	# def start_holding(self,event):
	# 	self.player.keyheld = True
	# 	self.keys_pressed.append(str(event.keysym)) if event.keysym not in self.keys_pressed else None
	def start_holding(self, event):
		# self.player.keyheld = True
		for key in keys_held:
			if keys_held[key] == "":
				keys_held[key] = event.keysym
				return

	# def stop_holding(self,event):
	# 	self.player.keyheld = False
	# 	self.keys_pressed.remove(str(event.keysym)) if event.keysym in self.keys_pressed else None
	def stop_holding(self, event):
		# self.player.keyheld = False
		for key in keys_held:
			if keys_held[key] == event.keysym:
				keys_held[key] = ""
		for key in range(4,1,-1):
			if keys_held[key] == "":
				continue
			if keys_held[key] != "":
				if keys_held[key-1] == "":
					keys_held[key-1] = keys_held[key]
					keys_held[key] = ""
					self.stop_holding(event)
		
	def closegame(self):
		self.window = False

	def populate_tiles(self): # Draws map based on map_pattern
		wall_list = ["wall","strongwall"]
		
		for row in range(15): # Adds some variety to the floor
			for column in range(15):
				if (column%2) == 1 and (row%2)==1:
					self.canvas.create_rectangle((40*row),(40*column),40+(40*row),40+(40*column), fill="#439229", width=0)
		
		for row_index, row in enumerate(map_pattern): # Adds tiles
			for column_index, column in enumerate(row):
				if row[column_index] == 0:
					continue
				wall = wall_list[row[column_index]%2]
				destructible = True if column_index == 1 else False
				tile = Tile((row_index,column_index),destructible,wall)

	def bindings(self,key):
		movements = ["Down", "Up", "Left", "Right"]
		if key in movements:
			self.player.move(key)

	def populate_creatures(self):
		entity = Creature((1,1),"player")

	def debug_destroy_random(self):
		key = random.choice(list(tile_dict))
		if tile_dict[key].destructible == True:
			self.canvas.delete(tile_dict[key].shape)
			print("deleted")
			del tile_dict[key]
			
class Creature():
	creatures = {}
	
	def __init__(self,location, kind):
		self.possible_frames = ["stand", "walk_1", "walk_2", "walk_3"] # Used to import the frames
		self.frame_dict = {} # "stand":photoimage location
		self.current_frame = False
		# self.facing = "Left" # Direction currently facing. For frame flip check.
		self.location = location
		self.dx_dy = {0,0}
		self.kind = "bomberman"
		self.speed = 10 # Lower = faster
		self.passable = True # When running passable check, enemy AI can walk towards you
		self.destructible = True
		self.moving = False # can't move if you're already moving
		# self.keyheld = False
		self.trajectory = False
		self.move_queue = []
		self.shape_assign()
		self.creatures[self.kind] = self

	def frameflip(self, direction):
		if direction == "Right":
			return
		for frame in self.possible_frames:
			img = ImageTk.getimage(self.frame_dict[frame])
			img = img.transpose(Image.FLIP_LEFT_RIGHT)
			img = ImageTk.PhotoImage(img)
			self.frame_dict[frame] = img
		
	def shape_assign(self):
		self.frame_dict = {} # photoimage, shape_
		for frame in self.possible_frames:
			img = Image.open(f"sprites//{self.kind}//{frame}.png") #PIL transposeable image
			frame_img = ImageTk.PhotoImage(img)
			self.frame_dict[frame] = frame_img
		self.current_frame = App.canvas.create_image(60,40,image=self.frame_dict["stand"])

	def shape_grabber(self):
		pass
		
	def occupied_check(self,dx_dy):
		proposed_loc = (self.location[1]+dx_dy[1],self.location[0]+dx_dy[0])
		return Tile.find_by_location(proposed_loc)

	def move(self, direction):
		# cur_x, cur_y = App.canvas.coords(self.current_frame)
		dx_dy = {"Down":(0,1), "Up":(0,-1),"Left":(-1,0),"Right":(1,0)}[direction]
		if (self.moving == True) or (self.occupied_check(dx_dy)):
			return # Space occupied
		self.moving = True
		self.dx_dy = dx_dy
		self.frameflip(direction)
		self.move_tick(0)

	def move_tick(self,counter,frame_to_print = [1,2,3,2]):
			if counter == 40:
				self.location = (self.location[0]+self.dx_dy[0], self.location[1]+self.dx_dy[1])

				if keys_held[1] == "":
					self.moving = False
					self.place_image("stand")
					return
				else:
					self.place_image("stand")
					self.moving = False
					self.move(keys_held[1])

				return

			if counter%10 == 0:
				frame_to_print.append(frame_to_print.pop(0)) # cycles through the frames

			counter += 1

			self.place_image(self.possible_frames[frame_to_print[0]])
			App.canvas.move(self.current_frame, self.dx_dy[0], self.dx_dy[1])
			App.canvas.after(self.speed, self.move_tick, counter, frame_to_print)

	def place_image(self,frame):
		x, y = App.canvas.coords(self.current_frame)
		App.canvas.delete(self.current_frame)
		self.current_frame = App.canvas.create_image(x,y,image=self.frame_dict[frame])
		
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
	
	def __init__(self, location, destructible, kind):
		self.frame_dict = {} # "tile":photoimage location
		self.possible_frames = ["strongwall_1"]
		self.location = location
		self.kind = kind
		self.destructible = destructible
		self.shape = False
		self.shape_assign()
		self.tiles[location] = self

	def shape_assign(self):
		if self.kind == "wall":
			self.possible_frames = ["wall_1"]
		for frame in self.possible_frames:
			img = Image.open(f"sprites//tiles//{frame}.png") #PIL transposeable image
			frame_img = ImageTk.PhotoImage(img)
			self.frame_dict[frame] = frame_img
		row = self.location[1]*40+20
		self.current_frame = App.canvas.create_image(self.location[1]*40,self.location[0]*40,image=self.frame_dict[self.kind+"_1"], anchor=NW)
		
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

if platform.system() == "Linux":
	os.system("xset r on")