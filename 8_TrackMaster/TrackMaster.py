from bs4 import BeautifulSoup
import urllib2
import base64
from os import path, makedirs
from ConfigParser import SafeConfigParser
import re

URL     = "http://www.trackmaster.com/cgi-bin/old_prodlist.cgi?hpp"
SITE    = "http://www.trackmaster.com"
PATH    = "c:\\pdox40\\pps\\"

def getURL(url, username, password):
    request = urllib2.Request(SITE + url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)  
    soup = BeautifulSoup(urllib2.urlopen(request).read())
    tag = soup.find('a', {'href':re.compile('/nm/hpp_link/download')})
    return tag["href"]

def downloadFile(fileDescription, fileURL, username, password):
    filename = fileURL.split('/')[-1].split('?')[0]
    url = getURL(fileURL, username, password)
    if not path.exists(PATH + filename):
        if not path.exists( PATH ):
            makedirs( PATH )
        print "Downloading: ", fileDescription, " - %s" % (filename)
        filename = PATH + filename
        
        request = urllib2.Request(SITE + url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)   
        u = urllib2.urlopen(request)
        f = open(filename, 'wb')
        block_sz = 8192
        while True:
            buff = u.read(block_sz)
            if not buff:
                break
            f.write(buff)    
        f.close()
    
if __name__ == '__main__':
    """
    Read configuration 
    """
    parser = SafeConfigParser()
    parser.read('conf/config.ini')
    
    username = parser.get('trackmaster', 'username')
    password = parser.get('trackmaster', 'password')
    
    soup    = BeautifulSoup(urllib2.urlopen( URL ).read());
    tags    = soup.findAll('a')
    print "Checking for the latest files, this could take a couple of minutes..."
    for tag in tags:
        if tag.string and "TrackMaster PP for Harness" in tag.string:
            downloadFile(tag.string, tag["href"], username, password)
