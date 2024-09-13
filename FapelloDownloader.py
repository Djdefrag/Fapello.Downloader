

# Standard library imports
import sys
from time       import sleep
from webbrowser import open as open_browser
from warnings   import filterwarnings

from multiprocessing import ( 
    Process, 
    Queue          as multiprocessing_Queue,
    freeze_support as multiprocessing_freeze_support
)
from typing    import Callable
from shutil    import rmtree as remove_directory
from itertools import repeat as itertools_repeat
from threading import Thread
from multiprocessing.pool import ThreadPool

from os import (
    sep         as os_separator,
    makedirs    as os_makedirs,
    listdir     as os_listdir
)

from os.path import (
    dirname  as os_path_dirname,
    abspath  as os_path_abspath,
    join     as os_path_join,
    exists   as os_path_exists,
)


# Third-party library imports
from re             import compile as re_compile
from requests       import get as requests_get
from fnmatch        import filter as fnmatch_filter
from PIL.Image      import open as pillow_image_open
from bs4            import BeautifulSoup
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

filterwarnings("ignore")

app_name = "Fapello.Downloader"
version  = "3.6"

text_color      = "#F0F0F0"
app_name_color  = "#ffbf00"
 
githubme        = "https://github.com/Djdefrag/Fapello.Downloader"
telegramme      = "https://linktr.ee/j3ngystudio"
qs_link         = "https://github.com/Djdefrag/QualityScaler"

COMPLETED_STATUS   = "Completed"
DOWNLOADING_STATUS = "Downloading"
ERROR_STATUS       = "Error"
STOP_STATUS        = "Stop"

HEADERS_FOR_REQUESTS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36" }

# Utils 

def opengithub() -> None: open_browser(githubme, new=1)

def opentelegram() -> None: open_browser(telegramme, new=1)

def openqualityscaler() -> None: open_browser(qs_link, new=1)

def find_by_relative_path(relative_path: str) -> str:
    base_path = getattr(sys, '_MEIPASS', os_path_dirname(os_path_abspath(__file__)))
    return os_path_join(base_path, relative_path)

def create_temp_dir(name_dir: str) -> None:
    if os_path_exists(name_dir): remove_directory(name_dir)
    if not os_path_exists(name_dir): os_makedirs(name_dir, mode=0o777)

def stop_thread() -> None: 
    stop = 1 + "x"

def prepare_filename(file_url, index, file_type) -> str:
    first_part_filename = str(file_url).split("/")[-3]

    if   file_type == "image": extension = ".jpg"
    elif file_type == "video": extension = ".mp4"

    filename = first_part_filename + "_" + str(index) + extension

    return filename

def show_error_message(exception: str) -> None:
  
    messageBox_title    = "Download error"
    messageBox_subtitle = "Please report the error on Github or Telegram"
    messageBox_text     = f" {str(exception)} "

    CTkMessageBox(
        messageType   = "error", 
        title         = messageBox_title, 
        subtitle      = messageBox_subtitle,
        default_value = None,
        option_list   = [messageBox_text]
    )

def read_process_status() -> None:
    actual_step = processing_queue.get()

    if actual_step == DOWNLOADING_STATUS:
        write_process_status(processing_queue, DOWNLOADING_STATUS)

    return actual_step

def write_process_status(
        processing_queue: multiprocessing_Queue,
        step: str
        ) -> None:
    
    while not processing_queue.empty(): processing_queue.get()
    processing_queue.put(f"{step}")

def count_files_in_directory(target_dir: str) -> int:
    return len(fnmatch_filter(os_listdir(target_dir), '*.*'))

def thread_check_steps_download(
        link: str, 
        how_many_files: int
        ) -> None:
    
    sleep(1)
    target_dir = link.split("/")[3]

    try:
        while True:
            actual_step = read_process_status()

            if actual_step == COMPLETED_STATUS:
                info_message.set(f"Download completed! :)")
                stop_thread()

            elif actual_step == DOWNLOADING_STATUS:
                file_count = count_files_in_directory(target_dir)
                info_message.set(f"Downloading {str(file_count)} / {str(how_many_files)}")
                
            elif actual_step == STOP_STATUS:
                info_message.set(f"Download stopped")
                stop_thread()

            elif ERROR_STATUS in actual_step:
                error_message = f"Error while downloading :("
                info_message.set(error_message)

                error = actual_step.replace(ERROR_STATUS, "")
                show_error_message(error)
                stop_thread()

            else:
                info_message.set(actual_step)
                
            sleep(1)    
    except:
        place_download_button()



# Core

def check_button_command() -> None:

    selected_link = str(selected_url.get()).strip()

    if selected_link == "Paste link here https://fapello.com/emily-rat---/": info_message.set("Insert a valid Fapello.com link")

    elif selected_link == "": info_message.set("Insert a valid Fapello.com link")

    elif "https://fapello.com" in selected_link:

        if not selected_link.endswith("/"): selected_link = selected_link + '/'

        how_many_files = get_Fapello_files_number(selected_link)

        if how_many_files == 0:
            info_message.set("No files found for this link")
        else: 
            info_message.set(f"Found {how_many_files} files for this link")

    else: info_message.set("Insert a valid Fapello.com link")

def download_button_command() -> None:
    global process_download
    global cpu_number
    global processing_queue

    info_message.set("Starting download")
    write_process_status(processing_queue, "Starting download")

    try: cpu_number = int(float(str(selected_cpu_number.get())))
    except:
        info_message.set("Cpu number must be a numeric value")
        return

    selected_link = str(selected_url.get()).strip()

    if selected_link == "Paste link here https://fapello.com/emily-rat---/":
        info_message.set("Insert a valid Fapello.com link")

    elif selected_link == "":
        info_message.set("Insert a valid Fapello.com link")

    elif "https://fapello.com" in selected_link:

        download_type = 'fapello.com'

        if not selected_link.endswith("/"): selected_link = selected_link + '/'

        how_many_images = get_Fapello_files_number(selected_link)

        if how_many_images == 0:
            info_message.set("No files found for this link")
        else: 
            process_download = Process(
                target = download_orchestrator,
                args = (
                    processing_queue,
                    selected_link, 
                    cpu_number
                    )
                )
            process_download.start()

            thread_wait = Thread(
                target = thread_check_steps_download,
                args = (
                    selected_link, 
                    how_many_images
                    )
                )
            thread_wait.start()

            place_stop_button()

    else:
        info_message.set("Insert a valid Fapello.com link")

def stop_download_process() -> None:
    global process_download
    try:
        process_download
    except:
        pass
    else:
        process_download.kill()

def stop_button_command() -> None:
    stop_download_process()
    write_process_status(processing_queue, f"{STOP_STATUS}") 

def get_Fapello_file_url(link: str) -> tuple:
    
    page = requests_get(link, headers = HEADERS_FOR_REQUESTS)
    soup = BeautifulSoup(page.content, "html.parser")
    file_element = soup.find("div", class_="flex justify-between items-center")
    try: 
        if 'type="video/mp4' in str(file_element):
            file_url  = file_element.find("source").get("src")
            file_type = "video"
            print(f" > Video: {file_url}")
        else:
            file_url  = file_element.find("img").get("src")
            file_type = "image"
            print(f" > Image: {file_url}")

        return file_url, file_type
    except:
        return None, None

def get_Fapello_files_number(url: str) -> int:
    
    page = requests_get(url, headers = HEADERS_FOR_REQUESTS)
    soup = BeautifulSoup(page.content, "html.parser")

    all_href_links = soup.find_all('a', href = re_compile(url))

    for link in all_href_links:
        link_href          = link.get('href')
        link_href_stripped = link_href.rstrip('/')
        link_href_numeric  = link_href_stripped.split('/')[-1]
        if link_href_numeric.isnumeric():
            print(f"> Found {link_href_numeric} files")
            return int(link_href_numeric) + 1

    return 0

def thread_download_file(
        link: str, 
        target_dir: str, 
        index: int
        ) -> None:
    
    link       = link + str(index)       
    model_name = link.split('/')[3]

    file_url, file_type = get_Fapello_file_url(link)

    if file_url != None and model_name in file_url:
        try:        
            file_name = prepare_filename(file_url, index, file_type)
            file_path = os_path_join(target_dir, file_name)

            request  = Request(file_url, headers = HEADERS_FOR_REQUESTS)
            response = urlopen(request)

            with open(file_path, 'wb') as output_file: output_file.write(response.read())

        except:
            pass
                
def download_orchestrator(
        processing_queue: multiprocessing_Queue,
        selected_link: str, 
        cpu_number: int
        ):
    
    target_dir    = selected_link.split("/")[3]
    list_of_index = []

    write_process_status(processing_queue, DOWNLOADING_STATUS)
    
    try:
        create_temp_dir(target_dir)
        how_many_files = get_Fapello_files_number(selected_link)
        list_of_index  = [index for index in range(how_many_files)]
        
        with ThreadPool(cpu_number) as pool:
            pool.starmap(
                thread_download_file,
                zip(
                    itertools_repeat(selected_link), 
                    itertools_repeat(target_dir), 
                    list_of_index
                ) 
            )
            
        write_process_status(processing_queue, COMPLETED_STATUS)

    except Exception as error:
        print(error) 
        pass



#  UI function 

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
    qualityscaler_button = CTkButton(
        master = window, 
        image  = logo_qs,
        command = openqualityscaler,
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

    CTkMessageBox(
        messageType = 'info',
        title = "Simultaneous downloads",
        subtitle = "This widget allows to choose how many files are downloaded simultaneously",
        default_value = "6",
        option_list = []
    )

def open_info_tips():
    CTkMessageBox(
        messageType   = 'info',
        title         = "Connection tips",
        subtitle      = "In case of problems with reaching the website, follow these tips",
        default_value = None,
        option_list   = [
            " Many internet providers block access to websites such as fapello.com",
            " In this case you can use custom DNS or use a VPN",

            "\n To facilitate there is a free program called DNSJumper\n" +
            "    • it can find the best custom DNS for your internet line and set them directly\n" + 
            "    • it can quickly revert to the default DNS in case of problems \n" + 
            "    • has also a useful function called DNS Flush that solves problems connecting to the Fapello.com \n",

            " On some occasions, the download may freeze, just stop and restart the download"
        ]
    )

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
    link_textbox.place(relx = 0.435, rely = 0.3, relwidth = 0.7, anchor = CENTER)

def place_check_button():
    check_button = CTkButton(
        master     = window, 
        command    = check_button_command,
        text       = "CHECK",
        width      = 60,
        height     = 30,
        font       = bold11,
        border_width = 1,
        fg_color     = "#282828",
        text_color   = "#E0E0E0",
        border_color = "#0096FF"
    )
    check_button.place(relx = 0.865, rely = 0.3, anchor = CENTER)

def place_simultaneous_downloads_textbox():
    cpu_button  = create_info_button(open_info_simultaneous_downloads, "Simultaneous downloads")
    cpu_textbox = create_text_box(selected_cpu_number, 110, 32)

    cpu_button.place(relx = 0.42, rely = 0.42, anchor = CENTER)
    cpu_textbox.place(relx = 0.75, rely = 0.42, anchor = CENTER)

def place_tips():
    tips_button = create_info_button(open_info_tips, "Connection tips", width = 110)
    tips_button.place(relx = 0.8, rely = 0.9, anchor = CENTER)

def place_message_label():
    message_label = CTkLabel(
        master  = window, 
        textvariable = info_message,
        height       = 25,
        font         = bold11,
        fg_color     = "#ffbf00",
        text_color   = "#000000",
        anchor       = "center",
        corner_radius = 25
    )
    message_label.place(relx = 0.5, rely = 0.78, anchor = CENTER)

def place_download_button(): 
    download_button = CTkButton(
        master     = window, 
        command    = download_button_command,
        text       = "DOWNLOAD",
        image      = download_icon,
        width      = 140,
        height     = 30,
        font       = bold11,
        border_width = 1,
        fg_color     = "#282828",
        text_color   = "#E0E0E0",
        border_color = "#0096FF"
    )
    download_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)
    
def place_stop_button(): 
    stop_button = CTkButton(
        master     = window, 
        command    = stop_button_command,
        text       = "STOP",
        image      = stop_icon,
        width      = 140,
        height     = 30,
        font       = bold11,
        border_width = 1,
        fg_color     = "#282828",
        text_color   = "#E0E0E0",
        border_color = "#0096FF"
    )
    stop_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)



# Main/GUI functions ---------------------------

def on_app_close() -> None:
    window.grab_release()
    window.destroy()
    stop_download_process()

class CTkMessageBox(CTkToplevel):

    def __init__(
            self,
            messageType: str,
            title: str,
            subtitle: str,
            default_value: str,
            option_list: list,
            ) -> None:

        super().__init__()

        self._running: bool = False

        self._messageType = messageType
        self._title = title        
        self._subtitle = subtitle
        self._default_value = default_value
        self._option_list = option_list
        self._ctkwidgets_index = 0

        self.title('')
        self.lift()                          # lift window on top
        self.attributes("-topmost", True)    # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()                       # make other windows not clickable

    def _ok_event(
            self, 
            event = None
            ) -> None:
        self.grab_release()
        self.destroy()

    def _on_closing(
            self
            ) -> None:
        self.grab_release()
        self.destroy()

    def createEmptyLabel(
            self
            ) -> CTkLabel:
        
        return CTkLabel(master = self, 
                        fg_color = "transparent",
                        width    = 500,
                        height   = 17,
                        text     = '')

    def placeInfoMessageTitleSubtitle(
            self,
            ) -> None:

        spacingLabel1 = self.createEmptyLabel()
        spacingLabel2 = self.createEmptyLabel()

        if self._messageType == "info":
            title_subtitle_text_color = "#3399FF"
        elif self._messageType == "error":
            title_subtitle_text_color = "#FF3131"

        titleLabel = CTkLabel(
            master     = self,
            width      = 500,
            anchor     = 'w',
            justify    = "left",
            fg_color   = "transparent",
            text_color = title_subtitle_text_color,
            font       = bold22,
            text       = self._title
            )
        
        if self._default_value != None:
            defaultLabel = CTkLabel(
                master     = self,
                width      = 500,
                anchor     = 'w',
                justify    = "left",
                fg_color   = "transparent",
                text_color = "#3399FF",
                font       = bold17,
                text       = f"Default: {self._default_value}"
                )
        
        subtitleLabel = CTkLabel(
            master     = self,
            width      = 500,
            anchor     = 'w',
            justify    = "left",
            fg_color   = "transparent",
            text_color = title_subtitle_text_color,
            font       = bold14,
            text       = self._subtitle
            )
        
        spacingLabel1.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = "ew")
        
        self._ctkwidgets_index += 1
        titleLabel.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 25, pady = 0, sticky = "ew")
        
        if self._default_value != None:
            self._ctkwidgets_index += 1
            defaultLabel.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 25, pady = 0, sticky = "ew")
        
        self._ctkwidgets_index += 1
        subtitleLabel.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 25, pady = 0, sticky = "ew")
        
        self._ctkwidgets_index += 1
        spacingLabel2.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = "ew")

    def placeInfoMessageOptionsText(
            self,
            ) -> None:
        
        for option_text in self._option_list:
            optionLabel = CTkLabel(master = self,
                                    width  = 600,
                                    height = 45,
                                    corner_radius = 6,
                                    anchor     = 'w',
                                    justify    = "left",
                                    text_color = "#C0C0C0",
                                    fg_color   = "#282828",
                                    bg_color   = "transparent",
                                    font       = bold12,
                                    text       = option_text)
            
            self._ctkwidgets_index += 1
            optionLabel.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 25, pady = 4, sticky = "ew")

        spacingLabel3 = self.createEmptyLabel()

        self._ctkwidgets_index += 1
        spacingLabel3.grid(row = self._ctkwidgets_index, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = "ew")

    def placeInfoMessageOkButton(
            self
            ) -> None:
        
        ok_button = CTkButton(
            master  = self,
            command = self._ok_event,
            text    = 'OK',
            width   = 125,
            font         = bold11,
            border_width = 1,
            fg_color     = "#282828",
            text_color   = "#E0E0E0",
            border_color = "#0096FF"
            )
        
        self._ctkwidgets_index += 1
        ok_button.grid(row = self._ctkwidgets_index, column = 1, columnspan = 1, padx = (10, 20), pady = (10, 20), sticky = "e")

    def _create_widgets(
            self
            ) -> None:

        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.placeInfoMessageTitleSubtitle()
        self.placeInfoMessageOptionsText()
        self.placeInfoMessageOkButton()

def create_info_button(
        command: Callable, 
        text: str,
        width: int = 150
        ) -> CTkButton:
    
    return CTkButton(
        master  = window, 
        command = command,
        text          = text,
        fg_color      = "transparent",
        hover_color   = "#181818",
        text_color    = "#C0C0C0",
        anchor        = "w",
        height        = 22,
        width         = width,
        corner_radius = 10,
        font          = bold12,
        image         = info_icon
    )

def create_text_box(textvariable, width, heigth):
    return CTkEntry(
        master        = window, 
        textvariable  = textvariable,
        border_width  = 1,
        width         = width,
        height        = heigth,
        font          = bold11,
        justify       = "center",
        fg_color      = "#000000",
        border_color  = "#404040"
    )
    


class App:
    def __init__(self, window):
        window.title('')
        width        = 500
        height       = 500
        window.geometry("500x500")
        window.minsize(width, height)
        window.resizable(False, False)
        window.iconbitmap(find_by_relative_path("Assets" + os_separator + "logo.ico"))

        window.protocol("WM_DELETE_WINDOW", on_app_close)

        place_app_name()
        place_qualityscaler_button()
        place_github_button()
        place_telegram_button()
        place_link_textbox()
        place_check_button()
        place_simultaneous_downloads_textbox()
        place_tips()
        place_message_label()             
        place_download_button()

if __name__ == "__main__":    
    multiprocessing_freeze_support()

    set_appearance_mode("Dark")
    set_default_color_theme("dark-blue")

    processing_queue = multiprocessing_Queue(maxsize=1)

    window = CTk() 

    selected_url        = StringVar()
    info_message        = StringVar()
    selected_cpu_number = StringVar()

    selected_url.set("Paste link here https://fapello.com/emily-rat---/")
    selected_cpu_number.set("6")
    info_message.set("Hi :)")

    font   = "Segoe UI"    
    bold8  = CTkFont(family = font, size = 8, weight = "bold")
    bold9  = CTkFont(family = font, size = 9, weight = "bold")
    bold10 = CTkFont(family = font, size = 10, weight = "bold")
    bold11 = CTkFont(family = font, size = 11, weight = "bold")
    bold12 = CTkFont(family = font, size = 12, weight = "bold")
    bold13 = CTkFont(family = font, size = 13, weight = "bold")
    bold14 = CTkFont(family = font, size = 14, weight = "bold")
    bold16 = CTkFont(family = font, size = 16, weight = "bold")
    bold17 = CTkFont(family = font, size = 17, weight = "bold")
    bold18 = CTkFont(family = font, size = 18, weight = "bold")
    bold19 = CTkFont(family = font, size = 19, weight = "bold")
    bold20 = CTkFont(family = font, size = 20, weight = "bold")
    bold21 = CTkFont(family = font, size = 21, weight = "bold")
    bold22 = CTkFont(family = font, size = 22, weight = "bold")
    bold23 = CTkFont(family = font, size = 23, weight = "bold")
    bold24 = CTkFont(family = font, size = 24, weight = "bold")

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
    

