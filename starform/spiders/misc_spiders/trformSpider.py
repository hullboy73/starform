#! usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from decimal import Decimal
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider
from starform.items import trformItem
import os
import re
import unicodecsv

def amend_date(somedate):
	splitdates = somedate.split(" ")
	day = splitdates[0]
	mon = splitdates[1]
	months = {"Jan": '01', "Feb": '02', "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
	if len(day) == 1:
		day = "0" + day[0] 	
	mon = months[mon]
	yr = "20" + splitdates[2]
	strdate = yr + "-" + mon + "-" + day
	return strdate

def calculate_furlongs(distance):
	miles = re.search(r'([0-9]]*)m', distance)
	furlongs = re.search(r'([0-9]*)f', distance)
	# yards = re.search(r'\s([0-9]*)yds', distance)
	if miles:
		miles = int(miles.group(1)) * 8
	else:
		miles = 0.00
	if furlongs:
		furlongs = int(furlongs.group(1))
	else:
		furlongs = 0.00
	# if yards:
	# 	yards = round((float(yards.group(1)) / 220), 2)
	# else:
	# 	yards = 0.00
	newdist = miles + furlongs #+ yards
	return newdist

def read_starturls(links_path):
	resultpages = []
	if not os.path.exists(links_path): 
		open(links_path, 'w').close()
	with open(links_path, 'r') as infile:
		csvreader = unicodecsv.reader(infile, delimiter=",")
		csvlist = list(csvreader)
		for eachrow in csvlist[1:]:
			resultpage = 'http://form.horseracing.betfair.com{}'.format(eachrow[5].encode('utf-8'))
			resultpages.append(resultpage)
	return resultpages

class trformSpider(Spider):
	name = "trform"
	start_urls = read_starturls('/home/benjamin/Documents/programming/github/scrapy/starform/cards.csv')
	# print start_urls

	def parse(self, response):
		item = trformItem()

		formxpath = response.selector.xpath("/html/body/div/div[2]/div[1]/div[3]/div/div[2]/table/tbody/tr")

		try:
			item['trainer'] = "".join(response.selector.xpath("/html/body/div/div[2]/div[1]/div[1]/div/div/div[1]/h2/text()").extract())
			item['trid']      = response.url.replace("http://form.horseracing.betfair.com/trainer?trainerId=1.","")
			# print trainer
			# print trid
		except:
			pass
		for eachrow in formxpath:			
			try:
				racedate           = "".join(eachrow.xpath('td[1]/a/text()').extract()).strip()
				item['racedate']   = amend_date(racedate)
				racelink           = "".join(eachrow.xpath('td[1]/a/@href').extract()).strip()
				item['racelink']   = racelink
				reracelink		   = racelink.replace('.','')            
				match2             = re.search(r'[0-9]+', reracelink)
				item['raceid']     = match2.group()
				item['racecourse'] = "".join(eachrow.xpath('td[2]/a/text()').extract()).strip()
				item['position']   = "".join(eachrow.xpath('td[3]/text()').extract()).strip().split("/")[0]
				item['ran']        = "".join(eachrow.xpath('td[3]/text()').extract()).strip().split("/")[1]
				distance		   = "".join(eachrow.xpath('td[4]/text()').extract())
				item['distance']   = distance
				item['furlongs']   = calculate_furlongs(distance) 
				item['going']      = "".join(eachrow.xpath('td[5]/text()').extract())
				item['o_r']        = "".join(eachrow.xpath('td[6]/text()').extract())
				item['eq']         = "".join(eachrow.xpath('td[7]/text()').extract())
				item['racetype']   = "".join(eachrow.xpath('td[8]/text()').extract())
				item['racehorse']  = "".join(eachrow.xpath('td[9]/p[1]/a/text()').extract()).strip()
				item['rhid']	   = "".join(eachrow.xpath('td[9]/p[1]/a/@href').extract()).replace("/horse?horseId=1.","")
				item['jockey']     = "".join(eachrow.xpath('td[9]/p[2]/a/text()').extract()).strip()
				item['jkid']       = "".join(eachrow.xpath('td[9]/p[2]/a/@href').extract()).replace("/jockey?jockeyId=1.","")
				item['hi_ir']      = "".join(eachrow.xpath('td[10]/text()').extract()).strip().split(" / ")[0]
				item['lo_ir']      = "".join(eachrow.xpath('td[10]/text()').extract()).strip().split(" / ")[1]
				item['isp']        = "".join(eachrow.xpath('td[11]/text()').extract()).strip().split(" / ")[1]
				item['bsp']        = "".join(eachrow.xpath('td[11]/text()').extract()).strip().split(" / ")[0]
				item['place']      = "".join(eachrow.xpath('td[12]/text()').extract()).strip()
				# print racedate
				# print racelink
				# print racecourse
				# print position
				# print ran
				# print distance
				# print furlongs
				# print going
				# print o_r
				# print eq
				# print racetype
				# print racehorse
				# print rhid
				# print jockey
				# print jkid
				# print hi_ir
				# print lo_ir
				# print isp
				# print bsp
				# print place
				# newpage    = response.selector.xpath("/html/body/div/div[2]/div[1]/div[4]/div/div[2]/div/a[@class='number']/@href").extract()
				# print newpage
			except:
				pass
			yield item
		return
