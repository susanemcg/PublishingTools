import re
import os
import argparse


def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="html file to have chapter headings extracted")
	arg_parser.add_argument("filename")

	args = arg_parser.parse_args()


	chapterHeading = re.compile("(<h1 id=\")(.*)(\">)(.*)(</h1>)")

	# e.g. load the file passed in from the command line
	targetFile = args.filename
	print "hi"

	# strip the file extension from the target file to create target folder
	outputFileName = targetFile[:-5]+"_rr.html"

	revisedOutputFile = targetFile[:-5]+"_web.html"

	print outputFileName

	sourceStream = open(targetFile, "rU")
	sourceText = sourceStream.readlines()
	myOutput = open(outputFileName, "w")
	revisedOutput = open(revisedOutputFile, "w")

	lastlineHolder = ""

	for line in sourceText:

		# if we're at a chapter break, write the appropriate link to the right rail file
		if chapterHeading.match(line):

			headline_match = chapterHeading.match(line)

			right_rail_line = '<a href="#'+headline_match.group(2)+'">'+headline_match.group(4)+'</a><br/>' 
			myOutput.write(right_rail_line)

			# however! also write a special anchor tag to the _web content file, and 
			# remove the anchor tag from the original header

			anchor_span = '<span id="'+headline_match.group(2)+'" class="anchor"></span><br/>'
			new_header = '<h1>'+headline_match.group(4)+'</h1><br/>'

			revisedOutput.write(anchor_span)
			revisedOutput.write(new_header)

		else:
			revisedOutput.write(line)
		
		lastlineHolder = line


	sourceStream.close()
	myOutput.close()


main()          
    
