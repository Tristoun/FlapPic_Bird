from PIL import Image, ImageTk
from enum import Enum

class BirdState(Enum) :
    FALL = 0
    JUMP = 1

class Bird:
    def __init__(self, canvas, x : int=50, y : int =50, path : str ="src/images/animation/bird_wingsup.png", size : tuple =(60, 48)) :
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

        # img_anim_path = "src/images/animation/bird_wingsdown.png"
        img_anim_path = "src/images/images/dog_jump.png"

        img_anim_photo = Image.open(img_anim_path).convert("RGBA")
        img_anim_photo = img_anim_photo.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self.anim = ImageTk.PhotoImage(img_anim_photo)

        # Draw the bird on the canvas
        self.image = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")
        self.image_anim = None #Nothing since we not created the animation image

    def gravity (self, speed : int = 7) :
        self.y += speed
        # self.canvas.delete(self.image)
        # self.image = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")
        self.canvas.move(self.image, 0, speed)

    def jump(self, speed : int = 10) :
        self.y -= speed
        # self.canvas.delete(self.image)
        # self.image = self.canvas.create_image(self.x, self.y, image=self.anim, anchor="nw")
        self.canvas.move(self.image, 0, -speed)

    def death(self) :
        speed = 15
        self.y += speed
        self.canvas.delete(self.image)
        self.image = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")
        self.canvas.move(self.image, 0, speed)

    def set_position(self, x : int =50, y : int=50) -> None :
        self.canvas.coords(self.image, x, y)

    def check_collision(self, height : int = 600) -> bool :
        if(self.y + self.height > height or self.y  <= 0) :
            return True
        return False