#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys , argparse
from utils import listFiles
import numpy as np
import matplotlib.pyplot as plt

def get_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="",
            epilog="""
            Convert Arrow raw data to tsv file
            
            Input: .cfg
            
            Although no arguments is mandatory there is an order, if case 1 then it won't do case 2 or 3 and so on
            1. dataset Folder
            2. subject Folder
            3. single File
            """)

    parser.add_argument(
            "-s", "--singleFile",
            required=False, nargs="+",
            help="Multiple single files can be use as an input: convert_arrow_to_tsv.py -s file1.cfg file2.cfg",
            )     
    
    parser.add_argument(
            "-d", "--dataset",
            required=False, nargs="+",
            help="dataset folder",
            )
    
    parser.add_argument(
            "-f", "--subjectFolder",
            required=False, nargs="+",
            help="Multiple subjects folders can be use as an input: convert_arrow_to_tsv.py -f folder1 folder2",
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
    
class convertArrow(object):
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
        self.iCFG = ''
        self.iLOG = ''
        
        # Design
        self.designUnique = ['FlipSeq-FlipArrow',
                             'FlipSeq-NoFlipArrow',
                             'Random-FlipArrow',
                             'Random-NoFlipArrow', 
                             'Seq-FlipArrow',
                             'Seq-NoFlipArrow']
        
        # Position on the screen
        self.positions = [[   0.        ,  163.84      ],
                          [ 155.82109963,   50.62934436],
                          [  96.30273574, -132.54934436],
                          [ -96.30273574, -132.54934436],
                          [-155.82109963,   50.62934436]]
        
        self.screens = (1024, 768)
        
        self.positions[0][0] += 512
        self.positions[0][1] = 384 + self.positions[0][1] 

        self.positions[1][0] += 512  
        self.positions[1][1] = 384 + self.positions[1][1]

        self.positions[2][0] += 512
        self.positions[2][1] = 384 - np.abs(self.positions[2][1])

        self.positions[3][0] = 512 - np.abs(self.positions[3][0])
        self.positions[3][1] = 384 - np.abs(self.positions[3][1])

        self.positions[4][0] = 512 - np.abs(self.positions[4][0])
        self.positions[4][1] = 384 + self.positions[4][1]

    def run(self):
        allCFGFiles = []
        if self.dataset:
            allCFGFiles = listFiles(self.dataset[0], allCFGFiles, '.cfg')
        elif self.subjectFolder:
            for currFolders in self.subjectFolder:
                allCFGFiles = listFiles(currFolders, allCFGFiles, '.cfg')
        elif self.singleFile:
            allCFGFiles = self.singleFile
        
        # Valid if cfg and log exist
        arrowCFGFiles = [x for x in allCFGFiles if 'Arrow' in x and os.path.exists(x.replace('.cfg','.log'))]
            
        arrowCFGFiles.sort(reverse=False)
        
        if not arrowCFGFiles:
            print 'No file were found'
        else:
            for currArrowCFGFile in arrowCFGFiles:
                self.iLOG = currArrowCFGFile.replace('.cfg','.log')
                self.iCFG = currArrowCFGFile
                
                self.oLOG = os.path.join(self.outputFolder[0], os.path.split(self.iCFG)[1].replace('.cfg','_arrow_extracted.tsv'))
                
                if os.path.exists(self.oLOG):
                    print 'File: ' + self.oLOG + ' already exists'
                    continue
                
                cfg = self.readCFG()
                design = self.readDesign(cfg['seqFilename'])

                log = self.readLOG()
                data = self.extractLOG(log)    
            
                self.saveTSV(data, design)
            
                print self.iLOG + ' has been converted successfully'
            
    def saveTSV(self, data, design):
    
        oTSV = open(self.oLOG, 'w')
        oTSV.write('NBlock\tTypeBlock\tKey\tTime\tStayTime\tDistance\tClosestKey-Err\tTime-Err\tStayTime-Err\tDistance-Err\n')
    
        endFile = False
    
        idxData = 0
        verbose = False
        isDown = False
        index = 0
    
        waitLastUP = False # Init False in case first press is wrong
    
        NbBlock = 0
        while not endFile:
            currData = data[idxData]

            if 'Key' in currData[1]:
                if not isDown:
                    answers = []
                    currKey = int(currData[2].split('.')[0])
                    currKeyPos = np.asarray(self.positions[currKey])
                    start = currData[0]
                    self.message('Look for key : '+str(currKey)) 
                else:
                    self.message('Look for new key : '+str(currData[2].split('.')[0])) 
                    
                    index = idxData
                    waitLastUP = True
        
            elif 'Input-DOWN' in currData[1]: # Check press down
                distance = np.linalg.norm(currKeyPos-np.asarray(currData[2])) # Distance to currKey
                pressDown = currData[0]
                isDown = True
                self.message('Press Down')
            
            elif 'Input-UP' in currData[1] and isDown:
                self.message('Press Up')
                isDown = False
                stay = currData[0] - pressDown
                if waitLastUP: # If last answer 
                    self.message('Wait for last UP')
                    waitLastUP = False
                    idxData = index-1
                    text = str(NbBlock) + '\t' + design[NbBlock] + '\t' + str(currKey) + '\t' + str(pressDown-start) + '\t' + str(stay) + '\t' + str(distance*4.8/163)
                    for err in answers:
                        text += '\t' + err[0] + '\t' + err[1]  + '\t' + err[2]  + '\t' +  err[3]
                    
                    text += '\n'
                    oTSV.write(text)
                else:
                    #ClosestKey-Err Time-Err StayTime-Err Distance-Err
                    timeErr = str(pressDown-start)
                    stayErr = str(stay)
                    distanceErr = str(distance*4.8/163)
                    closestKeyErr = self.closestKey(currData[2], self.positions) 
                    answers.append((closestKeyErr,timeErr,stayErr,distanceErr))
        
            elif 'Rest' in currData[1]:
                isDown = False
                stay = currData[0] - pressDown
                text = str(NbBlock) + '\t' + design[NbBlock] + '\t' + str(currKey) + '\t' + str(pressDown-start) + '\t' + str(0) + '\t' + str(distance*4.8/163)
                for err in answers:
                    text += '\t' + err[0] + '\t' + err[1]  + '\t' + err[2]  + '\t' +  err[3]
                        
                text += '\n'
                oTSV.write(text)
                NbBlock += 1
            
            idxData += 1
            if idxData>len(data)-1:
                endFile = True

    def readCFG(self):
        print 'Reading config file ' + self.iCFG    
        with open(self.iCFG, 'r') as f:
            data = f.readlines()

        data = data[0]
        data = data.replace('true','"True"')
        data = data.replace('false','"False"')
        data = eval(data)
    
        return data

    def readLOG(self):
        print 'Reading log file ' + self.iLOG
        with open(self.iLOG, 'r') as f:
            data = f.readlines()

        return data

    def extractLOG(self, iLOG):
        indexStartExp = [i for i, string in enumerate(iLOG) if 'StartExp' in string][0]
        iLOG = iLOG[indexStartExp:]
        startExp = float(iLOG[0].split()[0])
        iLOG = iLOG[1:]
        data = []
        
        for currLOG in iLOG:
        
            currLOG = currLOG.split()
            data.append([float(currLOG[0])-startExp, 0, 0])
        
            if len(currLOG) == 3:
                if 'StartRest' in currLOG:
                    data[-1][1] =  'Rest'
                elif 'Key' in currLOG:
                    data[-1][1] = 'Key'
                    data[-1][2] = currLOG[2]
            elif len(currLOG) == 7:
                exec(currLOG[-1])
                data[-1][2] = pos
                if 'up' in currLOG[5]:
                    data[-1][1] = 'Input-UP'
                elif 'down' in currLOG[5]:
                    data[-1][1] = 'Input-DOWN'
    
        return data

    def closestKey(self, currPos, positions):
        distance = 10000
        for idx, position in enumerate(positions):
            newDistance = np.linalg.norm(np.asarray(currPos)-np.asarray(position))
            if newDistance<distance:
                distance = newDistance
                index = idx
            
        return str(index)

    def message(self, mess):
        if self.verbose:
            print('-> '+ mess)
    
    def readDesign(self, designFile):

        design = []

        seq = np.array([0.,2.,1.,0.,3.,4.,0.,1.,3.,2.,4.])
        seqTransfered = np.mod(seq+1,5)
    
        seq = ''.join([str(i) for i in seq])
        seqTransfered = ''.join([str(i) for i in seqTransfered])
    
        print 'Reading design file ' + designFile
        allKeys = np.loadtxt(designFile)
        restIndexes = np.where(allKeys[:,0]==999)
        restPeriods = np.concatenate((np.zeros(1)-1, restIndexes[0]+1), axis=0)

        for indexBlock, item in np.ndenumerate(restPeriods[:-1]):
            currKeys = allKeys[int(restPeriods[indexBlock[0]])+1:int(restPeriods[indexBlock[0]+1]),:]
            currKeysStr = ''.join([str(i) for i in currKeys[:,1]])
            SeqName = '' 
            if seq in currKeysStr:
                SeqName = 'Seq'
            elif seqTransfered in currKeysStr:
                SeqName = 'FlipSeq' 
            else:
                SeqName = 'Random'

            if currKeys[0,0] == 72:
                SeqName += '-FlipArrow'             
            else:
                SeqName += '-NoFlipArrow'
               
            design.append(SeqName)
    
        return design

def main():
    """Let's go"""
    args = get_arguments()
    app = convertArrow(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())
