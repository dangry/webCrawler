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
        # print tracklist['tracklistArtist']
        # tracklist['tracklistLinks'] = response.xpath("//td[@class='left']/a/@href").extract()
        for sel in response.xpath('.//*[@itemtype="http://schema.org/MusicPlaylist"]/*[@itemprop="genre"]'):
            tracklist['tracklistGenres'].append(', '.join(sel.xpath('@content').extract()))
            # i+=1
        # for sel in response.xpath('//*[@itemtype="http://schema.org/MusicRecording"]/div[contains(@id, "media_buttons")]'):
        tracklist['tracklistLinks'] = sel.xpath("//a[@class='floatL iconHeight32']/@href").extract()

        yield tracklist
        i=0
        for sel in response.xpath('//tr[contains(@id, "tlp_")]'):
        # for sel in response.xpath('.//*[@itemtype="http://schema.org/MusicRecording"]'):
            #check item info, call web service, 
            #http://www.1001tracklists.com/ajax/get_medialink.php?idObject=5&idItem=256063&idMediaType=4&viewSource=1&viewItem=827
            #store the response (whatever we can use)
            item = DjtestItem()
            item['songLinks'] = []
            params = {}
            var1 = sel.xpath('.//div[contains(@id, "tr")]//div//div//div//div//text()').extract()
            try:
                # print var1[0]
                var2 = var1[0].split(" - ")
            except IndexError:
                break  
            #Changes 
            print "START CHANGES"   
            testString = sel.xpath(".//div[contains(@class,'trackFormat')]/span[1]/text() | .//div[contains(@class,'trackFormat')]/span/following-sibling::text()[1]").extract()
            print testString
            testString = map(unicode.strip, testString)
            testString = ' '.join(testString)
            #print testString
            testString = testString.replace(" (  )", "")
            testString = testString.replace(" ( )", "")
            testString = testString.replace(u"\u00A0", " ")
            print testString.strip()
            print "END CHANGES"
            #Changes    
            item['songNumber'] = ', '.join(sel.xpath('.//span[contains(@id, "tracknumber_value")]/text()').extract())
            # item['artistName'] =  ''.join(var2[0]).encode('utf-8')
            item['artistName'] =  testString.strip()
            try:
                item['songName'] = var2[1]
            except IndexError:
                item['songName'] = ', '.join(sel.xpath('.//*[@itemprop="name"]/@content').extract())    
            item['songPublisher'] = ', '.join(sel.xpath('.//*[@itemprop="publisher"]/@content').extract())
            item['songIndex'] = i
            i+=1
            if len(item['songName']) > 0:
                #Loop for saving links // needs to be tested, seems like it works
                for sel in sel.xpath(".//div[contains(@class, 's32')]"):
                    try:
                        params = str(sel.xpath('.//@onclick').extract())
                        params = params[params.find("{")-1:params.find("}")+1]
                        params = re.sub(r'([a-z]\w+)', r'"\1"', params)
                        dataform = str(params).strip("'<>() ").replace('\'', '\"')
                        #print dataform
                        j = simplejson.loads(dataform)
                        print j
                        try:
                            j["idMediaType"] 
                        except KeyError:
                            j["idMediaType"] = 1
                        r = requests.get("http://www.1001tracklists.com/ajax/get_medialink.php?idObject="+str(j["idObject"])+"&idItem="+str(j["idItem"])+"&idSource="+str(j["idSource"])+"&viewSource="+str(j["viewSource"])+"&viewItem="+str(j["viewItem"]))
                        rJson = r.json()
                        rJsonPlayer = rJson["data"][0]["player"]
                        soup = BeautifulSoup(rJsonPlayer, 'html.parser')
                        item['songLinks'].append(soup.iframe['src'])
                        if "embed.beatport.com" in soup.iframe['src']:
                            print "FOUND BEATPORT HERE"
                            r2 = requests.get(soup.iframe['src'])
                            soup2 = BeautifulSoup(r2.text, 'html.parser')
                            # print(soup2.prettify())
                            beatportUrl = soup2.find(id="input-share-link").get('value')
                            r3 = requests.get(beatportUrl)
                            soup3 = BeautifulSoup(r3.text, 'html.parser')
                            soup4 = soup3.find("li", class_='interior-track-content-item interior-track-bpm')
                            soup5 = soup3.find("li", class_='interior-track-content-item interior-track-key')
                            bpmVar = soup4.find("span", class_='value').text
                            keyVar = soup5.find("span", class_='value').text.encode('utf-8')
                            print "BPM IS: " + bpmVar
                            print "KEY IS: " + keyVar
                            item['songBpm'] = bpmVar
                            item['songKey'] = keyVar
                    except:
                        pass
                yield item
