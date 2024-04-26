import customtkinter
from PIL import Image
from tkinter import filedialog
import tkinter.ttk as ttk
import os
import re  # For regular expressions
import shutil  # Import shutil module for file operations
import threading  # Import threading for asynchronous operations
import tkinter as tk
from tkinter import ttk
import threading
import requests
import os
import subprocess


selected_m = ""

class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("tab 1")
        self.add("tab 2")
        self.add("tab 3")
        
        # Configure tab size
        self.configure("tab 1", width=500, height=400)
        self.configure("tab 2", width=500, height=400)
        self.configure("tab 3", width=500, height=400)

        # Add images
        self.browse_icon = customtkinter.CTkImage(
            light_image=Image.open(".\\assets\\input\\browse.png"),
            dark_image=Image.open(".\\assets\\input\\browse.png"),
            size=(24, 24)
        )
        self.drive_icon = customtkinter.CTkImage(
            light_image=Image.open(".\\assets\\input\\drive.png"),
            dark_image=Image.open(".\\assets\\input\\drive.png"),
            size=(24, 24)
        )

        # add widgets on tabs
        self.label = customtkinter.CTkLabel(master=self.tab("tab 1"), text="Upload File")
        self.label.grid(row=0, column=0, padx=110, pady=25, sticky="nsew")  # Center alignment

        # Create buttons
        self.button1 = customtkinter.CTkButton(master=self.tab("tab 1"), text="Browse Files", compound="left", image=self.browse_icon, command=self.open_window1)
        self.button1.grid(row=1, column=0, padx=170, pady=30, sticky="nsew")

        self.button2 = customtkinter.CTkButton(master=self.tab("tab 1"), text="Upload From Drive", compound="left", image=self.drive_icon, command=self.open_window2)
        self.button2.grid(row=2, column=0, padx=170, pady=10, sticky="nsew")
        # Create model menu in tab 2
        self.create_model_menu(self.tab("tab 2"))
        
        self.button3 = customtkinter.CTkButton(master=self.tab("tab 3"), text="Run Analysis", command=self.run_analysis)
        self.button3.grid(row=2, column=0, padx=170, pady=100, sticky="nsew")
        
        self.button4 = customtkinter.CTkButton(master=self.tab("tab 3"), text="Check Output", command=self.run_output, state="disabled")
        self.button4.grid(row=3, column=0, padx=170, pady=0, sticky="nsew")
        
        
    def open_window1(self):
        # Create top-level window for button 1
        top_window1 = customtkinter.CTkToplevel(self.master)
        top_window1.title("Browse Files")
        top_window1.geometry("400x300")

        # Add file browse functionality to top-level window
        self.add_file_browse(top_window1)

    def open_window2(self):
        # Create top-level window for button 2
        top_window2 = customtkinter.CTkToplevel(self.master)
        top_window2.title("Google Drive Upload")
        top_window2.geometry("400x300")
        
        # Add drive upload functionality to top-level window
        self.add_drive_upload(top_window2)

    def add_file_browse(self, window):
        """Add file browsing functionality to a top-level window."""
        file_box = customtkinter.CTkLabel(
            master=window,
            text="Select a File",
            width=50,  # Adjust as needed
            height=30,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            wraplength=250,  # Adjust wrap length as needed
            font=customtkinter.CTkFont(size=12)  # Adjust font size for better fit
        )
        file_box.pack(pady=18, expand=True)

        browse_button = customtkinter.CTkButton(
            master=window, text="Browse", command=lambda: self.browse_file(file_box)
        )
        browse_button.pack(pady=19, expand=True)

    def add_drive_upload(self, window):
        """Add drive upload functionality to a top-level window."""
        drive_link_label = customtkinter.CTkLabel(master=window, text="Enter Drive Link:")
        drive_link_label.pack(pady=13)

        drive_link_entry = customtkinter.CTkEntry(master=window, width=230)
        drive_link_entry.pack(pady=10)

        upload_button = customtkinter.CTkButton(master=window, text="Upload from Drive", command=lambda: threading.Thread(target=self.download_from_drive, args=(drive_link_entry,)).start())
        upload_button.pack(pady=10)


        self.progress_bar = ttk.Progressbar(window, mode="determinate", length=400, orient="horizontal")
        self.progress_bar.pack(pady=10)

    def browse_file(self, file_box):
        """Handles file browsing and displaying selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4")])
        if file_path:
            file_box.configure(text=file_path)
            try:
                self.copy_and_rename(file_path, "test1.mp4")
                print("File copied and renamed successfully!")
            except Exception as e:
                print("Error copying file:", e)
        else:
            file_box.configure(text="Select a File")

    def download_from_drive(self, drive_link_entry):
        """Handles drive link download, renaming, and copying."""
        drive_link = drive_link_entry.get()
        try:
            # Extract file ID from the sharing link
            file_id_match = re.search(r"/file/d/([^/]+)/", drive_link)
            if file_id_match:
                file_id = file_id_match.group(1)
                output_filename = "test1.mp4"  # Destination filename
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

                response = requests.get(download_url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                chunk_size = 1024  # 1 KB
                downloaded = 0

                with open(output_filename, 'wb') as f:
                    for data in response.iter_content(chunk_size=chunk_size):
                        f.write(data)
                        downloaded += len(data)
                        progress = (downloaded / total_size) * 100
                        # Update progress bar
                        self.progress_bar["value"] = progress
                        self.update_idletasks()

                print(f"File downloaded successfully from drive link and renamed to {output_filename}!")
            else:
                print("Invalid Google Drive link format. Please provide a valid sharing link.")
        except Exception as e:
            print("Error downloading file from drive link:", e)

            
    @staticmethod
    def copy_and_rename(source_path, destination_filename):
        """Copy and rename a file."""
        if not destination_filename:
            raise ValueError("Destination filename cannot be empty.")

        destination_path = os.path.join(os.path.dirname(__file__), destination_filename)

        try:
            shutil.copy(source_path, destination_path)
            return True
        except Exception as e:
            raise ValueError(f"Error copying file from {source_path} to {destination_path}: {e}") from e

                  
    def create_model_menu(self, tab):
        """Creates a menu for selecting model options in a tab."""
        model_menu_label = customtkinter.CTkLabel(master=tab, text="Select a Model:")
        model_menu_label.pack(pady=15)

        model_options = ["Select a Model", "yolov8n.pt", "yolov8s.pt", "yolov8l.pt", "yolov8x.pt"]
        self.model_menu = customtkinter.CTkOptionMenu(
            master=tab, values=model_options, command=self.model_selected
        )
        self.model_menu.pack(pady=5)

    def model_selected(self, selected_model):
        global selected_m
        """Handles model selection from the menu."""
        print("Selected Model:", selected_model)
        selected_m = selected_model
        if selected_m == "Select a Model":
            print("Warning: Please select a model!")
        
        # Process the selected model here

    def run_analysis(self):
        """Run analysis based on selected model."""
        global selected_m
        if not selected_m:
            print("Warning: Please select a model before running analysis!")
            return
        
        def run_analysis_command():
            command = f"python predict.py model={selected_m} source=\"test1.mp4\""
            subprocess.run(command, shell=True)
            self.button4.configure(state = "normal")
                
        
        # Run the analysis command in a separate thread
        threading.Thread(target=run_analysis_command).start()
    
    def run_output(self):
        command = f"python app2.py"
        def run_ouput_command():
            subprocess.run(command, shell=True)
        
        # Run the analysis command in a separate thread
        threading.Thread(target=run_ouput_command).start()
        


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        print("Current directory:", os.getcwd())
        detect_dir = os.path.join("YOLOv8-DeepSORT-Object-Tracking", "ultralytics", "yolo", "v8", "detect")
        os.chdir(detect_dir)
        print("Current directory:", os.getcwd())
        self.tab_view = MyTabView(master=self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        # Configure row and column weights to make the tab view fill the screen
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.resizable(0, 0)
        self.title("Input Window")

app = App()
app.mainloop()
