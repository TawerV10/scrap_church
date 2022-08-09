import requests
import time
import pandas as pd
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def get_data():
    df = pd.DataFrame()
    count = 1

    for i in range(0, 6):
        url = f'https://www.adventistdirectory.org/default.aspx?&page=searchresults&CtryCode=US&StateProv=AL&PageIndex={i}'
        r = requests.get(url)

        soup = BS(r.text, 'lxml')

        rows = soup.find(class_='nopad').find('table').find_all('tr')
        for row in rows:
            try:
                title = row.find_all('td')[1].find('a').text
                link = 'https://www.adventistdirectory.org' + row.find_all('td')[1].find('a').get('href')

                html = get_html_sel(link)
                soup = BS(html, 'lxml')

                lines = soup.find(id='_ctl0_pnlMainContent').find_all('table')[-1].find_all('tr')

                street = None
                city = None
                state = None
                postcode = None
                country = None
                members = None
                pastor = None
                phone = None
                email = None
                website = None
                conference = None
                union = None

                for el in lines:
                    if 'Address' in el.find_all('td')[0].text.strip():
                        street_address = el.find_all('td')[-1].text.strip().split('\n')
                        street = street_address[0].strip()
                        city = ''
                        for item in street_address[1].split(' ')[:-3]:
                            city += item + ' '
                        city = city.strip()
                        state = street_address[1].split(' ')[-3].strip()
                        postcode = street_address[1].split(' ')[-1].split('-')[0].strip()
                        country = street_address[-1].strip()

                    if 'Members' in el.find_all('td')[0].text.strip():
                        members = el.find_all('td')[-1].text.strip()
                    if 'Pastor' in el.find_all('td')[0].text.strip():
                        pastor = el.find_all('td')[-1].text.strip()
                    if 'Phone' in el.find_all('td')[0].text.strip():
                        phone = el.find_all('td')[-1].text.strip()
                    if 'Email' in el.find_all('td')[0].text.strip():
                        email = el.find_all('td')[-1].text.strip()
                    if 'Website' in el.find_all('td')[0].text.strip():
                        website = el.find_all('td')[-1].text.strip()
                    if 'Conference' in el.find_all('td')[0].text.strip():
                        conference = el.find_all('td')[-1].text.replace('(website)', '').strip()
                    if 'Union' in el.find_all('td')[0].text.strip():
                        union = el.find_all('td')[-1].text.replace('(website)', '').strip()

                print(f'Count [{count}]')
                print(title)
                count += 1

                data = {
                    'Church Name': title,
                    'Street': street,
                    'City': city,
                    'State': state,
                    'Postal Code': postcode,
                    'Country': country,
                    'Members': members,
                    'Pastor Name': pastor,
                    'Phone': phone,
                    'Email': email,
                    'Website': website,
                    'Conference': conference,
                    'Union': union
                }

                temp_df = pd.DataFrame(data, index=[1])
                df = df.append(temp_df, ignore_index=True)

            except:
                title = None
                link = None

        print(f'Page #{i} was scraped!')

    df.to_excel('full_al_data.xlsx', index=False)

def get_html_sel(url):
    ua = UserAgent().random
    path = r'C:\Users\name\Documents\GitHub\chromedriver.exe'

    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={ua}')
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.binary_location = 'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'

    service = Service(path)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(1)

        return driver.page_source
    except Exception as ex:
        print(ex)
    finally:
        driver.stop_client()
        driver.close()
        driver.quit()

def main():
    t0 = time.time()
    get_data()
    print(time.time() - t0)

if __name__ == '__main__':
    main()