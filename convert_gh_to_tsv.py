#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys , argparse
from utils import listFiles, oldVersionArrow
import numpy as np
import matplotlib.pyplot as plt

def get_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="",
            epilog="""
            Convert Guitar Hero raw data to tsv file
            
            Input: .txt
            
            Although no arguments is mandatory there is an order, if case 1 then it won't do case 2 or 3 and so on
            1. dataset Folder
            2. subject Folder
            3. single File
            """)

    parser.add_argument(
            "-s", "--singleFile",
            required=False, nargs="+",
            help="single GuitarHero file",
            )     
    
    parser.add_argument(
            "-d", "--dataset",
            required=False, nargs="+",
            help="dataset folder",
            )
    
    parser.add_argument(
            "-f", "--subjectFolder",
            required=False, nargs="+",
            help="subject folder",
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

class convertGH(object):
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
        self.perfectData = []
        self.oLOG = ''
        self.iLOG = ''
        self.subject = ''
        
        # LOG Perfect Data to compare with "normal" subjects
        for currTask in ['BioPark_perfect_VIT1.txt', 'BioPark_perfect_VIT2.txt']:
            iLOG = self.readLOG(currTask)
            self.perfectData.append(self.extractPerfectData(iLOG))
        
    def run(self):
        allLOGFiles = []
        if self.dataset:
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, 'VI')
        elif self.subjectFolder:
            for currFolders in self.subjectFolder:
                allLOGFiles = listFiles(currFolders, allLOGFiles, 'VI')
        elif self.singleFile:
            allLOGFiles = self.singleFile

        # All LOG Files
        allLOGFiles.sort(reverse=False)

        for idx, currLogFile in enumerate(allLOGFiles):
            self.iLOG = currLogFile
            self.subject = os.path.split(self.iLOG)[1].split('_VI')[0]
			
            print self.subject
            
            if self.subject.lower() in oldVersionArrow:
                continue
			
            iLOG = self.readLOG()
            
            self.oLOG = os.path.join(self.outputFolder[0], os.path.split(self.iLOG)[1].replace('.txt','_gh_extracted.tsv'))
            
            if os.path.exists(self.oLOG):
                print 'File: ' + self.oLOG + ' already exists'
                continue

            if 'T1' in currLogFile:
                self.extractDataAndSaveTSV(iLOG, 0)
            elif 'T2' in currLogFile:
                self.extractDataAndSaveTSV(iLOG, 1)
            
            print self.iLOG + ' has been converted successfully'
    
    def readLOG(self, iLOG=False):
        if not iLOG: # iLOG = current Log
            if self.verbose:
                print 'Read log file ' + self.iLOG
            with open(self.iLOG, 'r') as f:
                data = f.readlines()
        else: # iLOG Perfect Data
            if self.verbose:
                print 'Read log file ' + iLOG
            with open(iLOG, 'r') as f:
                data = f.readlines()    
                
        return data
    
    def extractDataAndSaveTSV(self, iLOG, nPerfectData):
        # Return data
        # Type:
        # 0- Lost Key
        # 1- Correct Key
        # 2- Wrong Key
        
        perfectData = self.perfectData[nPerfectData]
        
        oTSV = open(self.oLOG, 'w')
        oTSV.write('Subject_Code\tCode\tKeyR\tTimeR\tKeyB\tTimeB\tKeyA\tTimeA\n')
    
        posBefore = 0
        keyBefore = 0
    
        data = [] # type, Note, Position Note, Note played, Position played Note
        for currLOG in iLOG:
            currLOG = currLOG.split('\r\n')[0]
        
            if 'osition of the played note' in currLOG:
                val = perfectData[:,1] - float(currLOG.split()[-1])
                if val[val>0].size:
                    posAfter = np.min(val[val>0])
                    keyAfter = int(perfectData[int(np.where(val == posAfter)[0]), 0]) 
                    posAfter = perfectData[int(np.where(val == posAfter)[0]), 1] 
                if val[val<0].size:
                    posBefore = np.max(val[val<0])
                    keyBefore = int(perfectData[int(np.where(val == posBefore)[0]), 0]) 
                    posBefore = perfectData[int(np.where(val == posBefore)[0]), 1] 
            
            if '' == currLOG:
                nextNote = True
                val = 0
                posBefore = 0
                keyBefore = 0
                posAfter = 0
                keyAfter = 0
            elif 'Wrong Note ' in currLOG:
                note = int(currLOG.split()[-1])
            elif 'Lost Note :' in currLOG:
                note = int(currLOG.split()[-1]) 
            elif 'Note :' in currLOG:
                noteOrig = int(currLOG.split()[-1])
            elif 'Lost position of the played note' in currLOG:
                code = 0 # Lost NOTE
                pos = float(currLOG.split()[-1])
                oTSV.write(self.subject+'\tLOST_NOTE\t' + str(note) + '\t' + str(pos) + '\t' + str(keyBefore) + '\t' + str(posBefore) + '\t' + str(keyAfter) + '\t' + str(posAfter)+ '\n')
            elif 'Note played :' in currLOG:
                note = int(currLOG.split()[-1])
            elif 'Wrong position of the played note' in currLOG:
                pos = float(currLOG.split()[-1])
            elif 'Wrong Position of the original note:' in currLOG:
                code = 2 # WRONG NOTE
                posOrig = float(currLOG.split()[-1])
                oTSV.write(self.subject+'\tWRONG_NOTE\t' + str(note) + '\t' + str(pos) + '\t' + str(keyBefore) + '\t' + str(posBefore) + '\t' + str(keyAfter) + '\t' + str(posAfter)+ '\n')
            elif 'Position of the played note' in currLOG:            
                pos = float(currLOG.split()[-1])
            elif 'Position of the original note:' in currLOG:
                code = 1 # CORRECT NOTE
                posOrig = float(currLOG.split()[-1])
                oTSV.write(self.subject+'\tCORRECT_NOTE\t' + str(note) + '\t' + str(pos) + '\t' + str(keyBefore) + '\t' + str(posBefore) + '\t' + str(keyAfter) + '\t' + str(posAfter)+ '\n')
            
        return np.asarray(data)

    def extractPerfectData(self, iLOG):
        # Return data
        # Type:
        # 0- Lost Key
        # 1- Correct Key
        # 2- Wrong Key
        data = [] # Note, Position Note
        for currLOG in iLOG:
            currLOG = currLOG.split('\r\n')[0]
            if '' == currLOG:
                continue
            elif 'Position of the original note:' in currLOG:
                pos = float(currLOG.split()[-1])
                data.append((note, pos))
            elif 'Note :' in currLOG:
                note = int(currLOG.split()[-1])
    
        return np.asarray(data)

def main():
    """Let's go"""
    args = get_arguments()
    app = convertGH(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())
