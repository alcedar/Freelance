from bs4 import BeautifulSoup
import urllib2
import base64
from os import path, makedirs
from ConfigParser import SafeConfigParser

URL     = "http://www.brisnet.com/cgi-bin/trk_report.cgi?ccf"
PATH    = "c:\comchart\out\\"

def downloadFile(trackname, url, username, password):
    filename = url.split('/')[-1].split('?')[0]
    if not path.exists(PATH + trackname + "\\" + filename):
        if not path.exists( PATH + trackname ):
            makedirs( PATH + trackname )
        print "  ---> Downloading: %s" % (filename)
        filename = PATH + trackname + "\\" + filename
        request = urllib2.Request(url)
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

def processSection(tr, username, password):
    tdList = tr.findAll("td")
    trackName = tdList[0].string
    print "Cheking '%s' for new tracks:" % (trackName)
    files = tdList[1].findAll("a")
    for file in files:
        downloadFile(trackName.strip(), file["href"], username, password)
    
if __name__ == '__main__':
    """
    Read configuration 
    """
    parser = SafeConfigParser()
    parser.read('conf/config.ini')
    
    username = parser.get('brisnet', 'username')
    password = parser.get('brisnet', 'password')
    
    soup= BeautifulSoup(urllib2.urlopen( URL ).read());
    tag = soup.find('table', {'class':'report'}).next
    while tag:
        if tag and str(tag).strip() and tag.td.string != "Track":
            processSection(tag, username, password)
        tag = tag.nextSibling
