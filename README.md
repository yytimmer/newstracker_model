# Code associated with "Automated monitoring of online news accuracy with change classification models"

In this repository, the code that was written in the context of the research article with title "Automated monitoring of online news accuracy with change classification models", submitted for review to Information Processing & Management, is shared.

More specifically, two folders can be found in this repository:

* **Data scraping**: Python scripts are present that are capable of scraping the newspapers investigated in our work (VRT, Knack, HLN, Nieuwsblad, De Morgen and De Standaard).
A separate file is present for each newspaper (*VRTScraper.py*, *KnackScraper.py*, *HLNScraper.py*, *NieuwsbladScraper.py*, *MorgenScraper.py* and *StandaardScraper.py*).
Moreover, a main file is present (*main.py*), taking as arguments (1) the newspaper for which you want to start the scraping procedure ('VRT', 'Knack', 'HLN', 'Nieuwsblad', 'Demorgen' and 'Standaard'), and (2) the filepath to the storage location of the chromedriver.exe file that is necessary to be able to use the Selenium package.
Using these files, one is able to gather online news articles and their updates from the different newspapers and store them in an underlying relational database (as is described in the methodological section of the manuscript).

Be aware of the fact that one should download the most recent Chromedriver [here](https://chromedriver.chromium.org/home) and install the Selenium package first before being able to execute the scripts.

Finally, this folder also contains a schema-only backup of the PostgreSQL database in which the online news articles were stored (*newstrackerdb_backup.sql).
Be aware of the fact that the parameters (i.e., hostname, port number, database name, username and password) of the database should be filled in correctly in *main.py* for the program to be able to run correctly.

* **Model building**: This folder contains a notebook for each classification model at hand (*objective_errors_model.ipynb*, *subjective_errors_model.ipynb* and *linguistic_errors_model.ipynb*), containing the different methodological steps as explained in the paper. Moreover, the same notebooks are also present in this folder in html format such that installation of Jupyter notebook is not necessary to have insight in the code.
