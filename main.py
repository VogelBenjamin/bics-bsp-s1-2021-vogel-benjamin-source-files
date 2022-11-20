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

num_lst = ["0","1","2","3","4","5","6","7","8","9"]

# counter for frames
frame_counter = 0

# boolean - if end = True the program terminates
end = False

# create an object to help track time
clock = pygame.time.Clock()

# dictionnary of all constants used during the simulation
sim_const = {"initial_sheep": 40,"initial_wolves": 10,"food_cap": 30,
             "food_respawn_time": 1,"number_cycles": 3,"sheep_speed": 2,
             "wolf_speed": 2,"sim_speed": 10,"search_radius": 1000,
             "cycle_duration":100,"special_attribute_prob":20}

# miscelaneous constants
PI = math.pi

# Screen Size
SIZE_X = 1400 
SIZE_Y = 800


# Decleration of functions
def modify_constants():
    
    print("Default values:")
    # Displays the names and values of the simulation constants
    for key,value in sim_const.items():
        print(f"{key}: {value}")
    

    while True:
        # Ask the user whether a change of constants is desired
        question = input("Do you want to change any constants?(0-no;1-yes): ")
        try:
            if question == "0":
                break
            elif question != "1":
                raise Exception("Invalid answer, please try again!")
        except Exception as error:
            print(error)
            continue


        # If change of constants is desired, the program asks what constant 
        # should be changed
        while True:
            #to_be_changed
            try:
                t_b_c = input("Which constant do you want to change?: ")
                if t_b_c not in sim_const:
                    raise Exception("Variable name not found! Try again!")
                n_v = input(f"Input value for {t_b_c}: ")
                for letter in n_v:
                    if (letter not in num_lst):
                        raise Exception(f"{n_v} is invalid input")
                    elif ("prob" in t_b_c and n_v > 100):
                        raise Exception(f"{n_v} is invalid input, value<=100")
                    
                sim_const[t_b_c] = int(n_v)
                break
            except Exception as error:
                print(error)


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
    takes in a dictionary of information and either creates a csv file if
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
    
    l = ["timestamp","cycle","num_sheep","num_of_huge_sheep","numb_wolves","num_of_speed_wolves","num_food"]

    for i in range(len(l)):
        file.write(f"{l[i]},")
    file.write(f"\n")

    for key,item in information.items():
        if key != "constants":
            file.write(f"{key},")
            for element in item:
                file.write(f"{element},")
            file.write("\n")
    file.write("\n\n")
    file.close()
    print("Document successfully created")

def add_information(info):
    '''
    adds a list of information to the sim_info disctionary
    key is delta time
    '''
    n_t = datetime.now()
    delta = (n_t - S_T)*sim_const["sim_speed"]
    sim_info[delta] = info

def distance(point_1,point_2):
    return math.sqrt((point_1.x-point_2.x)**2+(point_1.y-point_2.y)**2)


# Decleration of classes


class Environment:
    
    def __init__(self):
        self.wolves = []
        self.sheep = []
        self.food = []
        self.cycle_obj = Countdown(self)
    
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
            if s1.feed == True and s1.sex == "w":
                for s2 in remove_from_lst(self.sheep,s1):
                    if s2.sex == "m":
                        s1.mate(s2)
        
        for w1 in self.wolves:
            if w1.feed == True and w1.sex == "w":
                for w2 in remove_from_lst(self.wolves,w1):
                    if w2.sex == "m":
                        w1.mate(w2)

    def search_all(self):
        for s in self.sheep:
                for f in self.food:
                    s.search_target(f)

        for w in self.wolves:
            for s in self.sheep:
                w.search_target(s)

    # The following methodes add an instance of a class to this objects list 
    # corresponding to the class.

    def add_Wolf(self, x, y):
        if random.random() > sim_const["special_attribute_prob"]*0.005:
            w = Wolf(x,y,sim_const["wolf_speed"],self)
        else:
            w = Speed_wolf(x,y,sim_const["wolf_speed"],self)
        self.wolves.append(w)
    
    def add_Sheep(self, x, y):
        for i in range(random.randint(1,3)):
            if random.random() > sim_const["special_attribute_prob"]*0.01:
                s = Sheep(x,y,sim_const["sheep_speed"],self)
            else:
                s = Huge_sheep(x,y,sim_const["sheep_speed"],self)
            self.sheep.append(s)
    
    def add_Food(self):
        for i in range(5):
            if len(self.food) < sim_const["food_cap"]:
                f = Food(random.randint(0,SIZE_X), random.randint(0,SIZE_Y))
                self.food.append(f)

    def reset_target(self):
        for element in self.wolves + self.sheep:
            element.target = None
    
    # This methode spawns a new instance of an object if the attribute 
    # pregnant is true.
    def check_birth(self):
        for w in self.wolves:
            if w.pregnant:
                self.add_Wolf(w.x, w.y)
                w.pregnant = False

        for s in self.sheep:
            if s.pregnant:
                self.add_Sheep(s.x, s.y)
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
    def remove_from_lst(self, other):
        lst = []

        if isinstance(other, Food):
            lst = self.food
        elif isinstance(other, Wolf) or isinstance(other,Speed_wolf):
            lst = self.wolves
        elif isinstance(other, Sheep) or isinstance(other,Huge_sheep):
            lst = self.sheep

        lst.remove(other)
    
    # change feed attribute of all animals to False
    def make_hungry(self):
        for anim in self.sheep+self.wolves:
            anim.feed = False

    def end_of_cycle(self):
        self.check_birth()
        self.check_survival()
        self.make_hungry()
        
    
    
class Animal:
    
    def __init__(self, x, y, speed, e):
        self.x = x
        self.y = y 
        self.speed = speed
        self.direction = random.random()*2*PI # random angle in radians
        self.radius = 7
        self.sex = random.choice(["m","w"])

        self.feed = False
        self.pregnant = False
        self.special = False
        
        self.target = None
        self.e = e


    def draw(self):
        '''
        displays the object onto the pygame screen
        '''
        x = self.x
        y = self.y
        color = self.color

        pygame.draw.circle(screen, color, (x,y), self.radius)
        pygame.draw.circle(screen, Color("Black"), (x,y), self.radius, 2)

        if self.feed == True:
            pygame.draw.circle(screen, Color("blue"),(x,y),1)


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
            if d_x < 0 and d_y > 0:
                self.direction+=PI
            elif d_x < 0 and d_y < 0:
                self.direction+=PI
        except:
            if d_y >0:
                self.direction = PI/2
            elif d_y < 0:
                self.direction = -PI/2
            
        
    
    def check_collision(self, other, distance = 0):
        '''
        takes an object wiht coordinates as input
        checks if objects is colliding with another one
        '''
        s_x, s_y, s_r = self.x, self.y, self.radius
        o_x, o_y, o_r = other.x, other.y, other.radius
        if math.sqrt((s_x-o_x)**2+(s_y-o_y)**2)<=(s_r+o_r+distance):
            return True
        return False
    
    def mate(self, other):
        '''
        takes an object of the same class as input
        checks whether or not both objects' feed attribute is true, 
        if so puts pregnant attribute to true
        '''
        if (self.feed and other.feed and self.check_collision(other) and 
           self.sex != other.sex):
            self.pregnant = True

    def eat(self, other):
        '''
        takes as input a food object
        checks if it collides, if so food objects gets removed and this 
        objects feed attribute becomes true
        '''

        if (self.check_collision(other) and not self.feed and 
            not isinstance(other, Huge_sheep)):
            self.feed = True
            self.e.remove_from_lst(other)
            self.e.reset_target()
            return True
        return False 
    
    def search_target(self, other):
        s = self
        t = self.target
        if (self.check_collision(other, sim_const["search_radius"]) and 
            (t == None or distance(s,t)>distance(s,other))):

            if self.feed == False and isinstance(other,Food):
                # makes sure that an object is the target of maximum 3 
                # other objects
                counter = 0

                for anim in (environment.sheep):
                    if anim.target == other:
                        counter += 1
                    if counter > 3:
                        return
                self.target = other
            
            elif self.feed == True and other in environment.sheep:
                if other.sex != self.sex:

                    self.target = other
            
 
class Sheep(Animal):
    
    def __init__(self, x, y, speed, e):
        Animal.__init__(self, x, y, speed, e)
        self.color = Color("Yellow")


class Wolf(Animal):
    
    def __init__(self, x, y, speed, e):
        Animal.__init__(self, x, y, speed, e)
        self.color = Color("Gray")
    

class Huge_sheep(Animal):

    def __init__(self, x, y, speed, e):
        Animal.__init__(self, x, y, speed//2, e)
        self.color = Color("lightblue")
        self.special = True
        self.radius += 3
            

class Speed_wolf(Animal):

    def __init__(self, x, y, speed, e):
        Animal.__init__(self, x, y, speed*2, e)
        self.color = Color("violetred")
        self.food_count = 0
        self.special = True

    def eat(self,other):
        '''
        takes as input a food object 
        checks if it collides, if so food objects gets removed and this 
        objects feed attribute becomes true
        '''

        if (self.check_collision(other) and not self.feed and 
            not isinstance(other, Huge_sheep)):
            self.food_count += 1
            self.e.remove_from_lst(other)
            self.e.reset_target()
            if self.food_count >= 2:
                self.feed = True
            return True
        return False 
    
    
class Food:
    
    def __init__(self, x, y):
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

        pygame.draw.circle(screen, self.color, (x,y), self.radius)
        pygame.draw.circle(screen, Color("Black"), (x,y), self.radius, 1)

        


class Countdown:
    
    def __init__(self, e):
        self.x = SIZE_X *19 // 20
        self.y = SIZE_Y // 20
        self.completion = 0
        self.num_finished_cycles = 0
        self.environment = e
        self.text_box = TextBox( f"Cycle_num = {self.num_finished_cycles+1}")
    
    def draw(self):
        '''
        displays the object onto the pygame screen
        '''
        d_r = pygame.draw.rect
        s_x, s_y, s_c = self.x, self.y, self.completion
        d_r(screen, Color("Gray"), (s_x,s_y,SIZE_X//36,SIZE_Y*0.6))
        d_r(screen, Color("Purple"), (s_x,s_y,SIZE_X//36,SIZE_Y*0.6*s_c//100))
        self.text_box.display()
    
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
            self.environment.end_of_cycle()    
            self.text_box.change_txt(f"Cycle_num = {self.num_finished_cycles+1}")
            
            num_of_food = len(environment.food)
            num_of_n_wolves,num_of_speed_wolves = 0,0
            num_of_n_sheep,num_of_huge_sheep = 0,0
            for w in environment.wolves:
                if w.special == False:
                    num_of_n_wolves += 1
                else:
                    num_of_speed_wolves += 1
            for s in environment.sheep:
                if s.special == False:
                    num_of_n_sheep += 1
                else:
                    num_of_huge_sheep += 1
            num_of_cycle = environment.cycle_obj.num_finished_cycles

            add_information([num_of_cycle,num_of_n_sheep,num_of_huge_sheep,
                             num_of_n_wolves,num_of_speed_wolves,num_of_food])


class TextBox:
    
    def __init__(self, text, font=pygame.font.SysFont("Palatino",20)):
        self.x = SIZE_X *  13 // 14
        self.y = SIZE_Y * 2 // 3
        self.font = font
        self.text = font.render(text, True, "black")
    
    def display(self):
        '''
        displays text on pygame screen
        '''
        screen.blit(self.text, (self.x,self.y))
    
    def change_txt(self, txt):
        '''
        changes the text of the textbox
        '''
        self.text = self.font.render(txt, True, "black")

#asks the user if he wants to change ismulation constants
modify_constants()

# reference of time
S_T = datetime.now() #Start time

# Number of frames, per second. Incrementing FPS causes the simulation to 
# perform faster.
FPS = 60*sim_const["sim_speed"]

# dictionary that stores all occurences.
sim_info = {"constants": sim_const,}

# initialize a window or screen for display
screen = pygame.display.set_mode((SIZE_X,SIZE_Y))

#Create instances of Environment and class elements
environment = Environment()

# set the current window caption
pygame.display.set_caption("vogel.benjamin: BSP-S1")

for i in range(sim_const["initial_sheep"]):
    environment.add_Sheep(random.randint(0,SIZE_X), random.randint(0,SIZE_Y))

for i in range(sim_const["initial_wolves"]):
    environment.add_Wolf(random.randint(0,SIZE_X), random.randint(0,SIZE_Y))

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

    #functions called every x seconds
    if every_x_seconds(1):
        environment.change_dir_All()
        environment.add_Food()
        
    environment.move_All()

    #animal behaviour methods execution
    environment.eat_All()
    environment.check_mate_all()
    
    if every_x_seconds(sim_const["cycle_duration"]/(sim_const["sim_speed"]*100)):
        environment.cycle_obj.tick()

    #amount added to frame counter proportional to simulation speed.
    frame_counter += sim_const["sim_speed"]

    pygame.display.update()
    clock.tick(FPS)

    #check whether the simulation has ended
    if environment.cycle_obj.num_finished_cycles==sim_const["number_cycles"]:
        
        end = True

#stops all pygame functionallities
pygame.quit()

# asks the user whether he wants to create a csv/ add information to a csv about the simulation.
print("Simulation is done!")
while True:
    try:
        qt = int(input("Create csv file about the simulation?(0-no;1-yes): "))
        if qt:
            write_csv(sim_info)
        break
    except:
        print("invalid answer! Please try again!")
        continue

sys.exit()