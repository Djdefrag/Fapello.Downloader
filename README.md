<div align="center">
    <br>
    <img src="https://user-images.githubusercontent.com/32263112/205343453-e2f61261-3fb4-4d9b-8fe7-2be67fc0fcfb.png" width="175"> </a> 
    <br><br> Fapello.Downloader - NSFW Windows app to batch download images and videos from Fapello.com <br><br>
    <a href="https://jangystudio.itch.io/fapellodownloader">
         <img src="https://user-images.githubusercontent.com/86362423/162710522-c40c4f39-a6b9-48bc-84bc-1c6b78319f01.png" width="200">
    </a>
</div>

<br>

<div align="center">
    <img src="https://user-images.githubusercontent.com/32263112/205343688-74447412-0f9d-4177-90fe-d0567b03fb80.png"> </a> 
</div>


## Other projects.🤓

https://github.com/Djdefrag/QualityScaler / QualityScaler - image/video deeplearning upscaler with any GPU (BSRGAN/Pytorch)

https://github.com/Djdefrag/ReSR.Scaler / ReSR.Scaler - image/video deeplearning upscaler with any GPU (Real-ESRGAN/Pytorch)


## How is made. 🛠

Fapello.Downloader is completely written in Python, from backend to frontend. External packages are:
- [ ] Core -> beautifulsoup / Selenium
- [ ] GUI -> Tkinter / Tkdnd / Sv_ttk
- [ ] Image/video -> OpenCV
- [ ] Packaging   -> Pyinstaller
- [ ] Miscellaneous -> Pywin32 / Win32mica / split_image

## HOW TO USE. 👨‍💻
#### Prerequisites: 
* (Important!) FapelloDownloader will ONLY work with Google Chrome installed.
* Install Visual-C-Runtimes with the archive in this folder or download from this link https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-al...
  
#### Installation:
 * download Fapello.Downloader release .zip
 * unzip using 7zip or similar

#### HOW TO USE.
* Execute FapelloDownloader.exe
* Copy the Fapello link of interest (for example: https://fapello.com/mia-kha***/)
* Paste the copied link in FapelloDownloader textbox
* Press Download button
* Wait for the download to complete
* A folder named with the name associated with the downloaded link will be created in the FapelloDownloader directory (for example FapelloDownloader/mia-kha***/)

## Next steps. 🤫
- [ ] Support for other browser instead of Chrome (Brave / Firefox / Edge / Opera)
- [ ] Update libraries 
    - [ ] Python 3.10 (expecting ~10% more performance) 
    - [ ] Python 3.11 (expecting ~30% more performance)

