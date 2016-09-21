#! usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from decimal import Decimal
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider
from starform.items import resultsItem
import os
import re
import unicodecsv

def amend_distbtn(distbtn):
	distreps = {'\xc2' : '', '\xbd' : '.5', '\xbc' : '.25', '\xbe' : '.75', 'dh' : '', 'dht' : '',  'ns' : '.05', 'nse' : '.05', 's.h' : '.1', 'sh' : '.1', 'hd' : '.2', 'snk' : '.25', 'nk' : '.3', 'ds' : '30', 'dist' : '30'}
	distbtn = distbtn.encode('utf-8', 'ignore')
	for i, j in distreps.iteritems():
		distbtn = distbtn.replace(i, j)
	return distbtn

def amend_going(going):
	goingwords = going.split(" ")
	if len(goingwords) == 1:
		going = goingwords[0]
	elif len(goingwords) == 3:
		going = " ".join(goingwords[0:3])
	elif goingwords[1][0] == "(":
		going = goingwords[0]
	elif goingwords[3][0] == "(":
		going = " ".join(goingwords[0:3])
	# elif goingwords[1] == "course:":
	# 	going = goingwords[2]
	else:
		going = "n/a"
	return going

def amend_weight(sometext):
	weight = "".join(sometext).split("-")
	stones = int(weight[0]) * 14
	if len(weight) > 1:
		pounds = int(weight[1])
		weight = stones + pounds
	else:
		pounds = 0
		weight = stones + pounds
	weight = str(weight)
	return weight

def calculate_furlongs(distance):
    miles = re.search(r'([0-9]*)m', distance)
    furlongs = re.search(r'([0-9]*)f', distance)
    yards = re.search(r'\s([0-9]*)y', distance)
    if miles:
        miles = int(miles.group(1)) * 8
    else:
        miles = 0.00
    if furlongs:
        furlongs = int(furlongs.group(1))
    else:
        furlongs = 0.00
    if yards:
        yards = round((float(yards.group(1)) / 220), 3)
    else:
        yards = 0.00
    newdist = miles + furlongs + yards
    return newdist

def calculate_wintime(wintime):
    minutes = re.search(r'([0-9]*)m', wintime)
    seconds = re.search(r'([0-9\.]*)s', wintime)
    if minutes:
        minutes = float(minutes.group(1)) * 60
    else:
        minutes = 0.00
    if seconds:
        seconds = float(seconds.group(1))
    else:
        seconds = 0.00
    newtime = minutes + seconds
    return newtime  

def get_raceclass(racetitle):
    title = racetitle.split(" ")
    # # remove '(D.I)' and '(D.II)' from racetitle
    # if title[-1][-1] == 'I':
    #     racetitle = racetitle.pop()
    # # regex checking of racetitle list to extract Class
    classmatch = re.search(r"\((\w)\)", racetitle)
    if classmatch:
        raceclass = classmatch.group(1)
    else:
        raceclass = "n/a"
    return raceclass

def get_racetype(racetitle, racecode):
	title = racetitle.split(" ")
	if (racecode == "Chase") or (racecode == "Hurdle") or (racecode == "Bumper"):
		nh_list = set(["handicap", "novices'", "beginners'", "juvenile", "hunters'", "maiden", "mares'", "chase", "hurdle", "conditional", "amateur"])
		racetypes = []
		for each in title:
			if each in nh_list:
				racetypes.append(each)
			elif each == 'flat':
				racetypes.append("nh flat")
			else:
				pass
		racetype = " ".join(racetypes)
		gradematch = re.search(r'\(grade\s\d\)', racetitle)
		if gradematch:
			racetype = racetype + " " + gradematch.group()
	else:
		flat_list = set(["fillies'", "selling", "claiming", "conditions", "maiden", "nursery", "handicap", "atakes", "apprentice", "amateur"])
		racetypes = []
		for each in title:
			if each in flat_list:
				racetypes.append(each)
		racetype = " ".join(racetypes)
		groupmatch = re.search(r'\(group\s\d\)', racetitle)
		listedmatch = re.search(r'\(listed\)', racetitle)
		if groupmatch:
			racetype = racetype + " " + groupmatch.group()
		if listedmatch:
			racetype = racetype + " " + listedmatch.group()			
	return racetype

def read_starturls(links_path):
	resultpages = []
	if not os.path.exists(links_path): 
		open(links_path, 'w').close()
	with open(links_path, 'r') as infile:
		csvreader = unicodecsv.reader(infile, delimiter=",")
		csvlist = list(csvreader)
		for eachrow in csvlist[1:]:
			resultpage = 'https://www.timeform.com{}'.format(eachrow[0])
			resultpages.append(resultpage)
	return resultpages

def remove_entities(sometext):
	newtext = re.sub('[\(\)\,\-\/]','',sometext)
	return newtext

class resultsSpider(Spider):
	name = "results"
	start_urls = read_starturls('/home/benjamin/Documents/programming/github/scrapy/starform/links2016.csv')
	# print start_urls

	def parse(self, response):
		item = resultsItem()

		racexpath     = response.selector.xpath('/html/body/div/div/div/div[1]/div[2]/section[2]/table')
		resultxpath   = response.selector.xpath('/html/body/div/div/div/div[3]/table/tbody[@class="rp-table-row"]')	

		for eachrow in racexpath:
			item['racelink'] = response.url.replace('https://www.timeform.com/horse-racing/result/','')
			spliturl = response.url.split("/")
			racecourse = spliturl[5]
			item['racedate'] = spliturl[6]
			item['racetime'] = spliturl[7]
			item['rcid'] = spliturl[8]
			item['racenumber'] = spliturl[9]
			# print racecourse
			# print racedate
			# print racetime
			# print racecourseid
			# print racenumber
			date_and_time = "".join(eachrow.xpath('tr[1]/td/h2/text()').extract())											
			racetitle 	  = "".join(eachrow.xpath('tr[2]/td[1]/h3/text()').extract()).lower()
			distance 	  = "".join(eachrow.xpath('tr[2]/td[2]/span[@title="Distance expressed in miles, furlongs and yards"]/text()').extract())
			prize 		  = "".join(eachrow.xpath('tr[3]/td[1]/span[@title="Prize money to winner"]/text()').extract())
			agerange      = "".join(eachrow.xpath('tr[3]/td[1]/span[@title="Horse age range"]/text()').extract())
			racecode 	  = "".join(eachrow.xpath('tr[3]/td[1]/span/span[@title="The type of race"]/text()').extract())
			# surface 	  = "".join(eachrow.xpath('tr[3]/td[1]/span[@title="Surface of the race"]/text()').extract())	
			going    	  = "".join(eachrow.xpath('tr[3]/td[2]/span[@title="Race going"]/text()').extract())
			wintime 	  = " ".join("".join(response.selector.xpath('/html/body/div/div/div/div[5]/div/section/table/tr[2]/td/p/text()').extract()).split())
			# print date_and_time
			# print racetitle
			# print distance
			# print prize
			# print agerange
			# print surface
			item['prize']    = prize
			item['agerange'] = agerange
			item['going']    = amend_going(going)
			item['furlongs'] = calculate_furlongs(distance)
			item['distance'] = distance
			item['wintime']  = calculate_wintime(wintime)
			# print going
			# print furlongs
			# print wintime
			aw_set = set(["lingfield-park", "wolverhampton", "southwell", "kempton-park", "dundalk", "chelmsford-city", "great-leighs"])
			if (racecode == "Flat") and (racecourse in aw_set): 
			 	racecode = "AW"
			item['racecode'] = racecode 	
			item['racetype'] = get_racetype(racetitle, racecode)
			item['raceclass'] = get_raceclass(racetitle)
			item['racetitle'] = racetitle
			item['racecourse'] = racecourse
			# print racecode
			# print racetype
			# print raceclass

			totdistbtn = 0.00

			for eachrow in resultxpath:
				position = "".join(eachrow.xpath('tr[1]/td[1]/span[@title="Finishing Position"]/text()').extract())
				item['draw'] = "".join(eachrow.xpath('tr[1]/td[1]/span[2]/text()').extract()).replace('(','').replace(')','')
				distbtn  = "".join(eachrow.xpath('tr[1]/td[@title="The number of lengths behind the horse that finished in front of it"]/text()').extract())
				item['racehorse'] = "".join(eachrow.xpath('tr[1]/td[3]/a[@title="Horse"]/text()').extract()).lower().replace('/horse-racing/horse-form/','').split("/")[0].replace('-',' ')
				item['jockey'] = "".join(eachrow.xpath('tr[1]/td[9]/a[@title="Jockey"]/@href').extract()).replace('/horse-racing/jockey-form/','').split("/")[0]
				item['allowance'] = "".join(eachrow.xpath('tr[1]/td[9]/span[@title="Jockey allowance"]/text()').extract())
				item['age'] = "".join(eachrow.xpath('tr[1]/td[10]/text()').extract())
				item['weight'] = "".join(eachrow.xpath('tr[1]/td[11]/text()').extract())
				item['isp'] = "".join(eachrow.xpath('tr[1]/td[13]/span[2]/text()').extract())
				item['bsp'] = "".join(eachrow.xpath('tr[1]/td[14]/text()').extract())
				item['hi_ir'] = "".join(eachrow.xpath('tr[1]/td[15]/text()').extract()).split("/")[0]
				item['lo_ir'] = "".join(eachrow.xpath('tr[1]/td[15]/text()').extract()).split("/")[1]
				item['trainer'] = "".join(eachrow.xpath('tr[2]/td[2]/a[@title="Trainer"]/@href').extract()).replace('/horse-racing/trainer-form/','').split("/")[0]
				item['eq'] = "".join(eachrow.xpath('tr[2]/td[3]/span/text()').extract()).replace('(','').replace(')','')
				item['o_r'] = "".join(eachrow.xpath('tr[2]/td[4]/text()').extract()).replace('(','').replace(')','')
				item['place'] = " ".join("".join(eachrow.xpath('tr[2]/td[6]/text()').extract()).split()).replace('(','').replace(')','')
				item['rhid'] = "".join(eachrow.xpath('tr[2]/td[2]/a[@title="Horse"]/@href').extract()).replace('/horse-racing/horse-form/','').split("/")[0]
				item['jkid'] = "".join(eachrow.xpath('tr[2]/td[2]/a[@title="Jockey"]/@href').extract()).replace('/horse-racing/jockey-form/','').split("/")[0]
				item['trid'] = "".join(eachrow.xpath('tr[2]/td[2]/a[@title="Trainer"]/@href').extract()).replace('/horse-racing/trainer-form/','').split("/")[1]
				# print draw				
				# print racehorse
				# print rhlink
				# print jockey
				# print jklink
				# print allowance
				# print age
				# print weight
				# print isp
				# print bsp
				# print hi_ir
				# print lo_ir
				# print trainer
				# print trlink
				# print eqpmnt
				# print o_r
				# print place
				# print rhid
				# print jkid
				# print trid				
			 	distbtn = amend_distbtn(distbtn)
			 	try:
					if distbtn == "":
						if position.isdigit():
							if position == '1':
								distbtn = 0.00
								totdistbtn = 0.00
							else:
								totdistbtn = totdistbtn
						else:
							distbtn = 'NaN'
							totdistbtn = 'NaN'
					else:
						totdistbtn += round(float(distbtn), 2)
					if totdistbtn != 'NaN':
						totdistbtn = float("{0:.2f}".format(totdistbtn))
					item['position'] = position	
					item['distbtn'] = distbtn	
					item['totdistbtn'] = totdistbtn
					# print position
					# print distbtn
					# print totdistbtn
				except ValueError, e:
					print "error",e
					break
				yield item
		return
