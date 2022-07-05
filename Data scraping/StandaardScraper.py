from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import logging


class StandaardScraper:
    driver = None
    start_link = 'http://www.standaard.be/nieuws/chronologisch'
    chromepath = ''

    def __init__(self, chromepath):
        self.chromepath = chromepath

    def currentArticles(self):
        logging.basicConfig(filename='Standaardscraper.log', level=logging.DEBUG)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('./'+ self.chromepath, chrome_options=chrome_options)
        #self.driver = webdriver.Chrome('./' + self.chromepath)
        self.driver.implicitly_wait(3)

        self.driver.set_page_load_timeout(10)

        try:
            self.driver.get(self.start_link)

        except Exception as e:
            logging.error("time out")
        # article URLS
        urls = self.driver.find_elements_by_xpath("//div[@data-mht-widget='mostrecentarticlesoverview-for-chronological-extra-page']/descendant::a[@class='link-live']")
        exclusive_urls = self.driver.find_elements_by_xpath(
            "//div[@data-mht-widget='mostrecentarticlesoverview-for-chronological-extra-page']/descendant::a[@class='link-live']/*[name()='svg' and @class = 'icon icon-logo_naasttitel icon-logo_naasttitel']/parent::a")
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
        try:
            self.driver.get(url)

        except Exception as e:
            logging.error("time out article")

        try:
            error = self.driver.find_element_by_xpath("//div[@class='island']/h4").text

        except Exception as e:
            error = ""

        try:
            cookie_alert = self.driver.find_element_by_xpath("//button[@id='didomi-notice-agree-button']")

        except Exception as e:
            cookie_alert = None

        if cookie_alert != None:
            cookie_alert.click()
            time.sleep(3)

        try:
            title = self.driver.find_element_by_xpath("//header[@class='article__header']/h1").text
            title = None if title == "" else title

        except Exception as e:
            title = None

        try:
            intro = self.driver.find_element_by_xpath("//article/div[@class='article__body']/div[@class='intro']|//div[@class='col-5']/descendant::div[@class='slideshow__intro']").text
            intro = None if intro == "" else intro

        except Exception as e:
            intro = None

        try:
            els = self.driver.find_elements_by_xpath(
                "//div[@class='grid__col']/descendant::div[@class='slideshow__intro']/p[1]|(//div[@class='article__body'])[1]/p[not(b) and not(strong)]|//div[@class='NB-body']/p[not(strong) and not(b)]")

        except Exception as e:
            els = []

        text = None if len(els) == 0 else ''

        for text_el in els:
            if text != '':
                text += '\n'
            try:
                text += text_el.text
            except Exception as e:
                logging.error("No text present")

        try:
            els = self.driver.find_elements_by_xpath("//div[@class='live-feed__item__body']")
            els_time = self.driver.find_elements_by_xpath("//header[@class='live-feed__item__header']/time")

        except Exception as e:
            els = []
            els_time = []

        text = '' if (text is None) and (len(els) > 0) else text

        for i, text_el in enumerate(els):
            if text != '':
                text += '\n\n'

            try:
                text += els_time[i].text + '\n'
                text += text_el.text

            except Exception as e:
                logging.error("No text present")

        text = text if text != "" else None

        try:
            els = self.driver.find_elements_by_xpath("//p[@class='tag-list']/a")
            tags = [el.text for el in els]
            tags = sorted(tags, key=str.casefold)

        except Exception as e:
            tags = []

        try:
            timestamp = self.driver.find_elements_by_xpath("//time")
            if len(timestamp) == 0:
                raise Exception

            timestamp = timestamp[0].get_attribute('datetime')
            time_now = datetime(int(timestamp[:4]), int(timestamp[5:7]), int(timestamp[8:10]), int(timestamp[11:13]),
                                int(timestamp[14:16]))

        except Exception as e:
            time_now = None

        return title, intro, text, tags, time_now, error
