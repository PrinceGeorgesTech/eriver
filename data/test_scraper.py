import os
import unittest

from bs4 import BeautifulSoup
from scraper import GeneralAssemblyScraper


class ScraperTests(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.scraper = GeneralAssemblyScraper(cache_name='test_cache')

    def tearDown(self):
        os.remove('test_cache.sqlite')

    def test_organize_name(self):

        # Test regular name
        test_str = 'Washington, Alonzo T.'
        result = self.scraper.organize_name(test_str)
        self.assertEqual(
            result,
            {'last': u'Washington', 'first': u' Alonzo T.'})

        # Test name with prefix
        test_str = 'DeGrange, James E., Sr.'
        result = self.scraper.organize_name(test_str)
        self.assertEqual(
            result,
            {
                'sufix_prefix': u' Sr.',
                'last': u'DeGrange',
                'first': u' James E.'
            })

        # Test no name
        test_str = 'To Be Announced'
        result = self.scraper.organize_name(test_str)
        self.assertEqual(result, None)

    def test_fix_url(self):
        test_str = 'frmMain.aspx?pid=sponpage&tab=subject6&id=zucker&stab=01'
        result = self.scraper.fix_url(test_str)
        self.assertEqual(result, self.scraper.SITE + test_str)

    def test_extract_name_url(self):
        test_str = '<td><a href="frmMain.aspx?pid=sponpage&amp;tab=subject6&'
        test_str += 'amp;id=zucker&amp;stab=01">Zucker, Craig J.</a></td>'
        name, url = self.scraper.extract_name_url(BeautifulSoup(test_str))
        expected_name = {'last': 'Zucker', 'first': ' Craig J.'}
        expected_url = 'http://www.mgaleg.maryland.gov/webmga/frmMain.aspx'
        expected_url += '?pid=sponpage&tab=subject6&id=zucker&stab=01'
        self.assertEqual(name, expected_name)
        self.assertEqual(url, expected_url)

    def test_clean_phone_number(self):
        """Test various phone formats and make sure bad formats produce
        errors"""

        for line in ("+4 123-456-7890", "4-(123) 456 7890", "41234567890"):
            self.assertEqual(
                "+4 123-456-7890", self.scraper.clean_phone_number(line))
        for line in ("  123-456-7890", "(123) 456 7890", "1234567890"):
            self.assertEqual(
                "123-456-7890",
                self.scraper.clean_phone_number(line))
        test_lines = (
            "(928) 779-2727, ext. 145",
            "(928) 779-2727, (ext. 145)",
            "(928) 779-2727 ext. 145")
        for line in test_lines:
            self.assertEqual(
                "928-779-2727 x145", self.scraper.clean_phone_number(line))

    def test_extract_numbers(self):
        """ Verify that phone numbers are extracted and added to list"""

        phone_str = "Toll-free in MD: (928) 779-2727 ext. 145"
        expected_output = ['928-779-2727 x145']
        self.assertEqual(expected_output,
                         self.scraper.extract_numbers(phone_str))

        # Still extracts 2 numbers even if their formatting is ugly
        phone_str += "| (928) 779-1111 (ext. 145)"
        expected_output.append('928-779-1111 x145')
        self.assertEqual(expected_output,
                         self.scraper.extract_numbers(phone_str))

        # Won't extract incorrect phone numbers
        phone_str += ", (928) 779-111"
        self.assertEqual(expected_output,
                         self.scraper.extract_numbers(phone_str))

        phone_str = " (202) 663-4634 | (202) 663-7026"
        expected_output = ['202-663-4634', '202-663-7026']
        self.assertEqual(expected_output,
                         self.scraper.extract_numbers(phone_str))

if __name__ == "__main__":
    unittest.main()
