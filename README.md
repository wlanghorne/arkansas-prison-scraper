# Arkansas prison scraper

Arkansas prison scraper is a web scraper that iterates through all the incarcerated people listed by the [Arkansas Department of Corrections](https://apps.ark.org/inmate_info/index.php) and outputs a csv file. 

The script functions by searching for incarcerated people by age from 10 to 110 and generating a separate csv file for each age with each row containing information on a separate incarcerated person. The script then concatenates all the csv files into a single csv file.

When I started this project in March of 2022, ADC didn't have a readily available, free, comprehensive and up-to-date database with the information of all incarcerated people in the state. At the same time, the state was expanding its prison system. This project makes the state's data accessible to everyone, allowing the public to keep an eye on Arkansas's shifting incarceration program. 
