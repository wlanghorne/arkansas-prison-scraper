from scraper_functions import scrape_inmates_of_age, cat_outputs
from time import sleep
import sys 
import os

# Path to folder that will store data 
outputs_path = './outputs/'
final_path = './outputs/final/final.csv'
driver_path ='./chromedriver'
url = 'https://apps.ark.org/inmate_info/index.php'


# Handle command line args 
arg_len = len(sys.argv)
min_age = 10 
max_age = 110 

if arg_len == 2:
  min_age = sys.argv[1]
elif arg_len == 3:
  min_age = sys.argv[1]
  max_age = sys.argv[2]

print('Program will iterate from ' + str(min_age)+ ' to ' + str(max_age))

for age in range(int(min_age),int(max_age)):
  str_age = str(age)
  print('Current age = ' + str_age)
  scrape_inmates_of_age(os.path.join(outputs_path,str_age+'.csv'), driver_path, url, age)
  # Sleep to ensure don't crash server
  if age < 20 or age > 81:
    print('Long sleep')
    sleep(5)
  else:
    sleep(1)

print('Concatenating output files')
cat_outputs (outputs_path, final_path)