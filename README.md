# STARFORM SCRAPER

## Update:
* [Timeform](http://form.horseracing.betfair.com/) recently updated its website, thus breaking much of the code in this repository.
* Starform is getting up and running again now.
* Links and results can be crawled but cards and specific form are not yet able to be scraped.

## What does this program do?
* Starform scrapes the links to any number of previous days' racing results or future days' racecards.
* Starform scrapes the results for any number of previous days' racing.
* ~~Starform scrapes the racecards of tomorrow's racing.~~
* ~~Starform scrapes the recent 10 runs of all racehorses running tomorrow.~~
* ~~Starform scrapes the lifetime performance summaries of all racehorses running tomorrow.~~

## Notes:
* The user enters the date and number of days they wish to scrape.
* The horse racing data is scraped from [Timeform](http://form.horseracing.betfair.com/).
* Starform is the only one of my current horse racing data scraping programs that works. I really should delete the rest from this repo. 

## Requirements:
* Python ([Python](http://python.org/) is an interactive, object-oriented, extensible programming language.)
* Scrapy ([Scrapy](http://scrapy.org/) is a fast high-level screen scraping and web crawling framework.)

## Set-Up:
* Install Python
* Install Scrapy
* scrapy startproject starform
* git clone https://github.com/hullboy73/starform.git

## To run (from the command line):

```
$ cd scrapy/starform
$ scrapy crawl links -o links.csv
~~$ scrapy crawl cards -o cards.csv~~
~~$ scrapy crawl rhform -o rhform.csv~~
~~$ scrapy crawl rhsumm -o rhsumm.csv~~
$ scrapy crawl results -o results.csv
```

* Updated : 03.05.2016
* Authored: hullboy73
