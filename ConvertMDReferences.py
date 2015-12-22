import re
import os
import argparse
from roman import toRoman

#because I am lazy

citation_counter = 1

def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="MD file to be corrected for endnote citations")
	arg_parser.add_argument("filename")


	args = arg_parser.parse_args()


	citations_title = "citations"


	# e.g. load the file passed in from the command line
	targetFile = args.filename

	file_leader = targetFile[:-5]

	myOutput = open(file_leader+"_fixed.md", "w")
	
	sourceStream = open(targetFile, "rU")
	sourceText = sourceStream.readlines()
	num_lines = len(sourceText)


	for line_num, line in enumerate(sourceText):
	
			corrected_buffer = fix_media(line, citations_title)

			myOutput.writelines(corrected_buffer)
			

	myOutput.close()
	sourceStream.close()



def fix_media(text_line, citations_title):

	line = text_line

#	footnote_format = re.compile("(.*?)(\[\^)(\d+)(\])(.*?)")
#	if footnotes_roman == "True":
#		footnote_format = re.compile("(.*?)(\[\^)(\w+)(\])(.*?)")

	citation_format = re.compile("(.*?)(\[@)(\w+)(\])(.*?)")

	#print "hi"
	#print citation_counter

	if citation_format.match(line):
		# instead of rewriting in a separate function, just get the match object and use it here
		citation_iter = citation_format.finditer(line)
		new_holder = []
		for match in citation_iter:
			line_frag = match.group(1)+"<sup><a href=#"+citations_title+">"+str(citation_counter)+"</a></sup>"
			new_holder.append(line_frag)
			global citation_counter
			citation_counter+=1
		new_holder.append(line[match.end():])
		line = "".join(new_holder)

	return line


main()          
    
