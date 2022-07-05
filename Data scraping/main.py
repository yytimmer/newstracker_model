import sys, argparse, time
import psycopg2
from datetime import datetime
import re, copy
from HLNScraper import HLNScraper
from NieuwsbladScraper import NieuwsbladScraper
from StandaardScraper import StandaardScraper
from MorgenScraper import DemorgenScraper
from KnackScraper import KnackScraper
from VRTScraper import VRTScraper
import logging


# connects to article database
#TODO: these parameters should be changed by your local settings!
def connectDatabase():
    params = {
        'database': 'newstracker',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432
    }

    return psycopg2.connect(**params)

# adds a new article to the database
def addArticle(url):
    logging.info("nieuw artikel:" + str(url))
    cur = connection.cursor()
    title, intro, text, tags, time_now, error = scraper.extractArticle(url)

    if not (error) and time_now != []:

        cur.execute(
            """INSERT INTO article_version(url, version_number, online_from, online_until, article_title, article_intro, article_text, article_tags, nr_users_categorized, revision_needed, fraction_total_changed_old, fraction_total_changed_new, characters_total_changed_old, characters_total_changed_new, characters_changed_title_old, characters_changed_title_new, characters_changed_intro_old, characters_changed_intro_new, characters_changed_text_old, characters_changed_text_new, fraction_changed_title_old, fraction_changed_title_new, fraction_changed_intro_old, fraction_changed_intro_new, fraction_changed_text_old, fraction_changed_text_new) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (url, 1, time_now, None, title, intro, text, str(tags), 0, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None))

        if not ((intro is None) or (text is None)):
            total_length = len(intro) + len(text)
        else:
            if intro is None and text is None:
                total_length = 0

            else:
                if intro is None:
                    total_length = len(text)

                else:
                    total_length = len(intro)

        if total_length >= 10000:
            cur.execute("INSERT INTO long_articles(url) VALUES (%s) ON CONFLICT DO NOTHING", (url, ))

        URLPool[url] = time_now

        connection.commit()
    cur.close()


# creates new version of an already existing article
def updateArticle(url):
    cur = connection.cursor()
    title, intro, text, tags, timestamp, error = scraper.extractArticle(url)
    tags = str(tags)

    if (title != None) or (intro != None) or (text != None):

        cur.execute(
            "SELECT article_title, article_intro, article_text, article_tags, version_number FROM article_version WHERE url LIKE (%s) AND version_number = (SELECT MAX(version_number) FROM article_version WHERE url LIKE(%s))",
            (url, url))
        old_data = cur.fetchall()
        old_title = old_data[0][0]
        old_intro = old_data[0][1]
        old_text = old_data[0][2]
        old_tags = old_data[0][3]
        old_version = old_data[0][4]

        if (error == "De pagina kon niet gevonden worden") or (error == "Sorry, we kunnen u deze pagina niet tonen."):
            time_now = datetime.now()
            # time_now = datetime.now()
            cur.execute("UPDATE article_version SET online_until = (%s) WHERE url LIKE (%s) AND version_number = (%s)",
                        (time_now, url, old_version))

        elif (title != old_title) or (intro != old_intro) or (text != old_text) or (tags != old_tags):

            time_now = datetime.now()
            # time_now = datetime.now()
            cur.execute("UPDATE article_version SET online_until = (%s) WHERE url LIKE (%s) AND version_number = (%s)",
                        (time_now, url, old_version))

            cur.execute(
                "INSERT INTO article_version(url, version_number, online_from, online_until, article_title, article_intro, article_text, article_tags, nr_users_categorized, revision_needed, fraction_total_changed_old, fraction_total_changed_new, characters_total_changed_old, characters_total_changed_new, characters_changed_title_old, characters_changed_title_new, characters_changed_intro_old, characters_changed_intro_new, characters_changed_text_old, characters_changed_text_new, fraction_changed_title_old, fraction_changed_title_new, fraction_changed_intro_old, fraction_changed_intro_new, fraction_changed_text_old, fraction_changed_text_new) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (url, old_version + 1, time_now, None, title, intro, text, tags, 0, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None))

            if not((intro is None) or (text is None)):
                total_length = len(intro) + len(text)
            else:
                if intro is None and text is None:
                    total_length = 0

                else:
                    if intro is None:
                        total_length = len(text)

                    else:
                        total_length = len(intro)

            if total_length >= 10000:
                cur.execute("INSERT INTO long_articles(url) VALUES (%s) ON CONFLICT DO NOTHING", (url,))

        connection.commit()
    cur.close()


# input contains articles just scraped from newspaper
# database is updated such that new articles are added and existing articles are updated if necessary
def updateDatabaseNewArticles(new_urls):
    cur = connection.cursor()
    # cur.execute("SELECT url, online_from FROM article INNER JOIN article_version USING(url) WHERE version_number = 1")
    cur.execute("SELECT url, online_from FROM article_version WHERE version_number = 1")
    earlier_urls = cur.fetchall()

    for earlier_url in earlier_urls:
        URLPool[earlier_url[0]] = earlier_url[1]

    cur.close()

    for new_url in new_urls:
        if not (new_url in URLPool.keys()):
            addArticle(new_url)


def updateDatabaseOldArticles():

    tempPool = copy.deepcopy(URLPool)
    for url in tempPool:
        # 24 hours = 86400 seconds
        if tempPool[url] is None:
            URLPool.pop(url)

        elif ((datetime.now() - tempPool[url]).total_seconds() < 86400):
            updateArticle(url)

        else:
            URLPool.pop(url)

# main function
def main(argv):
    try:
        while True:
            articles = scraper.currentArticles()

            updateDatabaseNewArticles([article.get_attribute('href') for article in articles if article.get_attribute('href') is not None])
            updateDatabaseOldArticles()

            scraper.closeDriver()

            # sleep for ten minutes between subsequent rounds
            time.sleep(180)

    except Exception as e:
        logging.exception("program failed")
        connection.close()


connection = connectDatabase()
parser = argparse.ArgumentParser()
parser.add_argument("newspaper")
parser.add_argument("chromepath")
newspaper = parser.parse_args().newspaper
chromepath = parser.parse_args().chromepath
URLPool = {}

logSwitcher = {'HLN': 'HLNscraper.log', 'Nieuwsblad': 'Nieuwsbladscraper.log', 'Standaard': 'Standaardscraper.log',
               'DeMorgen': 'DeMorgenscraper.log', 'Knack': 'Knackscraper.log', 'VRT': 'VRTscraper.log'}
scraperSwitcher = {'HLN': HLNScraper(chromepath), 'Nieuwsblad': NieuwsbladScraper(chromepath),
                   'Standaard': StandaardScraper(chromepath), 'DeMorgen': DemorgenScraper(chromepath),
                   'Knack': KnackScraper(chromepath), 'VRT': VRTScraper(chromepath)}
logging.basicConfig(filename=logSwitcher[newspaper], level=logging.DEBUG)
scraper = scraperSwitcher[newspaper]

cur = connection.cursor()
cur.execute("SET search_path TO " + newspaper.lower())
cur.close()

if __name__ == "__main__":
    main(sys.argv[:-1])

