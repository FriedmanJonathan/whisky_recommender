"""
Whisky Scraping Module

This module provides functionality to scrape whisky data from a specified website.
It uses Selenium to automate web page scrolling and BeautifulSoup to parse the
retrieved HTML content. Extracted data is saved into a CSV file.

Functions:
    initialize_webdriver(service, options): Initializes the Chrome WebDriver.
    scroll_web_page(driver, num_scrolls, page_height_to_scroll):
    Scrolls web page to load content dynamically.
    parse_web_page(driver): Parses the current page source using BeautifulSoup.
    extract_whisky_data(parsed_html): Extracts whisky data from the parsed HTML content.
    extract_individual_whisky_data(title_div, rating_div): Extracts data for one whisky entry.
    save_data_to_csv(data, file_path): Saves the extracted data into a CSV file.
    scrape_whisky_website(url): Main function to scrape whisky data from the specified URL.

Example usage:
    main_url = "https://www.whisky.com/whisky-database/bottle-search.html"
    whisky_data = scrape_whisky_website(main_url)
    csv_file_path = "../../data/raw/2024_05/whisky_main_page_with_ratings.csv"
    save_data_to_csv(whisky_data, csv_file_path)
"""

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
    """
    Initializes the Chrome WebDriver.

    Parameters:
    service (Service): The ChromeDriver service to use.
    options (Options): The Chrome options to configure the WebDriver.

    Returns:
    WebDriver: The initialized WebDriver instance.
    """
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scroll_web_page(driver, num_scrolls, page_height_to_scroll):
    """
    Scrolls the web page to load content dynamically.

    Parameters:
    driver (WebDriver): The WebDriver instance controlling the browser.
    num_scrolls (int): The number of times to scroll the page.
    page_height_to_scroll (int): The height to scroll up after reaching the bottom.

    Returns:
    None
    """
    for _ in range(num_scrolls):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        driver.execute_script(f"window.scrollBy(0, -{page_height_to_scroll});")
        time.sleep(1.5)  # Allow time for content to load


def parse_web_page(driver):
    """
    Parses the current page source using BeautifulSoup.

    Parameters:
    driver (WebDriver): The WebDriver instance controlling the browser.

    Returns:
    BeautifulSoup: The parsed HTML content.
    """
    page_source = driver.page_source
    parsed_html = BeautifulSoup(page_source, "html.parser")
    return parsed_html


def extract_whisky_data(parsed_html):
    """
    Extracts whisky data from the parsed HTML content.

    Parameters:
    parsed_html (BeautifulSoup): The parsed HTML content.

    Returns:
    list: A list of dictionaries containing whisky data.
    """
    data = []
    title_divs = parsed_html.find_all("div", class_="title")
    rating_divs = parsed_html.find_all("div", class_="rating-wrap")
    for title_div, rating_div in zip(title_divs, rating_divs):
        individual_whisky_data = extract_individual_whisky_data(title_div, rating_div)
        data.append(individual_whisky_data)
    return data


def extract_individual_whisky_data(title_div, rating_div):
    """
    Extracts data for an individual whisky entry.

    Parameters:
    title_div (Tag): The HTML tag containing the title information.
    rating_div (Tag): The HTML tag containing the rating information.

    Returns:
    dict: A dictionary containing the whisky data.
    """
    link = title_div.find("a", href=True)
    whisky_data_dict = {
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
            whisky_data_dict["whisky_rating"] = rating_parts[0]
            whisky_data_dict["num_ratings"] = rating_parts[1]

    # Extract the number of reviews
    if len(rating_links) > 1:
        num_reviews_text = rating_links[1].text.strip()
        whisky_data_dict["num_reviews"] = num_reviews_text

    return whisky_data_dict


def save_data_to_csv(data, file_path):
    """
    Saves the extracted data into a CSV file.

    Parameters:
    data (list): The extracted whisky data.
    file_path (str): The file path where the CSV will be saved.

    Returns:
    None
    """
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def scrape_whisky_website(url):
    """
    Main function to scrape whisky data from the specified URL.

    Parameters:
    url (str): The URL of the whisky website to scrape.

    Returns:
    list: A list of dictionaries containing the scraped whisky data.
    """
    driver = initialize_webdriver(SERVICE, OPTIONS)
    driver.get(url)
    scroll_web_page(driver, NUM_SCROLLS, PAGE_HEIGHT_TO_SCROLL)
    parsed_html = parse_web_page(driver)
    data = extract_whisky_data(parsed_html)
    driver.quit()
    return data


if __name__ == "__main__":
    MAIN_URL = "https://www.whisky.com/whisky-database/bottle-search.html"
    whisky_data = scrape_whisky_website(MAIN_URL)
    CSV_FILE_PATH = "../../data/raw/2024_05/whisky_main_page_with_ratings.csv"
    save_data_to_csv(whisky_data, CSV_FILE_PATH)
