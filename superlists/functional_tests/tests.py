from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys


class NewVisitorTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        time.sleep(0.5)
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Mudi has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get(self.server_url)
        # She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # She types "Buy cake" into a text box (she loves cake)
        inputbox.send_keys('Buy cake')

        # When she hits enter, the page updates, and now the page lists
        # "1: Buy cake" as an item in a to-do list
        inputbox.send_keys(Keys.ENTER)
        time.sleep(0.5)
        mudi_list_url = self.browser.current_url
        self.assertRegex(mudi_list_url, '/lists/.+')
        self.check_for_row_in_list_table('1: Buy cake')

        # There is still a text box inviting her to add another item. She
        # enters "Eat cake" (Mudi is very methodical)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Eat cake')
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both items on her list
        self.check_for_row_in_list_table('1: Buy cake')
        self.check_for_row_in_list_table('2: Eat cake')

        # A new user, Frank, comes along to the site.

        # We use a new browser session to ensure nothing from Mudi is coming
        # through from cookies etc.
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Frank visits the home page with no sign of Mudi's list
        self.browser.get(self.server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy cake', page_text)
        self.assertNotIn('Eat cake', page_text)

        # Frank starts a new list by entering a new item. He is less
        # interesting than Mudi...
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)

        # Frank gets his own browser URL
        time.sleep(1)
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, mudi_list_url)

        # Again, there is no trace of Mudi's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy cake', page_text)
        self.assertNotIn('Eat cake', page_text)

        # Satisfied, they both go back to sleep

    def test_layout_and_styling(self):
        """ Tests the layout and styling of the home and list pages"""
        # Mudi goes to the home page
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=5
        )

        # She starts a new list and sees the input is nicely centered there
        # too
        inputbox.send_keys('testing\n')
        inputbox = self.browser.find_element_by_id('id_new_item')

        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=5
        )
