import facebookinsights as fi
import unittest


class TestBase(unittest.TestCase):
    def setUp(self):
        pages = fi.authorize()
        if not len(pages):
            raise Exception("Cannot proceed with unit testing: \
                the authorized Facebook account does not have access \
                to any Facebook Page Insights.")
        
        self.page = pages[0]


class TestAuthorization(TestBase):
    pass


class TestQuerying(TestBase):
    def test_range_days(self):
        """ It should support various ways of defining date ranges, 
        and these will result in the correct start and end dates. """

    def test_range_months(self):
        """ It should support various ways of defining date ranges, 
        and these will result in the correct start and end dates. """

    def test_page_query(self):
        """ It should be able to run a page query and return a report. """

    def test_post_query(self):
        """ It should be able to run a post query and return a report. """

    def test_query_immutable(self):
        """ It should always refine queries by creating a new query and 
        never modify the original base query. """

    def test_period(self):
        """ It should have shortcut functions that make it easier to
        define the period (day, week, 28_days, lifetime) at which 
        the API should return results. """

    def test_latest(self):
        """ It can limit the total amount of results. """


if __name__ == '__main__':
    unittest.main()