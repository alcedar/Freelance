'''
Created on 06 Jan 2012

@author: Anatolie P.

'''
import urllib2, re
import time
import threading

class ReadingThread (threading.Thread):
    def __init__(self, fileHandler, keyword):
        self.fileHandler = fileHandler
        self.keyword = keyword
        threading.Thread.__init__(self)
    def run(self):
        key = "\"" + self.keyword + "\""
        search_url = "https://www.youtube.com/results?search_query=" + urllib2.quote(key) 
        pageData = urllib2.urlopen(search_url).read();
        # <p class="num-results">About <strong>144,000</strong> results </p>
        match = re.findall(r'<p class=\"num-results\".*</p>?', pageData, re.DOTALL)[0]
        start = match.index(startTag) + len(startTag)
        end = match.index(endTag)
        number = match[start:end]
        outFileWriteLock.acquire()
        outputFile.write("[" + self.keyword + "]" + "," + number.replace(',', '') + "\n")
        outFileWriteLock.release()

"""
Main
"""
'''
This has been done in order to avoid data overwritting
'''
outputFileName = "output_" + time.strftime("%H_%M_%S", time.gmtime()) + ".csv"

inputFile = open("strings.txt", "r")
outputFile = open(outputFileName, "w")
startTag = "<strong>"
endTag = "</strong>"

threadsNumber = 10;
outFileWriteLock = threading.Lock();

for line in inputFile:
    if line.rstrip() != "":
        print "\nProcessing: ", line,
        while threading.activeCount() >= threadsNumber:
            time.sleep(1)
        thread = ReadingThread(outputFile, line.rstrip())
        thread.start()
            
while(threading.activeCount() > 1):
    time.sleep(2)

inputFile.close()
outputFile.close()
