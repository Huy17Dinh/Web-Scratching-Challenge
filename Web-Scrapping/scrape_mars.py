from http.server import executable
from matplotlib.pyplot import cla, text
import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

#Setting up the database
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars

#Setting up initial browser
def initial_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = initial_browser()
    collection.drop()

    # Nasa Mars news
    news_url = 'https://redplanetscience.com/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html, 'html.parser')
    news_title = news_soup.find("div", class_="content_title").text
    news_parag = news_soup.find("div", class_="article_teaser_body").text 

    # JPL Mars Space images - Featured images
    jpl_url = 'https://spaceimages-mars.com/'
    browser.visit(jpl_url)
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, 'html.parser')
    img_url = jpl_soup.find('div', class_='div1').a['href']
    feature_url = 'https://spaceimages-mars.com/' + img_url


    #Mars fact 
    m_url = 'https://space-facts.com/mars/'
    table = pd.read_html(m_url)
    mars_df = table[0]
    mars_df.columns = ['Category', 'Measurement']
    mars_df = mars_df.set_index('Category')
    mars_fact_html = mars_df.to_html()

    # Mars Hemispheres
    mh_url = 'https://marshemispheres.com/'
    browser.visit(mh_url)
    mhtml = browser.html
    mh_soup = bs(mhtml, 'html.parser')
    results = mh_soup.find_all("div", class_='item')
    hemisphere_image_urls = []
    for result in results:
        product_dict = {}
        titles = result.find('h3').text
        end_link = result.find('a')['href']
        image_link = f"https://marshemispheres.com/{end_link}" 
        browser.visit(image_link)
        html = browser.html
        soup = bs(html, 'html.parser')
        download = soup.find("div", class_="downloads")
        image_url = "https://marshemispheres.com/" + download.find("img")["src"]
        product_dict['title'] = titles
        product_dict['image_url'] = image_url
        hemisphere_image_urls.append(product_dict)

    browser.quit()

    mars_data = {
        'news_title': news_title,
        'summary': news_parag,
        'fact_table': mars_fact_html,
        'featured_image': feature_url,
        'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jpl_url,
        'fact_url': m_url,
        'hemisphere_url': mh_url
    }
    collection.insert(mars_data)


