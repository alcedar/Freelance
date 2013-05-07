from bs4 import BeautifulSoup
from os import path, makedirs
from urllib2 import urlopen
from codecs import encode, decode
import re
from time import strftime, gmtime

MYLANGUAGES_URL = 'http://mylanguages.org/'
OUTPUT_DIR      = 'output\\'

"""
These are the sections we are not interested in, as there is nothing to scrap there
"""
FILTER = ['English', 'Homepage', 'Translation', 'Transliteration', 'Videos', 'Dictionary',
          'Keyboard', 'Quiz', 'Radio', 'Audio', 'Video', 'Grammar', 'Reading', 'AlphabetA',
          'Script', 'Cases', 'Verb Forms', 'Grammar', 'Romanization', 'Audio Lessons', 'Prefixes']

if not path.exists( 'logs' ):
    makedirs( 'logs' )
logFile = open('logs\\log' + strftime("%H_%M_%S", gmtime()) + '.txt', 'w')

def Log( entry ):
    print entry
    logFile.write(strftime("%H_%M_%S", gmtime()) + " : " + entry + '\n')

class Language:
    def __init__( self ):
        self.name = ""
        self.data = dict()

def IsFiltered( key ):
    return not key in FILTER
  
def PopulateLanguagePages( language, url ):
    pageData = urlopen( MYLANGUAGES_URL + url).read();
    soup = BeautifulSoup( pageData )
    paragraph = soup.find('table', {'summary':re.compile('Learn ')}).tbody.tr
    while paragraph:
        simpleTheme = paragraph.td
        while simpleTheme:
            key = simpleTheme.a
            if key:
                if key.string in language.data:
                    """
                    In order to preserve keys in dictionary
                    """
                    key.string += 'A'
                if IsFiltered( key.string ):
                    language.data[key.string] = simpleTheme.a["href"]
            simpleTheme = simpleTheme.findNextSibling('td')
      
        paragraph = paragraph.findNextSibling('tr')

def GetLanguages():
    pageData = urlopen( MYLANGUAGES_URL + 'index.php').read();
    soup = BeautifulSoup( pageData )
    languagesList= []  
    languagesTag = soup.find('table', {'summary':'Learn Languages'}).tbody.tr
    #Temporary
    #i = 0
    while languagesTag:
        lTag = languagesTag.td
        while lTag:
            language = Language()
            if IsFiltered( lTag.a.string ):
                language.name = lTag.a.string
                Log("Collecting URLs for language: " + language.name)
                PopulateLanguagePages( language, lTag.a["href"] )
                languagesList.append( language )
            #i += 1
            #if i == 5:
            #    return languagesList

            lTag = lTag.nextSibling.nextSibling
        if languagesTag.nextSibling:
            languagesTag = languagesTag.nextSibling.nextSibling
        else:
            break
    return languagesList

def GetTablesFromURL( url ):
    pageData = urlopen( MYLANGUAGES_URL + url).read();
    soup = BeautifulSoup( pageData )
    tables = soup.findAll('table', {'summary':re.compile('[A-Za-z ]*')})
    strings = []
    for table in tables:
        row = table.tbody.tr
        while row:
            try:
                row.content
            except:
                row = row.nextSibling
                continue
            s = ""
            for i, t in enumerate(row.contents):
                if t.contents:
                    """
                    Some pages contain new line characters
                    """
                    tmp = t.text.replace('|', '\t')
                    tmp = tmp.replace('\n','')
                    tmp = tmp.replace('\r','')
                    """
                    Sometimes, ' - ' is used as a delimiter in case,
                    when there are lots of '-' in translation
                    """
                    if ' - ' in tmp:
                        tmp = tmp.replace(' - ', '\t')
                    else:
                        tmp = tmp.replace('-', '\t')
                    s += tmp + '\t'
            if s:
                if ' or ' in str(row.contents[-1]):
                    Log("The string: '" + encode(row.contents[0].text, 'utf-8') + "' for URL:" + url + 
                        ", was skipped due to ambiguity in processing. Please process it manually")
                else:
                    strings.append(s[:-1])
            row = row.nextSibling
    return strings

def GetMultimediaFromURL( url ):
    pageData = urlopen( MYLANGUAGES_URL + url).read();
    soup = BeautifulSoup( pageData )
    tables = soup.find('table', {'class':'ver-zebra', 'summary':re.compile('[A-Za-z ]*')})
    tr = tables.contents[1].tr
    strings = []
    while tr:
        tag = tr.td
        while tag and len(tag.text.strip()) > 0:
            original = tag.next.strip()
            translit = ''
            translat = ''
            """
            Separator is one of: -, |, <b></b>.
            Process each case separately
            """
            pos = tag.text.find('|')
            if pos != -1:
                translit = tag.text[len(original):pos].strip()
                translat = tag.text[pos:].replace('|','').strip()
                strings.append(original + '\t' + translat + '\t' + translit)
                tag = tag.findNextSibling('td')
                continue
            pos = tag.text.find('-')
            if pos != -1:
                translit = tag.text[len(original):pos].strip()
                translat = tag.text[pos:].replace('-','').strip()
                strings.append(original + '\t' + translat + '\t' + translit)
                tag = tag.findNextSibling('td')
                continue
            
            if '<b>' in str(tag) and '</b>' in str(tag):
                try:
                    translit = tag.next.next.next.next.next
                    translat = translit.next.next.text
                except:
                    try:
                        translit = tag.next.next.next
                        translat = translit.next.next.text
                    except:
                        Log("The string: " + original + ", for URL:" + url + 
                            ", was skipped due to ambiguity in processing. Please process it manually")
                        tag = tag.findNextSibling('td')
                        continue
                strings.append(original + '\t' + translat + '\t' + translit)
                tag = tag.findNextSibling('td')
                continue
            
            """
            At this point consider that this text does not contain transliteration
            """
            strings.append(original + '\t' + tag.text[len(original):])
            tag = tag.findNextSibling('td')
        tr = tr.findNextSibling('tr')
   
    nextURL = soup.find('a', {'href':re.compile(str(url[url.index('/', 1) + 1:url.index('.php')]) + '[1-9]')})
    if nextURL and nextURL != url:
        """
        There is another page which should be processed.
        Process it recursively
        """
        Log('There is a next URL. Process recursively. Next URL: ' + nextURL["href"])
        strings.extend(GetMultimediaFromURL('multimedia/' + nextURL["href"]))
    return strings

if __name__ == '__main__':
    
    #print(GetTablesFromURL('belarusian_alphabet.php'))
    #print(GetMultimediaFromURL('multimedia/urdu_audio_objects.php'))
    #exit()
    
    if not path.exists( OUTPUT_DIR ):
        makedirs( OUTPUT_DIR )

    languagesList = GetLanguages()
    #languagesList = []
    #language = Language()
    #PopulateLanguagePages( language, 'learn_urdu.php' )
    #languagesList.append(language)
    
    Log("Creating directory infrastructure, processing data.")
    Log("This might take several minutes. Please wait...")
    for i in languagesList:
        Log("Processing language: " + i.name)
        languageDir = OUTPUT_DIR + i.name
        if not path.exists(languageDir):
            makedirs(languageDir)
        for key in i.data:
            Log("    Downloading data for:  " + key)
            keyDir = languageDir + "\\" + key
            if not path.exists( keyDir ):
                makedirs( keyDir )
                
            wordsList = []
            try:
                if 'multimedia' in i.data[key]:
                    wordsList = GetMultimediaFromURL(i.data[key])
                else:
                    wordsList = GetTablesFromURL( i.data[key] )
                """
                Save data to different files
                """
                consolidatedFile = open(keyDir + "\\" + key + '.consolidated.snt', 'w')
                consolidatedFile.write(encode('\n'.join(wordsList), 'utf-8'))
                consolidatedFile.close()
                originalFile = open(keyDir + '\\' + key + '.original.snt', 'w')
                translatFile = open(keyDir + '\\' + key + '.translat.snt', 'w')
                
                translitWords = []
                transliterationExits = False
                for line in wordsList:
                    words = line.strip().split('\t')
                    originalFile.write(encode(words[0], 'utf-8') + '\n')
                    pos1 = -1
                    for it, word in enumerate(words[1:]):
                        if word.strip():
                            pos1 = it
                            break
                    if pos1 != -1:
                        translatFile.write(encode(words[1 + pos1], 'utf-8') + '\n')
                    else:
                        translatFile.write('\n')
                    tmp = ""
                    for it, word in enumerate(words[2 + pos1:]):
                        if word.strip():
                            tmp += word + ' '
                            transliterationExits = True
                    if tmp:
                        translitWords.append(encode(tmp.strip(), 'utf-8'))
                    else:
                        translitWords.append(' ')
                originalFile.close()
                translatFile.close()
                if transliterationExits:
                    translitFile = open(keyDir + '\\' + key + '.translit.snt', 'w')
                    translitFile.write('\n'.join(translitWords))
                    translitFile.close()
            except Exception as ex:
                print "EXCEPTION:=", ex

    logFile.close()  
   
   







