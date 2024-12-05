import sys
from PIL import Image, ImageTk
import color_picker as colpic

class Window():
    def __init__(self, name, wintype):
        self.name = name
        self.wintype = wintype
        self.graphics = [] #canvas objects
        self.objects = [] #buttons, other
        self.picker = None

        if wintype == "fullscreen":
            x0, y0 = 0, 0
            x1, y1 = width, height
        if wintype == "overlay":
            x0, y0 = width/4, height/4
            x1, y1 = (width/4)*3, (height/4)*3

        bg = canvas.create_rectangle(x0,y0,x1,y1, fill="orange")
        self.graphics.append(bg)

        if self.name == "mainmenu":
            img = Image.open(f"sprites//tkbombermanlogo.png") #PIL transposeable image
            self.logo = ImageTk.PhotoImage(img)
            canvas.create_image(300, 100,image=self.logo)
            # self.graphics.append(logo


    def create_button(self, name, xcord = 0, ycord = 0, method = False, width = 100, height = 50):
        self.objects.append(Button(name, xcord, ycord, method, width, height, self))

    def destroy(self):
        for graphic in self.graphics:
            canvas.delete(graphic)
        # canvas.delete(graphic for graphic in self.graphics) # can't take generator items as an arg
        for object in self.objects:
            for graphic in object.graphics:
                canvas.delete(graphic)
        del self

class Button():
    def __init__(self, name, xcord, ycord, method, width, height, parent):
        self.name = name
        self.parent = parent
        self.xcord, self.ycord = xcord, ycord
        self.graphics = [] #canvas objects
        self.method = self.assign_method(method) if method != False else False

        x0, y0 = 0+xcord, 0+ycord
        x1, y1 = width+xcord, height+ycord

        button_shape = canvas.create_rectangle(x0,y0,x1,y1, fill = "grey", outline = "black")
        self.graphics.append(button_shape)
        self.hover_behaviour()
        button_text = canvas.create_text(x0+(width/2),y0+(height/2), text=name, font=("sans-serif",10), state='disabled')
        self.graphics.append(button_text)
    
    def hover_behaviour(self):
        for graphic in self.graphics:
            canvas.tag_bind(graphic, '<Enter>', self.OnHover)
            canvas.tag_bind(graphic, '<Leave>', self.UnHover)
            canvas.tag_bind(graphic, '<ButtonRelease>', self.method)

    def assign_method(self,method):
        if method.split('_',1)[0] in ['target','start']:
            arg = method.split('_',1)[1]
            method = method.split('_',1)[0]
        return {
            'exit': lambda _: sys.exit(),
            'target': lambda _: create_menu(arg),
            'destroy': lambda _: self.parent.destroy(),
            'start': lambda _: handle_game_start(arg),
        }[method]
    
    def OnHover(self, event):
        canvas.itemconfig(self.graphics[0], fill='red')
    
    def UnHover(self, event):
        canvas.itemconfig(self.graphics[0], fill='grey')

def create_menu(menu):
    global menuwin
    match menu:
        case "mainmenu":
            menuwin = Window("mainmenu","fullscreen")
            menuwin.create_button("Singleplayer",xcord = 250,ycord = 150, method='target_spmenu')
            menuwin.create_button("Multiplayer",xcord = 250,ycord = 225, method='target_mpmenu')
            menuwin.create_button("Exit",xcord = 250,ycord = 300, method='exit')
        case 'spmenu':
            menuwin = Window('spmenu', 'fullscreen')
            menuwin.create_button("Start",xcord = 250,ycord = 400, method='start_singleplayer')
            print("here")
            menuwin.picker = colpic.Colorpicker(interface, canvas, x = 100, y = 100, bgcolor = 'grey')
        case 'mpmenu':
            menuwin = Window('mpmenu','fullscreen')
            menuwin.create_button('Host',xcord = 250,ycord = 150, method='exit')
            menuwin.create_button("Join",xcord = 250,ycord = 225, method='exit')
        case "pausemenu":
            menuwin = Window("pausemenu","overlay")
            menuwin.create_button("Exit",xcord = 250,ycord = 200, method='exit')
            menuwin.create_button("Return",xcord = 250,ycord = 350, method='destroy')
    return menuwin
    
def handle_game_start(arg):
    match arg:
        case 'singleplayer':
            print('here')
            hexcolor = menuwin.picker.hexcolor
            rgb = menuwin.picker.rgb()
            menuwin.picker.destroy()
            menuwin.destroy()
            App.start_single_player( (hexcolor,rgb) )
