from PIL import Image, ImageTk

from bird import Bird

class Pipe:
    def __init__(self, canvas, x, top, bot, y = 300, width=87, height = 600, gap=200):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.gap = gap

        self.width = width
        self.height = height

        self.top_photo = top
        self.bottom_photo = bot

        # Draw top pipe
        self.top_image = self.canvas.create_image(self.x, self.y, image=self.top_photo, anchor="nw")  # y=0 at top

        # Draw bottom pipe
        self.bottom_image = self.canvas.create_image(self.x, self.y + self.height + self.gap, image=self.bottom_photo, anchor="nw")


    def set_pos(self, x) :
        self.x = x
        self.canvas.coords(self.top_image, self.x, self.y)
        self.canvas.coords(self.top_image, self.x, self.y+self.gap)

    def move(self, speed = 5) :
        self.x -= speed
        self.canvas.move(self.top_image, -speed, 0)
        self.canvas.move(self.bottom_image, -speed, 0)

    def check_collision_player(self, player : Bird) -> bool :
        if(
            (player.x + player.width >= self.x and player.x < self.x + self.width) 
            and (
                (player.y <= self.y + self.height) or
                (player.y + player.height >= self.y + self.height + self.gap)
                )
            ) :
                return True
        
        return False
