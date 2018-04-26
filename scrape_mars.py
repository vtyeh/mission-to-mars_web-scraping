# Import Dependencies
import os
import pandas as pd
from bs4 import BeautifulSoup as bs
from splinter import Browser
from selenium import webdriver
import requests
import time

def init_browser():
    """ Connects path to chromedriver """
    
    executable_path = {'executable_path': '/Users/venessayeh/Downloads/chromedriver'}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    """ Scrapes all websites for Mars data """
    
    # Create a python dictionary to store all data
    scrape_mars_dict = {}
    
    # Use requests and BeautifulSoup to scrape Nasa News for latest news
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    response = requests.get(url)
    soup = bs(response.text, 'lxml')

    results = soup.find('div', class_='features')
    news_title = results.find('div', class_='content_title').text
    newsp = results.find('div', class_='rollover_description').text
    
    # Store scraped data into dictionary
    scrape_mars_dict['news_title'] = news_title
    scrape_mars_dict['newsp'] = newsp
    
    # Scrape Mars Weather twitter for latest weather report
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    twitter_response = requests.get(twitter_url)
    twitter_soup = bs(twitter_response.text, 'lxml')
    
    twitter_result = twitter_soup.find('div', class_='js-tweet-text-container')
    mars_weather = twitter_result.find('p', class_='js-tweet-text').text
    
    # Store scraped data into dictionary
    scrape_mars_dict['mars_weather'] = mars_weather

    # Scrape facts about Mars from space-facts.com using Pandas read_html function
    mars_facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(mars_facts_url)
    df = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace=True)

    # Export scraped table into an html script    
    mars_facts = df.to_html()
    mars_facts.replace("\n","")
    df.to_html('mars_facts.html')

    # Store html file to dictionary
    scrape_mars_dict['mars_facts'] = mars_facts

    # Call on chromedriver function to use for splinter
    browser = init_browser()
    
    # Scrape Nasa for url of latest featured image of Mars
    nasa_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(nasa_url)

    nasa_html = browser.html
    nasa_soup = bs(nasa_html, "lxml")

    featured_image = nasa_soup.find('div', class_='default floating_text_area ms-layer').find('footer')
    featured_image_url = 'https://www.jpl.nasa.gov'+ featured_image.find('a')['data-fancybox-href']
    
    # Store url to dictionary
    scrape_mars_dict['featured_image_url'] = featured_image_url

    # Scrape astrogeology.usgs.gov for urls of hemisphere images of Mars
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)

    hemisphere_html = browser.html
    hemisphere_soup = bs(hemisphere_html, 'lxml')
    base_url ="https://astrogeology.usgs.gov"

    image_list = hemisphere_soup.find_all('div', class_='item')

    # Create a list to store dictionary of urls and image titles
    hemisphere_image_urls = []

    # Loop through list of hemispheres and click on each one to find large resolution image
    for image in image_list:

        # Create a dicitonary to store urls and titles
        hemisphere_dict = {}
        
        # Find link to large image
        href = image.find('a', class_='itemLink product-item')
        link = base_url + href['href']

        # Visit the link
        browser.visit(link)

        # Wait 1 second 
        time.sleep(1)
        
        # Parse the html of the new page
        hemisphere_html2 = browser.html
        hemisphere_soup2 = bs(hemisphere_html2, 'lxml')

        # Find the title
        img_title = hemisphere_soup2.find('div', class_='content').find('h2', class_='title').text
        
        # Append to dict
        hemisphere_dict['title'] = img_title
    
        # Find image url
        img_url = hemisphere_soup2.find('div', class_='downloads').find('a')['href']
        
        # Append to dict
        hemisphere_dict['url_img'] = img_url
        
        # Append dict to list
        hemisphere_image_urls.append(hemisphere_dict)
    
    # Store hemisphere image urls to dictionary
    scrape_mars_dict['hemisphere_image_urls'] = hemisphere_image_urls

    return scrape_mars_dict