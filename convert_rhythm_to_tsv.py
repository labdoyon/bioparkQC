#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys , argparse
from utils import listFiles
import numpy as np
import matplotlib.pyplot as plt
import expyriment

def get_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="",
            epilog="""
            Convert Rhythm raw data to tsv file
            
            Input:  xpe
            
            Although no arguments is mandatory there is an order, if case 1 then it won't do case 2 or 3 and so on
            1. dataset Folder
            2. subject Folder
            3. single File
            """)

    parser.add_argument(
            "-s", "--singleFile",
            required=False, nargs="+",
            help="Multiple single files can be use as an input: convert_rhythm_to_tsv.py -s file1.xpe file2.xpe",
            )     
    
    parser.add_argument(
            "-d", "--dataset",
            required=False, nargs="+",
            help="dataset folder",
            )
    
    parser.add_argument(
            "-f", "--subjectFolder",
            required=False, nargs="+",
            help="Multiple subjects folders can be use as an input: convert_rhythm_to_tsv.py -d folder1 folder2",
            )
   
    parser.add_argument(
            "-o", "--outputFolder",
            required=True, nargs="+",
            help="Output Folder",
            )   

    parser.add_argument(
            "-v", "--verbose",
            required=False, nargs="+",
            help="Verbose",
            )

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    else:
        return args

class convertRhythm(object):
    """
    """
    def __init__(
            self, singleFile, dataset, subjectFolder, 
        outputFolder, verbose=False, log_level="INFO"):
        self.singleFile = singleFile
        self.dataset = dataset
        self.subjectFolder = subjectFolder
        
        if not os.path.exists(outputFolder[0]):
            os.mkdir(outputFolder[0])

        self.outputFolder = outputFolder
        self.verbose = verbose
        self.oLOG = ''
        self.iLOG = ''
        self.subject = ''
        self.freq = 0
        
    def run(self):
        allLOGFiles = []
        if self.dataset:
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, '.xpe')
        elif self.subjectFolder:
            for currFolders in self.subjectFolder:
                allLOGFiles = listFiles(currFolders, allLOGFiles, '.xpe')
        elif self.singleFile:
            allLOGFiles = self.singleFile
        
        allLOGFiles.sort(reverse=False)
        
        if not allLOGFiles:
            print 'No file were found'
        else:
            for currLOGFile in allLOGFiles:
                self.iLOG = currLOGFile
                    
                allData = self.readLOG()

                self.readHeader(allData)
                
                data = self.extractLOG(allData[0])
            
                self.freq = (data[1][1]-data[1][0])/1000
            
                self.oLOG = os.path.join(self.outputFolder[0], self.subject + '_rhythm_freq_' + str(self.freq) + '_extracted.tsv')
            
                if os.path.exists(self.oLOG):
                    print 'File: ' + self.oLOG + ' already exists'
                    continue

                self.saveTSV(data)
                
                print self.iLOG + ' has been converted successfully'
        
    def readLOG(self):
        if self.verbose:
            print 'Read log file ' + self.iLOG
        return expyriment.misc.data_preprocessing.read_datafile(self.iLOG)

    def readHeader(self, log):
        index = [i for i, s in enumerate(log[3].split('\n')) if 'Subject' in s][0] + 1
        self.subject = str(log[3].split('\n')[index]).replace('#design: #xpi: ','')

        if self.verbose:
            print 'Subject Name: ' + self.subject
    
    def extractLOG(self, log):
        logInputs = [] # Shape=(:,2) nBlock, time
        logBips = [] # Shape=(:,1) time
        logStimViz = [] # Shape=(:,1) time
        nBlock = 0
        for currLog in log:
            if 'Experiment' in currLog[1] and 'started' in currLog[2]:
                startExperimentTimer = int(currLog[0])
                
            if 'Keyboard' in currLog[1] and 'received' in currLog[2] and (int(currLog[3])==52 or int(currLog[3])==49):
                logInputs.append((nBlock,int(currLog[0])-startExperimentTimer))
            
            if 'Stimulus' in currLog[1] and 'played' in currLog[2]:
                logBips.append(int(currLog[0])-startExperimentTimer)
                if len(logBips)>1 and logBips[-1]-logBips[-2]> 2500: # 2000 hardcoded should be rest period  
                    nBlock += 1
        
            elif 'Stimulus' in currLog[1] and 'presented' in currLog[2]:
                logStimViz.append(int(currLog[0]))            

        return [np.asarray(logInputs), np.asarray(logBips), np.asarray(logStimViz), startExperimentTimer]

    def saveTSV(self, data):

        oTSV = open(self.oLOG, 'w')
        oTSV.write('NBlock\tResponseTime\tBipBefore\tBipAfter\tCode\n')
    
        code = 1
        
        freq = data[1][1]-data[1][0]

        if freq<1010:
            freq = 1000
            repeat = 140
        else:
            freq = 2000
            repeat = 70

        logBip = np.append(np.arange(data[1][0], data[1][0]+repeat*freq, freq), np.arange(data[1][len(data[1])/2], data[1][len(data[1])/2]+repeat*freq, freq))

        oldBlock = 0
        
        for currResponse in data[0]:
            
            code = 1
            val = logBip-currResponse[1]
        
            if val[val>=0].size:
                bipTimeAfter = np.min(val[val>=0])

            if val[val<=0].size:
                bipTimeBefore = np.max(val[val<=0])
            else:
                print currResponse
            
            idx = int(np.where(val == bipTimeBefore)[0])        
    
            if (logBip[idx]>data[1][len(data[1])/2-1] and logBip[idx]<data[1][len(data[1])/2]):
                code = 0
            elif logBip[idx] > data[1][-1]:
                code = 0

            oTSV.write(str(currResponse[0]) + '\t' + str(currResponse[1]) + '\t' +str(bipTimeBefore) + '\t' + str(bipTimeAfter) + '\t' + str(code) + '\n')

def main():
    """Let's go"""
    args = get_arguments()
    app = convertRhythm(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())