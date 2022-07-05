from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import logging


class KnackScraper:
    driver = None
    start_link = 'https://www.knack.be/nieuws/recent-nieuws/'
    chromepath = ''

    def __init__(self, chromepath):
        self.chromepath = chromepath

    def currentArticles(self):
        logging.basicConfig(filename='Knackscraper.log', level=logging.DEBUG)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('./'+self.chromepath, chrome_options=chrome_options)
        #self.driver = webdriver.Chrome('./' + self.chromepath)
        self.driver.implicitly_wait(3)

        self.driver.set_page_load_timeout(10)

        try:
            self.driver.get(self.start_link)

        except Exception as e:
            logging.error("time out")

        # cookie agreement
        try:
            self.driver.find_element_by_xpath("//button[@id='didomi-notice-agree-button']").click()
            self.driver.implicitly_wait(3)
            time.sleep(5)
        except Exception as e:
            logging.error('no button')

        try:
            self.driver.get(self.start_link)
        except Exception as e:
            logging.error("time out")

        # article URLS
        urls = self.driver.find_elements_by_xpath("//div[@class='rmgMasonry']/article/descendant::div[@class='rmgTeaser-title m-altTitle']/a")
        urls2 = self.driver.find_elements_by_xpath("//div[@class='rmgMasonry']/descendant::div[@class='rmgGrid js-replace-by-search']/article/descendant::div[@class='rmgTeaser-title m-altTitle']/a")
        urls.extend(urls2)

        exclusive_urls = self.driver.find_elements_by_xpath(
            "//div[@class='rmgMasonry']/article/descendant::span[@class='rmgIcon m-plus']/parent::div/following-sibling::a")
        exclusive_urls2 = self.driver.find_elements_by_xpath(
            "//div[@class='rmgMasonry']/descendant::div[@class='rmgGrid js-replace-by-search']/article/descendant::span[@class='rmgIcon m-plus']/parent::div/following-sibling::a")
        exclusive_urls.extend(exclusive_urls2)
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
            self.driver.find_element_by_xpath("//button[@id='didomi-notice-agree-button']").click()
            self.driver.implicitly_wait(3)
            time.sleep(5)
        except Exception as e:
            logging.error('no button')

        try:
            error = self.driver.find_element_by_xpath("//header[@class='page-header border']/h1").get_attribute('textContent')

        except Exception as e:
            error = ""

        try:
            self.driver.find_element_by_xpath("//a[@class='fancybox-item fancybox-close']").click()
            self.driver.implicitly_wait(3)
            time.sleep(5)

        except Exception as e:
            error = ""

        try:
            title = self.driver.find_element_by_xpath("//h1[@class='rmgDetail-title m-altTitle']").text
            title = None if title == "" else title

        except Exception as e:
            title = None

        try:
            intro = self.driver.find_element_by_xpath("//p[@class='rmgDetail-intro']").get_attribute('textContent')
            intro = None if intro == "" else intro

        except Exception as e:
            intro = None

        try:
            els = self.driver.find_elements_by_xpath("//div[@class='rmgDetail-body article-body']/p | //div[@class='js-detail-body']/descendant::p")

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
            els = self.driver.find_elements_by_xpath("//div[@class='rmgDetail-live-item']")

        except Exception as e:
            els = []

        text = '' if (text is None) and (len(els) > 0) else text

        for text_el in els:
            try:
                if text != '':
                    text += '\n'
                if text_el.tag_name == 'div':
                    text += '\n\n'

                text += text_el.get_attribute('textContent').replace('''OP ZOEK NAAR EEN JOB IN JOUW BUURT?
ONTDEK ONZE VACATURES
BEGIN MET ZOEKEN >>''', '').replace('''      Op zoek naar een job in jouw buurt? 
      Ontdek onze vacatures 
      
     
    BEGIN MET ZOEKEN >> ''', '')
            except Exception as e:
                logging.error("No text present")


        text = text if text != "" else None

        try:
            els = self.driver.find_elements_by_xpath("//ul[@id='detail-tags']/li/a")
            tags = [el.get_attribute('textContent') for el in els if el.get_attribute('textContent') != '']
            tags = sorted(tags, key=str.casefold)

        except Exception as e:
            tags = []
        try:
            timestamp = self.driver.find_elements_by_xpath("//ul[@class='rmgDetail-meta']/li[1]")[0].text
            time_now = datetime(2000 + int(timestamp[6:8]), int(timestamp[3:5]), int(timestamp[:2]), int(timestamp[12:14]),
                                int(timestamp[15:17]))

        except Exception as e:
            time_now = None

        return title, intro, text, tags, time_now, error
