import scrapy
import requests
import json
import simplejson
import re
import sys
from bs4 import BeautifulSoup


from djtest.items import DjtestItem
from djtest.items import DjtestTracklist

class DmozSpider(scrapy.Spider):
    name = "1001tracklists"
    allowed_domains = ["www.1001tracklists.com/tracklist/"]
    #Url to scrap
    # start_urls = [
        
    # ]

    def __init__(self, *args, **kwargs): 
      super(DmozSpider, self).__init__(*args, **kwargs) 

      self.start_urls = [kwargs.get('start_url')] 

    def parse(self, response):
        # for sel in response.xpath("//*[contains(@class, 'redTxt')]"):
        #     # if sel.xpath('text()').extract() == "u'ID - ID\u2009'":
        #     #     print "ID HERE"
        #     var = sel.xpath('text()').extract()
        #     var = var[0].strip()
        #     if (var == "ID - ID") | (var[-5:] == " - ID") | (var == "ID") | (var == "(ID Remix)"):
        #         print "UNIDENTIFIED TRACK HERE"
        #         with open('tracklist.json', 'a') as f:
        #             f.write("ERROR: UNIDENTIFIED TRACKS PRESENT")
        #         sys.exit()
        # print "SUCCESS"

        
        for sel in response.xpath(".//div[@class='redTxt floatL tlFont']"):
            # if sel.xpath('text()').extract() == "u'ID - ID\u2009'":
            #     print "ID HERE"
            var = sel.xpath('text()').extract()
            if var[0].strip() == "ID - ID":
                print "ID HERE"
                with open('tracklist.json', 'a') as f:
                    f.write("ERROR: ID TRACKS PRESENT")
                sys.exit()
        i = 0
        tracklist = DjtestTracklist()
        tracklist['tracklistGenres'] = []
        tracklist['tracklistName'] = response.xpath('.//*[@itemtype="http://schema.org/MusicPlaylist"]/*[@itemprop="name"]/@content').extract()
        #tracklist['tracklistArtist'] = response.xpath('.//*[@itemtype="http://schema.org/MusicPlaylist"]/*[@itemprop="author"]/@content').extract()
        tracklist['tracklistArtist'] = []
        tracklist['tracklistDate'] = response.xpath('.//*[@itemtype="http://schema.org/MusicPlaylist"]/*[@itemprop="datePublished"]/@content').extract()
        tracklist['tracklistNumTracks'] = response.xpath('.//*[@itemtype="http://schema.org/MusicPlaylist"]/*[@itemprop="numTracks"]/@content').extract()
        # tracklist['tracklistLinks']
        #Iterates over the artists
        for sel in response.xpath("//table[@class='default sideTop']"):
            tracklistArtist = {}
            tracklistArtist['artistLinks'] = []
            if len(sel.xpath(".//tr/td/a/text()").extract()) > 0 and len(sel.xpath('.//tr/th/a/text()').extract()) > 0:
                #Extracts the artist name for the links
                tracklistArtist['artistName'] = ', '.join(sel.xpath('.//tr/th/a/text()').extract())
                #print tracklistArtist['artistName']
                #Iterates over the links avoiding the Google search ones
                for sel2 in sel.xpath(".//tr/td/a"):
                    if not "Google" in str(sel2.xpath('text()').extract()):
                        #Extracts the artist links
                        tracklistArtist['artistLinks'].append(', '.join(sel2.xpath('@href').extract()))
                        #print tracklistArtist['artistLinks']
                tracklist['tracklistArtist'].append(tracklistArtist)
        print tracklist['tracklistArtist']
        # tracklist['tracklistLinks'] = response.xpath("//td[@class='left']/a/@href").extract()
        for sel in response.xpath('.//*[@itemtype="http://schema.org/MusicPlaylist"]/*[@itemprop="genre"]'):
            tracklist['tracklistGenres'].append(', '.join(sel.xpath('@content').extract()))
            # i+=1
        for sel in response.xpath('//*[@itemtype="http://schema.org/MusicRecording"]/div[contains(@id, "media_buttons")]'):
            tracklist['tracklistLinks'] = sel.xpath("//a[@class='floatL iconHeight32']/@href").extract()

        yield tracklist
        i=0
        for sel in response.xpath('//tr[contains(@id, "tlp_")]'):
        # for sel in response.xpath('.//*[@itemtype="http://schema.org/MusicRecording"]'):
            #check item info, call web service, 
            #http://www.1001tracklists.com/ajax/get_medialink.php?idObject=5&idItem=256063&idMediaType=4&viewSource=1&viewItem=827
            #store the response (whatever we can use)
            i=0
            item = DjtestItem()
            item['songLinks'] = []
            params = {}
            item['songNumber'] = ', '.join(sel.xpath('.//span[contains(@id, "tracknumber_value")]/text()').extract())
            item['artistName'] = ', '.join(sel.xpath('.//*[@itemprop="byArtist"]/@content').extract())
            item['songName'] = ', '.join(sel.xpath('.//*[@itemprop="name"]/@content').extract())
            item['songPublisher'] = ', '.join(sel.xpath('.//*[@itemprop="publisher"]/@content').extract())
            item['songIndex'] = i
            i+=1
            if len(item['songName']) > 0:
                #Loop for saving links // needs to be tested, seems like it works
                for sel in sel.xpath('.//td[contains(@id, "tlptr")]/*[@itemtype="http://schema.org/MusicRecording"]/div[contains(@id, "media_buttons")]/div[contains(@class, "s32")]'):
                    params = str(sel.xpath('.//@onclick').extract())
                    params = params[params.find("{")-1:params.find("}")+1]
                    params = re.sub(r'([a-z]\w+)', r'"\1"', params)
                    dataform = str(params).strip("'<>() ").replace('\'', '\"')
                    #print dataform
                    j = simplejson.loads(dataform)
                    try:
                        j["idMediaType"] 
                    except KeyError:
                        j["idMediaType"] = 1
                    r = requests.get("http://www.1001tracklists.com/ajax/get_medialink.php?idObject="+str(j["idObject"])+"&idItem="+str(j["idItem"])+"&idMediaType="+str(j["idMediaType"])+"&viewSource="+str(j["viewSource"])+"&viewItem="+str(j["viewItem"]))
                    rJson = r.json()
                    rJsonPlayer = rJson["data"][0]["player"]
                    soup = BeautifulSoup(rJsonPlayer, 'html.parser')
                    # rJsonPlayerParsed = rJsonPlayer.replace("\\", "")
                    item['songLinks'].append(soup.iframe['src'])
                    # print j
                    # r = requests.get("http://api.soundcloud.com/tracks/220209001?client_id=ybtyKcnlhP3RKXpJ58fg&format=json")
                    print soup.iframe['src']
                    #item['songLinks'].append(sel.xpath('.//@onclick').extract())
                    #i+=1
                yield item
