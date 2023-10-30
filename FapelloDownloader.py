

# Standard library imports
import sys
from threading     import Thread
from shutil        import rmtree
from time          import sleep
from webbrowser    import open as open_browser
from warnings      import filterwarnings as warnings_filterwarnings
from bs4           import BeautifulSoup

from multiprocessing import ( 
    Process, 
    freeze_support
)

from itertools import repeat as itertools_repeat
from multiprocessing.pool import ThreadPool

from os import (
    sep         as os_separator,
    chmod       as os_chmod,
    makedirs    as os_makedirs,
    remove      as os_remove,
    listdir     as os_listdir
)

from os.path import (
    dirname  as os_path_dirname,
    abspath  as os_path_abspath,
    join     as os_path_join,
    exists   as os_path_exists,
    splitext as os_path_splitext
)


# Third-party library imports
from PIL.Image import open as pillow_image_open
from requests  import get as requests_get
from fnmatch   import filter as fnmatch_filter
from re        import compile as re_compile
from urllib.request import Request, urlopen


# GUI imports
from tkinter import StringVar, CENTER
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFont,
    CTkImage,
    CTkLabel,
    CTkToplevel,
    set_appearance_mode,
    set_default_color_theme,
)

warnings_filterwarnings("ignore")

app_name = "Fapello.Downloader"
version  = "3.2"

text_color      = "#F0F0F0"
app_name_color  = "#ffbf00"
 
githubme        = "https://github.com/Djdefrag/Fapello.Downloader"
telegramme      = "https://linktr.ee/j3ngystudio"
qs_link         = "https://jangystudio.itch.io/qualityscaler"

log_file_path  = f"{app_name}.log"


# GUI

class CTkMessageBox(CTkToplevel):
    def __init__(self,
                 title: str = "CTkDialog",
                 text: str = "CTkDialog",
                 type: str = "info"):

        super().__init__()

        self._running: bool = False
        self._title = title
        self._text = text
        self.type = type

        self.title('')
        self.lift()                          # lift window on top
        self.attributes("-topmost", True)    # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()                       # make other windows not clickable

    def _create_widgets(self):

        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._text = '\n' + self._text +'\n'

        if self.type == "info":
            color_for_messagebox_title = "#0096FF"
        elif self.type == "error":
            color_for_messagebox_title = "#ff1a1a"


        self._titleLabel = CTkLabel(master  = self,
                                    width      = 500,
                                    anchor     = 'w',
                                    justify    = "left",
                                    fg_color   = "transparent",
                                    text_color = color_for_messagebox_title,
                                    font       = bold24,
                                    text       = self._title)
        
        self._titleLabel.grid(row=0, column=0, columnspan=2, padx=30, pady=20, sticky="ew")

        self._label = CTkLabel(master = self,
                                width      = 550,
                                wraplength = 550,
                                corner_radius = 10,
                                anchor     = 'w',
                                justify    = "left",
                                text_color = "#C0C0C0",
                                bg_color   = "transparent",
                                fg_color   = "#303030",
                                font       = bold12,
                                text       = self._text)
        
        self._label.grid(row=1, column=0, columnspan=2, padx=30, pady=5, sticky="ew")

        self._ok_button = CTkButton(master  = self,
                                    command = self._ok_event,
                                    text    = 'OK',
                                    width   = 125,
                                    font         = bold11,
                                    border_width = 1,
                                    fg_color     = "#282828",
                                    text_color   = "#E0E0E0",
                                    border_color = "#0096FF")
        
        self._ok_button.grid(row=2, column=1, columnspan=1, padx=(10, 20), pady=(10, 20), sticky="e")

    def _ok_event(self, event = None):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

def create_info_button(command, text):
    return CTkButton(master  = window, 
                    command  = command,
                    text          = text,
                    fg_color      = "transparent",
                    text_color    = "#C0C0C0",
                    anchor        = "w",
                    height        = 23,
                    width         = 150,
                    corner_radius = 12,
                    font          = bold12,
                    image         = info_icon)

def create_text_box(textvariable, width, heigth):
    return CTkEntry(master        = window, 
                    textvariable  = textvariable,
                    border_width  = 1,
                    width         = width,
                    height        = heigth,
                    font          = bold10,
                    justify       = "center",
                    fg_color      = "#000000",
                    border_color  = "#404040")



# Utils 

def opengithub():   
    open_browser(githubme, new=1)

def opentelegram(): 
    open_browser(telegramme, new=1)

def openqualityscaler():
    open_browser(qs_link, new=1)

def find_by_relative_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os_path_dirname(os_path_abspath(__file__)))
    return os_path_join(base_path, relative_path)

def remove_file(file_name): 
    if os_path_exists(file_name): 
        os_remove(file_name)

def remove_dir(name_dir):
    if os_path_exists(name_dir): 
        rmtree(name_dir)

def create_temp_dir(name_dir):
    if os_path_exists(name_dir): 
        rmtree(name_dir)
    if not os_path_exists(name_dir): 
        os_makedirs(name_dir, mode=0o777)

def write_in_log_file(text_to_insert):
    with open(log_file_path,'w') as log_file: 
        os_chmod(log_file_path, 0o777)
        log_file.write(text_to_insert) 
    log_file.close()

def read_log_file():
    with open(log_file_path,'r') as log_file: 
        os_chmod(log_file_path, 0o777)
        step = log_file.readline()
    log_file.close()
    return step

def remove_temp_files():
    remove_file(log_file_path)

def stop_thread(): 
    stop = 1 + "x"

def prepare_filename(file_url, index, file_type):
    first_part_filename = str(file_url).split("/")[-3]

    if   file_type == "image": extension = ".png"
    elif file_type == "video": extension = ".mp4"

    filename = first_part_filename + "_" + str(index) + extension

    return filename

def show_error_message(exception):
    messageBox_title = "Download error"

    messageBox_text  = str(exception) + "\n\n" + "Please report the error on Github/Telegram"

    CTkMessageBox(text = messageBox_text, title = messageBox_title, type = "error")

def update_process_status(actual_process_phase):
    print("> " + actual_process_phase)
    write_in_log_file(actual_process_phase) 

def count_files_in_directory(target_dir):
    return len(fnmatch_filter(os_listdir(target_dir), '*.*'))

def thread_check_steps_download(link, how_many_files):
    sleep(3)
    target_dir = link.split("/")[3]

    try:
        while True:
            actual_step = read_log_file()

            if "Completed" in actual_step or "Stopped" in actual_step:
                info_message.set(actual_step)
                remove_temp_files()
                stop_thread()

            elif "Error" in actual_step:
                info_message.set("Error while downloading :()")
                error_info = actual_step.replace("Error while downloading", "")
                show_error_message(error_info)
                remove_temp_files()
                stop_thread()

            elif "Downloading" in actual_step:
                file_count = count_files_in_directory(target_dir)
                info_message.set("Downloading " + str(file_count) + "/" + str(how_many_files))
            
            else:
                info_message.set(actual_step)

            sleep(2)
    except:
        place_download_button()



# Core

def download_button_command():
    global process_download
    global cpu_number

    info_message.set("Starting download")
    update_process_status("Starting download")

    try:
        cpu_number = int(float(str(selected_cpu_number.get())))
    except:
        info_message.set("Cpu number must be a numeric value")
        return


    selected_link = str(selected_url.get()).strip()

    if "https://fapello.com" in selected_link:

        download_type = 'fapello.com'

        if not selected_link.endswith("/"): 
            selected_link = selected_link + '/'

        how_many_images = get_Fapello_files_number(selected_link)
        
        process_download = Process(target = process_start_download,
                                   args   = (selected_link, cpu_number))
        process_download.start()

        thread_wait = Thread(target = thread_check_steps_download,
                            args   = (selected_link, how_many_images), 
                            daemon = True)
        thread_wait.start()

        place_stop_button()

    else:
        info_message.set("Insert a valid Fapello.com link")

def stop_button_command():
    global process_download
    process_download.terminate()
    process_download.join()
    
    write_in_log_file("Stopped") 

def get_Fapello_file_url(link):
    page = requests_get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    file_element = soup.find("div", class_="flex justify-between items-center")

    try: 
        if 'type="video/mp4' in str(file_element):
            file_url  = file_element.find("source").get("src")
            file_type = "video"
            print('> Fapello video: ' + file_url)
        else:
            file_url  = file_element.find("img").get("src")
            file_type = "image"
            print('> Fapello image: ' + file_url)

        return file_url, file_type
    except:
        return None, None

def get_Fapello_files_number(url):
    page = requests_get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a', href = re_compile(url)):
        link_href = link.get('href').rstrip('/')  # Remove trailing slash if present
        if link_href.split('/')[-1].isnumeric():
            return int(link_href.split('/')[-1]) + 1

    return None

def thread_download_file(link, target_dir, index):
    headers    = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36" }
    link       = link + str(index)       
    model_name = link.split('/')[3]

    file_url, file_type = get_Fapello_file_url(link)

    if file_url != None:
        try:        
            file_name = prepare_filename(file_url, index, file_type)
            request   = Request(file_url, headers=headers)
            
            with urlopen(request) as response:
                with open(os_path_join(target_dir, file_name), 'wb') as output_file:
                    output_file.write(response.read())

            stop_thread()
        except:
            pass

def process_start_download(link, cpu_number):
    target_dir    = link.split("/")[3]
    list_of_index = []

    update_process_status("Downloading")
    
    try:
        create_temp_dir(target_dir)
        how_many_images = get_Fapello_files_number(link)
        list_of_index   = [index for index in range(how_many_images)]

        with ThreadPool(cpu_number) as pool:
            pool.starmap(thread_download_file, 
                            zip(
                                itertools_repeat(link),
                                itertools_repeat(target_dir),
                                list_of_index)
                                )
            
        update_process_status("Completed")

    except Exception as exception:
        update_process_status('Error while downloading' + '\n\n' + str(exception)) 



#  GUI related 

def place_github_button():
    git_button = CTkButton(master      = window, 
                            command    = opengithub,
                            image      = logo_git,
                            width         = 30,
                            height        = 30,
                            border_width  = 1,
                            fg_color      = "transparent",
                            text_color    = "#C0C0C0",
                            border_color  = "#404040",
                            anchor        = "center",                           
                            text          = "", 
                            font          = bold11)
    
    git_button.place(relx = 0.055, rely = 0.875, anchor = CENTER)

def place_telegram_button():
    telegram_button = CTkButton(master     = window, 
                                image      = logo_telegram,
                                command    = opentelegram,
                                width         = 30,
                                height        = 30,
                                border_width  = 1,
                                fg_color      = "transparent",
                                text_color    = "#C0C0C0",
                                border_color  = "#404040",
                                anchor        = "center",                           
                                text          = "", 
                                font          = bold11)
    telegram_button.place(relx = 0.055, rely = 0.95, anchor = CENTER)
 
def place_qualityscaler_button():
    qualityscaler_button = CTkButton(master    = window, 
                                    image      = logo_qs,
                                    command    = openqualityscaler,
                                    width         = 30,
                                    height        = 30,
                                    border_width  = 1,
                                    fg_color      = "transparent",
                                    text_color    = "#C0C0C0",
                                    border_color  = "#404040",
                                    anchor        = "center",                           
                                    text          = "", 
                                    font          = bold11)
    qualityscaler_button.place(relx = 0.055, rely = 0.8, anchor = CENTER)

def open_info_simultaneous_downloads():
    messageBox_title = "Simultaneous downloads"

    messageBox_text = """This widget allows you to choose how many files you can download simultaneously with the app.

• default value is 4"""

    CTkMessageBox(text = messageBox_text, title = messageBox_title)

def place_app_name():
    app_name_label = CTkLabel(master     = window, 
                              text       = app_name + " " + version,
                              text_color = app_name_color,
                              font       = bold20,
                              anchor     = "w")
    
    app_name_label.place(relx = 0.5, 
                         rely = 0.1, 
                         anchor = CENTER)

def place_link_textbox():
    link_textbox = create_text_box(selected_url, 150, 32)
    link_textbox.place(relx = 0.5, rely = 0.3, relwidth = 0.85, anchor = CENTER)

def place_simultaneous_downloads_textbox():
    cpu_button = create_info_button(open_info_simultaneous_downloads, "Simultaneous downloads")
    cpu_textbox = create_text_box(selected_cpu_number, 110, 32)

    cpu_button.place(relx = 0.42, rely = 0.42, anchor = CENTER)
    cpu_textbox.place(relx = 0.75, rely = 0.42, anchor = CENTER)

def place_message_label():
    message_label = CTkLabel(master  = window, 
                            textvariable = info_message,
                            height       = 25,
                            font         = bold10,
                            fg_color     = "#ffbf00",
                            text_color   = "#000000",
                            anchor       = "center",
                            corner_radius = 25)
    message_label.place(relx = 0.5, rely = 0.78, anchor = CENTER)

def place_download_button(): 
    download_button = CTkButton(master     = window, 
                                command    = download_button_command,
                                text       = "DOWNLOAD",
                                image      = download_icon,
                                width      = 140,
                                height     = 32,
                                font       = bold11,
                                border_width = 1,
                                fg_color     = "#282828",
                                text_color   = "#E0E0E0",
                                border_color = "#0096FF")
    download_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)
    
def place_stop_button(): 
    stop_button = CTkButton(master     = window, 
                            command    = stop_button_command,
                            text       = "STOP",
                            image      = stop_icon,
                            width      = 140,
                            height     = 32,
                            font       = bold11,
                            border_width = 1,
                            fg_color     = "#282828",
                            text_color   = "#E0E0E0",
                            border_color = "#0096FF")
    stop_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)



# Main functions ---------------------------

def on_app_close():
    window.grab_release()
    window.destroy()

    global process_download
    try:
        process_download
    except: 
        pass
    else:
        process_download.terminate()
        process_download.join()

    remove_temp_files()

class App:
    def __init__(self, window):
        window.title('')
        width        = 500
        height       = 500
        window.geometry("500x500")
        window.minsize(width, height)
        window.iconbitmap(find_by_relative_path("Assets" + os_separator + "logo.ico"))

        window.protocol("WM_DELETE_WINDOW", on_app_close)


        place_app_name()
        place_qualityscaler_button()
        place_github_button()
        place_telegram_button()
        place_link_textbox()
        place_simultaneous_downloads_textbox()
        place_message_label()             
        place_download_button()

if __name__ == "__main__":    
    freeze_support()

    set_appearance_mode("Dark")
    set_default_color_theme("dark-blue")

    window = CTk() 

    selected_url        = StringVar()
    info_message        = StringVar()
    selected_cpu_number = StringVar()

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
    bold24 = CTkFont(family = "Segoe UI", size = 24, weight = "bold")
    
    # Images
    logo_git       = CTkImage(pillow_image_open(find_by_relative_path(f"Assets{os_separator}github_logo.png")),    size=(15, 15))
    logo_telegram  = CTkImage(pillow_image_open(find_by_relative_path(f"Assets{os_separator}telegram_logo.png")),  size=(15, 15))
    stop_icon      = CTkImage(pillow_image_open(find_by_relative_path(f"Assets{os_separator}stop_icon.png")),      size=(15, 15))
    info_icon      = CTkImage(pillow_image_open(find_by_relative_path(f"Assets{os_separator}info_icon.png")),      size=(14, 14))
    download_icon  = CTkImage(pillow_image_open(find_by_relative_path(f"Assets{os_separator}download_icon.png")), size=(15, 15))
    logo_qs        = CTkImage(pillow_image_open(find_by_relative_path(f"Assets{os_separator}qs_logo.png")),  size=(15, 15))

    app = App(window)
    window.update()
    window.mainloop()
    

