import tkinter as tk
from PIL import Image, ImageTk
from random import randint
from enum import Enum

from bird import Bird, BirdState
from background import Background
from pipe import Pipe

FPS = 17
WIDTH = 1600
HEIGHT = 900


class GameState(Enum) :
    MENU = 0
    RUN = 1
    STOP = 2

class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        # Player/bird
        self.bg = Background(self.canvas)

        self.player = Bird(self.canvas)
        self.pipe = []

        self.state = GameState.MENU
        self.score = 0
    

    def player_physic(self) :
        if(self.state == GameState.RUN) :
            if(self.player.state == BirdState.FALL) :
                self.player.gravity()
            self.root.after(FPS, self.player_physic)
        
    def jump_step(self) :
        self.player.jump()
        self.player.frame_anim += 1
        if(self.player.frame_anim == 10) :
            self.player.frame_anim = 0
            self.player.state = BirdState.FALL
        else :
            self.root.after(FPS, self.jump_step)


    def player_jump(self) :
        if(self.state == GameState.RUN) :
            if(self.player.state == BirdState.FALL) :
                self.player.state = BirdState.JUMP
                self.jump_step()

    def generate_pipes(self) :
        if(self.state == GameState.RUN) :
            pos_y = randint(-500, 0)
            
            if(self.pipe == []) : 
                self.pipe.append(Pipe(self.canvas, WIDTH, pos_y))
            elif(self.pipe[-1].x <= WIDTH - 600) :
                self.pipe.append(Pipe(self.canvas, WIDTH, pos_y))

            self.root.after(FPS, self.generate_pipes)

    def pipes_move(self) :
        if(self.state == GameState.RUN) :
            lst_delete = []

            for i in range (len(self.pipe)) :
                if(self.pipe[i].x < self.player.x) :
                    lst_delete.append(i)
                else : 
                    self.pipe[i].move()

            for j in lst_delete :
                del(self.pipe[j])
                self.score += 1
                print(self.score)
            self.root.after(FPS, self.pipes_move)

    def check_game_collisions(self) :
        pipe_check = 2
        if(len(self.pipe) < 2) :
            pipe_check = 1
        if(self.state == GameState.RUN) :
            result = self.player.check_collision(height=HEIGHT)
            if result == True :
                self.state = GameState.STOP

            if(self.pipe != []) :
                for i in range (pipe_check) :
                    result = self.pipe[i].check_collision_player(self.player)
                    if(result) :
                        self.state = GameState.STOP

            self.root.after(FPS, self.check_game_collisions)




    def play(self):
        self.root.title("Flappic Game")
        
        self.state = GameState.RUN

        if(self.state == GameState.RUN) :
            self.player.set_position(x=100)

            self.player_physic()
            self.check_game_collisions()

            #Pipes generation and moves
            self.generate_pipes()
            self.pipes_move()
            

        self.root.bind("<space>", lambda event : self.player_jump())


        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    game.play()
