#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys , argparse, csv
from utils import listFiles
import numpy as np
import matplotlib.pyplot as plt

def get_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="",
            epilog="""
            Convert Congruency tsv data to spss tsv file
            """)

    parser.add_argument(
            "-d", "--dataset",
            required=False, nargs="+",
            help="dataset folder",
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
    
class convertCONGRUENCY(object):
    """
    """
    def __init__(
            self, dataset, 
        outputFolder, verbose=False, overwrite=False, log_level="INFO"):
        self.dataset = dataset
        
        if not os.path.exists(outputFolder[0]):
            os.mkdir(outputFolder[0])

        self.outputFolder = outputFolder
        self.verbose = verbose
        self.overwrite = overwrite
        self.oLOG = os.path.join(self.outputFolder[0], 'congruency_task_preprocessing_template.tsv')
        self.iLOG = ''
        self.iID = ''
        self.subject = ''    

    def run(self):
        allLOGFiles = []
        if self.dataset:
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, 'congruency_extracted.tsv')

        # All LOG Files
        allLOGFiles.sort(reverse=False)
        
        self.initOutput()
        
        for idx, currLogFile in enumerate(allLOGFiles):
            print currLogFile
            self.iLOG = currLogFile
            self.subject = os.path.split(self.iLOG)[1].split('_Cond')[0]
            
            # Get Condition
            if 'Condition1' in self.iLOG:
                self.condition = 'cond1'
                self.condcogmot = 1
                
            elif 'Condition2' in self.iLOG:
                self.condition = 'cond2'
                self.condcogmot = 2
                    
            self.extractLOG() 
            print os.path.split(self.iLOG)[1] + ' has been extracted successfully'
        
    def extractLOG(self):
        # Read line by line in a dict            
        with open(self.iLOG, 'r') as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')

            previousNBlock = 0
            Nrtrialblock = 1
            
            for idx, trial in enumerate(reader):
                              
                if idx>1:
                    if previousNBlock != trial['NBlock']:
                        Nrtrialblock = 1
                        
                trial['correct'] = 0
                trial['RTcorrect'] = ''
                trial['cogincog'] = 0
                trial['nrblock'] = int(trial['NBlock']) + 1
                trial['nrtrial_wblock'] = Nrtrialblock
                
                
                if trial['ExpectedAnswer']==trial['Answer']:
                    trial['correct'] = 1
                    trial['RTcorrect'] = trial['RT']
                
                # Choosen color is blue as congrent
                if trial['Cog']=='blue':
                    if self.condcogmot == 1:
                        if trial['Color']=='Yellow':
                            trial['cogincog'] = 1
                    elif self.condcogmot == 2:
                        if trial['ExpectedAnswer']=='Right':
                            trial['cogincog'] = 1
                
                # Choosen color is yellow as congrent
                elif trial['Cog']=='yellow':                            
                    if self.condcogmot == 1:
                        if trial['Color']=='Blue':
                            trial['cogincog'] = 1
                    elif self.condcogmot == 2:
                        if trial['ExpectedAnswer']=='Left':
                            trial['cogincog'] = 1
                
                with open(self.oLOG, 'a') as f:
                    f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\n'.format(
                        self.subject,
                        trial['NBlock'],
                        trial['Side'],
                        trial['Color'],
                        trial['ExpectedAnswer'],
                        trial['Answer'],
                        trial['RT'],
                        trial['nrblock'],
                        trial['nrtrial_wblock'],
                        trial['correct'],
                        trial['RTcorrect'],
                        self.condcogmot,  
                        trial['cogincog']))    
                    
                previousNBlock = trial['NBlock']
                Nrtrialblock = Nrtrialblock + 1                                    
            
    def initOutput(self):
        if os.path.exists(self.oLOG):
            'Output file '+ os.path.split(self.oLOG)[1] + ' already exists and will be overwritten'
            
        oTSV = open(self.oLOG, 'w')
        oTSV.write('Subject_code\tNBlock\tSide\tColor\tExpectedAnswer\tAnswer\tRT\tnrblock\tnrtrial_wblock\tcorrect\tRTcorrect\tcondcogmot\tcogincog\n')
            
def main():
    """Let's go"""
    args = get_arguments()
    app = convertCONGRUENCY(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())      