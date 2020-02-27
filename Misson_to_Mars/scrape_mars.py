
import pandas as pd
from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from splinter import Browser

def init_browser():
    #get_ipython().system('which chromedriver')
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser= init_browser()
    mars={}

    #Scrape latest news about Mars

    url='https://mars.nasa.gov/news/'
    browser.visit(url)

    #Need to move mouse down on page to trigger the sites javascript. Otherwsie we can't see HTML for article
    browser.find_by_tag('li').mouse_over()

    html=browser.html
    soup = BeautifulSoup(html, 'html.parser')
    news=soup.find('div', class_="content_title")
    mars['news_title'] = news.text
    news_p= soup.find('div', class_="article_teaser_body")
    mars['news_p'] =news_p.text


    ## Scrape the feature image of Mars from nasa --------------------------------------------
    url_for_image = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_for_image)

    browser.links.find_by_partial_text('FULL IMAGE').click()
    browser.links.find_by_partial_text('more info').click()

    image_html = browser.html
    soup_image=BeautifulSoup(image_html, 'html.parser')
    
    target_url=soup_image.find('img', class_='main_image')['src']
    partial_url='https://www.jpl.nasa.gov/'

    mars['main_img']=partial_url+target_url


    ## Scrape the latest Weather on Mars via Twitter ------------------------------

    weather_url = 'https://twitter.com/marswxreport?lang=en'

    weather_response=requests.get(weather_url)
    soup_weather=BeautifulSoup(weather_response.text, 'html.parser')

    mars_weather=soup_weather.find('div', class_='js-tweet-text-container').p.text.strip()

    #Replace \n with a space
    mars_weather = mars_weather.replace("\n", " ")

    #remove unrelated text at the end
    mars['weather'] = mars_weather.split('pic.twitter', 1)[0]


    ## Scrape Mars Facts ----------------------------------------------------

    facts_url='https://space-facts.com/mars/'

    tables = pd.read_html(facts_url)
    df=tables[0]
    html_table=df.to_html(header=False, index=False)
    mars['facts'] = html_table


    ## Scrape images of Mars' Hemispheres ----------------------------------------------------

    hem_url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(hem_url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    title_list=[]
    img_sub_url_list=[]
    img_url_list=[]

    hemispheres=soup.find_all('div', class_='item')

    for hemi in hemispheres:
        title = hemi.find('h3').text
        sub_img_url=hemi.find('a')['href']
        title=title.split(' Enhanced', 1)[0]
        title_list.append(title)
        img_sub_url_list.append(sub_img_url)

    img_sub_url_list= ['https://astrogeology.usgs.gov' + url for url in img_sub_url_list]

    for link in img_sub_url_list:
        browser.visit(link)
        sub_html=browser.html
        sub_soup = BeautifulSoup(sub_html, 'html.parser')
        img_lnk=sub_soup.find('a', href=True, text='Sample')['href']
        img_url_list.append(img_lnk)

    browser.quit()

    hemisphere_image_urls=[{'title':title, 'img_url':url} for title, url in zip(title_list, img_url_list)]

    mars['hemispheres']=hemisphere_image_urls
    
    return mars