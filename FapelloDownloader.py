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
                           set_appearance_mode,
                           set_default_color_theme)
from PIL import Image

warnings.filterwarnings("ignore")

app_name = "Fapello.Downloader"
version  = "3.1"

text_color      = "#F0F0F0"
app_name_color  = "#ffbf00"
 
githubme     = "https://github.com/Djdefrag/Fapello.Downloader"
telegramme   = "https://linktr.ee/j3ngystudio"

log_file_path  = f"{app_name}.log"

# Utils 

def opengithub(): webbrowser.open(githubme, new=1)

def opentelegram(): webbrowser.open(telegramme, new=1)

def write_in_log_file(text_to_insert):
    with open(log_file_path,'w') as log_file: 
        os.chmod(log_file_path, 0o777)
        log_file.write(text_to_insert) 
    log_file.close()

def read_log_file():
    with open(log_file_path,'r') as log_file: 
        os.chmod(log_file_path, 0o777)
        step = log_file.readline()
    log_file.close()
    return step

def find_by_relative_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def create_temp_dir(name_dir):
    if os.path.exists(name_dir): shutil.rmtree(name_dir)
    if not os.path.exists(name_dir): os.makedirs(name_dir, mode=0o777)

def prepare_filename(file_url, index, file_type):
    first_part_filename = str(file_url).split("/")[-3]

    if file_type == "image":   extension = ".png"
    elif file_type == "video": extension = ".mp4"

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

def stop_thread(): stop = 1 + "x"

def remove_file(name_file): 
    if os.path.exists(name_file): os.remove(name_file)

def remove_temp_files(): remove_file(log_file_path)



# Core

def get_file_url(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    file_element = soup.find("div", class_="flex justify-between items-center")

    if 'type="video/mp4' in str(file_element):
        file_url = file_element.find("source").get("src")
        file_type = "video"
        print('> video: ' + file_url)
    else:
        file_url = file_element.find("img").get("src")
        file_type = "image"
        print('> image: ' + file_url)

    return file_url, file_type

def get_number_of_files_to_download(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a', href=re.compile(url)):
        link_href = link.get('href').rstrip('/')  # Remove trailing slash if present
        if link_href.split('/')[-1].isnumeric():
            return int(link_href.split('/')[-1]) + 1

    return None

def count_files_in_directory(target_dir):
    return len(fnmatch.filter(os.listdir(target_dir), '*.*'))

def thread_check_steps_download(link, how_many_files):
    time.sleep(2)
    target_dir = link.split("/")[3]
    try:
        while True:
            step = read_log_file()
            if "Completed" in step or "Error" in step or "Stopped" in step:
                info_message.set(step)
                remove_temp_files()
                stop_thread()
            elif "Downloading" in step:
                file_count = count_files_in_directory(target_dir)
                info_message.set("Downloading " + str(file_count) + "/" + str(how_many_files))
            else:
                info_message.set(step)

            time.sleep(2)
    except:
        place_download_button()

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

        if not selected_link.endswith("/"): selected_link = selected_link + '/'

        info_message.set("Starting download")

        how_many_images = get_number_of_files_to_download(selected_link)

        place_stop_button()
        
        process_download = multiprocessing.Process(target = process_start_download,
                                                   args   = (selected_link, cpu_number))
        process_download.start()

        thread_wait = threading.Thread( target = thread_check_steps_download,
                                        args   = (selected_link, how_many_images), 
                                        daemon = True)
        thread_wait.start()

    else:
        info_message.set("Insert a valid Fapello.com link")

def stop_button_command():
    global process_download
    process_download.terminate()
    process_download.join()
    
    write_in_log_file("Stopped") 

def process_start_download(link, cpu_number):
    target_dir    = link.split("/")[3]
    list_of_index = []

    update_process_status('Preparing')
    
    try:
        create_temp_dir(target_dir)

        how_many_images = get_number_of_files_to_download(link)

        for index in range(how_many_images): list_of_index.append(index)

        update_process_status("Downloading")

        with ThreadPool(cpu_number) as pool:
            pool.starmap(thread_download_file, 
                         zip(
                             itertools.repeat(link),
                             itertools.repeat(target_dir),
                             list_of_index)
                             )
            
        update_process_status("Completed")

    except Exception as exception:
        update_process_status('Error while downloading' + '\n\n' + str(exception)) 
        show_error(exception)

def thread_download_file(link, target_dir, index):
    link = link + str(index)       
    model_name = link.split('/')[3]
    try:
        file_url, file_type = get_file_url(link)
        
        if model_name in file_url:
            file_name = prepare_filename(file_url, index, file_type)

            download_file(file_url, file_name, target_dir)
            stop_thread()
    except:
        pass

def download_file(file_url, file_name, target_dir):
    if file_url != '' and target_dir.split(os.sep)[-1] in file_url:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        
        request = urllib.request.Request(file_url, headers=headers)
        
        with urllib.request.urlopen(request) as response, open(os.path.join(target_dir, file_name), 'wb') as out_file:
            data = response.read()
            out_file.write(data)




#  GUI related 

def place_github_button():
    git_button = CTkButton(master      = window, 
                            width      = 30,
                            height     = 30,
                            fg_color   = "black",
                            text       = "", 
                            font       = bold11,
                            image      = logo_git,
                            command    = opengithub)
    
    git_button.place(relx = 0.055, rely = 0.875, anchor = tk.CENTER)

def place_telegram_button():
    telegram_button = CTkButton(master     = window, 
                                width      = 30,
                                height     = 30,
                                fg_color   = "black",
                                text       = "", 
                                font       = bold11,
                                image      = logo_telegram,
                                command    = opentelegram)
    telegram_button.place(relx = 0.055, rely = 0.95, anchor = tk.CENTER)
 
def open_info_simultaneous_downloads():
    info = """This widget allows you to choose how many files you can download simultaneously with the app.

• The default value is 4"""
    
    tk.messagebox.showinfo(title = 'AI model', message = info)

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
                            text     = "Simultaneous downloads",
                            height   = 27,
                            width    = 140,
                            font     = bold11,
                            corner_radius = 25,
                            anchor  = "center",
                            command = open_info_simultaneous_downloads
                            )

    cpu_textbox = CTkEntry(master      = window, 
                            font       = bold12,
                            height     = 33,
                            width      = 140,
                            fg_color   = "#000000",
                            textvariable = selected_cpu_number, 
                            justify     = "center")
    
    cpu_button.place(relx = 0.42, rely = 0.42, anchor = tk.CENTER)
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
    stop_icon       = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "stop_icon.png")), size=(15, 15))
    logo_git        = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "github_logo.png")), size=(15, 15))
    logo_telegram   = CTkImage(Image.open(find_by_relative_path("Assets" + os.sep + "telegram_logo.png")),  size=(15, 15))
    
    app = App(window)
    window.update()
    window.mainloop()
    

