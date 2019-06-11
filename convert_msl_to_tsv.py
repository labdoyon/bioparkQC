#!/usr/bin/env python
# -*- coding: utf-8	-*-
# Convert MSL task

import os, sys,	argparse, json,	re
import scipy.io	as scio
import numpy as	np
from utils import listFiles
import matplotlib.pyplot as	plt
from matplotlib.backends.backend_pdf import	PdfPages
import matplotlib.gridspec as gridspec

def	get_arguments():
	parser	= argparse.ArgumentParser(
			formatter_class=argparse.RawDescriptionHelpFormatter,
			description="",
			epilog="""
			Convert MSL raw data	to MAT file
			
			Input:  .cfg	files
			
			Although	no arguments is	mandatory there	is an order, if	case 1 then	it won't do	case 2 or 3	and	so on
			1. dataset Folder
			2. subject Folder
			3. single File
			""")

	parser.add_argument(
			"-s", "--singleFile",
			required=False, nargs="+",
			help="Multiple single files can be use as an	input: convert_msl_matlab.py -s	file1.cfg file2.cfg",
			)
	
	parser.add_argument(
			"-d", "--dataset",
			required=False, nargs="+",
			help="dataset folder",
			)
	
	parser.add_argument(
			"-f", "--subjectFolder",
			required=False, nargs="+",
			help="Multiple subjects folders can be use as an	input: convert_msl_matlab.py -d	folder1	folder2",
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
	
	
class convertMSL(object):
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
		self.iLOG	= ''
		self.iCDG	= ''
		self.subject = ''
		self.sequence	= ''

	def run(self):
		allCFGFiles =	[]
		if self.dataset:
			allCFGFiles = listFiles(self.dataset[0],	allCFGFiles, '.cfg')
		elif self.subjectFolder:
			for currFolders in self.subjectFolder:
				allCFGFiles	= listFiles(currFolders, allCFGFiles, '.cfg')
		elif self.singleFile:
			allCFGFiles = self.singleFile

		#	Valid if log exists	and	within the right folder
		allCFGFiles =	[x for x in	allCFGFiles	if ('MSL' in x and 'task' in x and os.path.exists(x.replace('cfg','log')))]
		
		allCFGFiles.sort(reverse=False)
		
		if not allCFGFiles:
			print 'No file were found'
		else:
			for currCFGFile in allCFGFiles:
				self.iCFG =	currCFGFile
				self.iLOG =	currCFGFile.replace('cfg','log')
				
				cfg	= self.extractCFG()

				if self.verbose:
					print cfg['subject']
				
				self.oLOG =	os.path.join(self.outputFolder[0], self.subject	+ '_msl_' +	self.hand +	'.tsv')
				
				self.initOutput()
				
				self.extractDataAndSaveTSV()
				self.run_basicAnalysis()
                
				print self.iCFG	+ ' has been converted successfully'

	def extractCFG(self):
		#load	json file
		cfg =	json.loads(open(self.iCFG).read())

		#Remove u	before field (unicode)
		cfg =	dict([(str(k),v) for k,v in	cfg.items()])
				
		self.subject = cfg['subject']
		self.hand	= cfg['hand']
		self.sequence	= cfg['seq']
		
		return cfg				

	def initOutput(self):
		if os.path.exists(self.oLOG):
			'Output file	'+ os.path.split(self.oLOG)[1] + ' already exists and will be overwritten'
			
		oTSV = open(self.oLOG, 'w')
		oTSV.write('Subject_code\tHand\tNBlock\tKey\tRT\n')

	def extractDataAndSaveTSV(self):

		#Conversion of some fields
		seq =	[]
		for i in self.sequence.split(' - '):
			seq.append(int(i))

		self.sequence = np.asarray(seq)
		nBlock = 0

		#	Load data file
		log =	open(self.iLOG,	'r')
		num_lines	= sum(1	for	line in	open(self.iLOG,'r'))
		notRecord	= True
		for line in log: 
			val = line.split()
			val[0] =	float(val[0])
			
			if val[1] in	'StartExp':
				notRecord =	True

			elif val[1] in 'StartRest':
				notRecord =	True

			elif val[1] in 'StartPerformance':
				lastTime = val[0]
				nBlock = nBlock	+ 1
				notRecord =	False
			
			elif	val[1] in 'DATA' and not notRecord:
				if not val[3] in '5':
					tmpObj	= np.zeros((3,), dtype=np.object)
					tmpObj[0] = nBlock
					tmpObj[1] = val[3]	
					tmpObj[2] = val[0]-lastTime
					lastTime =	val[0]
					with open(self.oLOG, 'a') as f:
						f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
							self.subject,
							self.hand,
							tmpObj[0],
							tmpObj[1],
							tmpObj[2]))

	def run_basicAnalysis(self):
		"""
		Extract values/metrics and save everything within a pdf file
		4 graphs will be output to assess the QC of the data
		
		1- Block duration
		2- Average correct sequence duration with std
		3- Correct sequences per block
		"""
		
		# Load oLOG previously saved
		data = np.loadtxt(self.oLOG,skiprows=True,usecols=(2,3,4))
		maxNBlock	= np.max(data[:,0])
		
		# Output metric
		metrics = dict()
		"""
		AllRTs : 
		"""
		metrics['allRTs'] = np.zeros((480,2))

		"""
		Blocks duration : 
		"""
		metrics['blocksDur'] = np.zeros((int(maxNBlock),1))	
		
		"""
		correctSequences : 
		"""		
		metrics['correctSequences'] = np.zeros((int(maxNBlock),2))

		"""
		nCorrectSequences : 
		"""		
		metrics['nCorrectSequences'] = np.zeros((int(maxNBlock),1))
		
		"""
		interKeysInterval : 
		"""		
		metrics['interkeysInterval'] = np.zeros((int(maxNBlock),5,2))
		
		# Convert sequence easier to get substring and so on
		sequenceString = np.array2string(self.sequence)[1:-1].replace('\n','').replace('.','').replace(' ','')
		
		# Definition of the perfect "string" version of a block
		perfectBlock = (self.sequence * ((data[np.where(data[:,0]==1)].shape[0]/len(self.sequence))+1))[:data[np.where(data[:,0]==1)].shape[0]]
		
		# Creation of the figure
		fig =	plt.figure()
		spec = gridspec.GridSpec(ncols=2, nrows=2)
		
		for idx, nBlock in enumerate(range(1,int(maxNBlock)+1)):
			
			#print nBlock
			
			currData	= data[np.where(data[:,0]==nBlock)]
			
			metrics['blocksDur'][nBlock-1] = np.sum(currData[:,2])
			
			tmpData = currData.copy()

			keysString = np.array2string(tmpData[:,1])[1:-1].replace('\n','').replace('.','').replace(' ','')
			
			if keysString == perfectBlock:
				print 'Perfect block'
			
			# Number of correct sequences
			metrics['nCorrectSequences'][nBlock-1] = keysString.count(sequenceString)*100/(currData.shape[0]/len(sequenceString))
			
			
			# Indexes of	all	sequence
			sequenceIndexes = [m.start() for m in re.finditer(sequenceString, keysString)]
			
			# Validate Indexes
			currMetricRTs = []
			for index in sequenceIndexes:
				currMetricRTs.append(np.sum(currData[index:index+self.sequence.shape[0],2]))
			
			# Metric AVERAGE
			metrics['correctSequences'][nBlock-1,0] = np.average(np.asarray(currMetricRTs))
			# Metric STD
			metrics['correctSequences'][nBlock-1,1] = np.std(np.asarray(currMetricRTs))

			# RTs
			metrics['allRTs'][range(70*idx, 70*idx+currData.shape[0]),	1] = data[np.where(data[:,0]==nBlock), 2]
			# Indexes 1->60,	70->130, etc...
			metrics['allRTs'][range(70*idx, 70*idx+currData.shape[0]),	0] = range(1+70*idx, 1+70*idx+currData.shape[0])
			
			# PLOT	
			#axis1 = fig.add_subplot(211)
			#axis1.plot(range(1+70*idx, 1+70*idx+currData.shape[0]), currData[:,2], 'r--')
			#axis1.set_title('Histogram of IQ')
			
			
		# All Plots
		
		'''
		Correct sequences
		'''
		axis1 = fig.add_subplot(spec[1,:])
		axis1.plot(range(1,int(maxNBlock+1)),metrics['nCorrectSequences'],'o')
		axis1.set_ylim(0,120)
		axis1.set_xlim(0,int(maxNBlock+1))
		axis1.set_xlabel('Number of blocks')
		axis1.set_ylabel('Percentage of \ncorrect sequences')
		axis1.set_yticks(np.arange(0, 120, 20))
		axis1.grid()
		axis1.grid(alpha=0.2)
		
		'''
		Correct average sequence duration
		'''
		axis2 = fig.add_subplot(spec[0,1])
		axis2.errorbar(range(1,int(maxNBlock+1)), metrics['correctSequences'][:,0], metrics['correctSequences'][:,1], linestyle='None', marker='+')			   
		axis2.set_ylabel('Correct average\nsequence duration (s)', fontsize = 10.0)
		axis2.set_xlim(0,int(maxNBlock+2))
		axis2.set_ylim(np.min(metrics['correctSequences'][:,0])-np.max(metrics['correctSequences'][:,1]),np.max(metrics['correctSequences'][:,0])+np.max(metrics['correctSequences'][:,1]))
		axis2.set_xlabel('Number of blocks')
		axis2.grid(alpha=0.2)
		
		'''
		Block duration
		'''
		axis3 = fig.add_subplot(spec[0,0])
		axis3.plot(range(1,int(maxNBlock+1)),metrics['blocksDur'],'o')		
		axis3.grid()
		axis3.grid(alpha=0.2)
		axis3.set_ylabel('Block Duration (s)')
		axis3.set_xlabel('Number of blocks')
		axis3.set_ylim(np.min(metrics['blocksDur'])-np.std(metrics['blocksDur']), np.max(metrics['blocksDur'])+np.std(metrics['blocksDur']))
		axis3.set_xlim(0,int(maxNBlock+2))
		
		
		
		fig.suptitle("MSL - " + self.subject + ' - ' + self.hand + ' hand')
		
		fig.tight_layout()
		fig.subplots_adjust(top=0.88)
		
		with PdfPages(self.oLOG.replace('.tsv','_qc.pdf')) as pdf:
			pdf.savefig(fig)

def	main():
	"""Let's go"""
	args =	get_arguments()
	app = convertMSL(**vars(args))
	return	app.run()

if __name__	== '__main__':
	sys.exit(main())	