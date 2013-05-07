from __future__ import division
import os
import codecs

OUTPUT = 'output'

def get_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]

def get_files(directory):
    return [name for name in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, name)) and '.consolidated' not in name]

def process_directory( path, generic ):
    files  = get_files( path )
    if files:
        expected_number     = 0
        translit_ascii_rate = 0
        for filename in files:
            """
            1. For each f verify number of lines
            """
            lines_number = 0
            count_ascii  = 0
            with codecs.open( path + '//' + filename, 'r', 'utf-8' ) as f:
                if 'translat' in filename:
                    for lines_number, line in enumerate(f):
                        pass
                elif 'translit' in filename:
                    for lines_number, line in enumerate(f):
                        """
                        2. Check trans-literation
                        """
                        count_ascii += len(line.encode("ascii", "ignore"))
                    size = os.path.getsize(path + '//' + filename)
                    if size:
                        translit_ascii_rate = count_ascii / size
                else:
                    for lines_number, line in enumerate(f):
                        """
                        2. Check translation and trans-literation
                        """

            if expected_number == 0:
                expected_number = lines_number
            if expected_number != lines_number:
                print('EXCEPTION. NUMBER OF LINES DIFFER FOR: ', path, 
                      '\n Number for ', f, ' = ', lines_number )
        
        if translit_ascii_rate > 0 and translit_ascii_rate < 0.5:
            print "EXCEPTION. ASCII rate for translit file is low:", translit_ascii_rate, '%. Swap translit and translate file'
            print path + '\\' + generic 
            os.rename(path + '\\' + generic + '.translat.snt', path + '\\' + generic + '.tmp')
            os.rename(path + '\\' + generic + '.translit.snt', path + '\\' + generic + '.translat.snt')
            os.rename(path + '\\' + generic + '.tmp',          path + '\\' + generic + '.translit.snt')

if __name__ == '__main__':
    languagesList = get_subdirectories( OUTPUT )
    for language in languagesList:
        print('Processing: ', language)
        generics = get_subdirectories( OUTPUT + '\\' + language )
        for generic in generics:
            print('   Analysing: ', generic)
            path = OUTPUT + '\\' + language + '\\' + generic;
            process_directory( path, generic )

