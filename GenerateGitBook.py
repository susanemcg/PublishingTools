import re
import os
import argparse


def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="Markdown file to be processed into Gitbook format")
	arg_parser.add_argument("filename")

	args = arg_parser.parse_args()


	chapterHeading = re.compile("={5}.*")
	sectionHeading = re.compile("-{5}.*")

	# e.g. load the file passed in from the command line
	targetFile = args.filename

	# strip the file extension from the target file to create target folder
	folderName = targetFile[:-3]

	# create a folder w/the filename to put files into
	if not os.path.exists(folderName):
		os.makedirs(folderName)

	# create summary file, which will be used by Gitbook to generate the table of contents/links
	summaryFile = open(folderName+"/SUMMARY.md", "w")
	summaryFile.write("# Summary\n\n")

	sourceStream = open(targetFile, "rU")
	sourceText = sourceStream.readlines()
	num_lines = len(sourceText)

	lastlineHolder = ""

	currentChapter = ""

	chapterCounter = 1
	sectionCounter = 1

	textBuffer = []

	isFirst = True

	for line_num, line in enumerate(sourceText):
		#print line_num

		# if we're at a chapter or section break or at the end of the file AND we've got something in the buffer!
		if (chapterHeading.match(line) or sectionHeading.match(line) or line_num == num_lines-1) and textBuffer:

			# whether we've got a chapter or a section, we need to create the "title" element
			titleText = formatTitle(textBuffer[0])

			# if we are indeed at the last line of the file, we need to push it to the buffer *before* processing 
			if line_num == num_lines-1:
				textBuffer.append(lastlineHolder)

			# if what's in the buffer starts a chapter, create a directory UNLESS it is the first
			if chapterHeading.match(textBuffer[1]) and not isFirst:
				# what's in the buffer is the start of a chapter; make a folder
				# first, prepend the current chapterCounter, so we know what order the finished folders go in
				#titleText = str(chapterCounter)+"_"+titleText

				# create the directory (should update this to skip if exists)
				if not os.path.exists(folderName+"/"+titleText):
					os.makedirs(folderName+"/"+titleText)
				#write the outputfile from the buffer
				myOutput = open(folderName+"/"+titleText+"/README.md", "w")

				# write this folder info to summary file; note that link is relative to position of SUMMARY file, NOT python file
				# we use the raw title text from the buffer as the link text
				summaryFile.write("* ["+textBuffer[0].rstrip()+"]("+titleText+"/README.md)\n")

				#set currentChapter to titleText, so we know where to place sections (if they exist)
				currentChapter = titleText

				#increment chapterCounter, reset the section counter
				chapterCounter+=1;
				sectionCounter = 1;

			else:
				# what's in the buffer is a section, make a file
				# prepend the title with sectionCounter
				#titleText = str(sectionCounter)+"_"+titleText

				# if this is the first chapter/section, make it the main "README" file
				if isFirst:
					myOutput = open(folderName+"/README.md", "w")
					isFirst = False
				else:
					myOutput = open(folderName+"/"+currentChapter+"/"+titleText+".md", "w")

					# add section path to summary file
					# we use the raw title text from the buffer as the link text 
					summaryFile.write("\t* ["+textBuffer[0].rstrip()+"]("+currentChapter+"/"+titleText+".md)\n")	

				sectionCounter+=1;

			# whatever file we're writing to, write to it & empty the buffer				
			myOutput.writelines(textBuffer)
			myOutput.close()
			#empty the buffer
			textBuffer = []

		if(lastlineHolder):
			# convert md superscript ^...^ carrots to html <sup>...</sup> tags
			lastlineHolder = re.sub(r"\^\[", "<sup>[", lastlineHolder)
			lastlineHolder = re.sub(r"\)\^", ")</sup>", lastlineHolder)
			textBuffer.append(lastlineHolder)
		
		lastlineHolder = line


	sourceStream.close()
	summaryFile.close()


def formatTitle(aLine):
	# remove digits and punctuation from chapter/section title, make it lowercase and split it on spaces
	theTitleArray = re.sub('[!@#$&.:1234567890,]', '',aLine).lower().split()
	# join the first four "words" of the title together with underscores
	theTitle = "_".join(theTitleArray[0:3])
	return theTitle   


main()          
    
