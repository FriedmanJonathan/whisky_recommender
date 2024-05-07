import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup, Comment

# Define the delay between requests (in seconds)
REQUEST_DELAY = 10  # Adjust as needed

# Extract tasting notes

def extract_notes(section_tag):
    notes_dict = {}
    try:
        notes_sections = section_tag.find_all('div', class_='tasteicon-statistic')
        for section in notes_sections:
            title = section.find('div', class_='title left').text.strip()

            # Extract rating values from HTML comments
            rating_value_div = section.find('div', class_='items active')
            rating_value = rating_value_div['style'].split()[1].strip('%;')
            # Add the extracted data to the tasting_notes dictionary
            notes_dict[title] = rating_value
    except IndexError: pass  # Return just the empty dictionary
    except AttributeError: pass  # Same
    return [notes_dict]

async def scrape_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:

                page_content = await response.text()
                soup = BeautifulSoup(page_content, 'html.parser')

                # Extract data as specified
                distillery_name_inner = soup.find('tr', class_='brennerei').find('a').text.strip()
                try:
                    country = soup.find_all('tr', class_='')[1].find_all('a')[0].text.strip()
                except IndexError:
                    print(f"Country Index Error at {url}")
                    country = ""
                try:
                    region = soup.find_all('tr', class_='')[1].find_all('a')[1].text.strip()
                except IndexError:
                    print(f"Region Index Error at {url}")
                    region = ""
                try:
                    whisky_type = soup.find('tr', class_='sorte').find('a').text.strip()
                except AttributeError:
                    whisky_type = 'Unknown'
                try:
                    whisky_age_inner = soup.find('tr', class_='fassnummern').find('span', class_='value').text.strip()
                except AttributeError:
                    whisky_age_inner = "NAS" # if no age found, NAS (No Age Statement)
                alcohol_pct_inner = soup.find('tr', class_='alkoholgehalt').find('span', class_='value').text.strip()
                bottler = soup.find('tr', class_='abfueller').find('a').text.strip()

                # Extract post-treatment data
                try:
                    post_treatment_tags = soup.find('tr', class_='merkmale').find_all('img', title=True)
                    post_treatment = [tag['title'] for tag in post_treatment_tags]
                except AttributeError: post_treatment = ""
                # Create a DataFrame for the scraped data
                df = pd.DataFrame({
                    'whisky_url': [url],
                    'distillery_name_inner': [distillery_name_inner],
                    'country': [country],
                    'region': [region],
                    'whisky_type': [whisky_type],
                    'whisky_age_inner': [whisky_age_inner],
                    'alcohol_pct_inner': [alcohol_pct_inner],
                    'bottler': [bottler],
                    'post_treatment': [post_treatment]
                })

                # Now we extract the notes
                notes = ['nosing', 'tasting', 'finish']
                for note in notes:
                    section_tag = soup.find('div', class_=f"col-md-4 group-divider group group-{note}")
                    feature_name = note + '_notes'
                    print(url, note)
                    df[feature_name] = extract_notes(section_tag)

                return df

async def scrape_multiple_pages(urls):
    tasks = []
    for url in urls:
        tasks.append(scrape_page(url))
        await asyncio.sleep(REQUEST_DELAY)  # Add a delay between requests

    return await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Create an event loop and run the asynchronous tasks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Import the whisky_main_page DataFrame from the CSV file
    whisky_main_page = pd.read_csv('../../data/raw/2024_05/whisky_main_page_with_ratings.csv')

    # Drop duplicates based on the specified columns
    whisky_main_page.drop_duplicates(
        subset=['whisky_name', 'whisky_age', 'alcohol_pct', 'whisky_rating', 'num_reviews', 'num_ratings'],
        inplace=True
    )

    # Remove instances where there are no reviews, since we won't be able to compare notes.
    # (These are likely rarer whiskies anyway, therefore not easily obtainable to user)
    whisky_main_page = whisky_main_page.loc[whisky_main_page["num_reviews"] != ""]

    # Extract unique URLs from the whisky_link column
    unique_urls = whisky_main_page['whisky_link'].tolist()

    try:
        # Scrape data from multiple pages concurrently
        scraped_data = asyncio.run_until_complete(scrape_multiple_pages(unique_urls))

        # Concatenate the DataFrames into one final DataFrame
        whisky_details = pd.concat(scraped_data, ignore_index=True)

        # Print/export the final DataFrame
        csv_file_path = '../../data/raw/2024_05/whisky_details_all.csv'
        whisky_details.to_csv(csv_file_path, index=False)
        #print(whisky_details)
    finally:
        pass
        #Close the event loop
        #loop.close()