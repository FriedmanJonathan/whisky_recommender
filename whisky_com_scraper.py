import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
service = Service(r"C:\Users\yonif\Downloads\chromedriver.exe")
options = webdriver.ChromeOptions()
page_height_to_scroll = 2000  # Adjust this value as needed
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


def scrape_whisky_website(url):
    # Initialize the Selenium WebDriver and open website
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # Initialize an empty list to store data
    data = []

    # Scroll down to load more entries (adjust the number of scrolls as needed)
    num_scrolls = 105  # You may need to adjust this number based on the website
    for i in range(num_scrolls):
        css_selector_name = 'id.content'
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        driver.execute_script(f"window.scrollBy(0, -{page_height_to_scroll});")
        time.sleep(1.5)  # Allow time for content to load

    # Extract the page source after all entries have loaded and parse with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find and process the entries
    title_divs = soup.find_all('div', class_='title')
    rating_divs = soup.find_all('div', class_='rating-wrap')
    for title_div, rating_div in zip(title_divs, rating_divs):
        link = title_div.find('a', href=True)
        if link:
            whisky_link = link['href']
            # Extract data and append it to the list
            whisky_data = {
                'whisky_link': whisky_link,
                'whisky_name': title_div.find('span', class_='marke').text.strip(),
                'whisky_age': title_div.find('span', class_='alterEtikett').text.strip(),
                'bottling_date': title_div.find('span', class_='abfuelldatum').text.strip(),
                'whisky_name_suffix': title_div.find('span', class_='namenszusatz').text.strip(),
                'alcohol_pct': title_div.find('span', class_='alkoholgehalt').text.strip(),
                'whisky_rating': None,
                'num_ratings': None,
                'num_reviews': None
            }

            # Extract data from the rating section
            rating_inner_div = rating_div.find_all('a')[0]
            if rating_inner_div:
                rating_text = rating_inner_div.text.strip()
                rating_parts = rating_text.split()
                if len(rating_parts) == 2:
                    whisky_data['whisky_rating'] = rating_parts[0]
                    whisky_data['num_ratings'] = rating_parts[1]

            # Extract the number of reviews
            try:
                num_reviews_tag = rating_div.find_all('a')[1]
                if num_reviews_tag:
                    num_reviews_text = num_reviews_tag.text.strip()
                    whisky_data['num_reviews'] = num_reviews_text
            except IndexError: whisky_data['num_reviews'] = ""

            data.append(whisky_data)

    # Close the WebDriver
    driver.quit()

    # Create a DataFrame from the scraped data
    df = pd.DataFrame(data)

    return df


if __name__ == '__main__':
    main_url = 'https://www.whisky.com/whisky-database/bottle-search.html'

    # Scrape the website
    whisky_data = scrape_whisky_website(main_url)

    # Specify the file path where you want to save the CSV file
    csv_file_path = "whisky_main_page_with_ratings.csv"  # Replace with your desired file path

    # Use the to_csv method to export the DataFrame to a CSV file
    whisky_data.to_csv(csv_file_path, index=False)  # Set index to False if you don't want to include the index in the CSV file
