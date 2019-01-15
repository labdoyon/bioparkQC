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
            Convert Guitar Hero tsv data to spss tsv file
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
            "-w", "--overwrite",
            required=False, nargs="+",
            help="Overwrite",
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
            self, dataset, 
        outputFolder, verbose=False, overwrite=False, log_level="INFO"):
        self.dataset = dataset
        
        if not os.path.exists(outputFolder[0]):
            os.mkdir(outputFolder[0])

        self.outputFolder = outputFolder
        self.verbose = verbose
        self.overwrite = overwrite
        self.oLOG = os.path.join(self.outputFolder[0], 'guitar_hero_task_step1_preprocessing_template.tsv')
        self.iLOG = ''
        self.iID = ''
        self.speed = ''
        self.subject = ''
        self.chunckSpeed1 = np.array([82000, 141000])
        self.chunckSpeed1Codes = np.array([1, 2, 3])
        self.chunckSpeed2 = np.array([30000, 74000, 91000, 124000, 147000])
        self.chunckSpeed2Codes = np.array([2, 1, 3, 2, 3, 1])

    def run(self):
        allLOGFiles = []
        if self.dataset:
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, 'gh_extracted')
            
        # All LOG Files
        allLOGFiles.sort(reverse=False)
        
        IDs = self.getIDs(allLOGFiles)
        
        self.initOutput()
        
        for idx, currLogFile in enumerate(allLOGFiles):
            self.iLOG = currLogFile
            self.iID = IDs[idx]
            self.getSpeed()
            self.subject = os.path.split(self.iLOG)[1]
            if self.verbose:
                print self.subject + ', speed: ' + self.speed
            
            self.extractLOG()
        
    def initOutput(self):
        if not os.path.exists(self.oLOG) or (os.path.exists(self.oLOG) and self.overwrite):
            oTSV = open(self.oLOG, 'w')
            oTSV.write('Subj_code\tVITESSE\tCODE_NOTE\tKeyR\tTimeR\tKeyB\tTimeB\tKeyA\tTimeA\tbegin\ttrialno\tnotecode\tdif_time_B\tdif_time_A\tdifmin\tdifcorr\tBiopark_numcode\tGH_speed\tReal_speed\tRS1_code1\tRS1_code0\tRS1_code9\tRS2_code1\tRS2_code0\tRS2_code9\tRS3_code1\tRS3_code0\tRS3_code9\n')
    
    def getSpeed(self):
        self.speed = [x for x in os.path.split(self.iLOG)[1].split('_') if 'VI' in x][0]
    
    def getRealSpeed(self, data, speed):
        if speed == 1:
            chuncks = self.chunckSpeed1
            chuncksCode = self.chunckSpeed1Codes
        elif speed == 2:
            chuncks = self.chunckSpeed2
            chuncksCode = self.chunckSpeed2Codes
        
        chuncks = np.append(chuncks, data)
        chuncks.sort()
        
        return chuncksCode[np.where(chuncks==data)][0]
     
    def getIDs(self, iLOGs):
        LOGs = [os.path.split(x)[1].split('_VI')[0] for x in iLOGs]
        
        previousLOG = ''
        IDs = []
        nID = 1001
        for idx, currLOG in enumerate(LOGs):
            if idx == 0:
                IDs.append(nID)
            elif previousLOG == currLOG:
                IDs.append(nID)
            else:
                nID = nID + 1
                IDs.append(nID)
            
            previousLOG = currLOG
    
        return IDs    
        
    
    def extractLOG(self):
        
        # Read all lines
        with open(self.iLOG, 'r') as f:
            data = f.readlines()
            
        # Read line by line in a dict            
        with open(self.iLOG, 'r') as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')
            for idx, trial in enumerate(reader): #for idx, val in enumerate(ints):
        
                trial['Biopark_numcode'] = self.iID
        
                trial['RS1_code1'] = ''
                trial['RS1_code0'] = ''
                trial['RS1_code9'] = ''
                trial['RS2_code1'] = ''
                trial['RS2_code0'] = ''
                trial['RS2_code9'] = ''
                trial['RS3_code1'] = ''
                trial['RS3_code0'] = ''
                trial['RS3_code9'] = ''
                
                
                trial['VITESSE'] = self.speed
                
                if idx == 0: # First Trial
                    trial['begin'] =  1
                else:
                    trial['begin'] =  0
                
                # Trial number
                trial['trialno'] = idx + 1
                
                # Trial Speed
                trial['GH_speed'] =  1
                if 'T1' in self.iLOG:
                    trial['GH_speed'] =  1
                    trial['Real_speed'] = self.getRealSpeed(float(trial['TimeR']), 1)
                 
                    
                elif 'T2' in self.iLOG:
                    trial['GH_speed'] =  2
                    trial['Real_speed'] = self.getRealSpeed(float(trial['TimeR']), 2)
                
                
                # CORRECT NOTE
                if trial['Code'] == 'CORRECT_NOTE':
                    trial['notecode'] = 1 
                    trial['dif_time_B'] = float(trial['TimeR'])-float(trial['TimeB'])
                    trial['dif_time_A'] = float(trial['TimeR'])-float(trial['TimeA'])

 		    if np.abs(trial['dif_time_B'])>np.abs(trial['dif_time_A']):
                        trial['difmin'] = trial['dif_time_A']
		    else: 
                        trial['difmin'] = trial['dif_time_B']

                    if trial['Real_speed'] == 1:
                        trial['RS1_code1'] = 1
                    elif trial['Real_speed'] == 2:
                        trial['RS2_code1'] = 1
                    elif trial['Real_speed'] == 3:
                        trial['RS3_code1'] = 1
                    
                    # Not first trial
                    trial['difcorr'] = ''
                    if idx>1 and previousTrial is not None:
                        if previousTrial['Code'] == 'CORRECT_NOTE':
                            trial['difcorr'] = float(trial['TimeR']) - float(previousTrial['TimeR'])
                    
                # LOST NOTE    
                elif trial['Code'] == 'LOST_NOTE':
                    trial['notecode'] = 9 
                    trial['dif_time_B'] = ''
                    trial['dif_time_A'] = ''
                    trial['difmin'] = ''
                    trial['difcorr'] = ''
                    
                    if trial['Real_speed'] == 1:
                        trial['RS1_code9'] = 1
                    elif trial['Real_speed'] == 2:
                        trial['RS2_code9'] = 1
                    elif trial['Real_speed'] == 3:
                        trial['RS3_code9'] = 1
                    
                # WRONG NOTE    
                elif trial['Code'] == 'WRONG_NOTE':
                    trial['notecode'] = 0
                    trial['dif_time_B'] = ''
                    trial['dif_time_A'] = ''
                    trial['difmin'] = ''
                    trial['difcorr'] = ''

                    if trial['Real_speed'] == 1:
                        trial['RS1_code0'] = 1
                    elif trial['Real_speed'] == 2:
                        trial['RS2_code0'] = 1
                    elif trial['Real_speed'] == 3:
                        trial['RS3_code0'] = 1                                    

                previousTrial = trial
                
                with open(self.oLOG, 'a') as f:
                    f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}\t{17}\t{18}\t{19}\t{20}\t{21}\t{22}\t{23}\t{24}\t{25}\t{26}\t{27}\n'.format(
                        os.path.split(self.iLOG)[1].split('_VI')[0],
                        trial['VITESSE'],
                        trial['Code'],
                        trial['KeyR'],
                        trial['TimeR'],
                        trial['KeyB'],
                        trial['TimeB'],
                        trial['KeyA'],
                        trial['TimeA'],
                        trial['begin'],
                        trial['trialno'],
                        trial['notecode'],
                        trial['dif_time_B'],
                        trial['dif_time_A'],
                        trial['difmin'],
                        trial['difcorr'],
                        trial['Biopark_numcode'],
                        trial['GH_speed'],
                        trial['Real_speed'],
                        trial['RS1_code1'],
                        trial['RS1_code0'],
                        trial['RS1_code9'],
                        trial['RS2_code1'],
                        trial['RS2_code0'],
                        trial['RS2_code9'],
                        trial['RS3_code1'],
                        trial['RS3_code0'],
                        trial['RS3_code9']))

def main():
    """Let's go"""
    args = get_arguments()
    app = convertGH(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())
