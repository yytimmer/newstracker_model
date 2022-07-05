from builtins import Exception, int, len, sorted, str

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class VRTScraper:
    driver = None
    start_link = 'https://www.vrt.be/vrtnws/nl/net-binnen/'
    chromepath = ''

    def __init__(self, chromepath):
        self.chromepath = chromepath

    def currentArticles(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #self.driver = webdriver.Chrome('./'+self.chromepath, chrome_options=chrome_options)
        self.driver = webdriver.Chrome('./' + self.chromepath)
        self.driver.implicitly_wait(3)

        self.driver.set_page_load_timeout(10)

        try:
            self.driver.get(self.start_link)

        except Exception as e:
            logging.error("time out")

        # cookie agreement
        try:
            iframe_url = self.driver.find_element_by_xpath("//div[starts-with(@id, 'sp_message_container_')]/iframe").get_attribute("src")
            self.driver.get(iframe_url)
        except Exception as e:
            logging.error("no time frame")

        self.driver.get(self.start_link)

        try:
            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//div[starts-with(@id, 'sp_message_container_')]/iframe")))
        except Exception as e:
            logging.error("no button")

        try:
            self.driver.find_element_by_xpath("//button[@class='message-component message-button no-children focusable button sp_choice_type_11 last-focusable-el']").click()
        except Exception as e:
            logging.error("no button")
        self.driver.switch_to.default_content()
        self.driver.implicitly_wait(3)

        # article URLS
        urls = self.driver.find_elements_by_xpath("//li[@class='vrt-mostrecent__article']/descendant::a")
        exclusive_urls = self.driver.find_elements_by_xpath("//span[@class='vrt-teaser__tag-main vrt-tag-main' and (text()='Herbekijk' or text() = 'Live')]/ancestor::li[@class='vrt-mostrecent__article']/descendant::a")
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
            iframe_url = self.driver.find_element_by_xpath("//div[starts-with(@id, 'sp_message_container_')]/iframe").get_attribute("src")
            self.driver.get(iframe_url)
        except Exception as e:
            logging.error("no time frame")

        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//div[starts-with(@id, 'sp_message_container_')]/iframe")))
        except Exception as e:
            logging.error("no button")
        try:
            self.driver.find_element_by_xpath("//button[@class='message-component message-button no-children focusable button sp_choice_type_11 last-focusable-el']").click()
        except Exception as e:
            logging.error("no button")
        self.driver.switch_to.default_content()
        self.driver.implicitly_wait(3)

        try:
            error = self.driver.find_element_by_xpath("//div[@class='error__title']/h1").text

        except Exception as e:
            error = ""

        try:
            if 'sporza.be' in url:
                title = self.driver.find_element_by_xpath("//div[@class='title']/descendant::h1|//header[@class='vrt-article__header']/h1").text
            else:
                title = self.driver.find_element_by_xpath("//div[@class='article__title']/descendant::h1|//header[@class='vrt-article__header']/h1").text
            title = None if title == "" else title

        except Exception as e:
            title = None

        try:
            intro = self.driver.find_element_by_xpath("//div[@class='article__intro']/descendant::p|//div[@class='vrt-article__intro']/descendant::p").text
            intro = None if intro == "" else intro

        except Exception as e:
            intro = None

        try:
            els = self.driver.find_elements_by_xpath("//section[@class='article__body']/div[@class='article__par']/div[@class='text']/descendant::div[@class='cmp-text']/p[not(@id) and not(@class)]|//div[@class='text parbase']|//section[@class='article__body']/div[@class='article__par']/div[@class='paragraph-title title']/h2|//section[@class='article__body']/div[@class='article__par']/div[@class='text']//li|//section[@class='article__body']/div[@class='article__par']/div[@class='text']/descendant::div[@class='cmp-text']/div")

        except Exception as e:
            els = []


        text = None if len(els) == 0 else ''

        for text_el in els:
            if text != '':
                text += '\n'
            text += text_el.text

        try:
            els = self.driver.find_elements_by_xpath("//section[@class='article__body']/descendant::div[@class='liveblog-section']/descendant::div[@class='liveblog-item']")

        except Exception as e:
            els = []

        text = '' if (text is None) and (len(els) > 0) else text

        for text_el in els:
            if text != '':
                text += '\n'
            if text_el.tag_name == 'div':
                text += '\n\n'
            try:
                text += text_el.text
            except Exception as e:
                logging.error("No text present")

        try:
            els = self.driver.find_elements_by_xpath("//ol[@class='sc-timeline__list']/descendant::li[starts-with(@class,'sc-timeline__list-item sc-bg sc-timeline__list-item')]")

        except Exception as e:
            els = []

        text = '' if (text is None) and (len(els) > 0) else text

        for text_el in els:
            try:
                if text != '':
                    text += '\n'
                if text_el.tag_name == 'div':
                    text += '\n\n'

                text += text_el.text
            except Exception as e:
                logging.error("No text present")

        text = text if text != "" else None

        try:
            timestamp = self.driver.find_element_by_xpath("//div[@class='article__publication-date']/descendant::time")

            if timestamp:
                timestamp = timestamp.get_attribute('datetime')
                time_now = datetime(int(timestamp[:4]), int(timestamp[5:7]), int(timestamp[8:10]), int(timestamp[11:13]), int(timestamp[14:16]))

        except Exception as e:
            try:
                day = self.driver.find_element_by_xpath("//span[@class='vrt-publication-date__day']").text
                time = self.driver.find_element_by_xpath("//span[@class='vrt-publication-date__time']").text

                months = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7,
                        'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12}

                time_now = datetime(int(day[-4:]), int(months[day[6:-5]]), int(day[3:5]), int(time[0:2]), int(time[3:5]))

            except Exception as e:
                time_now = None

        try:
            if 'sporza.be' in url:
                els = self.driver.find_elements_by_xpath("//div[@class='vrt-tags']/descendant::a")
            else:
                els = self.driver.find_elements_by_xpath("//div[@class='vrt-tag-links']/descendant::a")

            tags = [el.text for el in els]
            tags = sorted(tags, key=str.casefold)

        except Exception as e:
            tags = []

        return title, intro, text, tags, time_now, error
