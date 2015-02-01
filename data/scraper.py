import requests

from bs4 import BeautifulSoup

PG_SITE = "http://msa.maryland.gov/msa/mdmanual/07leg/html/gacopg.html"
DISTRICT = "22"


def scrape_general_assembly():

    data = requests.get(PG_SITE)
    data = BeautifulSoup(data.text)

    for district in data.find_all("h3"):
        if district.text.replace("DISTRICT ", "") == DISTRICT:
            pass

if __name__ == "__main__":
    scrape_general_assembly()
