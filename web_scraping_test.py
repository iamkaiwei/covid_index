from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

# To use incognito mode when accessing the websites (I don't actually know if this works hahaha)
option = webdriver.ChromeOptions()
option.add_argument(" — incognito")

# path to your chrome driver
chrome_path = "C:\\Users\\steve\\OneDrive - Singapore Management University\\hasBrain Python Study Group\\chromedriver.exe"
browser = webdriver.Chrome(executable_path=chrome_path)

# S&P 500 sectors
SP_industry_names = [
    'consumer discretionary', 'consumer staples', 'energies', 'financials',
    'health care', 'industrials', 'information technology', 'materials',
    'real estate', 'telecom services', 'utilities'
]

# S&P 500 sector links in barchart.com
SP_industry_links = [
    'https://www.barchart.com/stocks/indices/sp-sector/consumer-discretionary',
    'https://www.barchart.com/stocks/indices/sp-sector/consumer-staples',
    'https://www.barchart.com/stocks/indices/sp-sector/energies',
    'https://www.barchart.com/stocks/indices/sp-sector/financials',
    'https://www.barchart.com/stocks/indices/sp-sector/health-care',
    'https://www.barchart.com/stocks/indices/sp-sector/industrials',
    'https://www.barchart.com/stocks/indices/sp-sector/information-technology',
    'https://www.barchart.com/stocks/indices/sp-sector/materials',
    'https://www.barchart.com/stocks/indices/sp-sector/real-estate',
    'https://www.barchart.com/stocks/indices/sp-sector/telecom-services',
    'https://www.barchart.com/stocks/indices/sp-sector/utilities'
]

# Dictionary to store information to save into a dataframe later on
stock_industry_dictionary = {
    'stock_names': [],
    'SP_indices_sectors': [],
    'SIC_industries_code': [],
    'SIC_industries_name': []
}

# Save stock names and links for Beautiful Soup
stock_names = []
stock_links = []
stock_SP_industry_name = []

for i in range(len(SP_industry_names)):
    link = SP_industry_links[i]
    SP_industry_name = SP_industry_names[i]
    browser.get(link)

    # Wait 20 seconds for page to load
    timeout = 20
    try:
        # load the webpage until it finds the CSS object
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "span>a[href^='/stocks/quotes/']")))
    except TimeoutException:
        print('Timed out waiting for page to load')
        browser.quit()

    # Finds all stock elements
    stocks_elements = browser.find_elements_by_css_selector(
        "span>a[href^='/stocks/quotes/']")

    # Append stock name and links to empty lists
    for stock in stocks_elements:
        stock_names.append(stock.text)
        stock_links.append(stock.get_attribute("href"))
        stock_SP_industry_name.append(SP_industry_name)

# Quit selenium, let's go on to use Beautiful Soup from here!
browser.quit()

for i in range(len(stock_links)):

    # Seems like I need to trick barchart that I am legit and not a bot, hence the headers
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    url = stock_links[i]
    stock_name = stock_names[i]

    # Get HTML response and save it as a Beautiful Soup object
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Get SIC industry element
    SIC_industry = soup.select_one(
        f"a[href^='/stocks/quotes/{stock_name}/competitors?quoteSectors=']>span"
    )

    # Had to add this because strangely, some stocks don't have a SIC industry classification
    if SIC_industry:
        SIC_industry = SIC_industry.text

        # Split the element into the code and name of the SIC industry
        SIC_code = SIC_industry.split(' ', 1)[0]
        SIC_name = SIC_industry.split(' ', 1)[1]

        # Save all important information into dictionary
        stock_industry_dictionary['stock_names'].append(stock_name)
        stock_industry_dictionary['SP_indices_sectors'].append(
            stock_SP_industry_name[i])
        stock_industry_dictionary['SIC_industries_code'].append(SIC_code)
        stock_industry_dictionary['SIC_industries_name'].append(SIC_name)

        print(f'Count down! {len(stock_links) - i} stocks')
    else:
        print(f'something went wrong at stock name {stock_name}')

    time.sleep(random.random() + 1)

# Convert dictionary into a dataframe and save it as a csv file
df = pd.DataFrame(stock_industry_dictionary)
df.to_csv('stocks_indsutry_categorisation.csv')

print('Done! :D')