from tkinter import *
import threading
import random
import time
import os

from PIL import Image, ImageTk

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
		self.interface.bind("<Key>", lambda event: self.bindings(event))
		self.interface.bind("<Destroy>", lambda event: self.closegame())
		self.interface.bind("<Escape>", lambda event: self.interface.destroy())
		self.key_pressed = False
		self.worker = threading.Thread(target=self.gameloop)
		self.worker.start()
		self.interface.mainloop()
	
	def gameloop(self):
		self.lock = threading.Lock()
		while self.window:
			self.lock.acquire()
			time.sleep(1)
			print("tick")
			self.lock.release()

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
				
	def release(self):
		self.key_pressed = False

	def bindings(self,event):
		# lock = threading.Lock()
		if self.key_pressed == False:
			# lock.acquire()
			player = Creature.creatures["bomberman"]
			binds = {
			# "x" : lambda: self.debug_destroy_random,
			"Down" : lambda: player.move("Down"),
			"Up" : lambda: player.move("Up"),
			"Left" : lambda: player.move("Left"),
			"Right" : lambda: player.move("Right"),
			}
			# print(event)
			if event.keysym in binds:
				binds[event.keysym]()
			# lock.release()

	def populate_creatures(self):
		entity = Creature((1,1),"player")

	def debug_destroy_random(self):
		key = random.choice(list(tile_dict))
		if tile_dict[key].destructible == True:
			self.canvas.delete(tile_dict[key].shape)
			del tile_dict[key]
			
class Creature():
	creatures = {}
	
	def __init__(self,location, kind):
		self.possible_frames = ["stand", "walk_1", "walk_2", "walk_3"] # Used to import the frames
		self.frame_dict = {} # "stand":photoimage location
		self.current_frame = False
		self.input_queue = False
		self.facing = "Left" # Direction currently facing. For frame flip check.
		self.location = location
		self.kind = "bomberman"
		self.speed = 10 # Lower = faster
		self.passable = True # When running passable check, enemy AI can walk towards you
		self.destructible = True
		self.moving = False # can't move if you're already moving
		self.shape_assign()
		self.creatures[self.kind] = self

	def frameflip_check(self, direction):
		if direction == self.facing:
			return
		self.facing = direction
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
		
	def passable_check(self,direction,dx_dy):
		proposed_loc = (self.location[1]+dx_dy[1],self.location[0]+dx_dy[0])
		return Tile.find_by_location(proposed_loc)
				
	def move(self, direction):
		dx_dy = {"Down":(0,1), "Up":(0,-1),"Left":(-1,0),"Right":(1,0)}[direction]
		if (self.moving == True) or (self.passable_check(direction, dx_dy) is True):
			return # Space occupied
		# self.moving = True
		self.frameflip_check(direction)
		self.move_tick(dx_dy,0)

	def move_tick(self,dx_dy,counter,frame_to_print = [1,2,3,2]):
		cur_x, cur_y = App.canvas.coords(self.current_frame)
		if counter == 40:
			self.location = (self.location[0]+dx_dy[0], self.location[1]+dx_dy[1])
			self.moving = False
			self.place_image(cur_x,cur_y,"stand")
			return
		if counter%10 == 0:
			popped = frame_to_print.pop(0)
			frame_to_print.append(popped)
		counter += 1
		self.place_image(cur_x,cur_y,self.possible_frames[frame_to_print[0]])
		App.canvas.move(self.current_frame, dx_dy[0], dx_dy[1])
		App.canvas.after(self.speed, self.move_tick, dx_dy, counter, frame_to_print)

	def place_image(self,x,y,frame):
		App.canvas.delete(self.current_frame)
		self.current_frame = App.canvas.create_image(x,y,image=self.frame_dict[frame])
		
	def move_execute(self,dx_dy):
		App.canvas.move(self.shape_stand, dx_dy[0], dx_dy[1])
		
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
