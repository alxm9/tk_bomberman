from tkinter import *
from PIL import Image, ImageTk
import tkinter_windows as tkwin

import sounddevice as sd
import soundfile as sf

import time
import random
import os
import platform
import threading

map_pattern = [ # 0-Nothing, 1-Indestructible, 2-Destructible, 3-Bomberman, 4-Bomberman_2
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
	[1,0,1,0,1,0,1,2,1,0,1,0,1,3,1],
	[1,0,0,2,2,0,2,2,2,2,0,0,0,0,1],
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

keys_held = []

movement_inputs = {
	'bomberman_1': ['Up', 'Down', 'Left', 'Right'],
	'bomberman_2': ['W', 'S', 'A', 'D', 'w', 's', 'a', 'd']
}

explosion_sprites = []

interface = Tk()
# tkSnack.initializeSnack(interface)
width = 600
height = 600
interface.geometry(f"{height}x{width}")
canvas = Canvas(interface, bg = "green", width = 600, height = 600)
canvas.pack()
tile_sqpixels = 40
tkwin.width = width
tkwin.height = height
tkwin.interface = interface
tkwin.canvas = canvas

loop = True


class App():
	sounds = {}
	def __init__(self):
		tkwin.App = self
		self.platform_handler()
		interface.bind('<KeyPress>', lambda event: self.hold_handler(event,'start'))
		interface.bind('<KeyRelease>', lambda event: self.hold_handler(event,'stop'))
		interface.bind('<Escape>', lambda _: interface.destroy())
		# interface.bind('<x>', self.obliterate)
		tkwin.menuwin = tkwin.create_menu('mainmenu')
		self.initialize_sound()
		interface.mainloop()

	def hold_handler(self, event, mode):
		match mode:
			case 'start':
				for key, creature in Creature.entities.items():
					creature.start_holding(event)
			case 'stop':
				for key, creature in Creature.entities.items():
					creature.stop_holding(event)
		
	def initialize_sound(self):
		for sound in os.listdir('audio'): # NEEDS REWORK
			data,fs = sf.read(f'audio//{sound}', dtype='float32')
			self.sounds[sound.split('.',1)[0]] = (data,fs)

	def start_local_game(self, colortuple):
		config_loop(True)
		interface.unbind('<Escape>')
		interface.bind('<Escape>', self.gotomainmenu)

		self.gameloop()
		self.populate_tiles()
		self.populate_creatures(colortuple)

	def gotomainmenu(self, event):
		interface.unbind('<Escape>')
		interface.bind('<Escape>', lambda _: interface.destroy())

		config_loop(False)
		self.obliterate()
		tkwin.menuwin = tkwin.create_menu('mainmenu')

	def obliterate(self):
		canvas.delete('gamesprites')
		for object in [Explosion, Bomb, Item, Creature]:
			object.entities.clear()

	def platform_handler(self):
		if platform.system() == "Linux": # Linux handles keys differently
			os.system("xset r off")
		if platform.system() == "Windows":
			import ctypes
			ctypes.windll.winmm.timeBeginPeriod(1) # fixes lag on windows, granularity related
					
	def gameloop(self):
		# for every player in creature here
		for key, creature in Creature.entities.items():
			creature.input_handler()
		if not loop:
			return
		interface.after(10, self.gameloop)

	def populate_tiles(self): # Draws map based on map_pattern
		wall_list = ["wall","strongwall"]
		
		canvas.create_rectangle(0,0,height, width, fill='green', width=0, tag='gamesprites')
		for row in range(15): # Adds some variety to the floor
			for column in range(15):
				if (column%2) == 1 and (row%2)==1:
					canvas.create_rectangle((40*row),(40*column),40+(40*row),40+(40*column), fill="#439229", width=0, tag='gamesprites')
						
		for row_index, row in enumerate(map_pattern): # Adds tiles
			for column_index, column in enumerate(row):
				if row[column_index] not in [1,2]:
					continue
				wall = wall_list[row[column_index]%2]
				destructible = True if column_index == 1 else False
				tile = Tile((row_index,column_index),destructible,wall)

	def populate_creatures(self, colortuple):
		counter = 0

		for row_index, row in enumerate(map_pattern): # Adds tiles
			for column_index, column in enumerate(row):
				if row[column_index] not in [3]:
					continue
				creature_type = {
					3: "bomberman"
				}[row[column_index]]
				if creature_type == "bomberman": 
					counter += 1
					Creature((row_index,column_index),f'bomberman_{counter}',colortuple[counter-1])
					if self.singleplayer:
						return
				else:
					Creature((row_index,column_index),creature_type)
			
class Creature():
	entities = {}

	def __init__(self,location, kind, colortuple):
		self.keys_held = []
		self.bomb_input = {'bomberman_1': 'space', 'bomberman_2': 'f'}[kind]

		self.location = location
		self.possible_frames = ["stand", "walk_1", "walk_2", "walk_3", "walk_4", "walk_5", "walk_6", "walk_7"] # Used to import the frames
		self.frame_dict = {} # "stand":photoimage location
		self.explosion_dict = { # preloading explosions in memory
			'core_0': {},
			'body_0': {}, # Horizontal
			'body_90': {}, # Vertical
			'tip_0': {}, # Left
			'tip_90': {}, # Up
			'tip_180': {}, # Right
			'tip_270': {}, # Down
		} # preloaded explosions
		self.bomb_dict = {} # preloading bombs in memory
		preload_explosions(self,colortuple[1])
		preload_bombs(self, colortuple[1])

		self.current_frame = False
		self.color = 'blue'
		self.facing = "Left" # Direction currently facing. For frame flip check.
		self.dx_dy = 0
		self.kind = kind
		self.bomblength = 5
		self.speed = 7 # Lower = faster
		self.moving = False # can't move if you're already moving
		shape_assign(self, 'stand', dy=0, color = colortuple[1])
		self.entities[self.kind] = self

	def input_handler(self):
		if len(self.keys_held) == 0:
			return
		# if "space" in self.keys_held:
		# 	Bomb(self.location, self.bomblength, self.explosion_dict, self.bomb_dict)	
		for key in self.keys_held:
			if key == self.bomb_input:
				Bomb(self.location, self.bomblength, self.explosion_dict, self.bomb_dict)	
			if key in movement_inputs[self.kind]:
				self.move(key)

	def start_holding(self, event):
		if event.keysym in self.keys_held:
			return
		if event.keysym in self.bomb_input:
			self.keys_held.append(event.keysym)
			return
		if event.keysym in movement_inputs[self.kind]:
			self.keys_held.insert(0, event.keysym)
			return

	def stop_holding(self, event):
		if len(self.keys_held) > 1:
			self.keys_held[0], self.keys_held[1] = self.keys_held[1], self.keys_held[0]
		self.keys_held.remove(event.keysym) if event.keysym in self.keys_held else None

	def kill(self):
		canvas.delete(self.current_frame)

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
		if self.kind != 'bomberman_1':
			direction = convert_secondary_inputs(direction)
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
		if not loop:
			return
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
		
		if counter == 20: # entity collision
			self.location = (self.location[0]+self.dx_dy[0], self.location[1]+self.dx_dy[1])
			item = grab_object(Item,self.location)
			if item:
				# worker = threading.Thread(target=runsound, args=(App.sounds['powerup'],))
				# worker.start()
				match item.kind:
					case 'up_speed':
						self.speed -= 1
					case 'up_bomb':
						pass
					case 'up_explosion':
						self.bomblength += 1
				item.destroy()

		if counter%10 == 0:
			frame_to_print.append(frame_to_print.pop(0)) # cycles through the frames
			place_image(self,self.possible_frames[frame_to_print[0]])

		counter += 1

		canvas.move(self.current_frame, self.dx_dy[0], self.dx_dy[1])
		canvas.after(self.speed, self.move_tick, counter, frame_to_print)

class Explosion():
	entities = {}

	def __init__(self, location, kind, explodict):
		self.possible_frames = range(1,12)
		self.location = location
		self.kind = kind
		self.frame_dict = explodict
		self.current_frame = canvas.create_image(20+(40*self.location[0]),20+(40*self.location[1]),image=self.frame_dict[1], tag='gamesprites')
		self.framecounter = 1
		self.explosion_tick()
		if self.kind == 'core':
			self.entities[str(location)] = self
			interface.after(50, self.destroy)

	def explosion_tick(self):
		if not loop:
			return
		self.framecounter += 1

		if self.framecounter == 12:
			canvas.delete(self.current_frame)
			del self
			return

		place_image(self,self.framecounter)
		canvas.after(50, self.explosion_tick)
	
	def destroy(self):
		del self.entities[str(self.location)], self

	def place_image(self,frame):
		x, y = canvas.coords(self.current_frame)
		canvas.delete(self.current_frame)
		self.current_frame = canvas.create_image(x,y,image=self.frame_dict[frame], tag='gamesprites')

class Bomb():
	entities = {}

	def __init__(self, location, bomblength, explodict, bombdict):
		if str(location) in self.entities:
			del self
			return
		self.explodict = explodict
		self.location = location
		self.kind = "bomb"
		self.bomblength = bomblength
		self.possible_frames = [1,2,3,4]
		self.frame_dict = bombdict
		self.current_frame = canvas.create_image(20+(40*self.location[0]),20+(40*self.location[1]),image=self.frame_dict[1], tag='gamesprites')
		self.time = 200
		self.entities[str(location)] = self
		self.bomb_handler()
	
	def bomb_handler(self):
		self.bomb_tick()

	def bomb_tick(self):
		if not loop:
			return
		self.time -= 1
		if self.time%10 == 0:
			self.possible_frames.append(self.possible_frames.pop(0))
			place_image(self,self.possible_frames[0])
		
		if self.time <= 0:
			# worker = threading.Thread(target=runsound, args=(App.sounds['explosion'],))
			# worker.start()
			# sd.play(*App.sounds['explosion'])
			canvas.delete(self.current_frame)
			self.destroy()
			return
		canvas.after(10, self.bomb_handler)

	def explosion_interaction(self, obj_met, direction, dx, dy):
		for object in [Tile, Bomb, Item, Explosion]:
			instance = grab_object(object,(dx,dy))
			if instance:
				obj_met[direction] = True
			else:
				continue

			match instance:
				case Bomb():
					instance.time = 0
					# interface.after(1, self.set_time)
				case Item():
					instance.destroy()
				case Tile(kind='wall'):
					instance.destroy()		

	def destroy(self):
		timer1 = time.time()
		origin_distance = {"Down":(0,1), "Up":(0,-1),"Left":(-1,0),"Right":(1,0)}
		obj_met = {"Down":False, "Up":False, "Left":False, "Right":False}
		Explosion(self.location, 'core', self.explodict['core_0'])
		for length in range(1,self.bomblength+1):
			for direction, distance in origin_distance.items():
				
				if obj_met[direction] == True:
					continue
				dx = self.location[0] + distance[0]*length
				dy = self.location[1] + distance[1]*length
				rotation_tip = {"Down": 90, "Up": 270, "Left": 0, "Right": 180}[direction]
				rotation_body = {"Down": 90, "Up": 90, "Left": 0, "Right": 0}[direction]

				self.explosion_interaction(obj_met, direction, dx, dy)
				
				if obj_met[direction]:
					continue

				if length == self.bomblength:
					Explosion((dx,dy),'tip',self.explodict[f'tip_{rotation_tip}'])
					continue
				Explosion((dx,dy),'body', self.explodict[f'body_{rotation_body}'])

		del self.entities[str(self.location)], self
		print(time.time() - timer1, "ELAPSED TIME")

class Item():
	entities = {}

	def __init__(self,location):
		self.location = location
		self.frame_dict = {}
		self.possible_frames = [1,2,3,4]
		self.kind = random.choice(['up_speed', 'up_bomb', 'up_explosion'])
		self.taken = False
		self.destroying = False 
		self.entities[str(location)] = self
		shape_assign(self,1,"powerup//")
		self.item_tick()
	
	def item_tick(self):
		if not loop:
			return
		if self.taken == False:
			self.possible_frames.append(self.possible_frames.pop(0))
			place_image(self,self.possible_frames[0])
			canvas.after(90, self.item_tick)

	def destroy(self):
		if self.destroying:
			return
		self.destroying = True
		self.taken = True
		canvas.delete(self.current_frame)

		self.frame_dict = {}
		self.kind = 'general_blowup'
		self.possible_frames = [1,2,3,4,5]
		shape_assign(self,1)

		self.frame = 0
		self.destroy_tick()
	
	def destroy_tick(self):
		if not loop:
			return
		self.frame += 1
		place_image(self,self.possible_frames[0])
		if self.frame == self.possible_frames[1]+1:
			del self.entities[str(self.location)], self
			return
		else:
			canvas.after(40, self.destroy_tick)


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

	def drop_item(self):
		Item(self.location) if (random.random() > 0.5) else None

	def tile_tick(self):
		if not loop:
			return
		
		self.framecounter += 1
		if self.framecounter == 10:
			canvas.delete(self.current_frame)
			self.drop_item()
			del self.entities[str(self.location)], self
			return

		place_image(self,f'wall_{self.framecounter}')
		canvas.after(15, self.tile_tick)

	def assign_item(self):
		pass
		# Random chance to assign an item upon

# Adds frames to the dictionary of the respective object
def shape_assign(object = None, firstframe = None, path='', dx=20, dy=20, color = None):
	for frame in object.possible_frames:
		spritesfolder = object.kind.split('_',1)[0] if 'bomberman' in object.kind else object.kind
		img = Image.open(f"sprites//{path}{spritesfolder}//{frame}.png") #PIL transposeable image
		if color != None:
			img = img.convert('RGBA')

			new_data = []
			imgdata = img.getdata()
			for item in imgdata:
				print(item)
				if item[:3] == (255,255,255):
					new_data.append((*color,item[3]))			
				elif item[:3] == (190,27,39) or item[:3] == (255,0,0) :
					colors = [int(color[0]//1.5), int(color[1]//1.5),int(color[2]//1.5)]
					new_data.append((*colors,item[3]))
				else:
					new_data.append(item)
			img.putdata(new_data)			
		frame_img = ImageTk.PhotoImage(img)
		object.frame_dict[frame] = frame_img
	object.current_frame = canvas.create_image(dx+(40*object.location[0]),dy+(40*object.location[1]),image=object.frame_dict[firstframe], tag='gamesprites')

def preload_bombs(object, color):
	for frame in range(1,5):
		img = Image.open(f"sprites//bomb//{frame}.png") #PIL transposeable image
		if color != None:
			img = img.convert('RGBA')

			new_data = []
			imgdata = img.getdata()
			for item in imgdata:
				print(item)
				if item[:3] == (91,91,91):
					new_data.append((int(color[0]//1.2), int(color[1]//1.2),int(color[2]//1.2),item[3]))	
				elif item[:3] == (119,119,119):
					new_data.append((color[0]+30, color[1]+30,color[2]+30,item[3]))	
				else:
					new_data.append(item)
			img.putdata(new_data)			
		frame_img = ImageTk.PhotoImage(img)
		object.bomb_dict[frame] = frame_img


def preload_explosions(object, color):
	for part in ['core', 'body', 'tip']:
		for rotation in [0,90,180,270]:
			for frame in range(1,12):
				if (part == 'core') and (rotation != 0):
					continue
				if (part == 'body') and (rotation in [180,270]):
					continue

				img = Image.open(f"sprites//explosion//{part}//{frame}.png")
				img = img.convert('RGBA')

				new_data = []
				imgdata = img.getdata()
				for item in imgdata:
					# print(item)
					if item[:3] == (255,0,0):
						new_data.append((*color,item[3])) # replace this with color
					else:
						new_data.append(item)
				img.putdata(new_data)

				img = img.rotate(rotation)	
				frame_img = ImageTk.PhotoImage(img)
				object.explosion_dict[f'{part}_{rotation}'][frame] = frame_img
			# print(object.explosion_dict)

def runsound(arg):
	sd.play(*arg)

def config_loop(arg):
	global loop
	if arg:
		loop = True
	else:
		loop = False

def convert_secondary_inputs(input):
	input = input.lower()
	map = {
		'w': 'Up',
		's': 'Down',
		'a': 'Left',
		'd': 'Right'
	}[input]
	return map

def place_image(object,frame):
	x, y = canvas.coords(object.current_frame)
	canvas.delete(object.current_frame)
	object.current_frame = canvas.create_image(x,y,image=object.frame_dict[frame], tag='gamesprites')

def find_by_location(object, location):
	return str(location) in object.entities

def grab_object(object,location):
	if str(location) in object.entities:
		return object.entities[str(location)]
	return False

def close_handler():
	if platform.system() == "Linux":
		os.system("xset r on")
	if platform.system() == "Windows":
		ctypes.windll.winmm.timeEndPeriod(1)
		
app = App()
close_handler()