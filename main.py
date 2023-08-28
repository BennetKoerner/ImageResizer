import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk


class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")

        self.image_folder = os.path.join(os.path.dirname(__file__), "input")
        self.output_folder = os.path.join(os.path.dirname(__file__), "cropped")
        os.makedirs(self.output_folder, exist_ok=True)

        self.image_list = []
        self.current_index = 0
        self.selected_grid_size = (512, 512)
        self.scaled_image_size = (512, 512)
        self.grid_start_x = 0
        self.grid_start_y = 0
        self.image_original = None

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.load_button = tk.Button(root, text="Load Images", command=self.load_images)
        self.load_button.pack()

        self.prev_button = tk.Button(root, text="Previous", command=self.show_previous_image)
        self.prev_button.pack()

        self.next_button = tk.Button(root, text="Next", command=self.show_next_image)
        self.next_button.pack()

        self.grid_size_var = tk.StringVar(root)
        self.grid_size_var.set("512x512")
        self.grid_size_dropdown = tk.OptionMenu(root, self.grid_size_var, "512x512", "1024x1024",
                                                command=self.update_grid_size)
        self.grid_size_dropdown.pack()

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<MouseWheel>", self.on_canvas_scroll)

        self.load_images()

    def load_images(self):
        self.image_list = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = 0
        self.show_current_image()

    def show_current_image(self):
        image_path = os.path.join(self.image_folder, self.image_list[self.current_index])
        self.image_original = cv2.imread(image_path)
        img = cv2.cvtColor(self.image_original, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.config(width=self.tk_img.width(), height=self.tk_img.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.draw_grid()

        self.grid_start_x = min(self.grid_start_x, self.tk_img.width() - self.selected_grid_size[0])
        self.grid_start_y = min(self.grid_start_y, self.tk_img.height() - self.selected_grid_size[1])
        self.draw_grid()

    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

    def show_next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.save_cropped_image()
            self.current_index += 1
            self.show_current_image()

    def update_grid_size(self, value):
        size_mapping = {"512x512": (512, 512), "1024x1024": (1024, 1024)}
        self.selected_grid_size = size_mapping[value]
        self.scaled_image_size = size_mapping[value]
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("grid")
        for x in range(self.selected_grid_size[0], self.tk_img.width(), self.selected_grid_size[0]):
            self.canvas.create_line(x, 0, x, self.tk_img.height(), fill="red", tags="grid")
        for y in range(self.selected_grid_size[1], self.tk_img.height(), self.selected_grid_size[1]):
            self.canvas.create_line(0, y, self.tk_img.width(), y, fill="red", tags="grid")

        self.canvas.create_rectangle(self.grid_start_x, self.grid_start_y,
                                     self.grid_start_x + self.selected_grid_size[0],
                                     self.grid_start_y + self.selected_grid_size[1], outline="blue", tags="grid")

    def on_canvas_click(self, event):
        self.grid_start_x = event.x
        self.grid_start_y = event.y
        self.draw_grid()

    def on_canvas_drag(self, event):
        self.grid_start_x = max(0, min(event.x, self.tk_img.width() - self.selected_grid_size[0]))
        self.grid_start_y = max(0, min(event.y, self.tk_img.height() - self.selected_grid_size[1]))
        self.draw_grid()

    def on_canvas_scroll(self, event):
        if event.delta > 0:
            new_size = min(self.selected_grid_size[0] + 32, self.tk_img.width(), self.tk_img.height())
        else:
            new_size = max(self.selected_grid_size[0] - 32, 32)
        self.selected_grid_size = (new_size, new_size)
        self.draw_grid()

    def save_cropped_image(self):
        cropped_image = self.image_original[self.grid_start_y:self.grid_start_y + self.selected_grid_size[1],
                        self.grid_start_x:self.grid_start_x + self.selected_grid_size[0]]

        resized_image = cv2.resize(cropped_image, self.scaled_image_size)

        cropped_image_path = os.path.join(self.output_folder, f"cropped_{self.image_list[self.current_index]}")
        cv2.imwrite(cropped_image_path, resized_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
