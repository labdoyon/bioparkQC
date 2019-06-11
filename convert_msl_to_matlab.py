#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Convert MSL task

import os, sys, argparse, json
import scipy.io as scio
import numpy as np
from utils import listFiles

def get_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="",
            epilog="""
            Convert MSL raw data to MAT file
            
            Input:  .cfg files
            
            Although no arguments is mandatory there is an order, if case 1 then it won't do case 2 or 3 and so on
            1. dataset Folder
            2. subject Folder
            3. single File
            """)

    parser.add_argument(
            "-s", "--singleFile",
            required=False, nargs="+",
            help="Multiple single files can be use as an input: convert_msl_matlab.py -s file1.cfg file2.cfg",
            )
    
    parser.add_argument(
            "-d", "--dataset",
            required=False, nargs="+",
            help="dataset folder",
            )
    
    parser.add_argument(
            "-f", "--subjectFolder",
            required=False, nargs="+",
            help="Multiple subjects folders can be use as an input: convert_msl_matlab.py -d folder1 folder2",
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
    
    
class convertMSL(object):
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
        self.oMAT = ''
        self.iLOG = ''
        self.iCDG = ''
        self.subject = ''

    def run(self):
        allCFGFiles = []
        if self.dataset:
            allCFGFiles = listFiles(self.dataset[0], allCFGFiles, '.cfg')
        elif self.subjectFolder:
            for currFolders in self.subjectFolder:
                allCFGFiles = listFiles(currFolders, allCFGFiles, '.cfg')
        elif self.singleFile:
            allCFGFiles = self.singleFile

        # Valid if log exists and within the right folder
        allCFGFiles = [x for x in allCFGFiles if ('MSL' in x and 'task' in x and os.path.exists(x.replace('cfg','log')))]
        
        allCFGFiles.sort(reverse=False)
        
        if not allCFGFiles:
            print 'No file were found'
        else:
            for currCFGFile in allCFGFiles:
                self.iCFG = currCFGFile
                self.iLOG = currCFGFile.replace('cfg','log')
                
                cfg = self.extractCFG()

                if self.verbose:
                    print cfg['subject']
				
                self.oMAT = os.path.join(self.outputFolder[0], self.subject + '_msl_' + self.hand + '.mat')
                
                if os.path.exists(self.oMAT):
                    print 'File: ' + self.oMAT + ' already exists'
                    continue

                self.extract4Matlab(cfg)
                
                print self.iCFG + ' has been converted successfully'

    def extractCFG(self):
        #load json file
        cfg = json.loads(open(self.iCFG).read())

        #Remove u before field (unicode)
        cfg = dict([(str(k),v) for k,v in cfg.items()])
                
        self.subject = cfg['subject']
        self.hand = cfg['hand']
        
        return cfg
    
    def extract4Matlab(self, cfg):

        #Conversion of some fields
        seq = []
        for i in cfg['seq'].split(' - '):
            seq.append(int(i))
        cfg['seq'] = seq
    
        obj_arr = np.zeros((int(cfg['nbBlocks'])*int(cfg['nbKeys']) + int(cfg['nbBlocks'])*2 + 50,), dtype=np.object)

        index = 0
        nBlock = 1

        # Load data file
        log = open(self.iLOG, 'r')
        num_lines = sum(1 for line in open(self.iLOG,'r'))
        obj_arr = np.zeros((num_lines+1,), dtype=np.object)
		    
        for line in log: 
            val = line.split()
            val[0] = str(val[0])
            
            if val[1] in 'StartExp':
                tmpObj = np.zeros((2,), dtype=np.object)
                tmpObj[0] = str(0)
                tmpObj[1] = 'start'
                obj_arr[index] = tmpObj
                index += 1
        
                tmpObj = np.zeros((2,), dtype=np.object)
                tmpObj[0] = val[0]
                tmpObj[1] = 'rest'
                obj_arr[index] = tmpObj
                index += 1
            elif val[1] in 'StartRest':
                tmpObj = np.zeros((2,), dtype=np.object)
                tmpObj[0] = val[0]
                tmpObj[1] = 'Rest'
                obj_arr[index] = tmpObj
                nBlock += 1
                index += 1
            elif val[1] in 'StartPerformance':
                tmpObj = np.zeros((3,), dtype=np.object)
                tmpObj[0] = val[0]
                tmpObj[1] = 'Practice'
                tmpObj[2] = 'Block' + str(nBlock)
                obj_arr[index] = tmpObj
                index += 1
            elif val[1] in 'DATA':
                if not val[3] in '5':
                    tmpObj = np.zeros((3,), dtype=np.object)
                    tmpObj[0] = val[0]
                    tmpObj[1] = 'rep'
                    tmpObj[2] = str(val[3])
                    obj_arr[index] = tmpObj
                    index += 1
            
        lastTmpObj = np.zeros((2,), dtype=np.object)
        lastTmpObj[0] = str(float(tmpObj[0]) + int(cfg['durRest']))
        lastTmpObj[1] = 'end'
		
        obj_arr[index] = lastTmpObj

        # Save file
        scio.savemat(self.oMAT, {'param':cfg, 'logoriginal':obj_arr})

def main():
    """Let's go"""
    args = get_arguments()
    app = convertMSL(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())
