#! usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from decimal import Decimal
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider
from starform.items import linksItem
import os
import re
import unicodecsv

def amend_going(going):
	going = going.replace("all-weather  ", "")
	goingwords = going.split(" ")
	if len(goingwords) == 1:
		going = goingwords[0]
	elif len(goingwords) == 3:
		going = " ".join(goingwords[0:3])
	elif goingwords[1] == "course:":
		going = goingwords[2]
	else:
		going = "n/a"
	return going

def amend_racedate(sometext):
    newtext = sometext[0:4] + "-" + sometext[4:6] + "-" + sometext[6:]
    return newtext

def calculate_furlongs(distance):
    miles = re.search(r'([0-9]]*)m', distance)
    furlongs = re.search(r'([0-9]*)f', distance)
    yards = re.search(r'\s([0-9]*)yds', distance)
    if miles:
        miles = int(miles.group(1)) * 8
    else:
        miles = 0.00
    if furlongs:
        furlongs = int(furlongs.group(1))
    else:
        furlongs = 0.00
    if yards:
        yards = round((float(yards.group(1)) / 220), 2)
    else:
        yards = 0.00
    newdist = miles + furlongs + yards
    return newdist

def get_user_dates():
    # creates timeform daypage links from user input and iterating python calendar dates
    daypages = []
    rawdate = raw_input('Please enter a start date for scraping (in the format yyyymmdd): ')
    yr = int(rawdate[0:4])
    mth = int(rawdate[4:6])
    day = int(rawdate[6:8])
    no_days = int(raw_input('How many days do you want to scrape?: '))
    n = 0
    while n < no_days:
        newdate = str(date(yr, mth, day) + timedelta(days=n))
        daypage = 'https://www.timeform.com/horse-racing/results/{}'.format(newdate)
        daypages.append(daypage)
        n += 1
    return daypages

class linksSpider(Spider):
    name = "links"
    # start_urls = get_user_dates()

    def parse(self, response):
        item = linksItem()

        racexpath = response.selector.xpath('/html/body/div/div/div[1]/div[2]/div/section/div/section[2]/div/a')
        for eachrow in racexpath:
            # print eachrow.extract()
            item['racelink'] = "".join(eachrow.xpath('@href').extract())
            yield item
        return
