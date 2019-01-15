#!/usr/bin/env python
# -*- coding: utf-8	-*-

import os, sys , argparse
from utils import listFiles, oldVersionCongruency, oldCongruency
import numpy as	np
import matplotlib.pyplot as	plt

def	get_arguments():
	parser	= argparse.ArgumentParser(
			formatter_class=argparse.RawDescriptionHelpFormatter,
			description="",
			epilog="""
			Convert Congruency raw data to tsv file
			
			Input: .cfg
			
			Although	no arguments is	mandatory there	is an order, if	case 1 then	it won't do	case 2 or 3	and	so on
			1. dataset Folder
			2. subject Folder
			3. single File
			""")

	parser.add_argument(
			"-s", "--singleFile",
			required=False, nargs="+",
			help="Multiple single files can be use as an	input: convert_congruency_to_tsv.py	-s file1.cfg file2.cfg",
			)	 
	
	parser.add_argument(
			"-d", "--dataset",
			required=False, nargs="+",
			help="dataset folder",
			)
	
	parser.add_argument(
			"-f", "--subjectFolder",
			required=False, nargs="+",
			help="Multiple subjects folders can be use as an	input: convert_congruency_to_tsv.py	-d folder1 folder2",
			)
   
	parser.add_argument(
			"-o", "--outputFolder",
			required=True, nargs="+",
			help="Output	Folder",
			)   

	parser.add_argument(
			"-v", "--verbose",
			required=False, nargs="+",
			help="Verbose",
			)

	args =	parser.parse_args()
	if	len(sys.argv) == 1:
		parser.print_help()
		sys.exit()
	else:
		return args

class convertCongruency(object):
	"""
	"""
	def __init__(
			self, singleFile, dataset, subjectFolder, 
		outputFolder,	verbose=False, log_level="INFO"):
		self.singleFile =	singleFile
		self.dataset = dataset
		self.subjectFolder = subjectFolder
		
		if not os.path.exists(outputFolder[0]):
			os.mkdir(outputFolder[0])

		self.outputFolder	= outputFolder
		self.verbose = verbose
		self.oLOG	= ''
		self.iCFG	= ''
		self.iLOG	= ''

	def run(self):
		allCFGFiles =	[]
		if self.dataset:
			allCFGFiles = listFiles(self.dataset[0],	allCFGFiles, '.cfg')
		elif self.subjectFolder:
			for currFolders in self.subjectFolder:
				allCFGFiles	= listFiles(currFolders, allCFGFiles, '.cfg')
		elif self.singleFile:
			allCFGFiles = self.singleFile
			
		#	Valid if CFG and LOG exist
		congruencyCFGFiles = []
		for currCFGFile in allCFGFiles:
			if 'Congruency' in currCFGFile:
				currLOGFile	= currCFGFile
				currLOGFile.replace('cfg','log')
				currLOGFile.replace('Condition1','task')
				currLOGFile.replace('Condition2','task')
				
				# Check	if log file	exists
				if os.path.exists(currLOGFile):
					congruencyCFGFiles.append(currCFGFile)
		
		congruencyCFGFiles.sort(reverse=False)
		
		if not congruencyCFGFiles:
			print 'No file were found'
		else:
			for currCongruencyCFGFile in	congruencyCFGFiles:
				self.iCFG =	currCongruencyCFGFile
				
				self.iLOG =	currCongruencyCFGFile
				self.iLOG =	self.iLOG.replace('cfg','log')
				self.iLOG =	self.iLOG.replace('Condition1','task')
				self.iLOG =	self.iLOG.replace('Condition2','task')

				# Current CFG File
				cfg	= self.readCFG()
				# Current LOG File
				log	= self.readLOG()
			
				self.oLOG =	os.path.join(self.outputFolder[0], os.path.split(self.iCFG)[1].replace('.cfg','_congruency_extracted.tsv'))
			
				if os.path.exists(self.oLOG):
					print 'File: '	+ self.oLOG	+ '	already	exists'
					continue
			
			
				if cfg['subject'] in oldVersionCongruency:
					correctAnswers	= self.readDesignAndSaveSPSS_oldVersion(cfg['design'], log,	cfg['congruency'])
					print self.iLOG + ' has been successfully converted'					 
				elif cfg['subject']	in oldCongruency:
					correctAnswers	= self.readDesignAndSaveTSV(cfg['design'], log,	cfg['congruency'])
					print self.iLOG + ' has been successfully converted'					 
				else:
					correctAnswers	= self.readDesignAndSaveTSV(cfg['design'], log,	cfg['congruency'], True)
					print self.iLOG + ' has been successfully converted'
				
	def extractLOG(self, iData):
		#	return np.array(nBlock,	Rt,	Answer(int), Answer(Side)) 
		lastInput	= 'dummy'
	
		outputList = []
	
		right	= 2
		left = [1, 4]
	
		allData =	[x.strip() for x in	iData]	
		for currData in allData:
			currData	= currData.split('\t')
			currTimer = float(currData[0])
			currInput = currData[1]
		
			if 'StartPerformance' in	currData[1]:
				nBlock = int(currData[2])
			
			elif	'DATA' in currData[1]:
				if 'DisplayTarget' in lastInput:
					if	int(currData[2].split()[1])	in left:
						outputList.append([nBlock, currTimer-lastTimer, int(currData[2].split()[1]), 'Left'])
					elif int(currData[2].split()[1])==right:				 
						outputList.append([nBlock, currTimer-lastTimer, int(currData[2].split()[1]), 'Right'])

			lastInput = currInput 
			lastTimer = currTimer
		
		output = np.asarray(outputList)

		return output

	def readLOG(self):
		if self.verbose:
			print 'Read log file	' +	self.iLOG
		with open(self.iLOG, 'r')	as f:
			data	= f.readlines()
		
		return self.extractLOG(data)

	def readCFG(self):
		if self.verbose:
			print 'Reading config file: ' + self.iCFG	
		with open(self.iCFG,'r') as f:
			data	= f.readlines()
		
		data = data[0]
		data = data.replace('true','"True"')
		data = data.replace('false','"False"')

		data = eval(data)
	
		return data

	def readDesignAndSaveSPSS_oldVersion(self,	iDesign, iLog, iRule):
		
		print	'Read design ' + iDesign  
		
		oSPSS = open(self.oLOG, 'w')
		oSPSS.write('NBlock\tSide\tColor\tExpectedAnswer\tAnswer\tRT\tCog\n')
	
		right	= 2
		left = 4
	
		outputList = []
	
		with open(iDesign, 'r') as f:
			data	= f.readlines()
	
		nBlock = 0
	
		nKey = -1
	
		for currData in data:
			currData	= [int(n) for n	in currData.split()]
		
			if 'yellow' in iRule and	currData[0]!=8:
				nKey +=	1
				if currData[1]==0: # Yellow
					if	currData[0]==0:	# LEFT
						outputList.append([nBlock, left])
						oSPSS.write(str(nBlock) +	'\tLeft\tYellow\tLeft\t' + iLog[nKey,3]	+ '\t' + str(iLog[nKey,1]) + '\tyellow\n')
					else:
						outputList.append([nBlock, right])
						oSPSS.write(str(nBlock) +	'\tRight\tYellow\tRight\t' + iLog[nKey,3] +	'\t' + str(iLog[nKey,1]) + '\tyellow\n')
				if currData[1]==1: # BLUE
					if	currData[0]==0:	# LEFT
						outputList.append([nBlock, right])
						oSPSS.write(str(nBlock) +	'\tLeft\tBlue\tRight\t'	+ iLog[nKey,3] + '\t' +	str(iLog[nKey,1]) +	'\tyellow\n')
					else:
						outputList.append([nBlock, left])
						oSPSS.write(str(nBlock) +	'\tRight\tBlue\tLeft\t'	+ iLog[nKey,3] + '\t' +	str(iLog[nKey,1]) +	'\tyellow\n')

			elif	'blue' in iRule	and	currData[0]!=8:
				nKey +=	1
				if currData[1]==0: # Yellow
					if	currData[0]==0:	# LEFT
						outputList.append([nBlock, right])
						oSPSS.write(str(nBlock) +	'\tLeft\tYellow\tRight\t' +	iLog[nKey,3] + '\t'	+ str(iLog[nKey,1])	+ '\tblue\n')
					else:
						outputList.append([nBlock, left])
						oSPSS.write(str(nBlock) +	'\tRight\tYellow\tLeft\t' +	iLog[nKey,3] + '\t'	+ str(iLog[nKey,1])	+ '\tblue\n')					   
				if currData[1]==1: # BLUE
					if	currData[0]==0:	# LEFT
						outputList.append([nBlock, left])
						oSPSS.write(str(nBlock) +	'\tLeft\tBlue\tLeft\t' + iLog[nKey,3] +	'\t' + str(iLog[nKey,1]) + '\tblue\n')
					else:
						outputList.append([nBlock, right])			
						oSPSS.write(str(nBlock) +	'\tRight\tBlue\tRight\t' + iLog[nKey,3]	+ '\t' + str(iLog[nKey,1]) + '\tblue\n')
				  
			elif	currData[0]==8:
				nBlock +=1
			
		output = np.asarray(outputList)

		return output
	
	def readDesignAndSaveTSV(self,	iDesign, iLog, iRule, newVersion = False):
		
		#	return np.array(NBlock,	Expected Answer)
		if self.verbose:
			print 'Read design: '  +	iDesign
	
		oTSV = open(self.oLOG, 'w')
		oTSV.write('NBlock\tSide\tColor\tExpectedAnswer\tAnswer\tRT\tCog\n')
	
		right	= 2
		left = 1
	
		outputList = []
	
		with open(iDesign, 'r') as f:
			data	= f.readlines()
	
		nBlock = 0
		nKey = -1
	
		currRule = iRule
	
		if 'yellow' in iRule:
			iRule = ['Yellow','Blue']
		else:
			iRule = ['Blue','Yellow']
		
		for currData in data:
			currData	= [int(n) for n	in currData.split()]

			if newVersion and 'blue'	in currRule	and	currData[0]!=8:
				currData[0]	= np.abs(currData[0]-1)
		
			if currData[0]!=8:
				nKey = nKey	+ 1
				if currData[1]==0: # Yellow
					if	currData[0]==0:	# LEFT
						outputList.append([nBlock, left])
						oTSV.write(str(nBlock) + '\tLeft\t'+ iRule[0] +	'\tLeft\t' + iLog[nKey,3] +	'\t' + str(iLog[nKey,1]) + '\t' + currRule + '\n')
					else:
						outputList.append([nBlock, right])
						oTSV.write(str(nBlock) + '\tRight\t'+ iRule[0] + '\tRight\t' + iLog[nKey,3]	+ '\t' + str(iLog[nKey,1]) + '\t' + currRule + '\n')
				if currData[1]==1: # BLUE
					if	currData[0]==0:	# LEFT
						outputList.append([nBlock, right])
						oTSV.write(str(nBlock) + '\tLeft\t'	+ iRule[1] + '\tRight\t' + iLog[nKey,3]	+ '\t' + str(iLog[nKey,1]) + '\t' + currRule + '\n')
					else:
						outputList.append([nBlock, left])
						oTSV.write(str(nBlock) + '\tRight\t' + iRule[1]	+ '\tLeft\t' + iLog[nKey,3]	+ '\t' + str(iLog[nKey,1]) + '\t' + currRule + '\n')

			elif	currData[0]==8:
				nBlock +=1
			
		output = np.asarray(outputList)			

		return output
	
def	main():
	"""Let's go"""
	args =	get_arguments()
	app = convertCongruency(**vars(args))
	return	app.run()

if __name__	== '__main__':
	sys.exit(main())