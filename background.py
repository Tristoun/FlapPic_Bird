from PIL import Image, ImageTk

class Background:
    def __init__(self, canvas, path="images/images/bg.png", size=(1600, 900), x=0, y=0):
        """
        canvas: Tkinter Canvas where the background will be drawn
        path: path to background image
        size: (width, height) to resize the image
        x, y: position of the background on the canvas
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size

        # Load and resize the background image
        bg_image = Image.open(path)
        bg_image = bg_image.resize(size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(bg_image)

        # Draw the image on the canvas
        self.id = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")
