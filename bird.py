from PIL import Image, ImageTk
from enum import Enum

class BirdState(Enum) :
    FALL = 0
    JUMP = 1

class Bird:
    def __init__(self, canvas, x : int=50, y : int =50, path : str ="src/images/images/bird.png", size : tuple =(85, 60)) :
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width  = size[0]
        self.height = size[1]
        img = Image.open(path).convert("RGBA")
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.state = BirdState.FALL

        self.frame_anim = 0

        # Draw the bird on the canvas
        self.image = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")

    def gravity (self, speed : int = 5) :
        self.y += speed
        self.canvas.move(self.image, 0, 5) #Move with absolute coordinate

    def jump(self, speed : int = 10) :
        self.y -= speed
        self.canvas.move(self.image, 0, -10)

    def set_position(self, x : int =50, y : int=50) -> None :
        self.canvas.coords(self.image, x, y)

    def check_collision(self, height : int = 600) -> bool :
        if(self.y + self.height > height or self.y  <= 0) :
            return True
        return False