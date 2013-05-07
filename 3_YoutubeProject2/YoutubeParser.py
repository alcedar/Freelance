'''
Created on Jan 11, 2013

@author: Anatolie P
'''
from codecs import open
from bs4 import BeautifulSoup
from time import strftime, gmtime, sleep
from urllib2 import urlopen, quote
import threading

THREADS_NUMBER  = 10
TOP_VIDEO_COUNT = 0

class VideoData:
    def __init__( self ):
        self.title    = ""
        self.descr    = ""
        self.tags     = ""
        self.views    = ""
        self.likes    = ""
        self.dislikes = ""

class PageReadingThread( threading.Thread ):
    def __init__( self, line ):
        """
        We need to separate keyword and google search results count from the line
        """
        line           = line.replace('\t', ' ')
        tokens         = line.split()
        
        self.keyword   = ' '.join( tokens[:-1] )
        self.google    = tokens[-1]
        self.number    = 0
        
        self.videosData= []
        
        threading.Thread.__init__(self)
    
    def run( self ):
        exactSearchKey  = "\"" + self.keyword + "\""
        youTubeURL      = YOUTUBE_URL + "/results?search_query=" + quote( exactSearchKey )
        self.populateData( youTubeURL )

    def populateData( self, URL ):
        youtubePageData = urlopen( URL ).read();
        soup = BeautifulSoup( youtubePageData )
        self.number     = soup.find('p', {'class':'num-results'}).contents[1].string.strip().replace(',','')
        searchResultsTag= soup.find('ol', {'id':'search-results'})
        videoTag = searchResultsTag.li

        """
        We are planning to iterate TOP_VIDEO_COUNT videos, but it might be that
        search result returned less videos
        """        
        it = 0
        while (it < min(TOP_VIDEO_COUNT, int(self.number)) and videoTag):
            """
            We need to include videos only (exclude channes, advert, etc)
            """
            if 'yt-lockup2-video' in ' '.join(videoTag["class"]):
                data = VideoData()
                data.title = videoTag["data-context-item-title"]
                try:
                    data.descr = videoTag.div.nextSibling.p.nextSibling.text.strip()
                except:    
                    """
                    There is no description for this video
                    """
                    data.descr = ' '
                self.getVideoData(videoTag["data-context-item-id"], data)
                self.videosData.append(data)
                it += 1    
            videoTag = videoTag.nextSibling.nextSibling           
        self.saveDataToFile()
    
    def getVideoData( self, contextItemID, data ):
        videoPageData = urlopen( YOUTUBE_URL + '/watch?v=' + contextItemID ).read();
        soup = BeautifulSoup( videoPageData )
        data.tags    = soup.find('meta', {'name':'keywords'})["content"].replace(',', ' ')
        try:
            data.views   = soup.find('span', {'class':'watch-view-count'}).string.strip().replace('views','').replace(',', '')
        except:
            data.views = "0"
        try:
            data.likes   = soup.find('img', {'class':'icon-watch-stats-like'}).contents[0].strip().replace(',','')
        except:
            data.likes = "0"
        try:
            data.dislikes= soup.find('img', {'class':'icon-watch-stats-like'}).img.string.strip().replace(',','')
        except:
            data.dislikes = "0"
            
    def saveDataToFile( self ):
        entry  = "[" + self.keyword + "],"
        entry += self.google + ","
        entry += self.number
        for data in self.videosData:
            if self.keyword.lower() in data.title.lower():
                entry += ",yes"
            else:
                entry += ",no"
            if self.keyword.lower() in data.descr.lower():
                entry += ",yes"
            else:
                entry += ",no"                
            if self.keyword.lower() in data.tags.lower():
                entry += ",yes"
            else:
                entry += ",no"
            entry += "," + data.views
            entry += "," + data.likes
            entry += "," + data.dislikes
        entry += "\n"
        
        outputFileWriteLock.acquire()
        outputFile.write(entry)
        outputFileWriteLock.release()
        
def prepareFileHeader( fileHandler ):
    header = "keyword,google search,youtube search count"
    i = 0
    while i < TOP_VIDEO_COUNT:
        it = str( i + 1 )
        header += ",title" + it
        header += ",descr" + it
        header += ",tags"  + it
        header += ",views" + it
        header += ",likes" + it
        header += ",dislikes" + it
        i += 1   
    header += "\n"
    fileHandler.write( header )

"""
Main entry point
"""
if __name__ == '__main__':
    """
    Constants
    """
    YOUTUBE_URL     = "https://www.youtube.com";
    INPUT_FILENAME  = "strings.txt"
    OUTPUT_FILENAME = "output_" + strftime("%H_%M_%S", gmtime()) + ".csv"
    
    inputFile  = open( INPUT_FILENAME,  "r" )
    outputFile = open( OUTPUT_FILENAME, "w" )
    prepareFileHeader( outputFile )
    
    outputFileWriteLock = threading.Lock();
    for line in inputFile:
        line = line.strip()
        if line:
            print "Processing: ", line
            while threading.active_count() >= THREADS_NUMBER:
                """
                All threads are active, lets wait for the one to finish its job
                """
                sleep(1)
            """
            Spawn a thread for each entry in input file
            """
            thread = PageReadingThread( line )
            thread.start()
    """
    All threads finished their jobs, lets join all of them here
    """
    while(threading.activeCount() > 1):
        sleep(1)
    
    """
    Save data and close file handlers
    """
    inputFile.close()
    outputFile.close()

