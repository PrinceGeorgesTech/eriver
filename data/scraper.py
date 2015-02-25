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
        self.ADDY_RE = re.compile(
            r"""(?P<city>.*)"""
            r"""[\s]*?,[\s]*?(?P<state>[A-Z\.]{2,4})"""
            r"""\s*(?P<zip>[0-9-]+)""")
        self.PHONE_RE = re.compile(
            r"""(?P<prefix>\+?[\d\s\(\)\-]*)"""
            r"""(?P<area_code>\(?\d{3}\)?[\s\-\(\)]*)"""
            r"""(?P<first_three>\d{3}[\-\s\(\)]*)"""
            r"""(?P<last_four>\d{4}[\-\s]*)"""
            r"""(?P<extension>[\s\(,]*?ext[ .]*?\d{3,5})?"""
            r"""(?P<tty>\s*\(tty)?""", re.IGNORECASE)

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

    def clean_phone_number(self, line):
        """
        Given "(123) 456-7890 (Telephone)", extract the number and format
        """
        match = self.PHONE_RE.search(line)
        if match:
            # kill all non-numbers
            prefix = "".join(ch for ch in match.group("prefix") if ch.isdigit())
            area_code = "".join(ch for ch in match.group("area_code")
                                if ch.isdigit())
            first_three = "".join(ch for ch in match.group("first_three")
                                  if ch.isdigit())
            last_four = "".join(ch for ch in match.group("last_four")
                                if ch.isdigit())
            number = "-".join([area_code, first_three, last_four])
            if prefix:
                number = "+" + prefix + " " + number
            extension = match.group("extension")
            if extension:
                extension = re.sub("\D", "", extension)
                number = number + " x" + extension
            return number

    def extract_numbers(self, phones):
        """
        Extracts all phone numbers from a line and adds them to a list
        """

        clean_numbers = []
        phones = re.sub('Toll-free in MD:', '', phones)
        phones = phones.split("|")
        for phone in phones:
            phone = phone.strip()
            if self.PHONE_RE.match(phone):
                clean_numbers.append(self.clean_phone_number(phone))
        return clean_numbers

    def parse_address(self, address_elements):
        """ Parse address and return address dict """

        address_dict = {}
        address_lines = []
        for line in address_elements:
            address_match = self.ADDY_RE.search(line)
            if address_match:
                address_dict['city'] = address_match.group('city')
                address_dict['state'] = address_match.group('state')
                address_dict['zip'] = address_match.group('zip')
            elif line.startswith('Phone'):
                phone = self.extract_numbers(line)
                if len(phone) > 0:
                    address_dict['phone_numbers'] = phone
            elif line.startswith('Fax'):
                fax = self.extract_numbers(line)
                if len(fax) > 0:
                    address_dict['fax'] = fax[-1]
            else:
                address_lines.append(line)
        address_dict['address_lines'] = address_lines
        return address_dict


    def extract_content_lines(self, title):
        """ Funnels html into correct scraper for formatting """

        content_lines = []
        if title.text.strip(' :') == "Contact":
            email = self.EMAIL.search(title.next_sibling.text)
            if email:
                content_lines = email.group(0)
        elif "Address" in title.text:
            content_lines = self.parse_address(title.next_sibling.strings)
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
