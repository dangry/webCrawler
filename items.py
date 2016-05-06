# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DjcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    songNumber = scrapy.Field()
    songName = scrapy.Field()
    artistName = scrapy.Field()
    songPublisher = scrapy.Field()
    songLinks = scrapy.Field()
    songIndex = scrapy.Field()
    songKey = scrapy.Field()
    songBpm = scrapy.Field()
    pass

class DjcrawlerTracklist(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tracklistName = scrapy.Field()
    tracklistGenres = scrapy.Field()
    tracklistArtist = scrapy.Field()
    tracklistDate = scrapy.Field()
    tracklistNumTracks = scrapy.Field()
    tracklistLinks = scrapy.Field()
    pass
