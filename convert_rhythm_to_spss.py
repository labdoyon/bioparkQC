#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys , argparse, csv
from utils import listFiles
from math import ceil
import numpy as np
import matplotlib.pyplot as plt

def get_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="",
            epilog="""
            Convert Rhythm tsv data to spss tsv file
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
    
class convertRhythm(object):
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
        self.oLOG = os.path.join(self.outputFolder[0], 'rhythm_task_preprocessing_template.tsv')
        self.iLOG = ''
        self.iID = ''
        self.subject = ''    

    def run(self):
        allLOGFiles = []
        if self.dataset:
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, 'rhythm_freq_1_extracted.tsv')
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, 'rhythm_freq_2_extracted.tsv')

        # All LOG Files
        allLOGFiles.sort(reverse=False)
        
        self.initOutput()
        
        for idx, currLogFile in enumerate(allLOGFiles):
            print currLogFile
            self.iLOG = currLogFile
            self.subject = os.path.split(self.iLOG)[1].split('_rhy')[0]
            
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
        
        data = np.genfromtxt(self.iLOG, skip_header=1, delimiter='\t')
        
        # Read line by line in a dict            
        with open(self.iLOG, 'r') as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')

            previousNBlock = 0
            Nrtrialblock = 1
            
            for idx, trial in enumerate(reader):
                #trial['NBlock'] = trial['NBlock'] + 1
                #trial['ResponseTime'] 
                #trial['BipBefore'],
                #trial['BipAfter'],
                #trial['Code'],                
                trial['nrtrial'] = Nrtrialblock
                
                '''
                Find Maximum trial for each block and code
                '''
                tmpData = data[data[:,0]==int(trial['NBlock'])]
                tmpData = tmpData[tmpData[:,4]==int(trial['Code'])]
                trial['maxtrial'] = tmpData.shape[0]
                
                trial['blockcode'] = 10*int(trial['NBlock']) + int(trial['Code'])
                trial['difresp'] = ''
                trial['IRI_code0'] = ''
                trial['IRI_code1'] = ''
                trial['deciles'] = 0                                
                trial['B0C0_D1'] = ''
                trial['B0C0_D2'] = ''
                trial['B0C0_D3'] = ''
                trial['B0C0_D4'] = ''
                trial['B0C0_D5'] = ''
                trial['B0C0_D6'] = ''
                trial['B0C0_D7'] = ''
                trial['B0C0_D8'] = ''
                trial['B0C0_D9'] = ''
                trial['B0C0_D10'] = ''
                trial['B0C1_D1'] = ''
                trial['B0C1_D2'] = ''
                trial['B0C1_D3'] = ''
                trial['B0C1_D4'] = ''
                trial['B0C1_D5'] = ''
                trial['B0C1_D6'] = ''
                trial['B0C1_D7'] = ''
                trial['B0C1_D8'] = ''
                trial['B0C1_D9'] = ''
                trial['B0C1_D10'] = ''
                trial['B1C0_D1'] = ''
                trial['B1C0_D2'] = ''
                trial['B1C0_D3'] = ''
                trial['B1C0_D4'] = ''
                trial['B1C0_D5'] = ''
                trial['B1C0_D6'] = ''
                trial['B1C0_D7'] = ''
                trial['B1C0_D8'] = ''
                trial['B1C0_D9'] = ''
                trial['B1C0_D10'] = ''
                trial['B1C1_D1'] = ''
                trial['B1C1_D2'] = ''
                trial['B1C1_D3'] = ''
                trial['B1C1_D4'] = ''
                trial['B1C1_D5'] = ''
                trial['B1C1_D6'] = ''
                trial['B1C1_D7'] = ''
                trial['B1C1_D8'] = ''
                trial['B1C1_D9'] = ''
                trial['B1C1_D10'] = ''
                
                trial['frequency'] = int(trial['ResponseTime']) + int(trial['BipBefore'])
                trial['freqdiff'] = ''
                             
                if idx>0:
                    
                    trial['freqdiff'] = int(trial['frequency'])-previousFrequency
                    trial['difresp'] = int(trial['ResponseTime']) - int(previousResponseTime)
                    if previousNBlock != trial['NBlock'] or previousCode != trial['Code']:
                        Nrtrialblock = 1
                        trial['deciles'] = 0
                        trial['nrtrial'] = Nrtrialblock
                    #elif previousNBlock != trial['NBlock']:
                        #trial['difresp'] = int(trial['ResponseTime']) - int(previousResponseTime)
                    #elif previousCode != trial['Code']:
                        #trial['difresp'] = int(trial['ResponseTime']) - int(previousResponseTime)
                    #else:
                        #trial['difresp'] = int(trial['ResponseTime']) - int(previousResponseTime)
                    if int(trial['Code']) == 1:
                        trial['IRI_code1'] = trial['difresp']
                    else:
                        trial['IRI_code0'] = trial['difresp']

                    trial['deciles'] = np.floor(trial['nrtrial']/(ceil(trial['maxtrial']*10)/100))        
                        
                    condition = 'B' + trial['NBlock'] + 'C' + trial['Code'] + '_D' + str(int(trial['deciles'])+1)
                    trial[condition] = trial['difresp']
                
                with open(self.oLOG, 'a') as f:
                    f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}\t{17}\t{18}\t{19}\t{20}\t{21}\t{22}\t{23}\t{24}\t{25}\t{26}\t{27}\t{28}\t{29}\t{30}\t{31}\t{32}\t{33}\t{34}\t{35}\t{36}\t{37}\t{38}\t{39}\t{40}\t{41}\t{42}\t{43}\t{44}\t{45}\t{46}\t{47}\t{48}\t{49}\t{50}\t{51}\t{52}\t{53}\t{54}\n'.format(
                        self.subject,
                        trial['NBlock'],
                        trial['ResponseTime'],
                        trial['BipBefore'],
                        trial['BipAfter'],
                        trial['Code'],
                        trial['nrtrial'],
                        trial['maxtrial'],
                        trial['blockcode'],
                        trial['difresp'],
                        trial['IRI_code1'],
                        trial['IRI_code0'],
                        trial['deciles'],
                        trial['B0C0_D1'],
                        trial['B0C0_D2'],
                        trial['B0C0_D3'],
                        trial['B0C0_D4'],
                        trial['B0C0_D5'],
                        trial['B0C0_D6'],
                        trial['B0C0_D7'],
                        trial['B0C0_D8'],
                        trial['B0C0_D9'],
                        trial['B0C0_D10'],
                        trial['B0C1_D1'],
                        trial['B0C1_D2'],
                        trial['B0C1_D3'],
                        trial['B0C1_D4'],
                        trial['B0C1_D5'],
                        trial['B0C1_D6'],
                        trial['B0C1_D7'],
                        trial['B0C1_D8'],
                        trial['B0C1_D9'],
                        trial['B0C1_D10'],
                        trial['B1C0_D1'],
                        trial['B1C0_D2'],
                        trial['B1C0_D3'],
                        trial['B1C0_D4'],
                        trial['B1C0_D5'],
                        trial['B1C0_D6'],
                        trial['B1C0_D7'],
                        trial['B1C0_D8'],
                        trial['B1C0_D9'],
                        trial['B1C0_D10'],
                        trial['B1C1_D1'],
                        trial['B1C1_D2'],
                        trial['B1C1_D3'],
                        trial['B1C1_D4'],
                        trial['B1C1_D5'],
                        trial['B1C1_D6'],
                        trial['B1C1_D7'],
                        trial['B1C1_D8'],
                        trial['B1C1_D9'],
                        trial['B1C1_D10'],
                        trial['frequency'],
                        trial['freqdiff']))    
                
                previousResponseTime = trial['ResponseTime']
                previousNBlock = trial['NBlock']
                previousCode =  trial['Code']
                previousFrequency = int(trial['frequency'])
                
                Nrtrialblock = Nrtrialblock + 1                                    
            
    def initOutput(self):
        if os.path.exists(self.oLOG):
            'Output file '+ os.path.split(self.oLOG)[1] + ' already exists and will be overwritten'
            
        oTSV = open(self.oLOG, 'w')
        oTSV.write('Subject_code\tNBlock\tResponseTime\tBipBefore\tBipAfter\tCode\tnrtrial\tmaxtrial\tblockcode\tdifresp\tIRI_code1\tIRI_code0\tdeciles\tB0C0_D1\tB0C0_D2\tB0C0_D3\tB0C0_D4\tB0C0_D5\tB0C0_D6\tB0C0_D7\tB0C0_D8\tB0C0_D9\tB0C0_D10\tB0C1_D1\tB0C1_D2\tB0C1_D3\tB0C1_D4\tB0C1_D5\tB0C1_D6\tB0C1_D7\tB0C1_D8\tB0C1_D9\tB0C1_D10\tB1C0_D1\tB1C0_D2\tB1C0_D3\tB1C0_D4\tB1C0_D5\tB1C0_D6\tB1C0_D7\tB1C0_D8\tB1C0_D9\tB1C0_D10\tB1C1_D1\tB1C1_D2\tB1C1_D3\tB1C1_D4\tB1C1_D5\tB1C1_D6\tB1C1_D7\tB1C1_D8\tB1C1_D9\tB1C1_D10\tfrequency\tfreqdiff\n')
            
def main():
    """Let's go"""
    args = get_arguments()
    app = convertRhythm(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())      
