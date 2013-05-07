'''
Created on 31 Dec 2012

@author: Anatolie P.

'''
import os, urllib2, HTMLParser, time
import xml.etree.ElementTree as ET

class TableParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.in_tr = False
        self.in_td = False
        self.data_present = False
        self.currentRow = ""
        self.rows = []
   
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            for name, value in attrs:
                """
                Unfortunately, the only one anchor we can use is the color,
                as there are not ids in this table
                """
                if name == "bgcolor" and (value == "#eeeeee" or value == "#f5f5f5"):
                    self.in_tr = True
        if self.in_tr == True and tag == "td":
            self.in_td = True
           
   
    def handle_data(self, data):
        if self.in_tr and self.in_td:
            self.data_present = True
            self.currentRow += data
            self.currentRow += ","
   
    def handle_endtag(self, tag):
        if self.in_tr and self.in_td and not self.data_present:
            self.currentRow += "NA,"
        if tag == "td":
            self.in_td = False
            self.data_present = False
        if tag == "tr":
            self.in_tr = False
            if self.currentRow != "":
                self.currentRow = self.currentRow[:-1]
                self.rows.append(self.currentRow)
                self.currentRow = ""

def getWeatherByStation(weatherStation):
    p = TableParser()
    """
    Returns the weather station info.
    """
    try:
        pageData = urllib2.urlopen('http://w1.weather.gov/obhistory/' + weatherStation + '.html').read()
       
        """
        There is an error on web page which has to be fixed before parsing,
        as HTMLParser throws an exception on it
        """
        if pageData.find("\" </span>") != -1:
            pageData = pageData.replace("\" </span>", "\"> </span>")
   
        p.feed(pageData)
    except HTMLParser.HTMLParseError as EX:
        print ('ERROR: Failed to parse HTML page. Page contains errors')
        print (EX)
    except Exception as inst:
        print ('ERROR: Failed to load data for weather station', weatherStation)   
        print (inst)
    return p.rows

def printToFile(outputFile, rows, delim = ''):

    for i in rows:
        l = delim + i
        outputFile.write(l)
        delim = '\n'

"""
Main
"""
outputDirectory = 'out'
configDirectory = 'conf'
header = '''Date,Time,Wind(mph),Vis,Weather,Sky Cond.,Temperature(Air),Temperature(Dwpt),Temperature(6h Max),Temperature(6h Min),Humidity,Wind Chill, HeatIndex,Pressure altimeter(in),Pressure sea level(mb),Precipitation(1h),Precipitation(3h),Precipitation(6h)'''

tree = ET.parse(configDirectory + '/config.xml')
root = tree.getroot()

if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

for states in root:
    print("-----------------\nPROCESSING DATA FOR STATE:" + states.attrib.get('value'))
    for station in states:
        print(" - ANALYSING DATA FOR LOCATION:" + station.text)
        stationCode = station.attrib.get('value')
        filePath = outputDirectory + "/" + stationCode + ".txt"
        outputFile = open(filePath, 'a')
        rows = getWeatherByStation(stationCode)
        rows.reverse()
        if os.path.getsize(filePath) == 0:
            """
            File is empty, just append the header and rows, no merging is required
            """
            outputFile.write(header + '\n')
            printToFile(outputFile, rows)
        else:
            """
            Get the last line of the file, which is the latest entry,
            and compare first 8 characters of it with each record from 'rows'
            """
            position = 0

            f = open(filePath, 'r')
            lastEntry = f.readlines()[-1];
            
            for i, value in enumerate(rows):
                if lastEntry == value:
                    position = i
                    break
            
            if position < len(rows) - 1:
                """
                We found some new rows, so append them to the file end
                """               
                print("Found new weather records:\n" + '\n'.join(rows[position + 1:]))
                printToFile(outputFile, rows[position + 1:], '\n')
            f.close()
        outputFile.close()
