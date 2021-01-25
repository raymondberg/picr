from pathlib import Path
from tkinter import *
import sys

# pip install pillow
from PIL import Image, ImageTk, UnidentifiedImageError

class Window(Frame):
    def __init__(self, starting_path, x=800, y=480, parent=None):
        Frame.__init__(self, parent)
        self.path_iterator = (f for f in Path(starting_path).glob("**/*") if f.is_file())
        self.x = x
        self.y = y
        self.parent = parent
        self.parent.wm_title("PiccR")
        self.parent.geometry("{}x{}".format(self.x,self.y))
        self.pack(fill=BOTH, expand=1)
        self.parent.bind("<KeyPress>", self.keydown)
        # self.bind("<KeyRelease>", self.keyup)
        self.keeps = []
        self.discards = []
        self.current_path = None
        self._load_img()

    def _load_img(self):
        self.image_label = Label(self, bg="black", wraplength=self.x, text="picr"*1000)
        self.image_label.place(x=0, y=0)
        try:
            self.current_path = next(self.path_iterator, None)
            if not self.current_path:
                self.parent.destroy()
            print("Loading", self.current_path)
            image = Image.open(self.current_path)
        except UnidentifiedImageError as e:
            print("Skipping ", self.current_path)
            return self._load_img()
        image = self._resize_image(image)
        render = ImageTk.PhotoImage(image)
        self.image_label = Label(self, image=render)
        self.image_label.image = render
        self.image_label.place(x=0, y=0)
        self.parent.configure(background="black")

    def _resize_image(self, image):
        width, height = image.size
        print("Original size:", width, height)
        if self.x - width < self.y - height and self.x - width < 0:
            print("image wider than tall")
            height = int((self.x / width) * height)
            width = self.x
        elif (self.y - height) < (self.x - width) and self.y - height < 0:
            print("image taller than wide")
            width = int((self.y / height) * width)
            height = self.y
        print("setting image to ", width, height)
        return image.resize((width, height))

    def keydown(self, event):
        should_load = False
        if event.keysym == 'Right':
            print("Right")
            self.keeps.append(self.current_path)
            should_load = True
        elif event.keysym == 'Left':
            print("Left")
            self.discards.append(self.current_path)
            should_load = True
        print("Keeps:", self.keeps)
        print("Discards:", self.discards)
        if should_load:
            self._load_img()


def piccr(location):
    root = Tk()
    app = Window(Path(location), x=800, y=480, parent=root)
    root.mainloop()

    print(f"About to discard {len(app.discards)} files:")
    for row in app.discards:
        print(row)

    print()
    if app.discards:
        confirm = input(f"Enter yes to confirm delete of {len(app.discards)}, anything else will cancel: ")
        if confirm == "yes":
            for row in app.discards:
                row.unlink()
        else:
            print("aborting")


if __name__ == '__main__':
    if sys.argv[-1]:
        piccr(sys.argv[-1])
