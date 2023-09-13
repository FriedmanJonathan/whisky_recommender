import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

async def scrape_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, 'html.parser')

                # Extract data as specified
                distillery_name_inner = soup.find('tr', class_='brennerei').find('a').text.strip()
                country = soup.find('tr', class_='').find_all('a')[0].text.strip()
                region = soup.find('tr', class_='').find_all('a')[1].text.strip()
                whisky_type = soup.find('tr', class_='sorte').find('a').text.strip()
                whisky_age_inner = soup.find('tr', class_='fassnumeren').find('span', class_='value').text.strip()
                alcohol_pct_inner = soup.find('tr', class_='alkoholgehalt').find('span', class_='value').text.strip()

                # Extract post-treatment data
                post_treatment_tags = soup.find('tr', class_='abfueller').find_all('img', title=True)
                post_treatment = [tag['title'] for tag in post_treatment_tags]

                # Create a DataFrame for the scraped data
                df = pd.DataFrame({
                    'whisky_url': [url],
                    'distillery_name_inner': [distillery_name_inner],
                    'country': [country],
                    'region': [region],
                    'whisky_type': [whisky_type],
                    'whisky_age_inner': [whisky_age_inner],
                    'alcohol_pct_inner': [alcohol_pct_inner],
                    'post_treatment': [post_treatment]
                })

                return df

async def scrape_multiple_pages(urls):
    tasks = [scrape_page(url) for url in urls]
    return await asyncio.gather(*tasks)

if __name__ == '__main__':
    # List of URLs to scrape (replace with your URLs)
    urls = ['https://example.com/page1', 'https://example.com/page2', 'https://example.com/page3']

    # Scrape data from multiple pages concurrently
    scraped_data = asyncio.run(scrape_multiple_pages(urls))

    # Concatenate the DataFrames into one final DataFrame
    whisky_details = pd.concat(scraped_data, ignore_index=True)

    # Print the final DataFrame
    print(whisky_details)
