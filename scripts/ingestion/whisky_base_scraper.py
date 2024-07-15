# Parameters:
num_whiskies_to_be_considered_major_distillery = 1980

# Crawling and scraping packages:
from selenium import webdriver
from bs4 import BeautifulSoup

# Basic and math packages:
import pandas as pd
from random import randint
from time import sleep
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# cv = CountVectorizer()

# Visualization and plotting packages:
# from PIL import Image, ImageOps
# from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
# % matplotlib inline   - if we move this to a notebook

# Timing the code:
import time

zero_time = time.perf_counter()

# STEP 1: Scraping the WhiskyBase website

# Initializing the driver and loading the main page on WhiskyBase:
DRIVER_PATH = r'C:/Users/yonif/Downloads/chromedriver.exe'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
driver.get('https://www.whiskybase.com/whiskies/distilleries')
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Extracting the header row from the table:
header = soup.find_all("table")[0].find_all("tr")[0]
list_header = []
for items in header:
    try:
        if items.get_text().strip(' \n\t') != '':  # Lots of spaces, tabs, newlines - cleared.
            list_header.append(items.get_text().strip(' \n\t'))
    except:
        continue

# Extracting the data from the table:
HTML_data = soup.find_all("table")[0].find_all("tr")[1:]
addresses_of_major_distilleries = []

data = []
for element in HTML_data:
    sub_data = []
    for sub_element in element:
        try:
            if sub_element.get_text().strip(' \n\t') != '':
                sub_data.append(sub_element.get_text().strip(' \n\t'))  # Jump of two because site has extra columns
        except:
            continue
    data.append(sub_data)

    try:  # Extracting the links for major distilleries for in-depth analysis:
        if float(sub_data[2]) > num_whiskies_to_be_considered_major_distillery:
            address_major = element.find('a').get('href')
            addresses_of_major_distilleries.append(address_major)
    except:
        continue

# print(addresses_of_major_distilleries)

# Storing the data from the main page into dataframe, then as a CSV file:
distillery_df = pd.DataFrame(data=data, columns=list_header)
major_distillery_df = distillery_df[
    distillery_df['Whiskies'].astype(float) > num_whiskies_to_be_considered_major_distillery]
major_distillery_df.to_csv('data/Distilleries.csv')

# For every distillery selected, we extract the core range whiskies.

core_range_data_header = [["Whisky", "Distillery", "Region", "Age", "Strength", "YearBottled",
                           "Category", "Bottler", "NumOfReviews", "AverageValueEuro", "Rating"]]
core_range_data = []

reviews_data_header = [["Whisky", "Review"]]
reviews_data = []

for distillery_url in addresses_of_major_distilleries:
    driver.get(distillery_url)
    distillery_page_source = driver.page_source
    soup = BeautifulSoup(distillery_page_source, 'html.parser')
    distillery_name = soup.find_all(id="company-name")[0].find_all("h1")[0].get_text().strip(' \n\t')
    region_name = soup.find_all(id="company-name")[0].find_all("li")[0].get_text().strip(' \n\t')
    if region_name == "Scotland":
        region_name = region_name + " " + soup.find_all(id="company-name")[0].find_all("li")[1].get_text().strip(
            ' \n\t')
    all_whiskies_from_distillery = soup.find_all("table")[0].find_all("tbody")[0].find_all("tr")[1:]
    for whisky in all_whiskies_from_distillery:
        try:  # Iterating all core-range whiskies (HTML tags have no class), until the seperator item which has a class.
            if whisky.attrs['class']:
                break
        except:
            pass
        whisky_attributes = whisky.find_all("td")

        # Name and URL (to access reviews)
        whisky_url = whisky_attributes[2].find('a').get('href')
        whisky_name = whisky_attributes[2].get_text().strip(' \n\t')

        # Age
        whisky_age_text = whisky_attributes[3].get_text()
        try:
            whisky_age = float(whisky_age_text)
        except:
            whisky_age = "NAS"

        # Strength
        whisky_strength_text = whisky_attributes[4].get_text()
        try:
            whisky_strength = float(whisky_strength_text.split('%')[0])  # e.g. '43.0% Vol.'
        except ValueError:  # 'proof' (divide by two) or 'gradi' (keep as is)
            if 'proof' in whisky_strength_text:
                whisky_strength = float(whisky_strength_text.split(' ')[0]) / 2
            else:
                whisky_strength = float(whisky_strength_text.split(' ')[0])

        # Year bottled
        whisky_year_bottled_text = whisky_attributes[5].get_text()
        try:
            whisky_year_bottled = float(whisky_year_bottled_text)
        except:
            whisky_year_bottled = "NA"

        # Rating
        try:
            whisky_rating = float(whisky_attributes[7].get_text())
        except:
            continue

        # Now we move on to the URL in order to extract the tertiary information: the reviews.
        driver.get(whisky_url)
        whisky_page_source = driver.page_source
        soup = BeautifulSoup(whisky_page_source, 'html.parser')

        # Let's extract some more info: # reviews,
        whisky_category = soup.find(attrs={"class": "block-desc"}).find('dl').find_all('dd')[1].get_text().strip(
            ' \n\t')
        whisky_bottler = soup.find(attrs={"class": "block-desc"}).find('dl').find_all('dd')[3].get_text().strip(' \n\t')
        whisky_num_reviews = float(soup.find(attrs={"class": "votes-count"}).get_text().strip(' \n\t'))
        try:
            whisky_average_value = float(
                soup.find(attrs={"class": "block-price"}).find_all('p')[1].get_text().split(' ')[1].strip(' \n\t'))
        except:
            whisky_average_value = 'NA'

        # whisky_category = soup.xpath('/html/body/div[1]/div[1]/div/div[2]/div[2]/div[1]/dl/dd[2]')[0].get_text().strip(' \n\t')
        # whisky_bottler = soup.xpath('/html/body/div[1]/div[1]/div/div[2]/div[2]/div[1]/dl/dd[4]')[0].get_text().strip(' \n\t')
        # whisky_num_reviews = soup.xpath('/html/body/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div/dl/dd[2]')[0].get_text().strip(' \n\t')
        # whisky_average_value = soup.xpath('/html/body/div[1]/div[1]/div/div[2]/div[2]/div[3]/div[1]/p[2]')[0].get_text().strip(' \n\t')

        # Creating a list of all items collected
        core_range_data.append(
            [whisky_name, distillery_name, region_name, whisky_age, whisky_strength, whisky_year_bottled,
             whisky_category, whisky_bottler, whisky_num_reviews, whisky_average_value, whisky_rating])

        # Finally, we extract the reviews, which we'll place in a separate table.
        whisky_reviews = soup.find_all(attrs={"class": "wb--note-content-wrapper"})
        for review in whisky_reviews:
            # print(review)
            review_text = ""
            try:
                review_text = review_text + review.find_all(attrs={"data-translation-field": "message"})[
                    0].get_text().strip(' \n\t')
            except:
                pass
            try:
                review_text = review_text + review.find_all(attrs={"data-translation-field": "nose_text"})[
                    0].get_text().strip(' \n\t')
            except:
                pass
            try:
                review_text = review_text + review.find_all(attrs={"data-translation-field": "taste_text"})[
                    0].get_text().strip(' \n\t')
            except:
                pass
            try:
                review_text = review_text + review.find_all(attrs={"data-translation-field": "finish_text"})[
                    0].get_text().strip(' \n\t')
            except:
                pass

            reviews_data.append([whisky_name, review_text])

        sleep(randint(1, 4))

# Storing the data from the main page into dataframe, then as a CSV file:
whiskies_df = pd.DataFrame(data=core_range_data, columns=core_range_data_header)
whiskies_df.to_csv('../../data/raw/2024_07/whisky_base_whiskies.csv')
reviews_df = pd.DataFrame(data=reviews_data, columns=reviews_data_header)
reviews_df.to_csv('data/Reviews.csv')
