import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import os
import time
from skimage.metrics import structural_similarity as ssim
from tkinter import filedialog, messagebox, Label
from PIL import Image, ImageTk

conversion_methods = [
    {"method": 0, "name": "Method 0"},
    {"method": 1, "name": "Method 1"},
    {"method": 2, "name": "Method 2"},
    {"method": 3, "name": "Method 3"},
    {"method": 4, "name": "Method 4"},
    {"method": 5, "name": "Method 5"},
    {"method": 6, "name": "Method 6"}
]

class KonverzijaSlike:
    def __init__(self, root):
        self.root = root
        self.root.title("Konverzija slike")

        self.jpeg_image_path = ""
        self.webp_image_path = ""
        self.quality = tk.DoubleVar(value=80)
        self.img_tk = None

        self.create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_widgets(self):
        choose_button = tk.Button(self.root, text="Odaberi JPEG sliku:", command=self.choose_jpeg_image)
        choose_button.pack(pady=10)

        quality_label = tk.Label(self.root, text="Odaberite kvalitetu (1-100):")
        quality_label.pack(pady=5)

        quality_slider = tk.Scale(self.root, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.quality)
        quality_slider.pack(pady=5)

        process_button = tk.Button(self.root, text="Procesiraj!", command=self.process_image)
        process_button.pack(pady=10)

        self.processed_image_label = tk.Label(self.root)
        self.processed_image_label.pack(pady=10)

    def choose_jpeg_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg;*.jpeg")])
        if file_path:
            self.jpeg_image_path = file_path
            self.show_image(file_path)

    def process_image(self):
        if not self.jpeg_image_path:
            tk.messagebox.showerror("Error", "Molim Vas odaberite JPEG sliku.")
            return

        self.webp_image_path = os.path.splitext(self.jpeg_image_path)[0] + "_output.webp"

        for method_info in conversion_methods:
            selected_method = method_info["method"]
            compare_images(self.jpeg_image_path, self.webp_image_path, selected_method, self.quality.get())

            self.display_selected_image_in_tkinter()

    def show_image(self, file_path):
        image = Image.open(file_path)
        img_tk = self.create_thumbnail(image)

        if self.processed_image_label.winfo_exists():
            self.processed_image_label.config(image=img_tk)
        else:
            self.processed_image_label = tk.Label(self.root, image=img_tk)
            self.processed_image_label.pack(pady=10)

        self.processed_image_label.image = img_tk


    def display_selected_image_in_tkinter(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, Label):
                widget.destroy()

        if self.img_tk:
            image_label = Label(self.root, image=self.img_tk)
            image_label.image = self.img_tk
            image_label.pack()

    def create_thumbnail(self, image):
        img = image.copy()
        img.thumbnail((400, 400))
        return ImageTk.PhotoImage(img)

    def on_exit(self):
        if self.webp_image_path and os.path.exists(self.webp_image_path):
            os.remove(self.webp_image_path)
        self.root.destroy()

def calculate_ssim(image1, image2):
    array_image1 = np.array(image1.convert('L'))
    array_image2 = np.array(image2.convert('L'))
    return ssim(array_image1, array_image2, win_size=11, multichannel=False)

def compare_images(jpeg_path, webp_path, method, quality):
    jpeg_image = Image.open(jpeg_path)
    start_time = time.time()
    jpeg_image.save(webp_path, 'webp', method=method, quality=quality)
    end_time = time.time()

    conversion_time_ms = (end_time - start_time) * 1000
    webp_image = Image.open(webp_path)
    ssim_value = calculate_ssim(jpeg_image, webp_image)
    fig, axes = plt.subplots(2, 2, figsize=(10, 20))

    axes[0, 0].imshow(np.array(jpeg_image))
    axes[0, 0].axis('off')
    axes[0, 0].set_title("JPEG slika", fontsize=12)

    axes[0, 1].imshow(np.array(webp_image))
    axes[0, 1].axis('off')
    axes[0, 1].set_title(f"WebP slika - {conversion_methods[method]['name']}", fontsize=12)

    jpeg_info_text = (
        f"Veličina JPEG-a: {os.path.getsize(jpeg_path)} bytes\n"
        f"Model boje JPEG-a: {jpeg_image.mode}\n"
        f"Dimenzije JPEG-a: {jpeg_image.size}"
    )
    
    webp_info_text = (
        f"Veličina WebP-a: {os.path.getsize(webp_path)} bytes\n"
        f"Model boje WebP-a: {webp_image.mode}\n"
        f"Dimenzije WebP-a: {webp_image.size}\n"
        f"Vrijeme konverzije: {conversion_time_ms:.2f} ms\n"
        f"SSIM: {ssim_value:.4f}"
    )

    axes[0, 0].text(0.5, -0.6, jpeg_info_text, ha="center", va="bottom", transform=axes[0, 0].transAxes, fontsize=10)
    axes[0, 1].text(0.5, -0.6, webp_info_text, ha="center", va="bottom", transform=axes[0, 1].transAxes, fontsize=10)

    fig.delaxes(axes[1, 0])
    fig.delaxes(axes[1, 1])

    plt.tight_layout(rect=[0, 0, 1, 0.9], h_pad=3)
    plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = KonverzijaSlike(root)
    root.mainloop()
