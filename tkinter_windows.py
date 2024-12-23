import sys
from PIL import Image, ImageTk
import color_picker as colpic

class Window():
    def __init__(self, name, wintype):
        self.name = name
        self.wintype = wintype
        self.host = False
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
            canvas.create_text(5,595, text = "Alex M. 2024\ngithub.com/alxm9", anchor = 'sw', font=("sans-serif",10))
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
            menuwin.create_button("Local Game",xcord = 250,ycord = 150, method='target_localmenu')
            menuwin.create_button("Online Game",xcord = 250,ycord = 225, method='target_mpmenu')
            menuwin.create_button("Exit",xcord = 250,ycord = 300, method='exit')
        case 'localmenu':
            menuwin = Window('localmenu', 'fullscreen')
            menuwin.create_button('1 Player',xcord = 250,ycord = 150, method='target_spmenu')
            menuwin.create_button('2 Players',xcord = 250,ycord = 225, method='target_2pmenu')
        case 'spmenu':
            App.singleplayer = True
            menuwin = Window('spmenu', 'fullscreen')
            menuwin.create_button("Start",xcord = 250,ycord = 400, method='start_localgame')
            menuwin.picker = colpic.Colorpicker(interface, canvas, x = 100, y = 100, bgcolor = 'grey')
        case '2pmenu':
            App.singleplayer = False
            menuwin = Window('spmenu', 'fullscreen')
            menuwin.create_button("Start",xcord = 250,ycord = 500, method='start_localgame_2')
            menuwin.picker = colpic.Colorpicker(interface, canvas, x = 100, y = 10, bgcolor = 'grey', name = "picker1")
            menuwin.picker2 = colpic.Colorpicker(interface, canvas, x = 100, y = 240, bgcolor = 'grey', name = "picker2")
        case 'mpmenu':
            menuwin = Window('mpmenu','fullscreen')
            menuwin.create_button('Host',xcord = 250,ycord = 150, method='target_mplobby_host')
            menuwin.create_button('Join',xcord = 250,ycord = 225, method='target_mplobby_join')
        # case "pausemenu":
        #     menuwin = Window("pausemenu","overlay")
        #     menuwin.create_button("Exit",xcord = 250,ycord = 200, method='exit')
        #     menuwin.create_button("Return",xcord = 250,ycord = 350, method='destroy')
        case 'mplobby_host':
            menuwin = Window('mplobby','fullscreen')
            menuwin.create_button('Start', xcord = 480, ycord = 20, method='exit')
            menuwin.create_button('Leave', xcord = 480, ycord = 90, method='target_mainmenu')
        case 'mplobby_join':
            menuwin = Window('mplobby','fullscreen')
            menuwin.create_button('Lock in', xcord = 480, ycord = 20, method='exit')
            menuwin.create_button('Leave', xcord = 480, ycord = 90, method='target_mainmenu')
            
    return menuwin
    
def handle_game_start(arg):
    match arg:
        case 'localgame':
            hex_rgb = menuwin.picker.hex_rgb()
            menuwin.picker.destroy()
            menuwin.destroy()
            App.start_local_game( (hex_rgb,) )
        case 'localgame_2':
            hex_rgb = menuwin.picker.hex_rgb()
            hex_rgb_2 = menuwin.picker2.hex_rgb()
            menuwin.picker.destroy()
            menuwin.picker2.destroy()
            menuwin.destroy()
            App.start_local_game( (hex_rgb, hex_rgb_2) )
