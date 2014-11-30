import re
import os
import argparse

# create an argument parser to take commandline arguments (e.g. target filename)
arg_parser = argparse.ArgumentParser(description="Markdown file to be processed into Gitbook format")
arg_parser.add_argument("filename")

args = arg_parser.parse_args()


chapterHeading = re.compile("={5}.*")
sectionHeading = re.compile("-{7}.*")

# e.g. load the file passed in from the command line
targetFile = args.filename


sourceText = open(targetFile, "rU")

lastlineHolder = ""

currentChapter = ""

textBuffer = []

for line in sourceText:
	if chapterHeading.match(line) or sectionHeading.match(line):
		print "hit delimiter"
		print line
		#e.g. if we've hit a chapter heading
		if(textBuffer):
			# this means we're not at the start of the file

			# whether we've got a chapter or a section, we need to create the "title" element
			# remove digits and punctuation from chapter/section title, make it lowercase and split it on spaces
			titleArray = re.sub('[!@#$&.:1234567890,]', '',textBuffer[0]).lower().split()
			# join the first four "words" of the title together with underscores
			titleText = "_".join(titleArray[0:3])

			# now, we need to check if this is going to be a directory or not
			if chapterHeading.match(line):
				if sectionHeading.match(textBuffer[1]):
					# what came before was just a section, so create another file
					myOutput = open(currentChapter+"/"+titleText+".md", "w")
					myOutput.writelines(textBuffer)
					myOutput.close()
					#empty the buffer
					textBuffer = []					
				else:
					# create the directory (should update this to skip if exists)
					if not os.path.exists(titleText):
						os.makedirs(titleText)
					#write the outputfile from the buffer
					myOutput = open(titleText+"/README.md", "w")
					myOutput.writelines(textBuffer)
					myOutput.close()

					#set currentChapter to titleText, so we know where to place sections (if they exist)
					currentChapter = titleText
					#empty the buffer
					textBuffer = []
			if sectionHeading.match(line):
				if chapterHeading.match(textBuffer[1]):
					# e.g. if what came before was in fact a chapter heading
					# then reset the chapter title do all the things we do if all that came before was an entire chapter
					
					chapterArray = re.sub('[!@#$&.:1234567890,]', '',textBuffer[0]).lower().split()
					chapterTitle = "_".join(titleArray[0:3])

					if not os.path.exists(chapterTitle):
						os.makedirs(chapterTitle)
					#write the outputfile from the buffer
					myOutput = open(chapterTitle+"/README.md", "w")
					myOutput.writelines(textBuffer)
					myOutput.close()

					#set currentChapter to titleText, so we know where to place sections (if they exist)
					currentChapter = chapterTitle
					#empty the buffer
					textBuffer = []
				else:
					# otherwise, what came before was just a section, so create another file
					myOutput = open(currentChapter+"/"+titleText+".md", "w")
					myOutput.writelines(textBuffer)
					myOutput.close()
					#empty the buffer
					textBuffer = []

	if(lastlineHolder):
		textBuffer.append(lastlineHolder)
	
	lastlineHolder = line


sourceText.close()


                             
    