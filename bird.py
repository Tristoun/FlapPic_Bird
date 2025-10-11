from PIL import Image, ImageTk
from enum import Enum

class BirdState(Enum):
    FALL = 0
    JUMP = 1

class Bird:
    def __init__(self, canvas, x: int=50, y: int=50, path: str="images/animation/bird_wingsup.png", size: tuple=(60, 48)):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = size[0]
        self.height = size[1]

        # Load main image
        img = Image.open(path).convert("RGBA")
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)

        rotated_pil_img = img.rotate(30)
        self.roup_down = ImageTk.PhotoImage(rotated_pil_img)
        rotated_pil_img = img.rotate(-30)
        self.rodown_down = ImageTk.PhotoImage(rotated_pil_img)


        self.photo = ImageTk.PhotoImage(img)

        # Load animation image
        img_anim_path = "images/images/dog_wingsup.png"
        img_anim = Image.open(img_anim_path).convert("RGBA")
        img_anim = img_anim.resize((self.width, self.height), Image.Resampling.LANCZOS)


        rotated_pil_img = img_anim.rotate(30)
        self.roup_up = ImageTk.PhotoImage(rotated_pil_img) #
        rotated_pil_img = img_anim.rotate(-30)
        self.rodown_up = ImageTk.PhotoImage(rotated_pil_img)

        self.anim = ImageTk.PhotoImage(img_anim)

        self.state = BirdState.FALL
        self.frame_anim = 0
        self.anim_state = 0  # 0 for photo, 1 for anim

        self.image = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")
        self.velocity = 0       
        self.gravity_force = 1  
        self.jump_strength = -15 # Negative because up is decreasing y
        self.anim_state = 0
        self.frame_anim = 0

    def apply_gravity(self):
        self.velocity += self.gravity_force
        self.y += self.velocity
        self.canvas.coords(self.image, self.x, self.y)
        self._update_image_animation()

    def jump(self):
        self.velocity = self.jump_strength
        self.state = BirdState.JUMP

    def _update_image_animation(self):
        self.frame_anim += 1
        if self.frame_anim >= 5:
            if self.anim_state == 0:

                if(self.state == BirdState.FALL) :
                    self.canvas.itemconfig(self.image, image=self.rodown_down)
                else :
                    self.canvas.itemconfig(self.image, image=self.roup_down)

                self.anim_state = 1
                self.frame_anim = 0

            else:
                if(self.state == BirdState.FALL) :
                    self.canvas.itemconfig(self.image, image=self.rodown_up)
                else :
                    self.canvas.itemconfig(self.image, image=self.roup_up)
                self.anim_state = 0
                self.frame_anim = 0

    def check_collision(self, height=600):
        return self.y + self.height > height or self.y <= 0

    def death(self, ground_y):
        """
        Make the bird fall smoothly to the bottom (ground_y)
        """
        if self.y + self.height < ground_y:
            self.y += 15  # falling speed
            self.canvas.coords(self.image, self.x, self.y)
        else:
            self.y = ground_y - self.height
            self.canvas.coords(self.image, self.x, self.y)