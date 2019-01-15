import os 
import sys

def	listFiles(rootFolder, allFiles=[], iFilter=None):
	for path, subdirs,	files in os.walk(rootFolder):
		for name in files:
			try:
				if iFilter in name and not 'edited'	in name	and	not	'notusefull' in	path.lower():
					allFiles.append(os.path.join(path,	name))
			except:
				continue

	return	allFiles

oldVersionCongruency = ['BioPark_026',
			   'BioPark_040',
			   'BioPark_042',
			   'BioPark_061',
			   'BioPark_062',
			   'BioPark_075',
			   'BioPark_085',
			   'BioPark_094',
			   'BioPark_102',
			   'BioPark_161',
			   'BioPark_165',
			   'BioPark_167',
			   'BioPark_175',
			   'BioPark_176',
			   'BioPark_177',
			   'BioPark_182',
			   'BioPark_191',
			   'BioPark_192',
			   'BioPark_198',
			   'BioPark_199',
			   'BioPark_200',
			   'BioPark_203',
			   'BioPark_207',
			   'BioPark_208',
			   'BioPark_209',
			   'BioPark_211',
			   'BioPark_214',
			   'BioPark_221',
			   'BioPark_224',
			   'BioPark_225',
			   'BioPark_231',
			   'BioPark_232',
			   'BioPark_238',
			   'BioPark_240',
			   'BioPark_246',
			   'BioPark_252',
			   'BioPark_257',
			   'BioPark_262',
			   'BioPark_263',
			   'BioPark_269']
			   
oldCongruency =	['BioPark_059',
			   'BioPark_230',
			   'BioPark_236',
			   'BioPark_242',
			   'BioPark_249',
			   'BioPark_250',
			   'BioPark_251',
			   'BioPark_255',
			   'BioPark_258',
			   'BioPark_300',
			   'BioPark_265',
			   'BioPark_272',
			   'BioPark_276',
			   'BioPark_277',
			   'BioPark_278',
			   'BioPark_281',
			   'BioPark_282',
			   'BioPark_287',
			   'BioPark_289',
			   'BioPark_290',
			   'BioPark_297',
			   'BioPark_299',
			   'BioPark_300',
			   'BioPark_303',
			   'BioPark_305',
			   'BioPark_306',
			   'BioPark_309',
			   'BioPark_312',
			   'BioPark_313',
			   'BioPark_317',
			   'BioPark_327',
			   'BioPark_328',
			   'BioPark_329',
			   'BioPark_330',
			   'BioPark_333',
			   'BioPark_336',
			   'BioPark_338']


oldVersionArrow = ['biopark_042',
                   'biopark_061',
                   'biopark_062',
                   'biopark_165',
                   'biopark_167',
                   'biopark_176',
                   'biopark_182',
                   'biopark_191']