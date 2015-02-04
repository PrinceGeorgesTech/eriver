import json
import re

from bs4 import BeautifulSoup
from requests_cache.core import CachedSession


class GeneralAssemblyScraper:

    def __init__(self, cache_name):
        self.SITE = "http://www.mgaleg.maryland.gov/webmga/"
        self.TABLE_SITE = self.SITE + "frmmain.aspx?pid=legisrpage"
        self.CLIENT = CachedSession(cache_name)
        self.EMAIL = re.compile('[\w+\.]+@[\w]+\.state\.md\.us')

    def organize_name(self, name_str):
        """ Get name field and transform it into a dictionary """

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

    def fix_url(self, url):
        """ Prepare url to make request """

        return self.SITE + url

    def extract_name_url(self, name_line):
        """ Extracts the url and name from line """

        url = name_line.find('a')
        if url:
            url = self.fix_url(url.get('href'))
        name = self.organize_name(name_line.text)
        return name, url

    def extract_content_lines(self, title):
        """ Funnels html into correct scraper for formatting """

        content_lines = []
        if title.text.strip(' :') == "Contact":
            email = self.EMAIL.search(title.next_sibling.text)
            if email:
                content_lines = email.group(0)
        else:
            for line in title.next_sibling.strings:
                content_lines.append(line)

        return content_lines

    def scrape_individual_site(self, url):
        """ Scrape the candidate's individual site for additional info """

        data = {}
        html = self.CLIENT.get(url)
        soup = BeautifulSoup(html.text)
        soup = soup.find("table", {"class": "spco"})
        for row in soup.find_all('tr'):
            title = row.find('th')
            content_lines = self.extract_content_lines(title)
            data[title.text.strip(' :')] = content_lines
        return data

    def get_legislator(self, row, position):
        """
        Get data for a individual legislator by cleaning row and
        scraping thier website
        """

        row = row.find_all('td')
        if row:
            contact_dict = {}
            name_line, district, county = row[0:-1]
            name, url = self.extract_name_url(name_line)
            # Get additional info if individual site exisits
            if url:
                contact_dict.update(self.scrape_individual_site(url))
            contact_dict.update({
                'name': name,
                'district': district.text,
                'county': county.text,
                'position': position})
            return contact_dict

    def parse_table(self, table):
        """ Prases table data and yeilds one contact at a time """

        position = [h.text for h in table.find_all('th')][0]
        for row in table.find_all('tr'):
            yield self.get_legislator(row=row, position=position)

    def scrape_ga_data(self):
        """ Scrapes data from MD's General Assembly website. """

        data = []
        html = self.CLIENT.get(self.TABLE_SITE)
        soup = BeautifulSoup(html.text)
        for table in soup.find_all("table", {"class": "grid"}):
            for contact in self.parse_table(table):
                if contact:
                    data.append(contact)
            with open('general_assembly_contacts.json', 'w') as f:
                f.write(json.dumps(
                    data,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')))


if __name__ == "__main__":
    scraper = GeneralAssemblyScraper(cache_name='leg_cache')
    scraper.scrape_ga_data()
