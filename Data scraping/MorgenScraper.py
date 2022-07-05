from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import logging
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re


class DemorgenScraper:
    driver = None
    start_link = 'https://www.demorgen.be/zoek/meest-recent'
    chromepath = ''

    def __init__(self, chromepath):
        self.chromepath = chromepath

    def currentArticles(self):
        logging.basicConfig(filename='DeMorgenscraper.log', level=logging.DEBUG)

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('./'+ self.chromepath, chrome_options = chrome_options)
        #self.driver = webdriver.Chrome('./' + self.chromepath)
        self.driver.implicitly_wait(3)

        self.driver.set_page_load_timeout(10)

        try:
            self.driver.get(self.start_link)

        except Exception as e:
            logging.error("time out")

        # cookie agreement
        try:
            iframe_url = self.driver.find_element_by_xpath("//div/iframe").get_attribute("src")
            self.driver.get(iframe_url)
            self.driver.get(self.start_link)

            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//div/iframe')))
            self.driver.find_element_by_xpath("//button[@title='Akkoord']").click()
            self.driver.switch_to.default_content();

        except Exception as ex:
            logging.error("cookies already accepted")


        # article URLS
        urls = self.driver.find_elements_by_xpath("//ul[@class='articles-list articles-list--bordered']/descendant::a|//article/a")
        exclusive_urls = self.driver.find_elements_by_xpath(
            "//ul[@class='articles-list articles-list--bordered']/descendant::article/descendant::span[@class='ankeiler__meta']/div[@class='ribbon-wrapper ribbon-wrapper--has-ribbon']/ancestor::article/a"
            "|//article/descendant::span[@class='teaser__plus-label']/ancestor::article/a")
        exclusive_urls = [excl_url.get_attribute('href') for excl_url in exclusive_urls]

        new_urls = []
        for url in urls:
            if not (url.get_attribute('href') in exclusive_urls):
                new_urls.append(url)
        return new_urls

    def closeDriver(self):
        self.driver.quit()
        self.driver = None

    def extractArticle(self, url):
        logging.info(url)
        try:
            self.driver.get(url)

        except Exception as e:
            logging.error("time out article")

        try:
            error = self.driver.find_element_by_xpath("//div[@class='four-o-four fjs-four-o-four']/descendant::h3").text

        except Exception as e:
            error = ""

        try:
            cookie = self.driver.find_element_by_xpath("//section[@class='page fjs-floater-area']/form/button[@class='button fjs-set-consent' and @value='accept-all']")
            cookie.click()

        except Exception as e:
            cookie = ""

        try:
            overlay = self.driver.find_element_by_xpath("//div[@id='pushengage-overlay-close']")
            overlay.click()

        except Exception as e:
            overlay = []

        try:
            title = self.driver.find_element_by_xpath("//header[@class='article__header']/h1|//h1[starts-with(@class, artstyle__header-title)]").text
            title = None if title == "" else title

        except Exception as e:
            title = None

        try:
            intro = self.driver.find_element_by_xpath("//p[@class='article__intro fjs-article__intro ']|//p[@class='artstyle__intro ']|p[@class='artstyle__intro artstyle__intro--type-luxe ']/span|//p[@class='artstyle__intro fu--type-luxe artstyle__intro--type-luxe ']|//p[@class='artstyle__intro artstyle__intro-- fu-- artstyle__intro--type-luxe fu--type-luxe']").get_attribute('textContent')
            intro = None if intro == "" else intro
            intro = intro.replace('\n    ', '')

        except Exception as e:
            intro = None

        try:
            els = self.driver.find_elements_by_xpath("//ul[@class='inline-list']/descendant::span|//ul[@class='tags-list']/li")
            tags = [el.get_attribute('textContent') for el in els]
            tags = sorted(tags, key=str.casefold)

        except Exception as e:
            tags = []

        try:
            timestamp = self.driver.find_element_by_xpath("//time[@class='artstyle__production__datetime']").get_attribute('dateTime')

            pattern = '(\d{2}) ([a-z]+) (\d{4})'

            match1 = re.search(pattern, timestamp)
            if match1 is None:
                pattern = '(\d{1}) ([a-z]+) (\d{4})'
                match1 = re.search(pattern, timestamp)

            try:
                timestamp2 = self.driver.find_element_by_xpath("//time[@class='artstyle__production__datetime']/span[@class='artstyle__production__time']").get_attribute('textContent')
                pattern = ', (\d{1,2}):(\d{1,2})'

                match2 = re.search(pattern, timestamp2)
                months = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8,
                          'september': 9, \
                          'oktober': 10, 'november': 11, 'december': 12}

                time_now = datetime(int(match1.group(3)), int(months[match1.group(2)]), int(match1.group(1)), int(match2.group(1)),
                                    int(match2.group(2)))
            except Exception as e:
                months = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7,
                          'augustus': 8,
                          'september': 9, \
                          'oktober': 10, 'november': 11, 'december': 12}

                time_now = datetime(int(match1.group(3)), int(months[match1.group(2)]), int(match1.group(1)), 0, 0)


        except Exception as e:
            time_now = None

        if not(time_now):
            try:
                timestamp = self.driver.find_elements_by_xpath("//time[@class='artstyle__production__datetime']")

                timestamp = timestamp[0].get_attribute('datetime')
                pattern = '(\d{2}) ([a-z]+) (\d{4}), (\d{2}):(\d{2})'
                match = re.search(pattern, timestamp)
                months = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8, 'september': 9, \
                          'oktober': 10, 'november': 11, 'december': 12}

                time_now = datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)), int(match.group(4)),
                                    int(match.group(5)))

            except Exception as e:
                time_now = None

        try:
            els = self.driver.find_elements_by_xpath("//section[@class='artstyle__main']//*[self::p[@class='artstyle__paragraph '] or self::h4[@class='artstyle__container__title'] or self::p[@class='artstyle__container__text']]")

        except Exception as e:
            els = []

        text = None if len(els) == 0 else ''

        for text_el in els:
            if text != '':
                text += '\n'
            try:
                text += text_el.get_attribute('textContent')
            except Exception as e:
                logging.error("No text present")

        try:
            els = self.driver.find_elements_by_xpath("//div[@class='artstyle__element--livefeed']//li[@class='live-blog__moment-list__item']//*[self::p or self::h2 or self::div[@class='live-blog__moment__date']]")

        except Exception as e:
            els = []

        text = '' if (text is None) and (len(els) > 0) else text

        for i, text_el in enumerate(els):
            wait = WebDriverWait(self.driver, 10)
            if text != '':
                text += '\n'

            stale = True
            while stale:
                try:
                    tag_name = wait.until(EC.presence_of_element_located((By.XPATH,"(//div[@class='artstyle__element--livefeed']//li[@class='live-blog__moment-list__item']//*[self::p or self::h2 or self::div[@class='live-blog__moment__date']])[" + str(i + 1) + "]"))).tag_name
                    stale = False
                except Exception as e:
                    stale = True

            if tag_name == 'div':
                text += '\n\n'
            try:
                stale = True
                while stale:
                    try:
                        textContent = wait.until(EC.presence_of_element_located((By.XPATH,"(//div[@class='artstyle__element--livefeed']//li[@class='live-blog__moment-list__item']//*[self::p or self::h2 or self::div[@class='live-blog__moment__date']])[" + str(
                                                                                  i + 1) + "]"))).get_attribute('textContent')
                        stale = False
                    except Exception as e:
                        stale = True

                text += textContent
            except Exception as e:
                logging.error("No text present")

        text = text if text != "" else None
        if text:
            text = text.replace('\n    ', '')
        return title, intro, text, tags, time_now, error
