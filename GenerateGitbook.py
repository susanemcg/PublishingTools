import re
import os
import argparse

# create an argument parser to take commandline arguments (e.g. target filename)
arg_parser = argparse.ArgumentParser(description="Markdown file to be processed into Gitbook format")
arg_parser.add_argument("filename")

args = arg_parser.parse_args()


chapterHeading = re.compile("={5}.*")

# e.g. load the file passed in from the command line
targetFile = args.filename


sourceText = open(targetFile, "rU")

lastlineHolder = ""

chapterBuffer = []

for line in sourceText:
	if chapterHeading.match(line):
		#e.g. if we've hit a chapter heading
		if(chapterBuffer):
			# this means we're not at the start of the file, so create the folder 
			# remove digits and punctuation from chapter title, make it lowercase and split it on spaces
			outputFolderArray = re.sub('[!@#$&.:1234567890,]', '',chapterBuffer[0]).lower().split()
			# join the first four "words" of the title together with underscores
			outputFolderTitle = "_".join(outputFolderArray[0:3])
			# create the directory (should update this to skip if exists)
			if not os.path.exists(outputFolderTitle):
				os.makedirs(outputFolderTitle)
			#write the outputfile from the buffer
			myOutput = open(outputFolderTitle+"/README.md", "w")
			myOutput.writelines(chapterBuffer)
			myOutput.close()

			#empty the buffer, but then add the previous line (e.g. the next chapter's title)
			chapterBuffer = []
	if(lastlineHolder):
		chapterBuffer.append(lastlineHolder)
	
	lastlineHolder = line


sourceText.close()


                             
    