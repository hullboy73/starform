#! usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from decimal import Decimal
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider
from starform.items import rhsummItem
import os
import re
import unicodecsv

def read_starturls(links_path):
	resultpages = []
	if not os.path.exists(links_path): 
		open(links_path, 'w').close()
	with open(links_path, 'r') as infile:
		csvreader = unicodecsv.reader(infile, delimiter=",")
		csvlist = list(csvreader)
		for eachrow in csvlist[1:]:
			resultpage = 'http://form.horseracing.betfair.com{}'.format(eachrow[28].encode('utf-8'))
			resultpages.append(resultpage)
	return resultpages

def remove_pound(lsp):
	if lsp[0] == "-":
	 	newlsp = lsp[0:1] + lsp[2:]
	else:
	 	newlsp = lsp[1:]
	return newlsp

class rhsummarySpider(Spider):
	name = "rhsumm"

	start_urls = read_starturls('/home/benjamin/Documents/programming/github/scrapy/starform/cards.csv')
	# print start_urls

	def parse(self, response):
		item = rhsummItem()
			
		detsxpath = response.selector.xpath("/html/body/div/div[2]/div[1]/div[1]/div/div/div[2]")
		lifexpath = response.selector.xpath("/html/body/div/div[2]/div[1]/div[3]/div/div/div[2]/div/table/tr")

		try:
			item['racehorse'] = "".join(response.selector.xpath("/html/body/div/div[2]/div[1]/div[1]/div/div/div[1]/h2/text()").extract())
			item['rhid']      = response.url.replace("http://form.horseracing.betfair.com/horse?horseId=1.","")
			# print racehorse
			# print rhid
		except:
			pass
		try:
			item['age']       = "".join(detsxpath.xpath('p[@class="age"]/span[2]/text()').extract())
			item['trainer']   = "".join(detsxpath.xpath('p[@class="trainer"]/span[2]/a/text()').extract()).strip()
			item['owner']     = "".join(detsxpath.xpath('p[@class="owner"]/span[2]/text()').extract())
			# print age
			# print pedigree
			# print trainer
			# print owner
		except:
			pass
		try:
			pedigree  = "".join(detsxpath.xpath('p[@class="pedigree"]/span[2]/text()').extract())
			# print pedigree
			pedituples    = re.findall(r'([brchg\s]*)\s([gcfm])\s([a-zA-Z\(\)\s\']*)\s\|\s([a-zA-Z\(\)\s\']*)', pedigree)
			for each in pedituples:
				item['colour']    = each[0]
				item['horsetype'] = each[1]
				item['sire']      = each[2]
				item['dam']       = each[3]
				# print colour
				# print horsetype
				# print sire
				# print dam
		except:
			pass

		for eachrow in lifexpath:
			try:
				item['category'] = "".join(eachrow.xpath('td[1]/text()').extract())
				item['runs']     = "".join(eachrow.xpath('td[2]/text()').extract())
				item['first']    = "".join(eachrow.xpath('td[3]/text()').extract())
				item['second']   = "".join(eachrow.xpath('td[4]/text()').extract())
				item['third']    = "".join(eachrow.xpath('td[5]/text()').extract())
				item['fourth']   = "".join(eachrow.xpath('td[6]/text()').extract())
				item['prize']    = "".join(eachrow.xpath('td[7]/text()').extract()).replace(",","")[1:]
				item['wins']     = "".join(eachrow.xpath('td[8]/text()').extract())[:-1]
				item['profit']   = "".join(eachrow.xpath('td[9]/text()').extract())[:-1]
				item['lsp']      = remove_pound("".join(eachrow.xpath('td[10]/text()').extract()).strip())
				# print category
				# print runs
				# print first
				# print second
				# print third
				# print fourth
				# print prize
				# print wins
				# print profit
				# print lsp
			except:
				pass
			yield item
		return
