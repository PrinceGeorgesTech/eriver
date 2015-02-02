import requests
import re
from bs4 import BeautifulSoup

SENATE = 'http://msa.maryland.gov/msa/mdmanual/05sen/html/senal.html'
HOUSE = 'http://msa.maryland.gov/msa/mdmanual/06hse/html/hseal.html'

CONTACT = re.compile(
    r'<li><a[\s]href="(.*?\.html)">(.*?)</a>([\s\w\(\)]+),(.*?\d+\w?)')


def clean_site(site):
    return "http://msa.maryland.gov/%s" % site


def clean_name(name):

    name_dict = {}

    split_name = name.split(',')
    name_dict["first"] = split_name[1]
    name_dict["last"] = split_name[0]

    # Extract Sufix/Prefix
    if len(split_name) == 3:
        name_dict["sufix_prefix"] = split_name[2]

    return name_dict


def clean_party(party):
    return party.strip("() ")


def clean_district(district):
    return district.replace('District', '').strip()


def scrape_personal_page(site):

    html = requests.get(site)
    soup = BeautifulSoup(html)
    for

def organize_contacts(contacts):

    contact_list = []
    for contact in contacts:

        # Get and clean data
        site, name, party, district = contact
        site = clean_site(site)
        name = clean_name(name)
        party = clean_party(party)
        district = clean_district(district)

        # Get personal page data
        data = scrape_personal_page(site)

        contact_list.append({
            'site': site,
            'name': name,
            'party': party,
            'district': district})

        break

    return contact_list


def scrape_general_assembly():

    # Get Senate
    html = requests.get(SENATE)
    senators = CONTACT.findall(html.text)
    senators = organize_contacts(contacts=senators)

    # Get House
    html = requests.get(HOUSE)
    representatives = CONTACT.findall(html.text)
    representatives = organize_contacts(contacts=representatives)


if __name__ == "__main__":
    scrape_general_assembly()
