from tkinter import *
# interface = Tk()
# interface.geometry("500x500")
# canvas = Canvas(width = 500, height = 500, bg = 'orange')
# canvas.pack()

class Colorpicker():
    def __init__(self, interface, canvas, x = 0, y = 0, bgcolor = 'grey'):
        self.graphics = []
        self.sliderdict = {
            'redslider': 0,
            'greenslider': 0,
            'blueslider': 0
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
        self.canvas.move('colorpicker', x,y)

        canvas.tag_bind('redslider', '<Enter>', lambda _: self.onhover('redslider'))
        canvas.tag_bind('greenslider', '<Enter>', lambda _: self.onhover('greenslider'))
        canvas.tag_bind('blueslider', '<Enter>', lambda _: self.onhover('blueslider'))

        canvas.tag_bind('redslider', '<Leave>', lambda _: self.unhover('redslider'))
        canvas.tag_bind('greenslider', '<Leave>', lambda _: self.unhover('greenslider'))
        canvas.tag_bind('blueslider', '<Leave>', lambda _: self.unhover('blueslider'))

        canvas.tag_bind('redslider', '<ButtonPress>', lambda _: self.onclick('redslider'))
        canvas.tag_bind('greenslider', '<ButtonPress>', lambda _: self.onclick('greenslider'))
        canvas.tag_bind('blueslider', '<ButtonPress>', lambda _: self.onclick('blueslider'))

        canvas.tag_bind('redslider', '<ButtonRelease>', lambda _: self.release('redslider'))
        canvas.tag_bind('greenslider', '<ButtonRelease>', lambda _: self.release('greenslider'))
        canvas.tag_bind('blueslider', '<ButtonRelease>', lambda _: self.release('blueslider'))

    def release(self,event):
        self.interface.unbind('<Motion>')
        self.interface.config(cursor="arrow")
    
    def rgb(self):
        return (self.sliderdict['redslider'], self.sliderdict['greenslider'], self.sliderdict['blueslider'])

    def onhover(self,event):
        self.canvas.itemconfig(event, fill='white')

    def unhover(self,event):
        self.canvas.itemconfig(event, fill='grey')
    
    def destroy(self):
        self.canvas.delete('colorpicker')

    def onclick(self,slider):
        self.anchor = self.canvas.coords(slider)[0]
        self.interface.bind('<Motion>', lambda event: self.controlslider(event,slider))
        self.canvas.itemconfig(slider, fill=slider.split("slider",1)[0])
        self.interface.config(cursor="none")
    
    def controlslider(self,event, button):
        self.canvas.itemconfig(button, fill=button.split("slider",1)[0])
        self.canvas.tag_raise(button)
        self.canvas.tag_raise(button.split('slider',1)[0]+'arrows')
        # if event.x > self.anchor:
        #     if self.sliderdict[button] == 255:
        #         return
        if (self.canvas.coords(button)[0] + (event.x - self.anchor) < (self.x+10)) or (self.canvas.coords(button)[0] + (event.x - self.anchor) > (self.x+265)):
            return
        self.sliderdict[button] += int((event.x - self.anchor))
        self.canvas.move(button, (event.x - self.anchor), 0)
        self.canvas.move(button.split('slider',1)[0]+'arrows', (event.x - self.anchor),0)
        # else:
        #     if self.sliderdict[button] == 0:
        #         return
        #     self.sliderdict[button] -= 1
        #     self.canvas.move(button, -1, 0)
        #     self.canvas.move(button.split('slider',1)[0]+'arrows', -1,0)
        self.anchor = event.x
        self.canvas.itemconfig('output_text', text=f'R: {self.sliderdict['redslider']}\nG: {self.sliderdict['greenslider']}\nB: {self.sliderdict['blueslider']}')
        self.hexcolor = '#%02x%02x%02x' % (self.sliderdict['redslider'], self.sliderdict['greenslider'], self.sliderdict['blueslider'])
        self.canvas.itemconfig('output', fill = self.hexcolor)

    def draw(self):
        self.canvas.create_rectangle(0,0,400,225, fill = self.bgcolor, tag = ('colorpicker', 'colorpickerbg'))

        self.canvas.create_rectangle(0,0,25,50, fill = 'grey', tag = ('colorpicker', 'redslider'))
        self.canvas.create_text(12.5,25,text=">>\n<<", tag = ('colorpicker', 'redarrows'), state = 'disabled')

        self.canvas.create_rectangle(0,0,25,50, fill = 'grey', tag = ('colorpicker', 'greenslider'))
        self.canvas.create_text(12.5,25,text=">>\n<<", tag = ('colorpicker', 'greenarrows'), state = 'disabled')

        self.canvas.create_rectangle(0,0,25,50, fill = 'grey', tag = ('colorpicker', 'blueslider'))
        self.canvas.create_text(12.5,25,text=">>\n<<", tag = ('colorpicker', 'bluearrows'), state = 'disabled')

        self.canvas.create_rectangle(0,0,255,10, fill = 'red', tag = ('colorpicker', 'linered'))

        self.canvas.create_rectangle(0,0,255,10, fill = 'green', tag = ('colorpicker', 'linegreen'))

        self.canvas.create_rectangle(0,0,255,10, fill = 'blue', tag = ('colorpicker', 'lineblue'))

        self.canvas.create_rectangle(0,0,50,50, fill = self.hexcolor, tag = ('colorpicker', 'output'))
        self.canvas.create_text(25,60,text=f'R: {self.sliderdict['redslider']}\nG: {self.sliderdict['greenslider']}\nB: {self.sliderdict['blueslider']}', 
                                tag = ('colorpicker', 'output_text'), font=("sans-serif",10))
    
    def initial_moveshapes(self):
        self.canvas.move('redslider', 10, 20)
        self.canvas.move('redarrows', 10,20)

        self.canvas.move('greenslider', 10, 80)
        self.canvas.move('greenarrows', 10, 80)

        self.canvas.move('blueslider', 10, 140)
        self.canvas.move('bluearrows', 10, 140)

        self.canvas.move('linered', 35,40)
        self.canvas.move('linegreen', 35,100)
        self.canvas.move('lineblue', 35,160)
        self.canvas.move('output', 325,75)
        self.canvas.move('output_text', 325,100)
    
# picker = Colorpicker(interface, canvas, x = 55, y = 200, bgcolor = 'grey')
# canvas.move('colorpicker', 20,0)