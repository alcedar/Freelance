import urllib2, re
import time
import threading
from bs4 import BeautifulSoup

"""
Please change these constants as per your requirements
"""
THREADS_NUMBER  = 10;
TOP_VIDEO_COUNT = 5

class YoutubeData:
    def __init__(self):
        self.title = ""
        self.descr = ""
        self.tags  = ""
        self.views = "" 
        self.likes = ""
        self.dislikes = ""

class ReadingThread (threading.Thread):
    def __init__(self, fileHandler, keyword):
        self.fileHandler = fileHandler
        self.keyword = keyword
        threading.Thread.__init__(self)
    def run(self):
        self.keyword = self.keyword.replace('\t',' ')
        inputs = self.keyword.split()
        self.keyword = ' '.join(inputs[:-1])
        key = "\"" + self.keyword + "\""
        
        outFileWriteLock.acquire()
        print "\nProcessing: ", self.keyword,
        outFileWriteLock.release()
        
        search_url = youtubeURL + "/results?search_query=" + urllib2.quote(key) 
        pageData = urllib2.urlopen(search_url).read();
        """
        Get number of results
        """
        # <p class="num-results">About <strong>144,000</strong> results </p>
        matchNumber = re.findall(r'<p class=\"num-results\".*</p>?', pageData, re.DOTALL)[0]
        start = matchNumber.index(startTag) + len(startTag)
        end = matchNumber.index(endTag)
        number = matchNumber[start:end]
        
        """
        Get title, tags, description, views, likes and dislikes
        """
        matchVideos = re.findall(r'<ol id=\"search-results\".*</ol>?', pageData, re.DOTALL)[0]
        
        soup = BeautifulSoup(matchVideos)
        videosTags = soup.find_all('li', {'data-context-item-type':'video'})
        videosCount = len(videosTags)
        if(videosCount > TOP_VIDEO_COUNT):
            videosCount = TOP_VIDEO_COUNT
        
        videos = []
        for videoTag in videosTags[:videosCount]:
            data = YoutubeData()
            data.title = videoTag["data-context-item-title"].replace(',', ' ').lower();
            videoURL   = youtubeURL + "/watch?v=" + videoTag['data-context-item-id'] 
            videoSoup  = BeautifulSoup(urllib2.urlopen(videoURL).read()) 
            try:
                data.descr = videoSoup.find_all('meta', {'name':'description'})[0]["content"].replace(',', ' ').lower()
            except:
                data.descr = ' '
            try:
                data.tags  = videoSoup.find_all('meta', {'name':'keywords'})[0]["content"].replace(',', ' ').lower()
            except:
                data.tags  = ' '
            try:
                data.views = videoSoup.find_all('div',  {'id':'watch7-views-info'})[0].span.string.replace(',','').replace('views','').strip()
            except:
                data.views = '0'
            try:
                data.likes = videoSoup.find('img', {'class':'icon-watch-stats-like'}).contents[0].strip().replace(',','')
            except:
                data.likes = '0'
            try:
                data.dislikes= videoSoup.find('img', {'class':'icon-watch-stats-like'}).img.string.strip().replace(',','')     
            except:
                data.dislikes='0'
            videos.append(data)
        
        outFileWriteLock.acquire()       
        outputFile.write("[" + self.keyword + "]" + "," + inputs[-1] + "," + number.replace(',', ''))
        for video in videos:
            if video.title.find(self.keyword.lower()) != -1:
                outputFile.write(",yes")
            else:
                outputFile.write(",no")
            if video.descr.find(self.keyword.lower()) != -1:
                outputFile.write(",yes")
            else:
                outputFile.write(",no")            
            if video.tags.find(self.keyword.lower()) != -1:
                outputFile.write(",yes")
            else:
                outputFile.write(",no")
            outputFile.write("," + video.views)
            outputFile.write("," + video.likes)
            outputFile.write("," + video.dislikes)
        outputFile.write("\n")
        outFileWriteLock.release()

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
Main
"""
'''
This has been done in order to avoid data overwritting
'''
youtubeURL = "https://www.youtube.com";
outputFileName = "output_" + time.strftime("%H_%M_%S", time.gmtime()) + ".csv"

inputFile = open("strings.txt", "r")
outputFile = open(outputFileName, "w")
prepareFileHeader( outputFile )
startTag = "<strong>"
endTag = "</strong>"

outFileWriteLock = threading.Lock();

for line in inputFile:
    if line.rstrip() != "":
        while threading.activeCount() >= THREADS_NUMBER:
            time.sleep(1)
        thread = ReadingThread(outputFile, line.rstrip())
        thread.start()
            
while(threading.activeCount() > 1):
    time.sleep(2)

inputFile.close()
outputFile.close()
