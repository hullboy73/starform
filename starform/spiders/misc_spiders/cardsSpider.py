#! usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from decimal import Decimal
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider
from starform.items import cardsItem
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
	elif goingwords[1] == "course:":
		going = goingwords[2]
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

def amend_wintime(wintime):
    data = re.findall(r'([\d+]+).', wintime)
    if len(data) < 2:
        return
    elif len(data) == 2:
        wintime = data[0] + '.' + data[1]
    elif len(data) == 3:
        wintime = str((int(data[0]))*60 + (int(data[1]))) + '.' + data[2]
    elif len(data) > 3:
        return
    else:
        return
    return wintime

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

def get_raceclass(racetitle):
    title = racetitle.split(" ")
    # remove '(D.I)' and '(D.II)' from racetitle
    if title[-1][-1] == 'I':
        racetitle = racetitle.pop()
    # regex checking of racetitle list to extract Class
    classmatch = re.search(r"\((\w)\)$", racetitle)
    if classmatch:
        raceclass = "Class " + classmatch.group(1)
    else:
        raceclass = "Class n/a"
    return raceclass

def get_racetype(racetitle, racecode):
	title = racetitle.split(" ")
	if racecode == "NH":
		nh_list = set(["Handicap", "Novices'", "Beginners'", "Juvenile", "Hunters'", "Maiden", "Mares'", "Chase", "Hurdle", "Conditional", "Amateur"])
		racetypes = []
		for each in title:
			if each in nh_list:
				racetypes.append(each)
			elif each == 'Flat':
				racetypes.append("NH Flat")
			else:
				pass
		racetype = " ".join(racetypes)
		gradematch = re.search(r'\(Grade\s\d\)', racetitle)
		if gradematch:
			racetype = racetype + " " + gradematch.group()
	else:
		flat_list = set(["Fillies'", "Selling", "Claiming", "Conditions", "Maiden", "Nursery", "Handicap", "Stakes", "Apprentice", "Amateur"])
		racetypes = []
		for each in title:
			if each in flat_list:
				racetypes.append(each)
		racetype = " ".join(racetypes)
		groupmatch = re.search(r'\(Group\s\d\)', racetitle)
		listedmatch = re.search(r'\(Listed\)', racetitle)
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
			resultpage = 'http://form.horseracing.betfair.com{}'.format(eachrow[5])
			resultpages.append(resultpage)
	return resultpages

def remove_entities(sometext):
	newtext = re.sub('[\(\)\,\-\/]','',sometext)
	return newtext

class cardsSpider(Spider):
	name = "cards"
	start_urls = read_starturls('/home/benjamin/Documents/programming/github/scrapy/starform/links.csv')

	def parse(self, response):
		item = cardsItem()
		
		racexpath     = response.selector.xpath('/html/body/div/div[2]/div[1]/div[2]/div/div[@class="vevent"]')
		commentsxpath = response.selector.xpath('/html/body/div/div[2]/div[1]/div[3]/div/div/div[2]/div')
		forecastxpath = response.selector.xpath('/html/body/div/div[2]/div[1]/div[5]/div/div/div[3]/span[2]/text()')
		runnersxpath  = response.selector.xpath('/html/body/div/div[2]/div[1]/div[5]/div/div/div[2]/div[2]/ul/li')
		# crsinfoxpath  = response.selector.xpath('/html/body/div/div[2]/div[1]/div[4]/div/div/div[2]/div/div[2]/div/div/div/div[1]/text()')
		# topjockxpath  = response.selector.xpath('/html/body/div/div[2]/div[1]/div[4]/div/div/div[2]/div/div[@class="top-jockeys-module course-details-submodule"]/div/div/div/table/tbody/tr')
		# toptrnrxpath  = response.selector.xpath('/html/body/div/div[2]/div[1]/div[4]/div/div/div[2]/div/div[@class="top-trainers-module course-details-submodule"]/div/div/table/tbody/tr')
		
		try:
			racelink = response.url.replace("http://form.horseracing.betfair.com","")
			item['cardlink']   = racelink
			reracelink		   = racelink.replace('.','')
			match2             = re.search(r'[0-9]+', reracelink)
			item['cardid']     = match2.group()
			# print cardlink
			# print cardid
		except:
			pass
		try:
			racecourse = " ".join(racexpath.xpath('div/h2/span/span/abbr[@class="geo"]/span[1]/text()').extract())
			item['racecourse'] = racecourse
			item['racedate']   = "".join(racexpath.xpath('div/div/div/h2/abbr[@class="dtstart"]/@title').extract()).split(" ")[0]
			item['racetime']   = "".join(racexpath.xpath('div/div/div/h2/abbr[@class="dtstart"]/@title').extract()).split(" ")[1]
			racedets = "".join(racexpath.xpath('div/p[@class="clearer race-info"]/span/text()').extract()).split("|")
			if racedets[0][0] == "G":
				going = racedets[0].strip()[7:].lower()
				if going[0] == "a":
					going = going[13:]
				item['going'] = amend_going(going)
				distance = racedets[1].strip()[10:]
				item['distance'] = distance
				item['furlongs'] = calculate_furlongs(distance)
				item['agerange'] = racedets[2].strip()[5:]
				item['prize'] = racedets[3].strip()[20:]
				item['runners'] = racedets[4].strip()[9:]
				racecode = racedets[5].strip()[11:]
			elif racedets[0][0] == "D":
				item['going'] = "n/a"
				distance = racedets[0].strip()[10:]
				item['distance'] = distance
				item['furlongs'] = calculate_furlongs(distance)
				item['agerange'] = racedets[1].strip()[5:]
				item['prize'] = racedets[2].strip()[20:]
				item['runners'] = racedets[3].strip()[9:]
				racecode = racedets[4].strip()[11:]
			else:
				pass
			aw_set = set(["Lingfield Park", "Wolverhampton", "Southwell", "Kempton Park", "Dundalk", "Chelmsford City", "Great Leighs"])
			if (racecode == "Flat") and (racecourse in aw_set): 
			 	racecode = "AW"
			elif racecode == "Flat":
				racecode = "Flat"
			else:
				racecode = "NH"
			item['racecode'] = racecode
			racetitle = "".join(racexpath.xpath('div/p[@class="race-description"]/text()').extract()).strip()
			item['racetype'] = get_racetype(racetitle, racecode)
			item['raceclass'] = get_raceclass(racetitle)
			# print racetime2
			# print racecourse
			# print racedate
			# print racetime
			# print racedets
			# print going
			# print distance
			# print furlongs
			# print agerange
			# print prize
			# print runners
			# print racecode
			# print racetype
			# print raceclass
		except:
			pass

		try:
			tfpred1st = "".join(commentsxpath.xpath('div[@class="racecard"]/table/tbody/tr[1]/td[3]/a/text()').extract())
			tfpred2nd = "".join(commentsxpath.xpath('div[@class="racecard"]/table/tbody/tr[2]/td[3]/a/text()').extract())
			tfpred3rd = "".join(commentsxpath.xpath('div[@class="racecard"]/table/tbody/tr[3]/td[3]/a/text()').extract())
			item['tfpredcomment'] = "".join(commentsxpath.xpath('div[@class="comment"]/p[2]/text()').extract())
			# print tfpred1st
			# print tfpred2nd
			# print tfpred3rd
			# print tfpredcomment
		except:
			pass
		try:
			fcastdict = {}	
			forecast = "".join(forecastxpath.extract()).split(", ")
			for each in forecast:
				match = re.search(r'([\d\.]+)\s([\w\s.]+)', each)
				rhprice = match.group(1)
				rhname = match.group(2).strip()
				fcastdict[rhname] = rhprice
			# print fcastdict
		except:
			pass

		### DOESN'T WORK
		# crsinfoxpath = response.selector.xpath(crsinfopath)
		# item['crsinfo'] = "".join(crsinfoxpath.extract())
		# print crsinfo

		### WORKS but probably not the right place for it
		# topjockdicts = []
		# for eachrow in response.selector.xpath(topjockpath):
		# 	newdict = {}
		# 	newdict['topj_name'] = "".join(eachrow.xpath('td[1]/a/text()').extract())
		# 	newdict['topj_runs'] = "".join(eachrow.xpath('td[2]/text()').extract())
		# 	newdict['topj_wins'] = "".join(eachrow.xpath('td[3]/text()').extract())
		# 	newdict['topj_2nds'] = "".join(eachrow.xpath('td[4]/text()').extract())
		# 	newdict['topj_3rds'] = "".join(eachrow.xpath('td[5]/text()').extract())
		# 	newdict['topj_prize'] = "".join(eachrow.xpath('td[6]/text()').extract())
		# 	newdict['topj_winperc'] = "".join(eachrow.xpath('td[7]/text()').extract())
		# 	newdict['topj_profit'] = "".join(eachrow.xpath('td[8]/text()').extract())
		# 	newdict['topj_lsp'] = "".join(eachrow.xpath('td[9]/text()').extract())			
		# 	topjockdicts.append(newdict)
		# item['topjockdicts'] = topjockdicts			

		### DOESN'T WORK
		# toptrnrdicts = []
		# for eachrow in response.selector.xpath(toptrnrpath):
		# 	newdict = {}
		# 	newdict['topt_name'] = "".join(eachrow.xpath('td[1]/a/text()').extract())
		# 	newdict['topt_runs'] = "".join(eachrow.xpath('td[2]/text()').extract())
		# 	newdict['topt_wins'] = "".join(eachrow.xpath('td[3]/text()').extract())
		# 	newdict['topt_2nds'] = "".join(eachrow.xpath('td[4]/text()').extract())
		# 	newdict['topt_3rds'] = "".join(eachrow.xpath('td[5]/text()').extract())
		# 	newdict['topt_prize'] = "".join(eachrow.xpath('td[6]/text()').extract())
		# 	newdict['topt_winperc'] = "".join(eachrow.xpath('td[7]/text()').extract())
		# 	newdict['topt_profit'] = "".join(eachrow.xpath('td[8]/text()').extract())
		# 	newdict['topt_lsp'] = "".join(eachrow.xpath('td[9]/text()').extract())
		# 	toptrnrdicts.append(newdict)
		# item['toptrnrdicts'] = toptrnrdicts				

		for eachrow in runnersxpath:
			try:
				item['mktlink'] = "".join(eachrow.xpath('div[1]/ul/li[1]/a/@href').extract()).replace("//sports.betfair.com/horseracing","")
				item['racecardno'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="number"]/text()').extract()).split())
				item['draw'] = remove_entities("".join("".join(eachrow.xpath('div[1]/ul/li[@class="draw"]/text()').extract()).split()))
				racehorse = "".join(eachrow.xpath('div[1]/ul/li[@class="horse"]/span/a/text()').extract())
				item['racehorse'] = racehorse
				if racehorse == tfpred1st:
					item['tfprediction'] = 1
				elif racehorse == tfpred2nd:
					item['tfprediction'] = 2
				elif racehorse == tfpred3rd:
					item['tfprediction'] = 3
				else:
					item['tfprediction'] = '-'
				rhlink = "".join(eachrow.xpath('div[1]/ul/li[@class="horse"]/span/a/@href').extract())
				item['rhlink'] = rhlink
				item['rhid'] = rhlink.replace("/horse?horseId=1.00",'')
				# print mktlink
				# print racecardno
				# print draw
				# print racehorse
				# print tfprediction
				# print rhlink
				# print rhid
			except:
				pass
			try:
				item['dslr'] = "".join(eachrow.xpath('div[1]/ul/li[@class="horse"]/span/sup/text()').extract())
				item['formline'] = "".join(eachrow.xpath('div[1]/ul/li[@class="horse"]/span/span/text()').extract())
				item['crswins'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="horse"]/span/span/span/text()').extract()).split())
				# print dslr
				# print formline
				# print crswins
			except:
				pass
			try:
				fcprice = fcastdict[racehorse]
				item['fcprice'] = fcprice
			except:
				pass
			try:
				item['age'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="age"]/text()').extract()).split())
				item['weight'] = amend_weight("".join(eachrow.xpath('div[1]/ul/li[@class="wgt-or"]/span/span[1]/text()').extract()))
				item['o_r'] = remove_entities("".join(eachrow.xpath('div[1]/ul/li[@class="wgt-or"]/span/span[2]/text()').extract()))
				item['eq'] = "".join(eachrow.xpath('div[1]/ul/li[@class="eq enabled"]/span[2]/text()').extract())
				# print age
				# print weight
				# print o_r
				# print eq
			except:
				pass
			try:	
				item['jockey']  = "".join(eachrow.xpath('div[1]/ul/li[@class="jockey-trainer noeq"]/span/a[1]/text()').extract())
				item['jklink']  = "".join(eachrow.xpath('div[1]/ul/li[@class="jockey-trainer noeq"]/span/a[1]/@href').extract())
				item['allwnce'] = remove_entities("".join(eachrow.xpath('div[1]/ul/li[@class="jockey-trainer noeq"]/span[2]/text()').extract()).strip())
				item['trainer'] = "".join(eachrow.xpath('div[1]/ul/li[@class="jockey-trainer noeq"]/span/a[2]/text()').extract())
				item['trlink']  = "".join(eachrow.xpath('div[1]/ul/li[@class="jockey-trainer noeq"]/span[2]/a[2]/@href').extract())
				# print jockey
				# print jklink
				# print allwnce
				# print trainer
				# print trlink
			except:
				pass
			try:
				item['backprice'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="back"]/button/span[1]/text()').extract()).split())
				item['backsize'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="back"]/button/span[2]/text()').extract()).split())[1:]
				item['layprice'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="lay"]/button/span[1]/text()').extract()).split())
				item['laysize'] = "".join("".join(eachrow.xpath('div[1]/ul/li[@class="lay"]/button/span[2]/text()').extract()).split())[1:]
				# print backprice
				# print backsize
				# print layprice
				# print laysize
			except:
				pass
			try:
				item['rhcomment'] = "".join(eachrow.xpath('div/div[@class="comments"]/text()').extract())
				# print rhcomment
			except:
				pass

			yield item
		return
