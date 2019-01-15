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
            Convert Arrow tsv data to spss tsv file
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
    
class convertARROW(object):
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
        self.oLOG = os.path.join(self.outputFolder[0], 'arrow_task_preprocessing_template.tsv')
        self.iLOG = ''
        self.subject = ''

    def run(self):
        allLOGFiles = []
        if self.dataset:
            allLOGFiles = listFiles(self.dataset[0], allLOGFiles, 'arrow_extracted.tsv')

        # All LOG Files
        allLOGFiles.sort(reverse=False)
        
        if os.path.exists(self.oLOG):
            'Output file '+ os.path.split(self.oLOG)[1] + ' already exists and will be overwritten'
            self.initOutput()
        
        for idx, currLogFile in enumerate(allLOGFiles):
            self.iLOG = currLogFile
            self.subject = os.path.split(self.iLOG)[1].split('_Run')[0]
            
            self.extractLOG()
            print self.subject + ' has been extracted successfully'
            
    def extractLOG(self):
        
        # Read line by line in a dict            
        with open(self.iLOG, 'r') as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')
            
            previousNBlock = ''
            Nrtrialblock = 1
            
            for idx, trial in enumerate(reader):
                
                trial['Blockcode'] = getTrialCode(trial['TypeBlock'])        
                trial['Nrtrial'] = idx
                
                if idx>1:
                    if previousNBlock != trial['NBlock']:
                        Nrtrialblock = 1
                        
                trial['Nrtrialblock'] = Nrtrialblock

                trial['correct'] = 1
                trial['nb_err_keys'] = 0
                trial['nb_err_samekeys'] = 0
                trial['nb_err_diffkeys'] = 0
                trial['Sum_time_err'] = 0
                trial['Sum_stay_err'] =  0
                
                if not trial['StayTime-Err'] is None:
                    trial['correct'] = 0
                
                if None in trial: # More than ONE ERROR

                    errors = np.asarray([float(x) for x in trial[None]])
                    errors = np.reshape(errors,(len(trial[None])/4, 4))
                    
                    first_error = [int(trial['ClosestKey-Err']), float(trial['Time-Err']), float(trial['StayTime-Err']), float(trial['Distance-Err'])]
                    first_error = np.asarray(first_error)
                    first_error = np.reshape(first_error,(1, 4))
                    
                    allErrors = np.concatenate((first_error, errors), axis=0)
                    
                    trial['Sum_time_err'] = np.sum(allErrors[:,1]) # Sum of time error
                    trial['Sum_stay_err'] = np.sum(allErrors[:,2]) # Sum of stay error
                    
                    trial['nb_err_samekeys'] = np.where(allErrors[:,0]==int(trial['Key']))[0].shape[0]
                    trial['nb_err_diffkeys'] = np.where(allErrors[:,0]!=int(trial['Key']))[0].shape[0]
                    
                elif not trial['ClosestKey-Err'] is None : # One ERROR
                    if int(trial['ClosestKey-Err'])==int(trial['Key']):
                        trial['nb_err_samekeys'] = 1
                    else:
                        trial['nb_err_diffkeys'] = 1
                        
                    trial['Sum_time_err'] = trial['Time-Err']
                    trial['Sum_stay_err'] = trial['StayTime-Err']
                    
                with open(self.oLOG, 'a') as f:
                    f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\n'.format(
                        self.subject,
                        trial['NBlock'],
                        trial['TypeBlock'],
                        trial['Key'],
                        trial['Time'],
                        trial['StayTime'],
                        trial['Distance'],
                        trial['Blockcode'],
                        trial['Nrtrial'],
                        trial['Nrtrialblock'],
                        trial['correct'],
                        trial['nb_err_keys'],
                        trial['nb_err_samekeys'],  
                        trial['nb_err_diffkeys'],
                        trial['Sum_time_err'],
                        trial['Sum_stay_err']))
                
                previousNBlock = trial['NBlock']
                Nrtrialblock = Nrtrialblock + 1

    def initOutput(self):
        if os.path.exists(self.oLOG):
            'Output file '+ os.path.split(self.oLOG)[1] + ' already exists and will be overwritten'
            
        oTSV = open(self.oLOG, 'w')
        oTSV.write('Subject_code\tNBlock\tTypeBlock\tKey\tTime\tStayTime\tDistance\tBlockcode\tNrtrial\tNrtrialblock\tcorrect\tnb_err_keys\tnb_err_samekeys\tnb_err_diffkeys\tSum_time_err\tSum_stay_err\n')
        
def getTrialCode(TypeBlock):
    if TypeBlock == 'Seq-NoFlipArrow':
        return 0
    elif TypeBlock == 'Random-NoFlipArrow':
        return 1
    elif TypeBlock == 'FlipSeq-NoFlipArrow':
        return 2        
    elif TypeBlock == 'FlipSeq-FlipArrow':
        return 3        
    elif TypeBlock == 'Seq-FlipArrow':
        return 4        
    elif TypeBlock == 'Random-FlipArrow':
        return 5        

def main():
    """Let's go"""
    args = get_arguments()
    app = convertARROW(**vars(args))
    return app.run()

if __name__ == '__main__':
    sys.exit(main())        
        
        
        
        
        