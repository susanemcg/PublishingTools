import re
import os
import argparse
from roman import toRoman

citation_counter = 1

def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="Markdown file to be processed into Gitbook format")
	arg_parser.add_argument("filename")
	arg_parser.add_argument("-footnotes_title")
	arg_parser.add_argument("-footnotes_roman")
	arg_parser.add_argument("-citations_title")


	args = arg_parser.parse_args()

	# right now this only matches chapter headings denoted by 5 equals signs and section headings by 5 dashes
	# other formats for these could optionally be added, if other markdown sources are used
	chapterHeading = re.compile("={5}.*")
	sectionHeading = re.compile("-{5}.*")

	footnote_title = "endnotes"
	if args.footnotes_title:
		footnote_title = args.footnotes_title

	citations_title = "citations"
	if args.citations_title:
		citations_title = args.citations_title

	footnotes_roman = "False"
	if args.footnotes_roman:
		footnotes_roman = "True"

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

	footnote_prepend = ""

	currentChapter = ""

	textBuffer = []

	isFirst = True

	for line_num, line in enumerate(sourceText):
		#print line_num

		# if we're at a chapter or section break or at the end of the file AND we've got something in the buffer!
		if (chapterHeading.match(line) or sectionHeading.match(line) or line_num == num_lines-1) and textBuffer:

			# whether we've got a chapter or a section, we need to create the "title" element
			wholeTitle = textBuffer[0].rstrip() # remove trailing whitespace
			
			# this deals with the way LaTeX will output titles that have been 
			# blocked from the TOC
			title_adds = re.compile("(.*?)({.*?})")
			title_matchObj = title_adds.match(wholeTitle)
			if(title_matchObj):
				wholeTitle = title_matchObj.group(1)


			titleText = formatTitle(wholeTitle)

			# if we are indeed at the last line of the file, we need to push it to the buffer *before* processing 
			if line_num == num_lines-1:
				textBuffer.append(lastlineHolder)

			# if what's in the buffer starts a chapter, create a directory UNLESS it is the first
			if chapterHeading.match(textBuffer[1]) and not isFirst:
				# what's in the buffer is the start of a chapter; make a folder

				# create the directory (should update this to skip if exists)
				if not os.path.exists(folderName+"/"+titleText):
					os.makedirs(folderName+"/"+titleText)
				#write the outputfile from the buffer
				myOutput = open(folderName+"/"+titleText+"/README.md", "w")

				# write this folder info to summary file; note that link is relative to position of SUMMARY file, NOT python file
				# we use the raw title text from the buffer as the link text

				summaryFile.write("* ["+wholeTitle+"]("+titleText+"/README.md)\n")

				# set currentChapter to titleText, so we know where to place sections (if they exist)
				currentChapter = titleText

				# set "footnote_prepend" to ../, because we only have to go up one directory to properly
				# reference the endnotes folder
				directory_prepend = "../"

			else:
				# what's in the buffer is a section, make a file

				# if this is the first chapter/section, make it the main "README" file
				if isFirst:
					myOutput = open(folderName+"/README.md", "w")
					isFirst = False

					# we're at the top level, no footnote_prepend at all
					directory_prepend = ""
				else:
					myOutput = open(folderName+"/"+currentChapter+"/"+titleText+".md", "w")

					# add section path to summary file
					# we use the raw title text from the buffer as the link text 
					summaryFile.write("\t* ["+wholeTitle+"]("+currentChapter+"/"+titleText+".md)\n")	

					# we're in a section, we'll need to go up one level to reference endnotes
					directory_prepend = "../"

			# whatever file we're writing to, write to it & empty the buffer
			# we need to handle footnotes here, so that we know where we are in the file structure
			corrected_buffer = fix_media(textBuffer, directory_prepend, footnotes_roman, footnote_title, citations_title)

			myOutput.writelines(corrected_buffer)
			myOutput.close()
			#empty the buffer
			textBuffer = []

		if(lastlineHolder):
			textBuffer.append(lastlineHolder)
		
		lastlineHolder = line


	sourceStream.close()
	summaryFile.close()



def fix_media(textBufferArray, directory_prepend, footnotes_roman, footnote_title, citations_title):

	text_holder = []

	footnote_format = re.compile("(.*)(\[\^)(\d+)(\])(.*)")

	citation_format = re.compile("(.*)(\[@ref)(\d+)(\])(.*)")

	graphics_link = re.compile("(!\[.*?\])(\(graphics)(.*?\))")

	for line in textBufferArray:

		if footnote_format.match(line):
			# instead of rewriting in a separate function, just get the match object and use it here
			footnote_matchObj = footnote_format.match(line)
			theNumber = footnote_matchObj.group(3)
			if footnotes_roman == "True":
				theNumber = toRoman(int(footnote_matchObj.group(3)))
			line = footnote_matchObj.group(1)+"<sup>["+theNumber+"]("+directory_prepend+footnote_title+"/README.html)</sup>"

		if citation_format.match(line):
				# instead of rewriting in a separate function, just get the match object and use it here
				# HACK: THIS EXPECTS @ REFERENCES TO CONTAIN THE CORRECT CITATION NUMBER (e.g. "ref27")
				citation_matchObj = citation_format.match(line)
				line = citation_matchObj.group(1)+"<sup>["+citation_matchObj.group(3)+"]("+directory_prepend+citations_title+"/README.html)</sup>"

		if graphics_link.match(line):
			# instead of rewriting in a separate function, just get the match object and use it here
			#print(line)
			graphics_matchObj = graphics_link.match(line)
			line = graphics_matchObj.group(1)+"("+directory_prepend+"graphics"+graphics_matchObj.group(3)

		# while we're at it, we might as well get real newlines into our footnote sections
		line = re.sub(r"\\\n", "\n\n", line)

		text_holder.append(line)

	return text_holder


def formatTitle(aLine):
	# remove digits and punctuation from chapter/section title, make it lowercase and split it on spaces
	theTitleArray = re.sub('[\'*!@#$&.:1234567890,]', '',aLine).lower().split()

	# join the first four "words" of the title together with underscores
	theTitle = "_".join(theTitleArray[0:3])

	return theTitle  


main()          
    
