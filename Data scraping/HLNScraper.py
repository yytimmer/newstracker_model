from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import logging
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HLNScraper:
    driver = None
    start_link = 'https://www.hln.be/net-binnen'
    chromepath = ''

    def __init__(self, chromepath):
        self.chromepath = chromepath

    def closeDriver(self):
        self.driver.quit()
        self.driver = None

    def currentArticles(self):
        logging.basicConfig(filename='HLNScraper.log',level=logging.DEBUG)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #self.driver = webdriver.Chrome('./'+ self.chromepath, chrome_options=chrome_options)
        self.driver = webdriver.Chrome('./' + self.chromepath)
        self.driver.implicitly_wait(3)

        try:
            self.driver.get(self.start_link)
        except Exception as e:
            logging.error("time out")

        # cookie agreement
        try:
            iframe_url = self.driver.find_element_by_xpath("//div/iframe").get_attribute("src")
            if 'https://cmp.dpgmedia.be/' in iframe_url:
                self.driver.get(iframe_url)
                self.driver.get(self.start_link)

                WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//div/iframe[contains(@src, 'cmp.hln.be')]")))
                self.driver.find_element_by_xpath("//button[@title='Akkoord']").click()
                self.driver.switch_to.default_content()

        except Exception as ex:
            logging.error("cookies already accepted")

        urls = self.driver.find_elements_by_xpath("//ul[@class='results__list']/li//a[@href]")
        exclusive_urls = self.driver.find_elements_by_xpath("//ul[@class='results__list']/li//a[@href]//span[@class='plus-label']/parent::div/parent::div/parent::div/parent::a[@href]")
        exclusive_urls = [excl_url.get_attribute('href') for excl_url in exclusive_urls]
        new_urls = []

        for url in urls:
            if not(url.get_attribute('href') in exclusive_urls):
                new_urls.append(url)

        return new_urls

    def extractArticle(self, url):
        logging.info(url)
        # cookie agreement
        error = []

        try:
            self.driver.get(url);
            iframe_url = self.driver.find_element_by_xpath("//div/iframe").get_attribute("src")
            if 'https://cmp.dpgmedia.be/' in iframe_url:
                self.driver.get(iframe_url)
                self.driver.get(self.url)

                WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//div/iframe')))
                self.driver.find_element_by_xpath("//button[@title='Akkoord']").click()
                self.driver.switch_to.default_content()

        except Exception as ex:
            logging.error("cookies already accepted")

        try:
            title = self.driver.find_element_by_xpath("//h1[@class='article__title']").get_attribute('textContent')

        except Exception as e:
            title = None
     
        try:
            intro_total = self.driver.find_element_by_xpath("//div[@class='article__wrapper']//p[@class='article__intro']").get_attribute('textContent')
            try:
                intro_category = '\n\t\t\t\t\t\t\t\t\t' + self.driver.find_element_by_xpath("//div[@class='article__wrapper']//p[@class='article__intro']/span").get_attribute('textContent')
            except:
               intro_category = '\n\t\t\t\t\t\t\t\t\t'

            intro = intro_total.replace(intro_category, '')


        except Exception as e:
            intro = None

        tags = []

        try:
            timestamp = self.driver.find_element_by_xpath("//div[@class='article__wrapper']//time[@class='article__time']").get_attribute('textContent')
            pattern = re.compile('(\d){2}-(\d){2}-(\d){2}, (\d){2}:(\d){2}')
            if pattern.match(timestamp):
                time_now = datetime(2000 + int(timestamp[6:8]), int(timestamp[3:5]), int(timestamp[:2]),
                                    int(timestamp[10:12]), int(timestamp[13:]))
            else:
                months = {'jan.': 1, 'feb.': 2, 'mar.': 3, 'apr.': 4, 'mei': 5, 'jun.': 6, 'jul.': 7, 'aug.': 8, 'sep.': 9, \
                          'okt.': 10, 'nov.': 11, 'dec.': 12}
                time_now = datetime(int(timestamp[8:]), months[timestamp[3:7]], int(timestamp[:2]))

        except Exception as e:
            time_now = []

          
        try:
            els = self.driver.find_elements_by_xpath("//div[@class='article__body fjs-login-gate fjs-load-remaining-content']/div/*[self::h2[@class='article__subheader'] or self::p[@class='article__paragraph']]")

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
            iframes = self.driver.find_elements_by_xpath("//div[@class='article__component article__component--snippet']//iframe")
            for iframe in iframes:
                iframe_url = iframe.get_attribute("src")
                if 'live.hln.be' in iframe_url:
                    self.driver.get(iframe_url)
                    els = self.driver.find_elements_by_xpath(
                        "//body[@itemscope='itemscope']/descendant::li[@class='instanews-moment-list__item' or @class='instanews-moment-list__item instanews-moment-list__item--highlight']/descendant::div[@class='instanews-moment  instanews-moment--simple ' or @class='instanews-moment instanews-moment--highlight instanews-moment--simple ']/descendant::text()/ancestor::*[@class='instanews-moment__paragraph' or @class='instanews-moment__title' or @class='instanews-moment__meta']")
                    break
            if len(iframes) == 0:
                iframes = None

        except Exception as e:
            els = []

        text = '' if (text is None) and (len(els) > 0) else text
        if not(iframes is None):
            for text_el in els:
                try:
                    if text != '':
                        text += '\n'

                    text += text_el.get_attribute('textContent')
                except Exception as e:
                    logging.error("No text present")

            text = None if text == "" else text

        return title, intro, text, tags, time_now, error
