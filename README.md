# Timstof Extractor GUI

## How to Download:

Naviagte to the releases tab of this github repo and download the .exe file from the latest release. 
Simply double click on the .exe file to run the program.

## Developers:

### How to run locally:
> pip clone https://github.com/pgarrett-scripps/timsTofExtractorGUI.git
> pip install -r requirements.txt
> python app.py

### How to compile exe:
> pip clone https://github.com/pgarrett-scripps/timsTofExtractorGUI.git
> pip install -r requirements.txt
> pyinstaller --onefile --log-level=DEBUG --add-data venv/Lib/site-packages/tdfpy/timsdata.dll;. app.py
> .\dist\app.exe


### How to compile linux executable
> pyinstaller --onefile --log-level=DEBUG --add-data=".venv/lib/python3.12/site-packages/tdfpy/libtimsdata.so:." tar_app.py


