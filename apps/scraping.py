#!/usr/bin/env python
# coding: utf-8

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)
    #browser = Browser('chrome', executable_path="chromedriver", headless=True)


    def mars_news(browser):
        # Visit the mars nasa news site
        url = 'https://mars.nasa.gov/news/'
        browser.visit(url)
        # Optional delay for loading the page
        browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

        html = browser.html
        news_soup = BeautifulSoup(html, 'html.parser')

        try:
            slide_elem = news_soup.select_one('ul.item_list li.slide')

            slide_elem.find("div", class_='content_title')

            # Use the parent element to find the first `a` tag and save it as `news_title`
            news_title = slide_elem.find("div", class_='content_title').get_text()

            # Use the parent element to find the paragraph text
            news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
        except AttributeError:
            return None, None

        return news_title, news_p

    # "### Featured Images"

    def featured_image(browser):

        # Visit URL
        url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        browser.visit(url)

        # Find and click the full image button
        full_image_elem = browser.find_by_id('full_image')
        full_image_elem.click()

        # Find the more info button and click that
        browser.is_element_present_by_text('more info', wait_time=1)
        more_info_elem = browser.find_link_by_partial_text('more info')
        more_info_elem.click()

        # Parse the resulting html with soup
        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        # Find the relative image url
        try:
            img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        except AttributeError:
            return None

        # Use the base URL to create an absolute URL
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
        return img_url

    def mars_facts():
        try:
            df = pd.read_html('http://space-facts.com/mars/')[0]
        except BaseException:
            return None
        df.columns=['description', 'value']
        df.set_index('description', inplace=True)
        return df.to_html()

    def get_hemispheres(browser):
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
        # Optional delay for loading the page
        browser.is_text_present('Products', wait_time=10)
        html = browser.html
        hemisphere_soup = BeautifulSoup(html, 'html.parser')

        # Scrape the hemispher name
        hemisphere_box = hemisphere_soup.find('div', class_='collapsible results')

        hemisphere_names = hemisphere_box.find_all('h3')

        hemisphere_list = []

        for names in hemisphere_names:
            name = names.text
            more_info_elem = browser.find_link_by_partial_text(names.text)
            more_info_elem.click()
            # Parse the resulting html with soup
            html = browser.html
            img_soup = BeautifulSoup(html, 'html.parser')
            browser.is_text_present('Mimetype', wait_time=10)
            # Find the relative image url
            img_url_rel = img_soup.select_one('img.wide-image').get("src")
            # Use the base URL to create an absolute URL
            full_img_url = f'https://astrogeology.usgs.gov{img_url_rel}'
            hemisphere_data = {
                "title": name,
                "img_url": full_img_url
            }
            hemisphere_list.append(hemisphere_data)
            browser.back()

        return hemisphere_list

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "mars_hemispheres":get_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    browser.quit()
    return data

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())