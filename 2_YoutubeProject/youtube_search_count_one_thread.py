'''
Created on 06 Jan 2012

@author: Anatolie P.

'''
import urllib2, re
from time import gmtime, strftime


"""
Main
"""
'''
This has been done in order to avoid data overwritting
'''
outputFileName = "output_" + strftime("%H_%M_%S", gmtime()) + ".txt"

inputFile = open("strings.txt", "r")
outputFile = open(outputFileName, "w")
startTag = "<strong>"
endTag = "</strong>"

for line in inputFile:
    print "\nProcessing: ", line,
    search_url = "https://www.youtube.com/results?search_query=" + urllib2.quote(line) 
    pageData = urllib2.urlopen(search_url).read();
    #<p class="num-results">About <strong>144,000</strong> results </p>
    match = re.findall(r'<p class=\"num-results\".*</p>?', pageData, re.DOTALL)[0]
    start = match.index(startTag) + len(startTag)
    end = match.index(endTag)
    outputFile.write(line.rstrip() + " - " + match[start:end] + "\r\n")
    print "  Found:", match[start:end]
inputFile.close()
outputFile.close()
