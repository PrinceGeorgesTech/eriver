import requests
import json
from bs4 import BeautifulSoup

SITE = "http://www.mgaleg.maryland.gov/webmga/"
TABLE_SITE = SITE + "frmmain.aspx?pid=legisrpage"


def organize_name(name_str):

    name_list = name_str.split(',')

    if len(name_list) == 1:
        return None

    name_dict = {}
    name_dict["first"] = name_list[1]
    name_dict["last"] = name_list[0]

    # Extract Sufix/Prefix
    if len(name_list) == 3:
        name_dict["sufix_prefix"] = name_list[2]

    return name_dict


def fix_url(url):

    return SITE + url


def clean_name(name_line):

    url = name_line.find('a')
    if url:
        url = fix_url(url.get('href'))
    name = organize_name(name_line.text)
    return name, url


def scraper_personal_site(url):

    data = {}

    html = requests.get(url)
    soup = BeautifulSoup(html.text)
    soup = soup.find("table", {"class": "spco"})

    for row in soup.find_all('tr'):
        title = row.find('th')
        content_lines = []

        for line in title.next_sibling.strings:
            content_lines.append(line)

        data[title.text.strip(' :')] = content_lines

    return data


def clean_row(row, position):

    row = row.find_all('td')
    if row:
        contact_dict = {}
        name_line, district, county = row[0:-1]
        name, url = clean_name(name_line)

        if url:
            contact_dict.update(scraper_personal_site(url))

        contact_dict.update({
            'name': name,
            'district': district.text,
            'county': county.text,
            'position': position})

        return contact_dict


def clean_table(table):

    position = [h.text for h in table.find_all('th')][0]
    for row in table.find_all('tr'):
        contact = clean_row(row=row, position=position)
        yield contact


def scrape_general_assembly():

    data = []

    html = requests.get(TABLE_SITE)
    soup = BeautifulSoup(html.text)

    for table in soup.find_all("table", {"class": "grid"}):
        for contact in clean_table(table):
            if contact:
                data.append(contact)

        with open('general_assembly_contacts.json', 'w') as f:
            f.write(json.dumps(
                data,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')))


if __name__ == "__main__":
    scrape_general_assembly()
