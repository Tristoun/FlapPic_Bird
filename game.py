import tkinter as tk
from PIL import Image, ImageTk
from random import randint
from enum import Enum

import pygame

from bird import Bird, BirdState
from background import Background
from pipe import Pipe
from bouton import Bouton


FPS = 17
WIDTH = 700
HEIGHT = 900



pygame.mixer.init()

def playNotificationSound():
    pygame.mixer.music.load('sound/megalovania.mp3')
    pygame.mixer.music.play()

# playNotificationSound()


class GameState(Enum) :
    MENU = 0
    RUN = 1
    STOP = 2

class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.root.bind("<KeyPress-space>", self.player_jump)

        self.root.tk.call('tk', 'busy', 'hold', self.root)  # Not perfect, hacky

        # Player/bird
        self.bg = Background(self.canvas, path="images/images/bg_undertale.jpg", size=(WIDTH, HEIGHT))

        self.player = Bird(self.canvas, path="images/images/dog_wingsdown.png")
        self.pipe = []

        self.state = GameState.MENU
        self.score = 0

        self.text_box = None
        self.text = str(self.score)

        self.bouton_start = ""

        self.speed = 1

        top_img = Image.open("images/images/os_top.png").resize((87,600), Image.Resampling.LANCZOS)
        self.top_photo = ImageTk.PhotoImage(top_img)
        bottom_img = Image.open("images/images/os_bot.png").resize((87,600), Image.Resampling.LANCZOS)
        self.bottom_photo = ImageTk.PhotoImage(bottom_img)

        self.cadre = None
        self.text_score = None
        self.space_pressed = False
        self.frame_jump = 0

    def launch_game(self) :
        if(self.state == GameState.RUN) :
            self.generate_text_score()


            self.player_physic()
            self.check_game_collisions()

            #Pipes generation and moves
            self.generate_pipes()
            self.pipes_move()

            self.root.after(FPS, self.launch_game)

    def reset(self) :
        for i in range(len(self.pipe)) :
            self.canvas.delete(self.pipe[i].top_image)
            self.canvas.delete(self.pipe[i].bottom_image) 

        self.pipe = []
        self.canvas.delete(self.player.image)
        self.canvas.delete(self.text_box)

        self.speed = 5


    def menu(self) :
        if(self.state == GameState.MENU) :
            self.bouton_start =  Bouton(self.canvas, size=(160, 56), x=WIDTH/2-80, y=HEIGHT/2-14)
            self.score = 0
            self.text = "0"
            self.text_box = None
            self.reset()
            self.player = Bird(self.canvas, path="images/images/dog.png", size=(60,55))

            self.root.bind("<Button>", self.click_menu)

    def scoring(self) :
        self.reset()
        self.cadre = Bouton(self.canvas, size=(550, 500),path="images/images/carre.png", x=80, y=80)
        self.text_score = Bouton(self.canvas, size=(220, 44), path="images/images/text_score.png", x=200, y=200)
        self.generate_text_score(x=450, y=220)
        self.bouton_start = Bouton(self.canvas, size=(160, 56), x=WIDTH/2-80, y=HEIGHT/2-14)
        self.state = GameState.MENU
        self.root.bind("<Button>", self.click_menu)


    def player_physic(self):
        if self.state == GameState.RUN:
            self.player.apply_gravity()
            # If velocity is negative (jump), bird is in jump state
            if self.player.velocity > 0:
                self.player.state = BirdState.FALL
        
    def jump_step(self):
        self.player.jump(speed=17)
        self.frame_jump += 1
        if(self.frame_jump == 10):
            self.frame_jump = 0
            self.player.state = BirdState.FALL
        else:
            self.root.after(FPS, self.jump_step)

    def player_jump(self, event):
        if self.state == GameState.RUN:
            if(self.frame_jump >= 0) :
                self.frame_jump = 0
            self.player.jump()


    def generate_pipes(self) :
        if(self.state == GameState.RUN) :
            pos_y = randint(-500, 0)
            
            if(self.pipe == []) : 
                self.pipe.append(Pipe(self.canvas, x=WIDTH, top=self.top_photo, bot=self.bottom_photo, y=pos_y))
            elif(self.pipe[-1].x <= WIDTH - 400) :

                self.pipe.append(Pipe(self.canvas, x=WIDTH, top=self.top_photo, bot=self.bottom_photo, y=pos_y))


    def pipes_move(self) :
        
        if(self.state == GameState.RUN) :
            lst_delete = []

            for i in range (len(self.pipe)) :
                if(self.pipe[i].x < self.player.x) :
                    lst_delete.append(i)
                else : 
                    self.pipe[i].move(speed=self.speed)

            for j in lst_delete :
                self.canvas.delete(self.pipe[j].top_image)
                self.canvas.delete(self.pipe[j].bottom_image) 
                del(self.pipe[j])
            
                self.score += 1
                if(self.score %10 == 0 and self.score != 0) :
                    self.speed += 1
                self.text = str(self.score)
                self.generate_text_score()

    def death_animation(self):
        if(self.state == GameState.STOP) :
            if(self.player.y + self.player.height <= HEIGHT-20) :
                self.player.death(HEIGHT)
            else :
                self.state = GameState.MENU
                self.scoring()
            self.root.after(FPS, self.death_animation)


    def check_game_collisions(self) :
        pipe_check = 2
        if(len(self.pipe) < 2) :
            pipe_check = 1
        if(self.state == GameState.RUN) :
            result = self.player.check_collision(height=HEIGHT)
            if result == True :
                self.state = GameState.STOP
                self.death_animation()

            if(self.pipe != []) :
                for i in range (pipe_check) :
                    result = self.pipe[i].check_collision_player(self.player)
                    if(result) :
                        self.state = GameState.STOP
                        self.death_animation()


    def generate_text_score(self, x=WIDTH//2, y=35) :
        self.canvas.delete(self.text_box)
        self.text_box = self.canvas.create_text(x, y, text=self.text, font=("Ariel", 40, "normal"), fill='white')

    def click_menu(self, event) :
        if(self.state == GameState.MENU) :
            if(event.x >= self.bouton_start.x and event.x <= self.bouton_start.x + self.bouton_start.size[0] and event.y >= self.bouton_start.y and event.y <= self.bouton_start.y + self.bouton_start.size[1]) :
                self.state = GameState.RUN
                self.canvas.delete(self.bouton_start.id)
                self.player = Bird(self.canvas, path="images/images/dog_wingsdown.png", size=(60,55))
                self.score = 0
                # self.text_box = None
                self.text = str(self.score)
                if(self.cadre!= None) :
                    self.canvas.delete(self.cadre.id)
                if(self.text_score!= None) :
                    self.canvas.delete(self.text_score.id)
                self.canvas.delete(self.text_box)
                self.launch_game()


    def play(self):
        self.root.title("Flappic Game")
        
        self.state = GameState.MENU

        self.menu()

        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    game.play()
