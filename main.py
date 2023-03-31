'''
Created on Mar 10, 2023

@author: hayam
'''

#imports
from board import boards
import pygame
import math
import copy
#end imports

pygame.init()

#variables
WIDTH = 900
HEIGHT = 950

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
lvl = copy.deepcopy(boards)
color = 'maroon'
PI = math.pi

'PICTURE IMPORTS:'
player_pics = []
for i in range(1, 5):
    player_pics.append(pygame.transform.scale(pygame.image.load(f'assets/player_pics/{i}.png'), (45, 45)))
m0_pic = pygame.transform.scale(pygame.image.load(f'assets/monster_pics/1.png'), (45, 45))
m1_pic = pygame.transform.scale(pygame.image.load(f'assets/monster_pics/2.png'), (45, 45))
m2_pic = pygame.transform.scale(pygame.image.load(f'assets/monster_pics/3.png'), (45, 45))
m3_pic = pygame.transform.scale(pygame.image.load(f'assets/monster_pics/4.png'), (45, 45))
powered_up_monster_pic = pygame.transform.scale(pygame.image.load(f'assets/monster_pics/powerup.png'), (45, 45))
dead_monster_pic = pygame.transform.scale(pygame.image.load(f'assets/monster_pics/dead.png'), (45, 45))

#player coordinates
player_X = 450
player_Y = 663
#player direction
dir = 0

#coordinates and direction of monsters
m0_x = 56
m0_y = 58
m0_dir = 0
m2_x = 440
m2_y = 388
m2_dir = 2
m1_x = 440
m1_y = 438
m1_dir = 2
m3_x = 440
m3_y = 438
m3_dir = 2

#for the wait timer in the while loop
counter = 0
#for power up animation points
flash = False

#right, left, up, down
valid_turns = [False, False, False, False]
dir_command = 0
player_speed = 2
score = 0

power_up = False
power_up_counter = 0


#to keep track of which monster died
dead_monsters = [False, False, False, False]
#monster targets
targets = [(player_X, player_Y), (player_X, player_Y), (player_X, player_Y), (player_X, player_Y)]

#are monster dead
m0_dead = False
m2_dead = False
m3_dead = False
m1_dead = False

#are the monsters in the respawn box (in the box, with the door)
m0_box = False
m2_box = False
m3_box = False
m1_box = False

#are the monster moving
moving = False

monsters_speeds = [2, 3, 1, 2]

#for the wait timer in the while loop
startup_counter = 0
lives = 3

gameOver = False
gameWon = False
#end variables


#CLASS FOR MONSTERS
#THIS IS BEFORE THE FUNCTIONS BC WE WILL BE USING THIS CLASS LATER ON SO KEEP IT HERE DONT MOVE IT SOMEWHERE ELSE
class Monster:
    #methods:
    'this method is defining all the variables that we will use in this class'
    #each monster has an x and y coordinate, a target, speed, a picture, direction, boolean if theyre dead or not, boolean if theyre in the box or not, and an identifying number.
    def __init__(self, x, y, target, speed, pic, dir, dead, box, num):
        #defining the coordinated of the monster
        self.x_coord = x
        self.y_coord = y
        #same idea as player center just to make sure the monster is tracked accuratly
        self.center_X = self.x_coord + 22
        self.center_Y = self.y_coord + 22
        
        self.target = target
        self.speed = speed
        self.pic = pic
        self.dir = dir
        self.dead = dead
        self.inside_box = box
        self.num = num
        #every single frame, we have to check collision and if theyre inside the box so we define these variables
        #same idea as the player, can the ghost turn? is the monster inside the box?
        self.turns, self.inside_box = self.collision_tracker()
        #outline of the collision box or the box that the monster occupies, we need this for when the player collides with the monster 
        self.rect = self.outline()
        
        

    'drawing the outline of the monster box'
    def outline(self):
        #either the monster is normal version, when the player eats the powerup, or when they are dead
        
        #if the monster is not powered up and not dead 
        #OR the monster number __ was eaten and was not dead and was powered up
        
        if (not power_up and not self.dead) or (dead_monsters[self.num] and power_up and not self.dead):
            screen.blit(self.pic, (self.x_coord, self.y_coord))
        #so the monster is not dead then of course its not in dead_monsters but keep this it doesnt matte
        elif power_up and not dead_monsters[self.num] and not self.dead:
            screen.blit(powered_up_monster_pic, (self.x_coord, self.y_coord))
        #OTHERWISE, there is no other scenario in which the monster would not be dead
        else:
            screen.blit(dead_monster_pic, (self.x_coord, self.y_coord))
        #defining the outline of the rectangle, we're not drawing an actual rectangle
        Monster_rect = pygame.rect.Rect((self.center_X - 18, self.center_Y - 18), (36, 36))
        return Monster_rect

    'monster movement function'
    def collision_tracker(self):
        #right,left,up,down
        row = ((HEIGHT - 50) // 32) #x coordinate
        col = (WIDTH // 30) #y coordinate
        pad = 15 #padding
        
        self.turns = [False, False, False, False]
        
        #collision is x and y +/- padding
        if 0 < self.center_X // 30 < 29:
            if lvl[(self.center_Y - pad) // row][self.center_X // col] == 9:
                self.turns[2] = True
            if lvl[self.center_Y // row][(self.center_X - pad) // col] < 3 \
                    or (lvl[self.center_Y // row][(self.center_X - pad) // col] == 9 and (
                    self.inside_box or self.dead)):
                self.turns[1] = True
            if lvl[self.center_Y // row][(self.center_X + pad) // col] < 3 \
                    or (lvl[self.center_Y // row][(self.center_X + pad) // col] == 9 and (
                    self.inside_box or self.dead)):
                self.turns[0] = True
            if lvl[(self.center_Y + pad) // row][self.center_X // col] < 3 \
                    or (lvl[(self.center_Y + pad) // row][self.center_X // col] == 9 and (
                    self.inside_box or self.dead)):
                self.turns[3] = True
            if lvl[(self.center_Y - pad) // row][self.center_X // col] < 3 \
                    or (lvl[(self.center_Y - pad) // row][self.center_X // col] == 9 and (
                    self.inside_box or self.dead)):
                self.turns[2] = True


            if self.dir == 2 or self.dir == 3:
                if 12 <= self.center_X % col <= 18:
                    if lvl[(self.center_Y + pad) // row][self.center_X // col] < 3 \
                            or (lvl[(self.center_Y + pad) // row][self.center_X // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[3] = True
                    if lvl[(self.center_Y - pad) // row][self.center_X // col] < 3 \
                            or (lvl[(self.center_Y - pad) // row][self.center_X // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_Y % row <= 18:
                    if lvl[self.center_Y // row][(self.center_X - col) // col] < 3 \
                            or (lvl[self.center_Y // row][(self.center_X - col) // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[1] = True
                    if lvl[self.center_Y // row][(self.center_X + col) // col] < 3 \
                            or (lvl[self.center_Y // row][(self.center_X + col) // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[0] = True


            if self.dir == 0 or self.dir == 1:
                if 12 <= self.center_X % col <= 18:
                    if lvl[(self.center_Y + pad) // row][self.center_X // col] < 3 \
                            or (lvl[(self.center_Y + pad) // row][self.center_X // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[3] = True
                    if lvl[(self.center_Y - pad) // row][self.center_X // col] < 3 \
                            or (lvl[(self.center_Y - pad) // row][self.center_X // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_Y % row <= 18:
                    if lvl[self.center_Y // row][(self.center_X - pad) // col] < 3 \
                            or (lvl[self.center_Y // row][(self.center_X - pad) // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[1] = True
                    if lvl[self.center_Y // row][(self.center_X + pad) // col] < 3 \
                            or (lvl[self.center_Y // row][(self.center_X + pad) // col] == 9 and (
                            self.inside_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_coord < 550 and 370 < self.y_coord < 480:
            self.inside_box = True
        else:
            self.inside_box = False
        return self.turns, self.inside_box


    def move_m3(self):
        #right, left, up, down
        if self.dir == 0:
            if self.target[0] > self.x_coord and self.turns[0]:
                self.x_coord += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                if self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                else:
                    self.x_coord += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.dir = 3
            elif self.target[0] < self.x_coord and self.turns[1]:
                self.x_coord -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                if self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                else:
                    self.x_coord -= self.speed
        elif self.dir == 2:
            if self.target[0] < self.x_coord and self.turns[1]:
                self.dir = 1
                self.x_coord -= self.speed
            elif self.target[1] < self.y_coord and self.turns[2]:
                self.dir = 2
                self.y_coord -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                else:
                    self.y_coord -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.y_coord += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                else:
                    self.y_coord += self.speed
        if self.x_coord < -30:
            self.x_coord = 900
        elif self.x_coord > 900:
            self.x_coord - 30
        return self.x_coord, self.y_coord, self.dir

    #initially,all monsters move to the player
    #movement is following the logic of the player movement
    
    def move_m0(self):
        #right, left, up, down
        if self.dir == 0:
            if self.target[0] > self.x_coord and self.turns[0]:
                self.x_coord += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
            elif self.turns[0]:
                self.x_coord += self.speed
        elif self.dir == 1:
            if self.target[0] < self.x_coord and self.turns[1]:
                self.x_coord -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[1]:
                self.x_coord -= self.speed
        elif self.dir == 2:
            if self.target[1] < self.y_coord and self.turns[2]:
                self.dir = 2
                self.y_coord -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
            elif self.turns[2]:
                self.y_coord -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.y_coord += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
            elif self.turns[3]:
                self.y_coord += self.speed
        if self.x_coord < -30:
            self.x_coord = 900
        elif self.x_coord > 900:
            self.x_coord - 30
        return self.x_coord, self.y_coord, self.dir


    def move_m2(self):
        #right, left, up, down
        if self.dir == 0:
            if self.target[0] > self.x_coord and self.turns[0]:
                self.x_coord += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                if self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                else:
                    self.x_coord += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.dir = 3
            elif self.target[0] < self.x_coord and self.turns[1]:
                self.x_coord -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                if self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                else:
                    self.x_coord -= self.speed
        elif self.dir == 2:
            if self.target[1] < self.y_coord and self.turns[2]:
                self.dir = 2
                self.y_coord -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[2]:
                self.y_coord -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.y_coord += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[3]:
                self.y_coord += self.speed
        if self.x_coord < -30:
            self.x_coord = 900
        elif self.x_coord > 900:
            self.x_coord - 30
        return self.x_coord, self.y_coord, self.dir


    def move_m1(self):
        #right, left, up, down
        if self.dir == 0:
            if self.target[0] > self.x_coord and self.turns[0]:
                self.x_coord += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
            elif self.turns[0]:
                self.x_coord += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.dir = 3
            elif self.target[0] < self.x_coord and self.turns[1]:
                self.x_coord -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[1]:
                self.x_coord -= self.speed
        elif self.dir == 2:
            if self.target[0] < self.x_coord and self.turns[1]:
                self.dir = 1
                self.x_coord -= self.speed
            elif self.target[1] < self.y_coord and self.turns[2]:
                self.dir = 2
                self.y_coord -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] > self.y_coord and self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_coord += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                else:
                    self.y_coord -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_coord and self.turns[3]:
                self.y_coord += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.target[1] < self.y_coord and self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_coord -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_coord and self.turns[0]:
                    self.dir = 0
                    self.x_coord += self.speed
                elif self.target[0] < self.x_coord and self.turns[1]:
                    self.dir = 1
                    self.x_coord -= self.speed
                else:
                    self.y_coord += self.speed
        if self.x_coord < -30:
            self.x_coord = 900
        elif self.x_coord > 900:
            self.x_coord - 30
        return self.x_coord, self.y_coord, self.dir





#functions
'This is the function that draws the board according to the map we agreed on, based on the actual PacMan map in the first level'
def board_display():
    row = ((HEIGHT - 50) // 32) #row number in the board
    col = (WIDTH // 30) #column number in the board
    for i in range(len(lvl)):
        for j in range(len(lvl[i])):
            if lvl[i][j] == 1:
                pygame.draw.circle(screen, 'brown', (j * col + (0.5 * col), i * row + (0.5 * row)), 4)
            if lvl[i][j] == 2 and not flash:
                pygame.draw.circle(screen, 'white', (j * col + (0.5 * col), i * row + (0.5 * row)), 10)
            if lvl[i][j] == 3:
                pygame.draw.line(screen, color, (j * col + (0.5 * col), i * row),
                                 (j * col + (0.5 * col), i * row + row), 3)
            if lvl[i][j] == 4:
                pygame.draw.line(screen, color, (j * col, i * row + (0.5 * row)),
                                 (j * col + col, i * row + (0.5 * row)), 3)
            if lvl[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * col - (col * 0.4)) - 2, (i * row + (0.5 * row)), col, row],
                                0, PI / 2, 3)
            if lvl[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * col + (col * 0.5)), (i * row + (0.5 * row)), col, row], PI / 2, PI, 3)
            if lvl[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * col + (col * 0.5)), (i * row - (0.4 * row)), col, row], PI,
                                3 * PI / 2, 3)
            if lvl[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * col - (col * 0.4)) - 2, (i * row - (0.4 * row)), col, row], 3 * PI / 2,
                                2 * PI, 3)
            if lvl[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * col, i * row + (0.5 * row)),
                                 (j * col + col, i * row + (0.5 * row)), 3)




'this is the function that rotates/flips the player according to which direction the user clicks. if right is the desired direction then the dir is 0 and the images are still the same'
'if the desired direction is left then dir = 1 and the images are flipped along the y-axis'
'if the desired direction is up  then dir = 1 and the images are rotated 90 degrees'
'if the desired direction is left then dir = 1 and the images are rotated -90 degrees (270 degrees)' 
def player_display():
    #right
    if dir == 0:
        screen.blit(player_pics[counter // 5], (player_X, player_Y))
    #left
    elif dir == 1:
        screen.blit(pygame.transform.flip(player_pics[counter // 5], True, False), (player_X, player_Y))
    #up
    elif dir == 2:
        screen.blit(pygame.transform.rotate(player_pics[counter // 5], 90), (player_X, player_Y))
    #down
    elif dir == 3:
        screen.blit(pygame.transform.rotate(player_pics[counter // 5], 270), (player_X, player_Y))



'this is the function that is concerned with the players movement. n3 is to make sure there is a bit of padding between the player and the boarders'
'also to check if turns are allowed based on the borders'
def get_pos(centerx, centery):
    turns = [False, False, False, False]
    row = (HEIGHT - 50) // 32 #row coord of player
    col = (WIDTH // 30) #col coord of player
    pad = 15 #padding from image to border
    # check collisions based on center x and center y of player +/- fudge number
    
    #CEHCK THE LOGIC IF IT MAKES SENSE????????
    #checked :) :)
    
    'check collisions based on center x and center y of player +/- padding'
    
    if centerx // 30 < 29:
        if dir == 0:
            if lvl[centery // row][(centerx - pad) // col] < 3:
                turns[1] = True
        if dir == 1:
            if lvl[centery // row][(centerx + pad) // col] < 3:
                turns[0] = True
        if dir == 2:
            if lvl[(centery + pad) // row][centerx // col] < 3:
                turns[3] = True
        if dir == 3:
            if lvl[(centery - pad) // row][centerx // col] < 3:
                turns[2] = True


        if dir == 2 or dir == 3:
            if 12 <= centerx % col <= 18:
                if lvl[(centery + pad) // row][centerx // col] < 3:
                    turns[3] = True
                if lvl[(centery - pad) // row][centerx // col] < 3:
                    turns[2] = True
            if 12 <= centery % row <= 18:
                if lvl[centery // row][(centerx - col) // col] < 3:
                    turns[1] = True
                if lvl[centery // row][(centerx + col) // col] < 3:
                    turns[0] = True
        if dir == 0 or dir == 1:
            if 12 <= centerx % col <= 18:
                if lvl[(centery + row) // row][centerx // col] < 3:
                    turns[3] = True
                if lvl[(centery - row) // row][centerx // col] < 3:
                    turns[2] = True
            if 12 <= centery % row <= 18:
                if lvl[centery // row][(centerx - pad) // col] < 3:
                    turns[1] = True
                if lvl[centery // row][(centerx + pad) // col] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True


    return turns



'this is the function that is concerned with the player animation'
def move(play_x, play_y):
    #right, left, up, down
    #testing if this function is working how its supposed to
    if dir == 0 and valid_turns[0]:
        play_x += player_speed
        #print('moving right')
    elif dir == 1 and valid_turns[1]:
        play_x -= player_speed
        #print('moving left')
    if dir == 2 and valid_turns[2]:
        play_y -= player_speed
        #print('moving up')
    elif dir == 3 and valid_turns[3]:
        play_y += player_speed
        #print('moving down')
    return play_x, play_y




def set_targets(mZero_x, mZero_y, mOne_x, mOne_y, mTwo_x, mTwo_y, mThree_x, mThree_y):
    if player_X < 450:
        run_X = 900
    else:
        run_X = 0
    if player_Y < 450:
        run_Y = 900
    else:
        run_Y = 0
    return_target = (380, 400)
    if power_up:
        if not m0.dead and not dead_monsters[0]:
            mZero_target = (run_X, run_Y)
        elif not m0.dead and dead_monsters[0]:
            if 340 < mZero_x < 560 and 340 < mZero_y < 500:
                mZero_target = (400, 100)
            else:
                mZero_target = (player_X, player_Y)
        else:
            mZero_target = return_target
        if not m2.dead and not dead_monsters[1]:
            mOne_target = (run_X, player_Y)
        elif not m2.dead and dead_monsters[1]:
            if 340 < mOne_x < 560 and 340 < mOne_y < 500:
                mOne_target = (400, 100)
            else:
                mOne_target = (player_X, player_Y)
        else:
            mOne_target = return_target
        if not m1.dead:
            mTwo_target = (player_X, run_Y)
        elif not m1.dead and dead_monsters[2]:
            if 340 < mTwo_x < 560 and 340 < mTwo_y < 500:
                mTwo_target = (400, 100)
            else:
                mTwo_target = (player_X, player_Y)
        else:
            mTwo_target = return_target
        if not m3.dead and not dead_monsters[3]:
            mThree_target = (450, 450)
        elif not m3.dead and dead_monsters[3]:
            if 340 < mThree_x < 560 and 340 < mThree_y < 500:
                mThree_target = (400, 100)
            else:
                mThree_target = (player_X, player_Y)
        else:
            mThree_target = return_target
    else:
        if not m0.dead:
            if 340 < mZero_x < 560 and 340 < mZero_y < 500:
                mZero_target = (400, 100)
            else:
                mZero_target = (player_X, player_Y)
        else:
            mZero_target = return_target
        if not m2.dead:
            if 340 < mOne_x < 560 and 340 < mOne_y < 500:
                mOne_target = (400, 100)
            else:
                mOne_target = (player_X, player_Y)
        else:
            mOne_target = return_target
        if not m1.dead:
            if 340 < mTwo_x < 560 and 340 < mTwo_y < 500:
                mTwo_target = (400, 100)
            else:
                mTwo_target = (player_X, player_Y)
        else:
            mTwo_target = return_target
        if not m3.dead:
            if 340 < mThree_x < 560 and 340 < mThree_y < 500:
                mThree_target = (400, 100)
            else:
                mThree_target = (player_X, player_Y)
        else:
            mThree_target = return_target
    return [mZero_target, mOne_target, mTwo_target, mThree_target]

'this is the function that makes the player consume the points => incrementing the score'
def increment_score(score, power, power_count, dead_monsterss):
    row = (HEIGHT - 50) // 32
    col = WIDTH // 30
    if 0 < player_X < 870:
        if lvl[center_Y // row][center_X // col] == 1:
            lvl[center_Y // row][center_X // col] = 0
            score += 10
        if lvl[center_Y // row][center_X // col] == 2:
            lvl[center_Y // row][center_X // col] = 0
            score += 50
            power = True
            power_count = 0
            dead_monsterss = [False, False, False, False]
    return score, power, power_count, dead_monsterss

#!!!!!!!!!!!!!! ATTENTION !!!!!!!!!!!!!!!!!
#layanlayanlayanlayanlayanlayan
#LAYAAAAAAAAAAAAAN CHECK IF THIS IS WORKING FR BC I CANT SEE IT ON MY LAPTOP MY SCREEN IS TOO SHORT
#LAYANNNNNNNNNNNNNNNNNNNNNNNNN DID YOU SEE THIS MESSEGE????????
#text me if you see this baliz

#figure out score display its not working
# SCORE IS NOT SHOWING
def display_text():
    '''
    score_txt = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_txt, (10, 920))
    if power_up:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
        
    #scale image, just like actual pacman. we start with 3 pacmans then with every life lost one image disappears
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_pics[0], (30, 30)), (650 + i * 40, 915))
    '''
    if gameOver:
        pygame.draw.rect(screen, 'maroon', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'pink', [70, 220, 760, 260], 0, 10)
        gameOver_txt = font.render('You lost :( Press the space bar to try again!', True, 'black')
        screen.blit(gameOver_txt, (250, 350))
    
    if gameWon:
        pygame.draw.rect(screen, 'maroon', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'pink', [70, 220, 760, 260], 0, 10)
        gameOver_txt = font.render('You win :) Press the space bar to try again!', True, 'black')
        screen.blit(gameOver_txt, (250, 350))

#end functions

'while the game is running'
#testing the functionality of the whole thing
run = True
while run:
    #implement waiting bc the game is starting directly!!!
    
    #player animation counter, 20 fps
    #powerups blinking, PacMan power ups flashing 
    timer.tick(fps)
    if counter < 19:
        counter += 1
        #every counter reset, blinks for 2 seconds
        if counter > 3:
            flash= False
    else:
        counter = 0
        flash= True
    if power_up and power_up_counter < 600:
        power_up_counter += 1
    elif power_up and power_up_counter >= 600:
        power_up_counter = 0
        power_up = False
        dead_monsters = [False, False, False, False]
    if startup_counter < 180 and not gameOver and not gameWon:
        moving = False
        startup_counter += 1
    else:
        moving = True


    screen.fill('pink')
    board_display()
    center_X = player_X + 23
    center_Y = player_Y + 24
    
    #10s at 60 fps
    #timer for score
    if power_up:
        monsters_speeds = [1, 1, 1, 1]
    else:
        monsters_speeds = [2, 2, 2, 2]
    if dead_monsters[0]:
        monsters_speeds[0] = 2
    if dead_monsters[1]:
        monsters_speeds[1] = 2
    if dead_monsters[2]:
        monsters_speeds[2] = 2
    if dead_monsters[3]:
        monsters_speeds[3] = 2
    if m0_dead:
        monsters_speeds[0] = 4
    if m2_dead:
        monsters_speeds[1] = 4
    if m1_dead:
        monsters_speeds[2] = 4
    if m3_dead:
        monsters_speeds[3] = 4


    gameWon = True
    for i in range(len(lvl)):
        if 1 in lvl[i] or 2 in lvl[i]:
            gameWon = False
            
    
    

#to make sure the monsters are colliding with the player (easier to detect collision on a uniform shape)
    collision_circle = pygame.draw.circle(screen, 'pink', (center_X, center_Y), 20, 2)
    
    #displaying player
    player_display()
    #displaying the monsters
    m0 = Monster(m0_x, m0_y, targets[0], monsters_speeds[0], m0_pic, m0_dir, m0_dead,m0_box, 0)
    m2 = Monster(m2_x, m2_y, targets[1], monsters_speeds[1], m2_pic, m2_dir, m2_dead,m2_box, 1)
    m1 = Monster(m1_x, m1_y, targets[2], monsters_speeds[2], m1_pic, m1_dir, m1_dead,m1_box, 2)
    m3 = Monster(m3_x, m3_y, targets[3], monsters_speeds[3], m3_pic, m3_dir, m3_dead,m3_box, 3)
    
    #display text
    display_text()
    
    #monster targets
    targets = set_targets(m0_x, m0_y, m2_x, m2_y, m1_x, m1_y, m3_x, m3_y)


    valid_turns = get_pos(center_X, center_Y)
    
    if moving:
        player_X, player_Y = move(player_X, player_Y)
        if not m0_dead and not m0.inside_box:
            m0_x, m0_y, m0_dir = m0.move_m0()
        else:
            m0_x, m0_y, m0_dir = m0.move_m3()
        if not m1_dead and not m1.inside_box:
            m1_x, m1_y, m1_dir = m1.move_m1()
        else:
            m1_x, m1_y, m1_dir = m1.move_m3()
        if not m2_dead and not m2.inside_box:
            m2_x, m2_y, m2_dir = m2.move_m2()
        else:
            m2_x, m2_y, m2_dir = m2.move_m3()
        m3_x, m3_y, m3_dir = m3.move_m3()
    score, power_up, power_up_counter, dead_monsters = increment_score(score, power_up, power_up_counter, dead_monsters)
    #same logic everywhere in this function
    # add to if not power_up to check if monsters are dead
    if not power_up:
        #again, the circles are to accuratly check collision
        if (collision_circle.colliderect(m0.rect) and not m0.dead) or \
                (collision_circle.colliderect(m2.rect) and not m2.dead) or \
                (collision_circle.colliderect(m1.rect) and not m1.dead) or \
                (collision_circle.colliderect(m3.rect) and not m3.dead):
            
            #if the monster collides with player
            if lives > 0:
                #decrement lives
                lives -= 1
                startup_counter = 0
                #remove powerups
                power_up = False
                power_up_counter = 0
                
                #return player to og coordinates
                player_X = 450
                player_Y = 663
                
                dir = 0
                dir_command = 0
                
                #return monsters to og coordinates
                m0_x = 56
                m0_y = 58
                m0_dir = 0
                m2_x = 440
                m2_y = 388
                m2_dir = 2
                m1_x = 440
                m1_y = 438
                m1_dir = 2
                m3_x = 440
                m3_y = 438
                m3_dir = 2
                
                #all monsters are not dead
                dead_monsters = [False, False, False, False]
                
                m0_dead = False
                m2_dead = False
                m3_dead = False
                m1_dead = False
            
            else:
                gameOver = True
                moving = False
                startup_counter = 0
                
    if power_up and collision_circle.colliderect(m0.rect) and dead_monsters[0] and not m0.dead:
        if lives > 0:
            power_up = False
            power_up_counter = 0
            lives -= 1
            
            startup_counter = 0
            
            player_X = 450
            player_Y = 663
            
            dir = 0
            dir_command = 0
            
            m0_x = 56
            m0_y = 58
            m0_dir = 0
            m2_x = 440
            m2_y = 388
            m2_dir = 2
            m1_x = 440
            m1_y = 438
            m1_dir = 2
            m3_x = 440
            m3_y = 438
            m3_dir = 2
            
            dead_monsters = [False, False, False, False]
            
            m0_dead = False
            m2_dead = False
            m3_dead = False
            m1_dead = False
        
        else:
            gameOver = True
            moving = False
            startup_counter = 0
    if power_up and collision_circle.colliderect(m2.rect) and dead_monsters[1] and not m2.dead:
        if lives > 0:
            power_up = False
            power_up_counter = 0
            lives -= 1
            startup_counter = 0
            
            player_X = 450
            player_Y = 663
            
            dir = 0
            dir_command = 0
            
            m0_x = 56
            m0_y = 58
            m0_dir = 0
            m2_x = 440
            m2_y = 388
            m2_dir = 2
            m1_x = 440
            m1_y = 438
            m1_dir = 2
            m3_x = 440
            m3_y = 438
            m3_dir = 2
            
            dead_monsters = [False, False, False, False]
            
            m0_dead = False
            m2_dead = False
            m3_dead = False
            m1_dead = False
            
        else:
            gameOver = True
            moving = False
            startup_counter = 0
            
    if power_up and collision_circle.colliderect(m1.rect) and dead_monsters[2] and not m1.dead:
        if lives > 0:
            power_up = False
            power_up_counter = 0
            lives -= 1
            startup_counter = 0
            
            player_X = 450
            player_Y = 663
            
            dir = 0
            dir_command = 0
            
            m0_x = 56
            m0_y = 58
            m0_dir = 0
            m2_x = 440
            m2_y = 388
            m2_dir = 2
            m1_x = 440
            m1_y = 438
            m1_dir = 2
            m3_x = 440
            m3_y = 438
            m3_dir = 2
            
            dead_monsters = [False, False, False, False]
            
            m0_dead = False
            m2_dead = False
            m3_dead = False
            m1_dead = False
            
        else:
            gameOver = True
            moving = False
            startup_counter = 0
            
    if power_up and collision_circle.colliderect(m3.rect) and dead_monsters[3] and not m3.dead:
        if lives > 0:
            power_up = False
            power_up_counter = 0
            lives -= 1
            startup_counter = 0
            
            player_X = 450
            player_Y = 663
            dir = 0
            dir_command = 0
            
            m0_x = 56
            m0_y = 58
            m0_dir = 0
            m2_x = 440
            m2_y = 388
            m2_dir = 2
            m1_x = 440
            m1_y = 438
            m1_dir = 2
            m3_x = 440
            m3_y = 438
            m3_dir = 2
            
            dead_monsters = [False, False, False, False]
            
            m0_dead = False
            m2_dead = False
            m3_dead = False
            m1_dead = False
            
        else:
            gameOver = True
            moving = False
            startup_counter = 0
            
    'FIX COMMENTS HERE'            
    if power_up and collision_circle.colliderect(m0.rect) and not m0.dead and not dead_monsters[0]:
        m0_dead = True
        dead_monsters[0] = True
        score += (2 ** dead_monsters.count(True)) * 100
    if power_up and collision_circle.colliderect(m2.rect) and not m2.dead and not dead_monsters[1]:
        m2_dead = True
        dead_monsters[1] = True
        score += (2 ** dead_monsters.count(True)) * 100
    if power_up and collision_circle.colliderect(m1.rect) and not m1.dead and not dead_monsters[2]:
        m1_dead = True
        dead_monsters[2] = True
        score += (2 ** dead_monsters.count(True)) * 100
    if power_up and collision_circle.colliderect(m3.rect) and not m3.dead and not dead_monsters[3]:
        m3_dead = True
        dead_monsters[3] = True
        score += (2 ** dead_monsters.count(True)) * 100

    #connecting animation with the users key
    for event in pygame.event.get():
        
        #stop running if game is quit
        if event.type == pygame.QUIT:
            run = False
        #when user presses a button, character flips/rotates acc to player_positions
        #testing this function   
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                dir_command = 0
                #print("right")
            if event.key == pygame.K_LEFT:
                dir_command = 1
                #print("left")
            if event.key == pygame.K_UP:
                dir_command = 2
                #print("up")
            if event.key == pygame.K_DOWN:
                dir_command = 3
                #print("down")
            
            #wont change direction instantly    
            if event.key == pygame.K_SPACE and (gameOver or gameWon):
                power_up = False
                power_up_counter = 0
                lives -= 1
                startup_counter = 0
                player_X = 450
                player_Y = 663
                dir = 0
                dir_command = 0
                m0_x = 56
                m0_y = 58
                m0_dir = 0
                m2_x = 440
                m2_y = 388
                m2_dir = 2
                m1_x = 440
                m1_y = 438
                m1_dir = 2
                m3_x = 440
                m3_y = 438
                m3_dir = 2
                dead_monsters = [False, False, False, False]
                m0_dead = False
                m2_dead = False
                m3_dead = False
                m1_dead = False
                score = 0
                lives = 3
                lvl = copy.deepcopy(boards)
                gameOver = False
                gameWon = False

        #to move across the board
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and dir_command == 0:
                dir_command = dir
            if event.key == pygame.K_LEFT and dir_command == 1:
                dir_command = dir
            if event.key == pygame.K_UP and dir_command == 2:
                dir_command = dir
            if event.key == pygame.K_DOWN and dir_command == 3:
                dir_command = dir

    
    #
    if dir_command == 0 and valid_turns[0]:
        dir = 0
    if dir_command == 1 and valid_turns[1]:
        dir = 1
    if dir_command == 2 and valid_turns[2]:
        dir = 2
    if dir_command == 3 and valid_turns[3]:
        dir = 3

    #if the player is out of frame, return it to the other side
    if player_X > 900:
        player_X = -47
    elif player_X < -50:
        player_X = 897

    #if the monsters are inside the box/respawn area
    if m0.inside_box and m0_dead:
        m0_dead = False
    if m2.inside_box and m2_dead:
        m2_dead = False
    if m1.inside_box and m1_dead:
        m1_dead = False
    if m3.inside_box and m3_dead:
        m3_dead = False


    pygame.display.flip()
pygame.quit()


