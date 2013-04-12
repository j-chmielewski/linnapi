#!/usr/bin/env python

import os
import os.path
import struct
import sys
import shutil
import urllib
import urllib2
import zipfile
import dircache
import re

def hashFile(name): 
    try: 
                 
        longlongformat = 'q'  # long long 
        bytesize = struct.calcsize(longlongformat) 
                    
        f = open(name, "rb") 
                    
        filesize = os.path.getsize(name) 
        hash = filesize 
                    
        if filesize < 65536 * 2: 
            return "SizeError" 
                 
        for x in range(65536 / bytesize): 
            buffer = f.read(bytesize) 
            (l_value,) = struct.unpack(longlongformat, buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
        f.seek(max(0, filesize - 65536), 0) 
        for x in range(65536 / bytesize): 
            buffer = f.read(bytesize) 
            (l_value,) = struct.unpack(longlongformat, buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
        f.close() 
        returnedhash = "%016x" % hash 
        return returnedhash    
    
    except(IOError): 
        return "IOError"


class linnapi:
    
    searchUrl = 'http://www.opensubtitles.org/pl/search2/sublanguageid-pol/moviehash-'
    downloadUrl = 'http://www.opensubtitles.org/pl/subtitleserve/sub/'
    
    movieIdRegex = '/pl/subtitleserve/sub/(\d+)'
    
    tmpFile = '/tmp/linnapi.tmp'
    tmpDir = '/tmp/linnapi/'
    
    subsExtensions = ['txt', 'srt', 'sub']
    movieExtensions = ('avi', 'mpg', 'mpeg', 'mp4', 'mkv', 'rmvb', 'ogm')
    
    def fetchSubs(self, path):
        
        tokens = os.path.abspath(path).split('/')

        filename = tokens[-1]
        directory = '/'.join(tokens[0:-1]) + '/'
        hashCode = hashFile(path)

        print 'Movie file: ' + filename
        
        reply = urllib2.urlopen(self.__buildUrl(hashCode)).read()
        movieId = re.findall(self.movieIdRegex, reply)
        
        if len(movieId) == 0:
            print '### Movie not found'
            raise Exception('Movie not found')
        movieId = movieId[0]
        
        urllib.urlretrieve(self.downloadUrl + movieId, self.tmpFile)
        zFile = zipfile.ZipFile(self.tmpFile, 'r')
        zFile.extractall(self.tmpDir)
        files = dircache.listdir(self.tmpDir)

        subsFile = ''
        for zFile in files:
            extension = zFile.split('.')[-1]
            if extension in self.subsExtensions:
                subsFile = zFile
                break
        
        shutil.copy(self.tmpDir + subsFile, directory + '.'.join(filename.split('.')[:-1]) + \
                                            '.' + subsFile.split('.')[-1])
        shutil.rmtree(self.tmpDir)
        os.remove(self.tmpFile)
        

    def findMovies(self, startPoint):
            
        if os.path.isfile(startPoint):
            return [startPoint]
        
        directories = [startPoint]
        mFiles = []
        while len(directories)>0:
            directory = directories.pop()
            for name in os.listdir(directory):
                fullpath = os.path.join(directory,name)
                if os.path.isfile(fullpath):
                    if fullpath.endswith(self.movieExtensions):
                        mFiles.append(fullpath)

                elif os.path.isdir(fullpath):
                    directories.append(fullpath)  
    
        return mFiles
    
    def __buildUrl(self, hashCode):
        return self.searchUrl + hashCode
        

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print 'Usage:\n' + sys.argv[0] + ' [dir|file]'
        exit(1)

    ln = linnapi();
    searchPath = sys.argv[1]
    
    mFiles = ln.findMovies(searchPath)
    counter = 1
    successCounter = 0
    for mFile in mFiles:
        print '\n[Downloading file %s/%s]' % (counter, len(mFiles))
        try:
            ln.fetchSubs(mFile)
        except:
            print "FAILED"
        else:
            print "OK"
            successCounter += 1

        counter += 1

    if len(mFiles) > 1:
        print "\nFinished downloading, " + str(successCounter) + "/" + str(len(mFiles)) + " subs found"




