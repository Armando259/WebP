from PIL import Image
from PIL import ImageTk
from skimage.metrics import structural_similarity as ssim
from tkinter import Tk, Label, Button, filedialog, Toplevel
from tkinter import messagebox
from tkinter import TclError
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import sys

num_iterations = 11

def convert_to_webp(input_path, output_path, quality=80, method=4):
    start_time = time.time()
    image = Image.open(input_path)
    image.save(output_path, 'webp', quality=quality, method=method)
    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000.0
    return elapsed_time_ms

def average_conversion_time(image_path, method, num_iterations=11):
    total_time = 0
    for _ in range(num_iterations):
        total_time += convert_to_webp(image_path, f"temp_webp_method{method}.webp", method=method)
    return total_time / (num_iterations - 1) if num_iterations > 1 else 0

def compare_images(image1_path, image2_path):
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    image1 = image1.convert("L")
    image2 = image2.convert("L")

    array1 = np.array(image1)
    array2 = np.array(image2)

    similarity_index = ssim(array1, array2)

    return similarity_index

#---------------------------------------------------------------------------

#open file prozorcici
def open_file_dialog_reset():
    global jpg_image_path
    try:
        script_folder = os.path.dirname(os.path.abspath(__file__))
        root.filename = filedialog.askopenfilename(
            initialdir=script_folder,
            title="Odaberi JPEG sliku: ",
            filetypes=(("JPEG files", "*.jpg;*.jpeg"), ("all files", "*.*"))
        )
    except TclError:
        return

    if root.filename:
        jpg_image_path = root.filename
        display_selected_image_in_tkinter(jpg_image_path)

def on_closing():
    root.withdraw()
    if messagebox.askokcancel("Izlazak", "Želite li izaći iz programa?"):
        root.destroy()
        sys.exit()
    else:
        root.deiconify()

def on_graph_window_close(graph_window):
    clear_temporary_files()
    graph_window.destroy()
    open_file_dialog_reset()

def clear_temporary_files():
    for method_info in conversion_methods:
        method = method_info["method"]
        for iteration in range(1, num_iterations + 1):
            webp_output_path = f"temp_webp_method{method}_{iteration}.webp"
            if os.path.exists(webp_output_path):
                os.remove(webp_output_path)

        txt_file_path = f"method_{method}_data.txt"
        if os.path.exists(txt_file_path):
            os.remove(txt_file_path)

    print("Privremene datoteke su izbrisane!.")

def display_selected_image_in_tkinter(image_path):
    img = Image.open(image_path)
    img.thumbnail((400, 400))
    img_tk = ImageTk.PhotoImage(img)

    image_label = Label(root, image=img_tk)
    image_label.image = img_tk
    image_label.pack()

    generate_graph_button = Button(root, text="Generiraj grafove!", command=lambda: show_graph(image_path))
    generate_graph_button.pack()

#---------------------------------------------------------------------------
    
def show_graph(image_path):
    global num_iterations

    for widget in root.winfo_children():
        if isinstance(widget, Label) or isinstance(widget, Button):
            widget.destroy()

    display_selected_image_in_tkinter(image_path)

    graph_window = Toplevel(root)
    graph_window.title("Analiza metoda konverzija")

    average_times = []
    average_ssim = []

    for method_info in conversion_methods:
        method = method_info["method"]
        method_times = []
        method_ssim = []

        with open(f"method_{method}_data.txt", "w") as file:
            file.write(f"Method {method} Data:\n")
            
            for iteration in range(1, num_iterations + 1):
                webp_output_path = f"temp_webp_method{method}_{iteration}.webp"
                file.write(f"Iteration {iteration}:\n")
                time_measurement = convert_to_webp(image_path, webp_output_path, method=method)
                if iteration != 1:
                    method_times.append(time_measurement)
                file.write(f"Conversion Time: {time_measurement:.2f} ms\n")

                ssim_measurement = compare_images(image_path, webp_output_path)
                if iteration != 1:
                    method_ssim.append(ssim_measurement)
                file.write(f"SSIM with Original: {ssim_measurement:.5f}\n\n")

        average_time = sum(method_times) / (num_iterations - 1) if num_iterations > 1 else 0
        average_ssim_value = round(sum(method_ssim) / (num_iterations - 1), 5) if num_iterations > 1 else 0

        print(f"Method {method} - Average Conversion Time (excluding first iteration): {average_time:.2f} ms")
        print(f"Method {method} - Average SSIM with Original (excluding first iteration): {average_ssim_value:.5f}\n")

        average_times.append(average_time)
        average_ssim.append(average_ssim_value)

    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.bar([f"Meth{method_info['method']}" for method_info in conversion_methods], average_times, color='blue')
    for i, v in enumerate(average_times):
        plt.text(i, v + 0.01, f"{v:.2f}", ha='center', va='bottom')
    plt.xlabel('Konverzijska metoda')
    plt.ylabel('Prosječno vrijeme konverzije (ms)')
    plt.title('Prosječno vrijeme konverzije za svaku konverzijsku metodu')

    plt.subplot(1, 2, 2)
    plt.bar([f"Meth{method_info['method']}" for method_info in conversion_methods], average_ssim, color='green')
    for i, v in enumerate(average_ssim):
        plt.text(i, v + 0.0001, f"{v:.4f}", ha='center', va='bottom')
    plt.xlabel('Konverzijska metoda')
    plt.ylabel('Prosječna SSIM vrijednost')
    plt.title('Prosječna SSIM vrijednost za svaku konverzijsku metodu')
    plt.ylim(0.95, 1)

    plt.subplots_adjust(bottom=0.15)

    canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    graph_window.protocol("WM_DELETE_WINDOW", lambda: on_graph_window_close(graph_window))
    graph_window.mainloop()

jpg_image_path = ""
conversion_methods = [
    {"method": 0, "name": "Method 0"},
    {"method": 1, "name": "Method 1"},
    {"method": 2, "name": "Method 2"},
    {"method": 3, "name": "Method 3"},
    {"method": 4, "name": "Method 4"},
    {"method": 5, "name": "Method 5"},
    {"method": 6, "name": "Method 6"}
]

root = Tk()
root.title("Analiza metoda konverzija")

file_label = Label(root, text="Odaberi JPEG sliku: ")
file_label.pack()

select_button = Button(root, text="Odaberi", command=open_file_dialog_reset)
select_button.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()