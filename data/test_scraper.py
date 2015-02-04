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

if __name__ == "__main__":
    unittest.main()
