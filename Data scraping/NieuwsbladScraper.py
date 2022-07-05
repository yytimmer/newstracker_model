from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time
import logging

class NieuwsbladScraper:
    driver = None
    start_link = 'https://www.nieuwsblad.be/nieuws/chronologisch'
    chromepath = ''

    def __init__(self, chromepath):
        self.chromepath = chromepath

    def currentArticles(self):
        logging.basicConfig(filename='Nieuwsbladscraper.log',level=logging.DEBUG)
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

            self.driver.find_element_by_xpath("//button[@id='didomi-notice-agree-button']").click()

        except Exception as e:
            logging.error("time out")
        # article URLS
        urls = self.driver.find_elements_by_xpath("//section[@data-testid='mostrecent-per-hour-0']//li/a[@data-teaser-type='free']")


        return urls

    def closeDriver(self):
        self.driver.quit()
        self.driver = None

    def extractArticle(self, url):
        try:
            self.driver.get(url)

        except Exception as e:
            logging.error("time out article")

        try:
            error = self.driver.find_element_by_xpath("//div[@class='island slab']/p").text

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
            title = self.driver.find_element_by_xpath("//div[@data-mht-block='article-detail__article-main']//h1[@data-testid='article-title']").text
            title = None if title == "" else title

        except Exception as e:
            title = None

        try:
            els = self.driver.find_elements_by_xpath("//div[@data-mht-block='article-detail__article-main']//div[@data-testid='article-intro']/p")

            intro = None if len(els) == 0 else ''

            for intro_el in els:
                if intro != '':
                    intro += '\n'
                try:
                    intro += intro_el.text
                except Exception as e:
                    logging.error("No text present")

            intro = None if intro == '' else intro

        except Exception as e:
            intro = None
    
        try:
            els = self.driver.find_elements_by_xpath("//div[@data-mht-block='article-detail__article-main']//div[@data-testid='article-body']/p")
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
            els = self.driver.find_elements_by_xpath("//div[@data-mht-block='article-detail__article-main']//div[@data-testid='scribble-native']//li[@data-testid='scribble-post']/*[self::header or self::div]")

        except Exception as e:
            els = []

        text = '' if (text is None) and (len(els) > 0) else text

        for text_el in els:
            if text != '':
                text += '\n'
            if text_el.tag_name == 'header':
                text += '\n\n'
            try:
                text += text_el.text
            except Exception as e:
                logging.error("No text present")

        text = text if text != "" else None

        tags = []

        try:
            timestamp = self.driver.find_elements_by_xpath("//time[@data-testid='article-date']")
            if len(timestamp) == 0:
                raise Exception

            timestamp = timestamp[0].get_attribute('datetime')
            if int(timestamp[11:13]) < 22:
                time_now = datetime(int(timestamp[:4]), int(timestamp[5:7]), int(timestamp[8:10]), int(timestamp[11:13]) + 2, int(timestamp[14:16]))

            else:
                time_now = datetime(int(timestamp[:4]), int(timestamp[5:7]), int(timestamp[8:10]),
                                    int(timestamp[11:13]) - 22, int(timestamp[14:16])) + timedelta(days=1)

        except Exception as e:
            time_now = None
         
        return title, intro, text, tags, time_now, error
