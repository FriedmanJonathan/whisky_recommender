import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

URL_PREFIX = "https://www.whisky.com"
SERVICE = Service(r"C:\Users\yonif\Downloads\chromedriver.exe")
OPTIONS = webdriver.ChromeOptions()

# Scroll parameters explicitly defined
NUM_SCROLLS = 105
PAGE_HEIGHT_TO_SCROLL = 2000


def initialize_webdriver(service, options):
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scroll_web_page(driver, num_scrolls, page_height_to_scroll):
    for i in range(num_scrolls):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        driver.execute_script(f"window.scrollBy(0, -{page_height_to_scroll});")
        time.sleep(1.5)  # Allow time for content to load


def parse_web_page(driver):
    page_source = driver.page_source
    parsed_html = BeautifulSoup(page_source, "html.parser")
    return parsed_html


def extract_whisky_data(parsed_html):
    data = []
    title_divs = parsed_html.find_all("div", class_="title")
    rating_divs = parsed_html.find_all("div", class_="rating-wrap")
    for title_div, rating_div in zip(title_divs, rating_divs):
        whisky_data = extract_individual_whisky_data(title_div, rating_div)
        data.append(whisky_data)
    return data


def extract_individual_whisky_data(title_div, rating_div):
    link = title_div.find("a", href=True)
    whisky_data = {
        "whisky_link": URL_PREFIX + link["href"] if link else None,
        "whisky_name": (
            title_div.find("span", class_="marke").text.strip()
            if title_div.find("span", class_="marke")
            else None
        ),
        "whisky_age": (
            title_div.find("span", class_="alterEtikett").text.strip()
            if title_div.find("span", class_="alterEtikett")
            else None
        ),
        "bottling_date": (
            title_div.find("span", class_="abfuelldatum").text.strip()
            if title_div.find("span", class_="abfuelldatum")
            else None
        ),
        "whisky_name_suffix": (
            title_div.find("span", class_="namenszusatz").text.strip()
            if title_div.find("span", class_="namenszusatz")
            else None
        ),
        "alcohol_pct": (
            title_div.find("span", class_="alkoholgehalt").text.strip()
            if title_div.find("span", class_="alkoholgehalt")
            else None
        ),
        "whisky_rating": None,
        "num_ratings": 0,
        "num_reviews": 0,
    }

    # Extract data from the rating section
    rating_links = rating_div.find_all("a")
    if len(rating_links) > 0:
        rating_text = rating_links[0].text.strip()
        rating_parts = rating_text.split()
        if len(rating_parts) == 2:
            whisky_data["whisky_rating"] = rating_parts[0]
            whisky_data["num_ratings"] = rating_parts[1]

    # Extract the number of reviews
    if len(rating_links) > 1:
        num_reviews_text = rating_links[1].text.strip()
        whisky_data["num_reviews"] = num_reviews_text

    return whisky_data


def save_data_to_csv(data, file_path):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def scrape_whisky_website(url):
    driver = initialize_webdriver(SERVICE, OPTIONS)
    driver.get(url)
    scroll_web_page(driver, NUM_SCROLLS, PAGE_HEIGHT_TO_SCROLL)
    parsed_html = parse_web_page(driver)
    data = extract_whisky_data(parsed_html)
    driver.quit()
    return data


if __name__ == "__main__":
    main_url = "https://www.whisky.com/whisky-database/bottle-search.html"
    whisky_data = scrape_whisky_website(main_url)
    csv_file_path = "../../data/raw/2024_05/whisky_main_page_with_ratings.csv"
    save_data_to_csv(whisky_data, csv_file_path)
