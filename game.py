from tkinter import *
import threading
import random
import time
import os
import platform

from PIL import Image, ImageTk

if platform.system() == "Linux": # Linux handles keys differently
	os.system("xset r off")

map_pattern = [ # 0-Nothing, 1-Indestructible, 2-Destructible, 3-Bomberman
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
	[1,0,0,3,0,0,0,0,0,2,0,0,0,0,1],
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

keys_held = []

movement_inputs = ["Up", "Down", "Left", "Right"]

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
		# self.interface.bind("<x>", lambda event: self.debug_destroy_random())
		self.interface.bind("<KeyPress>", lambda event: self.start_holding(event))
		self.interface.bind("<KeyRelease>", lambda event: self.stop_holding(event))
		self.interface.bind("<Destroy>", lambda event: self.closegame())
		self.interface.bind("<Escape>", lambda event: self.interface.destroy())
		self.key_held = ""
		self.keys_pressed = [] # keys currently being pressed
		self.worker = threading.Thread(target=self.gameloop)
		self.worker.start()
		self.interface.mainloop()

	def input_handler(self):
		if len(keys_held) == 0:
			return
		if "space" in keys_held:
			self.player.place_bomb()	
		for key in keys_held:
			if key in movement_inputs:
				self.player.move(key)
					
	def gameloop(self):
		self.lock = threading.Lock()
		while self.window:
			with self.lock:
				time.sleep(0.1)
				print(keys_held)
				self.input_handler()

	def start_holding(self, event):
		if event.keysym == "space":
			keys_held.append(event.keysym)
			return
		if event.keysym in movement_inputs:
			keys_held.insert(0, event.keysym)
			return

	def stop_holding(self, event):
		if len(keys_held) > 1:
			keys_held[0], keys_held[1] = keys_held[1], keys_held[0]
		keys_held.remove(event.keysym) if event.keysym in keys_held else None
		
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
				if row[column_index] not in [1,2]:
					continue
				wall = wall_list[row[column_index]%2]
				destructible = True if column_index == 1 else False
				tile = Tile((row_index,column_index),destructible,wall)

	def populate_creatures(self):
		# self.player = Creature((1,1),"player")
		for row_index, row in enumerate(map_pattern): # Adds tiles
			for column_index, column in enumerate(row):
				if row[column_index] not in [3]:
					continue
				creature_type = {
					3: "bomberman"
				}[row[column_index]]
				if creature_type == "bomberman": 
					print(row_index,column_index)
					self.player = Creature((row_index,column_index),"player")
					return
				else:
					creature = Creature((row_index,column_index),creature_type)

	def debug_destroy_random(self):
		key = random.choice(list(Tile.entities))
		if Tile.entities[key].destructible == True:
			self.canvas.delete(Tile.entities[key].shape)
			print("deleted")
			del Tile.entities[key]
			
class Creature():
	entities = {}
	
	def __init__(self,location, kind):
		self.location = location
		self.possible_frames = ["stand", "walk_1", "walk_2", "walk_3", "walk_4", "walk_5", "walk_6", "walk_7"] # Used to import the frames
		self.frame_dict = {} # "stand":photoimage location
		self.current_frame = False
		self.facing = "Left" # Direction currently facing. For frame flip check.
		self.dx_dy = 0
		self.kind = "bomberman"
		self.bomblength = 1 if self.kind == "bomberman" else 0
		self.speed = 10 # Lower = faster
		self.passable = True # When running passable check, enemy AI can walk towards you
		self.destructible = True
		self.moving = False # can't move if you're already moving
		self.trajectory = False
		self.move_queue = []
		shape_assign(self, 'stand', dy=0)
		self.entities[self.kind] = self

	def place_bomb(self):
		bomb = Bomb(self.location, self.bomblength)

	def frameflip(self):
		for frame in self.possible_frames:
			img = ImageTk.getimage(self.frame_dict[frame])
			img = img.transpose(Image.FLIP_LEFT_RIGHT)
			img = ImageTk.PhotoImage(img)
			self.frame_dict[frame] = img
		
	def occupied_check(self,dx_dy):
		proposed_loc = (self.location[0]+dx_dy[0],self.location[1]+dx_dy[1])
		for obj in [Bomb, Tile]:
			if find_by_location(obj, proposed_loc):
				return True
		return False

	def move(self, direction):
		dx_dy = {"Down":(0,1), "Up":(0,-1),"Left":(-1,0),"Right":(1,0)}[direction]
		if (self.moving == True) or (self.occupied_check(dx_dy)):
			return # Space occupied
		self.moving = True
		self.dx_dy = dx_dy
		frames_choice = {
			"Right": [1,2,3,2],
			"Left": [1,2,3,2],
			"Down": [4,5],
			"Up": [6,7] 
		}[direction]
		if (direction in ["Right","Left"]) and (direction != self.facing):
			self.facing = direction
			self.frameflip()
		self.move_tick(0, frames_choice)

	def move_tick(self,counter,frame_to_print):
			if counter == 40:
				if len(keys_held) == 0:
					self.moving = False
					place_image(self,"stand")
					return
				else:
					place_image(self,"stand")
					self.moving = False
					if keys_held[0] in movement_inputs:
						self.move(keys_held[0])
				return
			
			if counter == 20: # bomb/enemy collision
				self.location = (self.location[0]+self.dx_dy[0], self.location[1]+self.dx_dy[1])
				print(self.location)

			if counter%10 == 0:
				frame_to_print.append(frame_to_print.pop(0)) # cycles through the frames

			counter += 1

			place_image(self,self.possible_frames[frame_to_print[0]])
			App.canvas.move(self.current_frame, self.dx_dy[0], self.dx_dy[1])
			App.canvas.after(self.speed, self.move_tick, counter, frame_to_print)

class Explosion():
	entities = {}

	def __init__(self, location, kind, rotation):
		self.possible_frames = range(1,12)
		self.location = location
		self.kind = kind
		self.rotation = rotation
		self.frame_dict = {}
		shape_assign(self, 1, 'explosion//')
		self.framecounter = 1
		if self.rotation != 0:
			self.frameflip(rotation)
		self.explosion_tick()

	def explosion_tick(self):
		self.framecounter += 1

		if self.framecounter == 12:
			App.canvas.delete(self.current_frame)
			del self
			return

		place_image(self,self.framecounter)
		App.canvas.after(30, self.explosion_tick)

	def shape_assign(self):
		for frame in range(1,12):
			img = Image.open(f"sprites//explosion//{self.kind}//{frame}.png") #PIL transposeable image
			frame_img = ImageTk.PhotoImage(img)
			self.frame_dict[frame] = frame_img
		self.current_frame = App.canvas.create_image(20+(40*self.location[0]),20+(40*self.location[1]),image=self.frame_dict[1])

	def frameflip(self, rotation):
		for frame in range(1,12):
			img = ImageTk.getimage(self.frame_dict[frame])
			img = img.rotate(rotation)
			img = ImageTk.PhotoImage(img)
			self.frame_dict[frame] = img

	def place_image(self,frame):
		x, y = App.canvas.coords(self.current_frame)
		App.canvas.delete(self.current_frame)
		self.current_frame = App.canvas.create_image(x,y,image=self.frame_dict[frame])

class Bomb():
	entities = {}

	def __init__(self, location, bomblength):
		if str(location) in self.entities:
			del self
			return
		self.location = location
		self.kind = "bomb"
		self.bomblength = bomblength
		self.possible_frames = ["bomb_1","bomb_2","bomb_3","bomb_4"]
		self.frame_dict = {}
		self.time = 200
		self.entities[str(location)] = self
		shape_assign(self,"bomb_1")
		self.bomb_handler()
	
	def bomb_handler(self):
		# self.worker = threading.Thread(target=self.bomb_tick)
		# self.worker.start()
		self.bomb_tick()

	def bomb_tick(self):
		# self.lock = threading.Lock()
		# with self.lock:
		self.time -= 1
		if self.time%10 == 0:
			self.possible_frames.append(self.possible_frames.pop(0))
		
		if self.time <= 0:
			App.canvas.delete(self.current_frame)
			self.destroy()
			return
		place_image(self,self.possible_frames[0])
		App.canvas.after(10, self.bomb_handler)

	def destroy(self):
		origin_distance = {"Down":(0,1), "Up":(0,-1),"Left":(-1,0),"Right":(1,0)}
		obj_met = {"Down":False, "Up":False, "Left":False, "Right":False}
		core = Explosion(self.location, 'core', 0)
		for length in range(1,self.bomblength+1):

			for direction, distance in origin_distance.items():
				found = False
				if obj_met[direction] == True:
					continue
				dx = self.location[0] + distance[0]*length
				dy = self.location[1] + distance[1]*length
				rotation = {"Down": 90, "Up": 270, "Left": 0, "Right": 180}[direction]

				for object in [Tile, Bomb]:
					if find_by_location(object,(dx,dy)):
						obj_met[direction] = True
						instance = grab_object(object,(dx,dy))
						match instance.kind:
							case 'wall':
								instance.destroy()
							case 'bomb':
								instance.time = 0

						found = True
				
				if found:
					continue

				if length == self.bomblength:
					tip = Explosion((dx,dy),'tip',rotation)
					continue
				body = Explosion((dx,dy), 'body', rotation)

		del self.entities[str(self.location)], self

class Item():
	entities = {}

	def __init__(self):
		self.passable = True
		self.destructible = True

class Tile(): # Cannot pass through tiles
	entities = {}
	
	def __init__(self, location, destructible, kind):
		self.location = location
		self.frame_dict = {} # "tile":photoimage location
		self.kind = kind
		self.possible_frames = ["strongwall_1"] if self.kind == 'strongwall' else [f'wall_{num}' for num in range(1,10)]
		self.destructible = destructible
		self.framecounter = 1 
		shape_assign(self,self.kind+"_1", 'tiles//')
		self.entities[str(location)] = self
		
	def destroy(self): # If destructible tile, gets destroyed when touched by explosion
		self.tile_tick()

	def tile_tick(self):
		self.framecounter += 1

		if self.framecounter == 10:
			App.canvas.delete(self.current_frame)
			del self.entities[str(self.location)], self
			return

		place_image(self,f'wall_{self.framecounter}')
		App.canvas.after(15, self.tile_tick)

	def assign_item(self):
		pass
		# Random chance to assign an item upon

def shape_assign(object, firstframe, path='', dx=20, dy=20):
	for frame in object.possible_frames:
		img = Image.open(f"sprites//{path}{object.kind}//{frame}.png") #PIL transposeable image
		frame_img = ImageTk.PhotoImage(img)
		object.frame_dict[frame] = frame_img
	object.current_frame = App.canvas.create_image(dx+(40*object.location[0]),dy+(40*object.location[1]),image=object.frame_dict[firstframe])

def place_image(object,frame):
	x, y = App.canvas.coords(object.current_frame)
	App.canvas.delete(object.current_frame)
	object.current_frame = App.canvas.create_image(x,y,image=object.frame_dict[frame])

def find_by_location(object, location):
	return str(location) in object.entities

def grab_object(object,location):
	if str(location) in object.entities:
		return object.entities[str(location)]
	
app = App()

if platform.system() == "Linux":
	os.system("xset r on")