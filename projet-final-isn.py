import tkinter as tk
from tkinter.messagebox import showerror
from math import cos,sin,pi

shapes=([0,0,1,1], #Point
        [0,0,40,0,40,40,0,40], #Square
        [0,40,20,6,40,40], #Triangle
        [0,0,40,0,40,20,0,20], #Platform
        [0,0,20,34,40,0], #Reverse Triangle
        [0,40,5,10,10,40,15,0,20,30,25,0,30,40,35,10,40,40], #Trap
        [-15,0,15,0,15,-30,-15,-30]) #cube

        
def rotation(points,center=(0,0),angle=0): #angle radian
    xo,yo=center
    rotate_points=tuple()
    for i in range(pair(points)):
        x,y=points[2*i],points[2*i+1]
        x1,y1=x-xo,y-yo
        rotate_points+=(int(x1*cos(angle)+y1*sin(angle)+xo),int(y1*cos(angle)-x1*sin(angle)+yo))
    return rotate_points

pair=lambda points:len(points)//2
absciss=lambda points:[points[2*i] for i in range(pair(points))]
ordinate=lambda points:[points[2*i+1] for i in range(pair(points))]


def shape(shape_properties):
    n_shape,yo,xo=shape_properties
    points=shapes[n_shape]
    x=absciss(points)
    y=ordinate(points)
    result=tuple()
    for i in range(pair(points)):
        result+=(x[i]+xo,y[i]+yo)
    return result
    
def decode(data):
    data+="\n0-0"*15
    texture=list()
    lines=data.split("\n")
    last_instructions=list()
    maximum=0
    for line in lines:
        instructions=line.split("+")
        l=len(instructions)
        last_instructions.append(l)
        if len(last_instructions)>19:
            del last_instructions[0]
        maximum=max(maximum,sum(last_instructions))
        for i in range(l):
            instruction=instructions[i].split("-")
            if int(instruction[0]):
                texture.append((int(instruction[0]),int(instruction[1]),760+i*step))
            else:
                texture.append((0,0,0))
        for i in range(10-l):
            texture.append((0,0,0))
    return texture,maximum
    
class Display:
    def __init__(self,canvas):
        self.canvas=canvas

    def create(self,instruction):
        self.canvas.create_polygon(shape(instruction),fill="#2008F6",outline="white",width=2)

    def init(self,nb):
        for i in range(nb):
            self.canvas.create_polygon(0,0,1,1,fill="#2008F6",outline="white",width=2)

    def replace(self,instruction,item,tag):
        self.canvas.coords(item,shape(instruction))
        self.canvas.itemconfig(item,tag=tag)

    def Get_item_sensor(self,item,x1,y1,x2,y2):
        items=self.canvas.find_overlapping(x1,y1,x2,y2)
        if items:
            return items[-1]*(items[-1]!=item)
        else:
            return 0

def Loading():
    #decode map
    try:
        file=open("map.txt","r")
        data=file.read()
        file.close()
        data,max_shape=decode(data)
        Game(data,max_shape)
    except ValueError:
        showerror("Chamalow Dash","An error occured during loading the map.")
    except FileNotFoundError:
        showerror("Chamalow Dash","map.txt not found.")

def clean(parent):
    for i in parent.winfo_children():
        i.destroy()

def percent(counter,lenght):
    return str(int(counter/lenght*100))+"%"

########################################################################################################
class Game:
    def __init__(self,data,max_shape):
        clean(root)
        self.height={1:0,2:400}
        self.data=data        
        self.lenght=len(self.data)-1
        self.canvas=tk.Canvas(root,width=800,height=450,bg="#7B08C4")
        self.canvas.pack()
        self.cube=self.canvas.create_polygon(shape((6,200,200)),fill=color[0],outline=color[1],width=5)
        self.canvas.create_rectangle(0,400,800,450,fill="grey",width=3,outline="white")
        self.canvas.create_text(400,430,tag="text",font=("Arial","25"),fill="white")
        self.display=Display(self.canvas)
        self.display.init(max_shape)
        self.counter=0
        self.lenght_jmp=25
        #Movement
        self.vy=0
        self.y=200
        self.jmp=False
        self.last_jmp=0
        self.disable_jmp=0
        root.bind("<space>",self.jump)
        #initialisation
        self.append()

    def append(self):
        self.canvas.coords(self.cube,rotation(shape((6,self.y-4,200)),center=(200,self.y-19),angle=-self.disable_jmp/25*pi))
        destroy=self.canvas.find_overlapping(40,0,40,397) #return id of shapes which are on the line (d):x=40 
        if destroy:
            self.display.replace((0,0,0),destroy[0],'')
        available=self.canvas.find_overlapping(0,0,0,0)
        instruction=self.data[self.counter]
        if instruction[0] in [2,4,5]:
            self.height[available[0]]=450
        else:
            self.height[available[0]]=instruction[1]


        right_sensor=self.display.Get_item_sensor(self.cube,215,self.y-2,215,self.y-30)
        top_sensor=self.display.Get_item_sensor(self.cube,215,self.y-30,215,self.y-30)
        left_sensor=self.display.Get_item_sensor(self.cube,185,self.y-30,185,self.y-2)
        bottom_sensor=self.display.Get_item_sensor(self.cube,185,self.y,215,self.y)
        
        self.y-=int((3/5)*self.vy)
        self.vy-=1
       
        next_sensor=self.display.Get_item_sensor(self.cube,185,self.y,215,self.y)
        
        if next_sensor:
            self.y=self.height[next_sensor]
            self.vy=0

        if bottom_sensor and self.jmp:
            self.jmp=False
            self.last_jmp=self.counter
            self.vy=20 # Taille du saut
        
        self.disable_jmp=(self.counter-self.last_jmp)*(self.counter-self.last_jmp<self.lenght_jmp)
        death_sensor=right_sensor or top_sensor or left_sensor or self.y==450

        self.display.replace(instruction,available[0],bool(instruction[0])*"map")
        self.canvas.itemconfig("text",text=percent(self.counter,self.lenght))
        self.canvas.move("map",step,0)
        self.counter+=1

        
        if self.counter!=self.lenght and not death_sensor:
            root.after(10,self.append)
        else:
            Score(self.counter,self.lenght)

    def jump(self,event):
        #Si on se trouve au delà du milieu du saut, alors le saut est autorisé
        if not self.disable_jmp:
            self.jmp=True

####################################################################################################
class Settings:
    def __init__(self):
        clean(root)
        
        self.canvas=tk.Canvas(root,width=400,height=200)
        self.canvas.pack(side=tk.LEFT)

        self.canvas2=tk.Canvas(root,width=200,height=200)
        self.canvas2.pack(side=tk.RIGHT)
        self.canvas2.create_rectangle(50,50,150,150,fill=color[0],outline=color[1],width=12)
        
        tk.Label(self.canvas,text="fill").grid(row=0,column=0)
        cube_color=["#FBCEC4","#C1D9FB","#C6FBC1","#C1D9FB","#D9C1FB"]
        cube_color_2=["#F79C87","#83F6DB","#8BF683","#83B1F6","#B583F6"]
        #Listbox fill
        self.listbox1=tk.Listbox(self.canvas, bg="#B68A48", activestyle="underline", relief="sunken",font=("arial", 15),height=5)
        self.listbox1.grid(row=1,column=0)
        for i in cube_color:
            self.listbox1.insert(tk.END,i)
            self.listbox1.itemconfig(tk.END,bg=i)
        #End
        tk.Label(self.canvas,text="outline").grid(row=0,column=1)
        #Listbox outline
        self.listbox2=tk.Listbox(self.canvas, bg="#B68A48", activestyle="underline", relief="sunken",font=("arial", 15),height=5)
        self.listbox2.grid(row=1,column=1)
        for i in cube_color_2:
            self.listbox2.insert(tk.END,i)
            self.listbox2.itemconfig(tk.END,bg=i)
        #End
        self.listbox1.bind("<Double-Button-1>",lambda event:self.canvas2.itemconfig(1,fill=self.listbox1.get(self.listbox1.curselection())))
        self.listbox2.bind("<Double-Button-1>",lambda event:self.canvas2.itemconfig(1,outline=self.listbox2.get(self.listbox2.curselection())))    
        tk.Button(self.canvas, text="Cancel", bg="red", relief="sunken",font=("Arial",15),fg="#FEFEFE",command=Menu).grid(row=3,column=0)
        tk.Button(self.canvas, text="Save", bg="green", command=self.save_exit, relief="sunken",font=("Arial",15),fg="#FEFEFE").grid(row=3,column=1)
        
    def save_exit(self):
        global color
        fill=self.canvas2.itemcget(1,"fill")
        outline=self.canvas2.itemcget(1,"outline")
        color=fill,outline
        Menu()

#######################################################################################################        
def Score(counter,lenght):
    clean(root)
    score=percent(counter,lenght)
    canvas=tk.Canvas(root,width=800,height=450,bg='Black')
    canvas.pack()
    if score=="100%":
        message="You Win!"
        color='#C19610'
    else:
        message="You Lose!"
        color='#F41010'
            
    canvas.create_text(400,100,text=message,font=("fixedsys","60"),fill=color)
    canvas.create_text(400,200,text="Your Score:"+score,font=("fixedsys","30"),fill="white")
    canvas.bind("<space>",None)
    button=tk.Button(canvas,text="Retry",fg=color,font=("fixedsys","20"),bg='#0B0B0C',activebackground=color,activeforeground="black",command=Loading)
    button.place(x=275,y=300)
    button.focus_set()
    tk.Button(canvas,text="Menu",fg=color,font=("fixedsys","20"),bg='#0B0B0C',activebackground=color,activeforeground="black",command=Menu).place(x=425,y=300)       
    
#########################################################################################################
def Menu():
    clean(root)
    canvas=tk.Canvas(root, width=800, height=400, borderwidth=-2,bg="#7B08C4")
    canvas.pack(side=tk.RIGHT)
    display=Display(canvas)
        
    texture=[(1, 280, 0), (1, 280, 40), (1, 280, 80), (1, 280, 120), (1, 280, 160), (1, 280, 200), (1, 280, 240), (1, 280, 280), (1, 280, 320), (1, 280, 360), (1, 280, 400), (1, 280, 440), (1, 280, 480), (1, 280, 520), (1, 280, 560), (1, 280, 600), (1, 280, 640), (1, 280, 680), (1, 280, 720), (1, 280, 760), (1, 240, 0), (1, 200, 0), (1, 160, 0), (2, 120, 0), (1, 0, 0), (1, 40, 0), (1, 240, 40), (1, 200, 40), (1, 160, 40), (2, 120, 40), (1, 0, 40), (1, 40, 40), (5, 240, 80), (5, 240, 120), (1, 240, 160), (1, 240, 200), (1, 240, 240), (1, 240, 280), (1, 200, 160), (4, 0, 320), (4, 0, 440), (4, 0, 560), (4, 0, 680), (3, 240, 520), (3, 220, 600), (3, 200, 680), (1, 240, 720), (1, 200, 720), (4, 120, 720), (1, 80, 720), (1, 40, 720), (1, 0, 720), (1, 240, 760), (1, 200, 760), (4, 120, 760), (1, 80, 760), (1, 40, 760), (1, 0, 760)]
    for i in texture:
        display.create(i)
    canvas.create_text(400,100,text="Chamalow Dash",font=("fixedsys","100"),fill="#FBCEC4")
    tk.Button(root,text="Play",fg="white",bg="green",command=Loading,font=("Arial",15)).place(x=0,y=321,width=267,height=90)
    tk.Button(root, text="Setting", bg="brown", command=Settings, relief="sunken",font=("Arial",15),fg="#FEFEFE").place(x=267, y=321, width=267, heigh=90)       
    tk.Button(root, text="Quit", bg="red", command=root.destroy, relief="sunken",font=("Arial",15),fg="#FEFEFE").place(x=534, y=321, width=267, heigh=90)
                
##########################################################################################################
#Main Program
step=-4
root=tk.Tk()
root.title("Chamalow Dash")
root.resizable(False,False)
color=["#C0C0C0","#C19610"]
Menu()
root.mainloop()

