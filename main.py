# Import python modules
import sys 
import math 
import random
from datetime import datetime

# Import 3rd party python modules
import pygame
from pygame.locals import*

# initialize all imported pygame modules
pygame.init()

# Decleration of variables

# counter for frames
frame_counter = 0

# boolean - if end = True the program terminates
end = False

# create an object to help track time
clock = pygame.time.Clock()

# dictionnary of all constants used during the simulation
sim_const = {"initial_sheep": 5,"initial_wolves": 0,"food_cap": 5,
             "food_respawn_time": 2,"number_cycles": 3,"sheep_speed": 2,
             "wolf_speed": 2,"simulation_speed": 10}

# miscelaneous constants
PI = math.pi

# Screen Size
SIZE_X = 1400 
SIZE_Y = 800




# Decleration of functions
def ask_constant():
    
    print("Default values:")
    # Displays the names and values of the simulation constants
    for key,value in sim_const.items():
        print(f"{key}: {value}")
    

    while True:
        # Ask the user whether a change of constants is desired
        question = input("Do you want to change any constants?(0-no;1-yes): ")
        if question == "0":
            break
        elif question != "1":
            print("Invalid answer, please try again!")
            continue

        # If change of constants is desired, the program asks what constant 
        # should be changed
        while True:
            #to_be_changed
            t_b_c = input("Which constant do you want to change?: ")
            if t_b_c not in sim_const:
                print("Variable name not found! Try again!")
                continue
            
            try:
                n_v = int(input(f"Input value for {t_b_c}: "))
                sim_const[t_b_c] = n_v
                
            except:
                print(f"Invalid value for {t_b_c}")
                continue


# returns True for every x seconds
def every_x_seconds(x):
    '''
    returns true every time x seconds has passed
    '''
    if frame_counter%(x*FPS) == 0:
        return True
    return False

                  
def remove_from_lst(l,r_l):
    '''
    takes list as input
    returns the same list without the elements inside the parameter
    '''
    n_l = l.copy()
    n_l.remove(r_l)
    return n_l


def write_csv(information):
    '''
    takes in a dictionary of inforamtion and either creates a csv file if
    there does not already exist one or appends information into an existing
    csv
    '''
    file = open("animal_sim_csv.txt","a")

    file.write(str(S_T)+"\n")

    for key in information["constants"].keys():
        file.write(f"{key},")

    file.write("\n")

    for value in information["constants"].values():
        file.write(f"{value},")

    file.write("\n")
    
    l = ["timestamp","cycle","num_sheep","numb_wolves","num_food"]

    file.write(f"{l[0]},{l[1]},{l[2]},{l[3]},{l[4]},\n")

    for key,item in information.items():
        if key != "constants":
            file.write(f"{key},")
            for element in item:
                file.write(f"{element},")
            file.write("\n")
    file.write("\n\n")
    file.close()

def add_information(info):
    '''
    adds a list of information to the sim_info disctionary
    key is delta time
    '''
    n_t = datetime.now()
    delta = (n_t - S_T)*sim_const["simulation_speed"]
    sim_info[delta] = info

def distance(point_1,point_2):
    return math.sqrt((point_1.x-point_2.x)**2+(point_1.y-point_2.y)**2)


# Decleration of classes


class Environment:
    
    def __init__(self,cycle_duration = 100):
        self.wolves = []
        self.sheep = []
        self.food = []
        self.cycle_obj = Countdown(self)
        self.cycle_frame_counter = sim_const["number_cycles"]
        self.cycle_duration = cycle_duration
    
    # The following methodes call the methodes of the objects Wolf and Sheep 
    # contained in this objects lists.

    def draw_All(self):
        for w in self.wolves:
            w.draw()

        for s in self.sheep:
            s.draw()

        for f in self.food:
            f.draw()

        self.cycle_obj.draw()
    
    def move_All(self):
        for w in self.wolves:
            w.move()

        for s in self.sheep:
            s.move()
    
    def change_dir_All(self):
        for w in self.wolves:
            if w.target == None:
                w.change_dir_random()
            else:
                w.change_dir_target()

        for s in self.sheep:
            if s.target == None:
                s.change_dir_random()
            else:
                s.change_dir_target()
    
    def eat_All(self):
        for s in self.sheep:
            for f in self.food:
                s.eat(f)

        for w in self.wolves:
            for s in self.sheep:
                w.eat(s)

    def check_mate_all(self):
        for s1 in self.sheep:
            if s1.feed == True:
                for s2 in remove_from_lst(self.sheep,s1):
                    s1.mate(s2)
        
        for w1 in self.wolves:
            if w1.feed == True:
                for w2 in remove_from_lst(self.wolves,w1):
                    w1.mate(w2)

    def search_all(self):
        for s in self.sheep:
                for f in self.food:
                    s.search_food(f)

        for w in self.wolves:
            for s in self.sheep:
                w.search_food(s)

    # The following methodes add an instance of a class to this objects list 
    # corresponding to the class.

    def add_Wolf(self, x, y):
        w = Wolf(x,y,sim_const["wolf_speed"],self)
        self.wolves.append(w)
    
    def add_Sheep(self, x, y):
        s = Sheep(x,y,sim_const["sheep_speed"],self)
        self.sheep.append(s)
    
    def add_Food(self):
        if len(self.food) < sim_const["food_cap"]:
            f = Food(random.randint(0,SIZE_X),random.randint(0,SIZE_Y))
            self.food.append(f)

    def reset_target(self):
        for element in self.wolves + self.sheep:
            element.target = None
    
    # This methode spawns a new instance of an object if the attribute 
    # pregnant is true.
    def check_birth(self):
        for w in self.wolves:
            if w.pregnant:
                self.add_Wolf(w.x,w.y)
                w.pregnant = False

        for s in self.sheep:
            if s.pregnant:
                for i in range(random.randint(1,4)):
                    self.add_Sheep(s.x,s.y)
                s.pregnant = False
    
    # checks whether animals have found food, if not --> remove from list

    def check_survival(self):
        for w in self.wolves:
            if w.feed == False:
                self.remove_from_lst(w)
        for s in self.sheep:
            if s.feed == False:
                self.remove_from_lst(s)

    # checks the class of an object and removes it from corresponding list
    def remove_from_lst(self,other):
        lst = []

        if isinstance(other,Food):
            lst = self.food
        elif isinstance(other,Wolf):
            lst = self.wolves
        elif isinstance(other,Sheep):
            lst = self.sheep

        lst.remove(other)
    
    # change feed attribute of all animals to False
    def make_hungry(self):
        for anim in self.sheep+self.wolves:
            anim.feed = False

    def end_of_cycle_functions(self):
        self.check_birth()
        self.make_hungry()
        self.check_survival()
    
    


class Animal:
    
    def __init__(self,x,y,speed,e):
        self.x = x
        self.y = y 
        self.speed = speed
        self.direction = random.random()*2*PI # random angle in radians
        self.radius = 10

        self.feed = False
        self.pregnant = False
        
        self.target = None
        self.e = e
        

    def move(self):
        '''
        Moves the object 
        '''
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        if self.x-self.radius > SIZE_X:
            self.x = 0
        elif self.x+self.radius < 0:
            self.x = SIZE_X 
        if self.y-self.radius > SIZE_Y:
            self.y = 0
        elif self.y+self.radius < 0:
            self.y = SIZE_Y  
    
    def change_dir_random(self):
        '''
        changes direction of movement of the object by a value 
        between [-PI/2,PI/2]
        '''
        random_degree = random.choice([-1,1])*random.random()*0.5*PI
        self.direction += random_degree
        
    def change_dir_target(self):
        other = self.target
        dist = distance(self,other)
        d_x = (other.x-self.x)/dist
        d_y = (other.y-self.y)/dist
        try:
            self.direction = math.atan(d_y/d_x)
        except:
            if d_y >0:
                self.direction = PI/2
            elif d_y < 0:
                self.direction = -PI/2
            return True
        if d_x < 0 and d_y > 0:
            self.direction+=PI
        elif d_x < 0 and d_y < 0:
            self.direction+=PI
    
    def check_collision(self,other,distance = 0):
        '''
        takes an object wiht coordinates as input
        checks if objects is colliding with another one
        '''
        s_x, s_y, s_r = self.x, self.y, self.radius
        o_x, o_y, o_r = other.x, other.y, other.radius
        if math.sqrt((s_x-o_x)**2+(s_y-o_y)**2)<=(s_r+o_r+distance):
            return True
        return False
    
    def mate(self,other):
        '''
        takes an object of the same class as input
        checks whether or not both objects' feed attribute is true, 
        if so puts pregnant attribute to true
        '''
        if self.feed and other.feed and self.check_collision(other):
            self.pregnant = True

    def eat(self,other):
        '''
        takes as input a food object
        checks if it collides, if so food objects gets removed and this 
        objects feed attribute becomes true
        '''

        if self.check_collision(other) and not self.feed:
            self.feed = True
            self.e.remove_from_lst(other)
            self.e.reset_target()
            return True
        return False 
    
    def search_food(self,other):
        if self.check_collision(other,50) and self.target == None and self.feed == False:
            
            self.target = other
            

 
class Sheep(Animal):
    
    def __init__(self,x,y,speed,e):
        Animal.__init__(self,x,y,speed,e)
        self.color = Color("Yellow")
    
    def draw(self):
        '''
        displays the object onto the pygame screen
        '''
        x = self.x
        y = self.y
        color = self.color
        
        pygame.draw.circle(screen,color,(x,y),self.radius)
        pygame.draw.circle(screen,Color("Black"),(x,y),self.radius,2)


class Wolf(Animal):
    
    def __init__(self,x,y,speed,e):
        Animal.__init__(self,x,y,speed,e)
        self.color = Color("Gray")
    
    def draw(self):
        '''
        displays the object onto the pygame screen
        '''
        x = self.x
        y = self.y
        color = self.color

        pygame.draw.circle(screen,color,(x,y),self.radius)
        pygame.draw.circle(screen,Color("Black"),(x,y),self.radius,2)
    
    


class Food:
    
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.color = Color("Red")
        self.radius = 6
    
    def draw(self):
        '''
        displays the object onto the pygame screen
        '''
        x = self.x
        y = self.y

        pygame.draw.circle(screen,self.color,(x,y),self.radius)
        pygame.draw.circle(screen,Color("Black"),(x,y),self.radius,1)


class Countdown:
    
    def __init__(self,e):
        self.x = SIZE_X *19 // 20
        self.y = SIZE_Y // 20
        self.completion = 0
        self.num_finished_cycles = 0
        self.environment = e
        self.text_box = TextBox(self.x, abs(self.y-SIZE_Y),"Cycle")
    
    def draw(self):
        '''
        displays the object onto the pygame screen
        '''
        d_r = pygame.draw.rect
        s_x, s_y, s_c = self.x, self.y, self.completion
        d_r(screen,Color("Gray"),(s_x,s_y,SIZE_X//40,SIZE_Y*0.6))
        d_r(screen,Color("Purple"),(s_x,s_y,SIZE_X//40,SIZE_Y*0.6*s_c//100))
    
    def tick(self):
        '''
        increments completion by 1%
        if completion rate is 100%: increment of finsihed cycles, call of the 
        environment methodes check_birth, make_hungry, check_survival and rest 
        to 0%
        '''
        
        self.completion += 1
        if self.completion == 100:
            self.completion = 0
            self.num_finished_cycles += 1
            self.environment.end_of_cycle_functions()    
            
            n_c = sim_const["number_cycles"]
            
            num_of_food = len(environment.food)
            num_of_wolves = len(environment.wolves)
            num_of_sheep = len(environment.sheep)
            num_of_cycle = environment.cycle_obj.num_finished_cycles
            add_information([num_of_cycle,num_of_sheep,num_of_wolves,num_of_food])


class TextBox:
    
    def __init__(self,x,y,text,font=pygame.font.SysFont("Palatino",30)):
        self.x = x
        self.y = y 
        self.font = font
        self.text = font.render(text,True,"black")
    
    def display(self):
        '''
        displays text on pygame screen
        '''
        screen.blit(self.text,(self.x,self.y))
    
    def change_txt(self,txt):
        '''
        changes the text of the textbox
        '''
        self.text = self.font.render(txt,True,"black")


ask_constant()

# reference of time
S_T = datetime.now() #Start time

# Number of frames, per second. Incrementing FPS causes the simulation to 
# perform faster.
FPS = 60*sim_const["simulation_speed"]

# dictionary that stores all occurences.
sim_info = {"constants": sim_const,}

#Create instances of Environment and class elements
environment = Environment(sim_const["number_cycles"])

# initialize a window or screen for display
screen = pygame.display.set_mode((SIZE_X,SIZE_Y))

# set the current window caption
pygame.display.set_caption("vogel.benjamin: BSP-1")

for i in range(sim_const["initial_sheep"]):
    environment.add_Sheep(random.randint(0,SIZE_X),random.randint(0,SIZE_Y))

for i in range(sim_const["initial_wolves"]):
    environment.add_Wolf(random.randint(0,SIZE_X),random.randint(0,SIZE_Y))

for i in range(sim_const["food_cap"]):
    environment.add_Food()


# Visualisation and computation loop
while not end:
    
    # ends loop when the user closes the window
    for event in pygame.event.get():
        if event.type == QUIT:
            end = True
    
    #clear screen
    screen.fill("Green")

    #modify position of elements and draw them
    environment.draw_All()
    environment.search_all()
    if every_x_seconds(1):
        environment.change_dir_All()
        
    environment.move_All()
    environment.eat_All()
    environment.check_mate_all()
    
    #functions called every x seconds
    if every_x_seconds(1):
        environment.add_Food()

    if every_x_seconds(environment.cycle_duration*sim_const["simulation_speed"]/100):
        environment.cycle_obj.tick()

    frame_counter += sim_const["simulation_speed"]

    pygame.display.update()
    clock.tick(FPS)

    if environment.cycle_obj.num_finished_cycles == sim_const["number_cycles"]:
        
        end = True

#stops all pygame functionallities
pygame.quit()

print("Simulation is done!")
qt = int(input("Create csv file about the simulation?(0-no;1-yes): "))
if qt:
    write_csv(sim_info)

sys.exit()