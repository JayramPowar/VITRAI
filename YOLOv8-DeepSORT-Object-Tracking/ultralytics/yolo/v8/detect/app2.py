import os
import threading
import webbrowser
from flask import Flask
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from customtkinter import CTk, CTkButton, CTkToplevel
import customtkinter
from PIL import Image
from tkinter import filedialog
from pandastable import Table

# Sample data
data = pd.read_csv("D:\\Mini Project\\YOLOv8-DeepSORT-Object-Tracking\\ultralytics\\yolo\\v8\\detect\\output_csv\\vehicle_data.csv")

# Create a Flask server
server = Flask(__name__)

# Create a Dash app
app_dash = Dash(__name__, server=server)

# Define the layout of the Dash app
app_dash.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Histogram', value='tab1'),
        dcc.Tab(label='Scatter', value='tab2'),
        dcc.Tab(label='Stacked Bar Chart', value='tab3'),
        dcc.Tab(label='Pie Chart', value='tab4')
    ]),
    html.Div(id='tab-content')
])

# Callback to update the content based on the selected tab
@app_dash.callback(Output('tab-content', 'children'),
                   [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab1':
        return html.Div(
            dcc.Graph(figure=px.histogram(data, x="Speed", nbins=10, title="Histogram of Speed", color="Speed")),
            style={'width': '100%', 'height': '100vh'}  # Set width to 100% and height to full viewport height
        )
    elif tab == 'tab2':
        return html.Div(
            dcc.Graph(figure=px.scatter(data, x="ID", y="Speed", color="Vehicle Type", title="Speed vs. ID Colored by Vehicle Type", size_max=50)),
            style={'width': '100%', 'height': '100vh'}  # Set width to 100% and height to full viewport height
        )
    elif tab == 'tab3':
        grouped_data = data.groupby(['Color', 'Vehicle Type']).size().unstack(fill_value=0)
        fig = px.bar(grouped_data, barmode='stack', title="Number of Vehicles by Color and Type", labels={'Color': 'Color', 'value': 'Count'})
        return html.Div(
            dcc.Graph(figure=fig),
            style={'width': '100%', 'height': '100vh'}  # Set width to 100% and height to full viewport height
        )
    elif tab == 'tab4':
        return html.Div(
            dcc.Graph(figure=px.pie(data, names='Vehicle Type', title="Vehicle Type Distribution")),
            style={'width': '100%', 'height': '100vh'}  # Set width to 100% and height to full viewport height
        )


# Function to run the Flask server in a separate thread
def run_server():
    server.run()

# Custom Tkinter window to display Dash visualization
class VisualizationWindow(CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("400x300")  # Adjust size as needed
        self.title("Visualization")

        # Add a button to open the Dash app in a web browser
        self.open_button = CTkButton(self, text="Open Dash App", command=self.open_browser)
        self.open_button.place(relx=0.5, rely=0.5, anchor='center')

        # Create a thread to run the Flask server
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    # Function to open the Dash app in a web browser
    def open_browser(self):
        webbrowser.open("http://127.0.0.1:5000/")

# Your existing Tkinter application
class App(CTk):
    def __init__(self):
        super().__init__()

        self.tab_view = MyTabView(master=self, open_toplevel_func=self.open_toplevel)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        # Configure row and column weights to make the tab view fill the screen
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.resizable(0, 0)
        self.title("Output Window")

    def open_toplevel(self):
        toplevel_window = ToplevelWindow(self)


class ToplevelWindow(CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")  # Adjust size as needed
        self.title("Video Viewer")

        # Video player components
        self.video_file = ''

        # Add the "Open Video" button
        self.button_open_video = customtkinter.CTkButton(self, text="Open Video", command=self.open_video)
        self.button_open_video.place(relx=0.5, rely=0.5, anchor="center")

    def open_video(self):
        self.video_file = filedialog.askopenfilename(filetypes =[('Video', ['*.mp4','*.avi','*.mov','*.mkv','*gif']),('All Files', '*.*')])
        if self.video_file:
            os.startfile(self.video_file)


class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, open_toplevel_func, **kwargs):
        super().__init__(master, **kwargs)
        self.open_toplevel_func = open_toplevel_func
        

        # create tabs
        self.add("tab 1")
        self.add("tab 2")
        self.add("tab 3")
        
        # Configure tab size
        self.configure("tab 1", width=500, height=400)
        self.configure("tab 2", width=500, height=400)
        self.configure("tab 3", width=500, height=400)
        
        # Load and resize images
        image1 = customtkinter.CTkImage(light_image=Image.open(".\\assets\\output\\video.png"), 
                                        dark_image=Image.open(".\\assets\\output\\video.png"), 
                                        size=(70, 70))
        self.image_label1 = customtkinter.CTkLabel(master=self.tab("tab 1"), image=image1, text=None)
        self.image_label1.place(relx=0.5, rely=0.3, anchor="center")

        image2 = customtkinter.CTkImage(light_image=Image.open(".\\assets\\output\\csv.png"),
                                        dark_image=Image.open(".\\assets\\output\\csv.png"),
                                        size=(70, 70))
        self.image_label2 = customtkinter.CTkLabel(master=self.tab("tab 2"), image=image2, text=None)
        self.image_label2.place(relx=0.5, rely=0.3, anchor="center")

        image3 = customtkinter.CTkImage(light_image=Image.open(".\\assets\\output\\DataViz.png"),
                                        dark_image=Image.open(".\\assets\\output\\DataViz.png"),
                                        size=(70, 70))
        self.image_label3 = customtkinter.CTkLabel(master=self.tab("tab 3"), image=image3, text=None)
        self.image_label3.place(relx=0.5, rely=0.3, anchor="center")
        
        # Add buttons on each tab and position them in the center
        self.button1 = customtkinter.CTkButton(master=self.tab("tab 1"), text="Check Out the Output Video", compound="top", command=self.open_toplevel_func)
        self.button1.place(relx=0.5, rely=0.7, anchor="center")

        self.button2 = customtkinter.CTkButton(master=self.tab("tab 2"), text="Examine the Vehicle Data CSV", compound="top", command=self.open_csv_viewer)
        self.button2.place(relx=0.5, rely=0.7, anchor="center")

        self.button3 = customtkinter.CTkButton(master=self.tab("tab 3"), text="Visualization of Traffic Data", compound="top", command=self.open_visualization)
        self.button3.place(relx=0.5, rely=0.7, anchor="center")

    def open_visualization(self):
        visualization_window = VisualizationWindow(self.master)

    def open_csv_viewer(self):
        csv_viewer_window = CSVViewerWindow(self.master)


class CSVViewerWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("800x600")  # Adjust size as needed
        self.title("CSV Viewer")
        
        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(fill='both', expand=True)
        pt = Table(self.frame, showtoolbar=True, showstatusbar=True)
        pt.show()


class App(CTk):
    def __init__(self):
        super().__init__()

        self.tab_view = MyTabView(master=self, open_toplevel_func=self.open_toplevel)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        # Configure row and column weights to make the tab view fill the screen
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.resizable(0, 0)
        self.title("Output Window")

    def open_toplevel(self):
        toplevel_window = ToplevelWindow(self)


app = App()
app.mainloop()
