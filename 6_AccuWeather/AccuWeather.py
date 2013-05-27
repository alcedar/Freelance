'''
Created on Jan 16, 2013

@author: popusoia
'''
from bs4 import BeautifulSoup
from urllib2 import quote
import re
from datetime import datetime, timedelta
from requests import Session
from ConfigParser import SafeConfigParser

ACCUWHEATHER_24HOURS_URL    = 'http://premiuma.accuweather.com/premium/past-24.asp?metric=0&&chngLocFormButton=Go&location='
ACCUWHEATHER_AUTH_URL       = 'https://wwwl.accuweather.com/authenticate.php'

INPUT_FILENAME              = 'locations.txt'
OUTPUT_FILENAME             = 'output/observed.txt'
ACCUM_FILENAME              = 'output/acc-all.txt'

def prepareFileHeader(fileHandler):
    fileHandler.write('Location,ZipCode,Report Time,Temp (F),RealFeel (F),Rel.Hum. (%),Wind Direction,Wind Spd (mph),Pressure (in),Precip (in),Vis. (Miles), Weather Cond\n')

if __name__ == '__main__':
    """
    Read configuration 
    """
    parser = SafeConfigParser()
    parser.read('conf/config.ini')
    
    username = parser.get('accu_weather', 'username')
    password = parser.get('accu_weather', 'password')
    
    """
    Initialise connection. Start session
    """
    print "Authorising user:", username, "..."
    print 'This might take a couple of seconds...'
    post_data   = {'username':username, 'password':password}
    session     = Session()
    request     = session.post(ACCUWHEATHER_AUTH_URL, data=post_data)
    if 'Your login information is incorrect' in request.text:
        print 'Your credentials are incorrect! Exiting...'
        exit()
    else:
        print "\n----\nLogin successful!\n----"
    """
    Initialising accumulator
    """
    accumulatorFile = 0
    accumulatorData = ""
    accumulatorFileExists = False
   
    try:
        accumulatorFile         = open( ACCUM_FILENAME, 'r' )
        accumulatorData         = accumulatorFile.read()
        accumulatorFileExists   = True    
    except IOError as err:
        accumulatorFile         = open( ACCUM_FILENAME, 'w' )
        prepareFileHeader( accumulatorFile )
   
    accumulatorDataList = []
    for i in accumulatorData.split('\n'):
        if i:
            accumulatorDataList.append(i.split(','))
    try:
        accumulatorDataList.pop(0)
    except:
        pass

    """
    Initialising input/output files
    """
    inputFile   = open( INPUT_FILENAME,  'r' )
    outputFile  = open( OUTPUT_FILENAME, 'w' )
   
    prepareFileHeader( outputFile )
   
    locationsWeatherList = []
    for line in inputFile:
        zipCode = re.findall(r'[ ]*[A-Z0-9 ]*$', line)[0].strip()
        inputLocation = line[:line.find(zipCode)].strip()
        print "\nProcessing: \n\tLOCATION:", inputLocation, "\n\tZIPCODE:", zipCode,

        pageData = session.get( ACCUWHEATHER_24HOURS_URL + quote( line.strip() ) ).text
        soup = BeautifulSoup( pageData )
   
        #<div class="textmedred">Past 24 Hours from Tuesday, January 15, 2013 7:00am</div>
        report_date = soup.find('div', {'class':'textmedred'}).string
        report_date = re.findall(r', [A-Za-z0-9,: ]*', report_date)[0][2:] 
        try:
            date_object = datetime.strptime(report_date, '%B %d, %Y %I:%M%p')
        except:
            print '\nThere is no weather data for this location!'
            continue

        fieldTag = soup.find('div', {'id':'pastBox0'}).div.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
        updatedDate = False
        while fieldTag:
            if fieldTag.contents:
                columnTag = fieldTag.div
                data = []
                data.append(inputLocation)
                data.append(zipCode)
                data.append(date_object.strftime('%m/%d/%Y'))
                while columnTag:       
                    if columnTag.contents:
                        column = columnTag.contents[0].strip()
                        if column[:2] == '12' and column[-2:] == 'am':
                            """
                            Increase the day
                            """
                            date_object = date_object + timedelta(days=1)
                            data[-1] = date_object.strftime('%m/%d/%Y')
                        data.append(column)
                    columnTag = columnTag.nextSibling.nextSibling
                locationsWeatherList.append(data)
            fieldTag = fieldTag.nextSibling.nextSibling
    
    print '\nProcessing the results...\n'
    locationsWeatherList = sorted(locationsWeatherList, key = lambda t: datetime.strptime(t[2] + t[3], '%m/%d/%Y%I:%M%p'))

    for i in locationsWeatherList:
        outputFile.write(','.join(i) + '\n')
   
    accumulatorDataList.extend(locationsWeatherList)
    
    accumulatorDataList = sorted(accumulatorDataList, key = lambda t: datetime.strptime(t[2] + t[3], '%m/%d/%Y%I:%M%p'))

    if accumulatorFileExists:
        accumulatorFile = open(ACCUM_FILENAME, 'w')
        prepareFileHeader(accumulatorFile)
    
    """
    Before adding the records to accumulator, we need to remove the duplicates
    """
    for i, x in enumerate(accumulatorDataList):
        if i > 0 and accumulatorDataList[i - 1] == accumulatorDataList[i]:
            accumulatorDataList.pop(i - 1)
    
    for i in accumulatorDataList:
        accumulatorFile.write(','.join(i) + '\n')
    
    inputFile.close()
    outputFile.close()
    accumulatorFile.close()
