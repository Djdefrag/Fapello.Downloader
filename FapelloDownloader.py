import fnmatch
import itertools
import multiprocessing
import os.path
import re
import shutil
import sys
import threading
import time
import tkinter as tk
import urllib.request
import warnings
import webbrowser
from multiprocessing.pool import ThreadPool

import requests
from bs4 import BeautifulSoup
from customtkinter import (CTk, 
                           CTkButton, 
                           CTkEntry, 
                           CTkFont, 
                           CTkImage,
                           CTkLabel, 
                           CTkOptionMenu, 
                           CTkScrollableFrame,
                           filedialog, 
                           set_appearance_mode,
                           set_default_color_theme)
from PIL import Image

warnings.filterwarnings("ignore")

app_name = "Fapello.Downloader"
version  = "3.0"

text_color            = "#F0F0F0"
app_name_color        = "#ffbf00"
 
githubme              = "https://github.com/Djdefrag/Fapello.Downloader"
itchme                = "https://jangystudio.itch.io/fapellodownloader"
telegramme            = "https://linktr.ee/j3ngystudio"


# ---------------------- Functions ----------------------

# ---------------------- Utils ----------------------

def openitch(): webbrowser.open(itchme, new=1)

def opengithub(): webbrowser.open(githubme, new=1)

def opentelegram(): webbrowser.open(telegramme, new=1)

def find_by_relative_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def write_in_log_file(text_to_insert):
    log_file_name = app_name + ".log"
    with open(log_file_name,'w') as log_file: 
        os.chmod(log_file_name, 0o777)
        log_file.write(text_to_insert) 
    log_file.close()

def read_log_file():
    log_file_name = app_name + ".log"
    with open(log_file_name,'r') as log_file: 
        os.chmod(log_file_name, 0o777)
        step = log_file.readline()
    log_file.close()
    return step

def create_temp_dir(name_dir):
    if os.path.exists(name_dir): shutil.rmtree(name_dir)
    if not os.path.exists(name_dir): os.makedirs(name_dir, mode=0o777)

def prepare_filename(file_url, index, file_type):
    first_part_filename = str(file_url).split("/")[-3]

    if file_type == "image":
        extension = ".png"
    elif file_type == "video":
        extension = ".mp4"
    filename = first_part_filename + "_" + str(index) + extension

    return filename

def show_error(exception):
    import tkinter as tk
    tk.messagebox.showerror(title   = 'Error', 
                            message = 'Download failed caused by:\n\n' +
                                        str(exception) + '\n\n' +
                                        'Please report the error on Github.com or Itch.io.' +
                                        '\n\nThank you :)')

def update_process_status(actual_process_phase):
    print("> " + actual_process_phase)
    write_in_log_file(actual_process_phase) 



# ---------------------- /Utils ----------------------

# ---------------------- Core ----------------------

def process_start_download(link, cpu_number):
    dir_name      = link.split("/")[3]
    target_dir    = dir_name

    update_process_status('Preparing')
    
    try:
        create_temp_dir(target_dir)

        how_many_images = int(get_number_of_images(link))  

        list_of_index = []
        for index in range(how_many_images): list_of_index.append(index)

        update_process_status("Downloading")

        with ThreadPool(cpu_number) as pool:
            pool.starmap(thread_download_file, 
                         zip(itertools.repeat(link),
                         list_of_index,
                         itertools.repeat(target_dir)))
            
        update_process_status("Completed")

    except Exception as exception:
        update_process_status('Error while downloading' + '\n\n' + str(exception)) 
        show_error(exception)

def thread_download_file(link, index, target_dir):
    link = link + str(index)       
    model_name = link.split('/')[3]
    try:
        file_url, file_type = get_file_url(link)
        
        if model_name in file_url:
            file_name = prepare_filename(file_url, index, file_type)

            if file_type == "image":
                download_image(file_url, file_name, target_dir)
                x = 1 + "x"
            elif file_type == "video":
                download_video(file_url, file_name, target_dir)
                x = 1 + "x"
    except:
        pass

def download_image(file_url, file_name, target_dir):
    if file_url != '' and target_dir.split(os.sep)[-1] in file_url:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        
        request = urllib.request.Request(file_url, headers=headers)
        
        with urllib.request.urlopen(request) as response, open(os.path.join(target_dir, file_name), 'wb') as out_file:
            data = response.read()
            out_file.write(data)

def download_video(file_url, file_name, target_dir):
    if file_url != '' and target_dir.split(os.sep)[-1] in file_url:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        
        request = urllib.request.Request(file_url, headers=headers)
        
        with urllib.request.urlopen(request) as response, open(os.path.join(target_dir, file_name), 'wb') as out_file:
            data = response.read()
            out_file.write(data)

def thread_check_steps_download( link, how_many_files ):
    time.sleep(2)

    dir_name      = link.split("/")[3]
    target_dir    = dir_name

    try:
        while True:
            step = read_log_file()
            if "Completed" in step or "Error" in step or "Stopped" in step:
                info_message.set(step)
                stop = 1 + "x"
            elif "Downloading" in step:
                count = len(fnmatch.filter(os.listdir(target_dir), '*.*'))
                info_message.set("Downloading " + str(count) + "/" + str(how_many_files))
            else:
                info_message.set(step)

            time.sleep(2)
    except:
        place_download_button()

def get_file_url(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    file_element = soup.find("div", class_="flex justify-between items-center")

    if 'type="video/mp4' in str(file_element):
        # Video
        file_url = file_element.find("source").get("src")
        file_type = "video"
        print('> video: ' + file_url)
    else:
        # Photo
        file_url = file_element.find("img").get("src")
        file_type = "image"
        print('> image: ' + file_url)

    return file_url, file_type

def get_number_of_images(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a', href=re.compile(url)):
        link_href = link.get('href').rstrip('/')  # Remove trailing slash if present
        if link_href.split('/')[-1].isnumeric():
            return link_href.split('/')[-1]

    return None



# ---------------------- /Core ----------------------

# ---------------------- GUI related ----------------------

def download_button_command():
    global process_download
    global cpu_number

    info_message.set("Checking link")

    try:
        cpu_number = int(float(str(selected_cpu_number.get())))
    except:
        info_message.set("Cpu number must be a numeric value")
        return

    selected_link = str(selected_url.get())

    if "https://fapello.com/" in selected_link:
        info_message.set("Starting download")

        how_much_images = int(get_number_of_images(selected_link))  

        place_stop_button()
        
        process_download = multiprocessing.Process(target = process_start_download,
                                                   args   = (selected_link, cpu_number))
        process_download.start()

        thread_wait = threading.Thread( target = thread_check_steps_download,
                                        args   = (selected_link, how_much_images), 
                                        daemon = True)
        thread_wait.start()

    elif selected_link == "Paste link here https://fapello.com/emily-rat---/":
        info_message.set("Please, insert a valid Fapello link")
    else:
        info_message.set("Please, insert a valid Fapello link")

def stop_button_command():
    global process_download
    process_download.terminate()
    process_download.kill()
    
    write_in_log_file("Stopped") 

def open_info_cpu():
    info = """This widget allows you to choose how many cpus to dedicate to the app.

The default value is 4:
- the app will use 4 cpus
- the app will download 4 files simultaneously""" 
    
    tk.messagebox.showinfo(title = 'AI model', message = info)

def place_github_button():
    git_button = CTkButton(master      = window, 
                            width      = 30,
                            height     = 30,
                            fg_color   = "black",
                            text       = "", 
                            font       = bold11,
                            image      = logo_git,
                            command    = opengithub)
    git_button.place(relx = 0.835, rely = 0.1, anchor = tk.CENTER)

def place_telegram_button():
    telegram_button = CTkButton(master = window, 
                                width      = 30,
                                height     = 30,
                                fg_color   = "black",
                                text       = "", 
                                font       = bold11,
                                image      = logo_telegram,
                                command    = opentelegram)
    telegram_button.place(relx = 0.92, rely = 0.1, anchor = tk.CENTER)

def place_app_name():
    app_name_label = CTkLabel(master     = window, 
                              text       = app_name + " " + version,
                              text_color = app_name_color,
                              font       = bold20,
                              anchor     = "w")
    
    app_name_label.place(relx = 0.5, 
                         rely = 0.1, 
                         anchor = tk.CENTER)

def place_link_textbox():
    link_textbox = CTkEntry(master      = window, 
                            font       = bold11,
                            height     = 33,
                            fg_color   = "#000000",
                            textvariable = selected_url, 
                            justify     = "center")
                            
    link_textbox.place(relx = 0.5, 
                        rely = 0.3, 
                        relwidth = 0.85,  
                        anchor = tk.CENTER)

def place_cpu_textbox():
    cpu_button = CTkButton(
                            master  = window, 
                            fg_color   = "black",
                            text_color = "#89CFF0",
                            text     = "Cpu number",
                            height   = 27,
                            width    = 140,
                            font     = bold11,
                            corner_radius = 25,
                            anchor  = "center",
                            command = open_info_cpu
                            )

    cpu_textbox = CTkEntry(master      = window, 
                            font       = bold12,
                            height     = 33,
                            width      = 140,
                            fg_color   = "#000000",
                            textvariable = selected_cpu_number, 
                            justify     = "center")
    
    cpu_button.place(relx = 0.45, rely = 0.42, anchor = tk.CENTER)
    cpu_textbox.place(relx = 0.75, rely = 0.42, anchor = tk.CENTER)

def place_message_label():
    message_label = CTkLabel(master  = window, 
                            textvariable = info_message,
                            height       = 25,
                            font         = bold10,
                            fg_color     = "#ffbf00",
                            text_color   = "#000000",
                            anchor       = "center",
                            corner_radius = 25)
    message_label.place(relx = 0.5, rely = 0.78, anchor = tk.CENTER)

def place_download_button(): 
    download_button = CTkButton(master     = window, 
                                width      = 150,
                                height     = 35,
                                fg_color   = "#282828",
                                text_color = "#E0E0E0",
                                text       = "DOWNLOAD", 
                                font       = bold11,
                                image      = download_icon,
                                command    = download_button_command)
    download_button.place(relx = 0.5, rely = 0.9, anchor = tk.CENTER)
    
def place_stop_button(): 
    stop_button = CTkButton(master      = window, 
                                width      = 150,
                                height     = 35,
                                fg_color   = "#282828",
                                text_color = "#E0E0E0",
                                text       = "STOP", 
                                font       = bold11,
                                image      = stop_icon,
                                command    = stop_button_command)
    stop_button.place(relx = 0.5, rely = 0.9, anchor = tk.CENTER)



# ---------------------- /GUI related ----------------------

# ---------------------- /Functions ----------------------

class App:
    def __init__(self, window):
        window.title('')
        width        = 500
        height       = 500
        window.geometry("500x500")
        window.minsize(width, height)
        window.iconbitmap(find_by_relative_path("Assets" + os.sep + "logo.ico"))

        place_app_name()
        place_github_button()
        place_telegram_button()
        place_link_textbox()
        place_cpu_textbox()
        place_message_label()             
        place_download_button()

if __name__ == "__main__":    
    multiprocessing.freeze_support()

    set_appearance_mode("Dark")
    set_default_color_theme("dark-blue")

    window = CTk() 

    selected_url        = tk.StringVar()
    info_message        = tk.StringVar()
    selected_cpu_number = tk.StringVar()

    selected_url.set("Paste link here https://fapello.com/emily-rat---/")
    selected_cpu_number.set("4")
    info_message.set("Hi :)")


    bold8  = CTkFont(family = "Segoe UI", size = 8, weight = "bold")
    bold9  = CTkFont(family = "Segoe UI", size = 9, weight = "bold")
    bold10 = CTkFont(family = "Segoe UI", size = 10, weight = "bold")
    bold11 = CTkFont(family = "Segoe UI", size = 11, weight = "bold")
    bold12 = CTkFont(family = "Segoe UI", size = 12, weight = "bold")
    bold15 = CTkFont(family = "Segoe UI", size = 15, weight = "bold")
    bold17 = CTkFont(family = "Segoe UI", size = 17, weight = "bold")
    bold20 = CTkFont(family = "Segoe UI", size = 20, weight = "bold")
    bold21 = CTkFont(family = "Segoe UI", size = 21, weight = "bold")

    download_icon   = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "download_icon.png")), size=(15, 15))
    stop_icon   = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "stop_icon.png")), size=(15, 15))
    logo_git   = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "github_logo.png")), size=(15, 15))
    logo_itch  = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "itch_logo.png")),  size=(13, 13))
    logo_telegram = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "telegram_logo.png")),  size=(15, 15))
    
    app = App(window)
    window.update()
    window.mainloop()
    

