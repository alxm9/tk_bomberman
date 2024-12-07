from tkinter import *
# interface = Tk()
# interface.geometry("500x500")
# canvas = Canvas(width = 500, height = 500, bg = 'orange')
# canvas.pack()

class Colorpicker():
    def __init__(self, interface, canvas, x = 0, y = 0, bgcolor = 'grey', name = "default"):
        self.name = name
        self.graphics = []
        self.sliderdict = {
            f'redslider_{self.name}': 0,
            f'greenslider_{self.name}': 0,
            f'blueslider_{self.name}': 0
        }
        self.x = x
        self.y = y 
        self.bgcolor = bgcolor
        self.canvas = canvas
        self.anchor = 0
        self.hexcolor = '#000000'
        self.interface = interface
        self.draw()
        self.initial_moveshapes()
        self.canvas.move(f'colorpicker_{self.name}', x,y)

        canvas.tag_bind(f'redslider_{self.name}', '<Enter>', lambda _: self.onhover(f'redslider_{self.name}'))
        canvas.tag_bind(f'greenslider_{self.name}', '<Enter>', lambda _: self.onhover(f'greenslider_{self.name}'))
        canvas.tag_bind(f'blueslider_{self.name}', '<Enter>', lambda _: self.onhover(f'blueslider_{self.name}'))

        canvas.tag_bind(f'redslider_{self.name}', '<Leave>', lambda _: self.unhover(f'redslider_{self.name}'))
        canvas.tag_bind(f'greenslider_{self.name}', '<Leave>', lambda _: self.unhover(f'greenslider_{self.name}'))
        canvas.tag_bind(f'blueslider_{self.name}', '<Leave>', lambda _: self.unhover(f'blueslider_{self.name}'))

        canvas.tag_bind(f'redslider_{self.name}', '<ButtonPress>', lambda _: self.onclick(f'redslider_{self.name}'))
        canvas.tag_bind(f'greenslider_{self.name}', '<ButtonPress>', lambda _: self.onclick(f'greenslider_{self.name}'))
        canvas.tag_bind(f'blueslider_{self.name}', '<ButtonPress>', lambda _: self.onclick(f'blueslider_{self.name}'))

        canvas.tag_bind(f'redslider_{self.name}', '<ButtonRelease>', lambda _: self.release(f'redslider_{self.name}'))
        canvas.tag_bind(f'greenslider_{self.name}', '<ButtonRelease>', lambda _: self.release(f'greenslider_{self.name}'))
        canvas.tag_bind(f'blueslider_{self.name}', '<ButtonRelease>', lambda _: self.release(f'blueslider_{self.name}'))

    def release(self,event):
        self.interface.unbind('<Motion>')
        self.interface.config(cursor="arrow")
    
    def hex_rgb(self):
        return (self.hexcolor,(self.sliderdict[f'redslider_{self.name}'], self.sliderdict[f'greenslider_{self.name}'], self.sliderdict[f'blueslider_{self.name}']))

    def onhover(self,event):
        self.canvas.itemconfig(event, fill='white')

    def unhover(self,event):
        self.canvas.itemconfig(event, fill='grey')
    
    def destroy(self):
        self.canvas.delete(f'colorpicker_{self.name}')

    def onclick(self,slider):
        self.anchor = self.canvas.coords(slider)[0]
        self.interface.bind('<Motion>', lambda event: self.controlslider(event,slider))
        self.canvas.itemconfig(slider, fill=slider.split("slider",1)[0])
        self.interface.config(cursor="none")
    
    def controlslider(self,event, button):
        self.canvas.itemconfig(button, fill=button.split("slider",1)[0])
        self.canvas.tag_raise(button)
        self.canvas.tag_raise(button.split('slider',1)[0]+f'arrows_{self.name}')
        # if event.x > self.anchor:
        #     if self.sliderdict[button] == 255:
        #         return
        if (self.canvas.coords(button)[0] + (event.x - self.anchor) < (self.x+10)) or (self.canvas.coords(button)[0] + (event.x - self.anchor) > (self.x+265)):
            return
        self.sliderdict[button] += int((event.x - self.anchor))
        self.canvas.move(button, (event.x - self.anchor), 0)
        self.canvas.move(button.split('slider',1)[0]+f'arrows_{self.name}', (event.x - self.anchor),0)
        # else:
        #     if self.sliderdict[button] == 0:
        #         return
        #     self.sliderdict[button] -= 1
        #     self.canvas.move(button, -1, 0)
        #     self.canvas.move(button.split('slider',1)[0]+'arrows', -1,0)
        self.anchor = event.x
        self.canvas.itemconfig(f'output_text_{self.name}', text=f'R: {self.sliderdict[f'redslider_{self.name}']}\nG: {self.sliderdict[f'greenslider_{self.name}']}\nB: {self.sliderdict[f'blueslider_{self.name}']}')
        self.hexcolor = '#%02x%02x%02x' % (self.sliderdict[f'redslider_{self.name}'], self.sliderdict[f'greenslider_{self.name}'], self.sliderdict[f'blueslider_{self.name}'])
        self.canvas.itemconfig(f'output_{self.name}', fill = self.hexcolor)

    def draw(self):
        self.canvas.create_rectangle(0,0,400,225, fill = self.bgcolor, 
                                    tag = (f'colorpicker_{self.name}',f'colorpickerbg_{self.name}'))

        self.canvas.create_rectangle(0,0,25,50, fill = 'grey', 
                                    tag = (f'colorpicker_{self.name}', f'redslider_{self.name}'))
        
        self.canvas.create_text(12.5,25,text=">>\n<<",
                                tag = (f'colorpicker_{self.name}',f'redarrows_{self.name}'),
                                state = 'disabled')

        self.canvas.create_rectangle(0,0,25,50,
                                     fill = 'grey',
                                     tag = (f'colorpicker_{self.name}',f'greenslider_{self.name}'))
        
        self.canvas.create_text(12.5,25,text=">>\n<<",
                                tag = (f'colorpicker_{self.name}',
                                       f'greenarrows_{self.name}'),
                                state = 'disabled')

        self.canvas.create_rectangle(0,0,25,50, 
                                     fill = 'grey', 
                                     tag = (f'colorpicker_{self.name}', f'blueslider_{self.name}'))
        
        self.canvas.create_text(12.5,25,text=">>\n<<", 
                                tag = (f'colorpicker_{self.name}', f'bluearrows_{self.name}'), 
                                state = 'disabled')

        self.canvas.create_rectangle(0,0,255,10, fill = 'red', 
                                     tag = (f'colorpicker_{self.name}', f'linered_{self.name}'))

        self.canvas.create_rectangle(0,0,255,10, fill = 'green', 
                                     tag = (f'colorpicker_{self.name}', f'linegreen_{self.name}'))

        self.canvas.create_rectangle(0,0,255,10, fill = 'blue', 
                                     tag = (f'colorpicker_{self.name}', f'lineblue_{self.name}'))

        self.canvas.create_rectangle(0,0,50,50, fill = self.hexcolor, 
                                     tag = (f'colorpicker_{self.name}', f'output_{self.name}'))

        self.canvas.create_text(25,60,text=f'R: {self.sliderdict[f'redslider_{self.name}']}\nG: {self.sliderdict[f'greenslider_{self.name}']}\nB: {self.sliderdict[f'blueslider_{self.name}']}', 
                                tag = (f'colorpicker_{self.name}', f'output_text_{self.name}'), font=("sans-serif",10))
    
    def initial_moveshapes(self):
        self.canvas.move(f'redslider_{self.name}', 10, 20)
        self.canvas.move(f'redarrows_{self.name}', 10,20)

        self.canvas.move(f'greenslider_{self.name}', 10, 80)
        self.canvas.move(f'greenarrows_{self.name}', 10, 80)

        self.canvas.move(f'blueslider_{self.name}', 10, 140)
        self.canvas.move(f'bluearrows_{self.name}', 10, 140)

        self.canvas.move(f'linered_{self.name}', 35,40)
        self.canvas.move(f'linegreen_{self.name}', 35,100)
        self.canvas.move(f'lineblue_{self.name}', 35,160)
        self.canvas.move(f'output_{self.name}', 325,75)
        self.canvas.move(f'output_text_{self.name}', 325,100)
    
# picker = Colorpicker(interface, canvas, x = 55, y = 200, bgcolor = 'grey')
# canvas.move('colorpicker', 20,0)