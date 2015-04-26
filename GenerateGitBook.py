import re
import os
import argparse



def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="Markdown file to be processed into Gitbook format")
	arg_parser.add_argument("filename")

	args = arg_parser.parse_args()

	# right now this only matches chapter headings denoted by 5 equals signs and section headings by 5 dashes
	# other formats for these could optionally be added, if other markdown sources are used
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

	footnote_prepend = ""

	currentChapter = ""

	textBuffer = []

	isFirst = True

	for line_num, line in enumerate(sourceText):
		#print line_num

		# if we're at a chapter or section break or at the end of the file AND we've got something in the buffer!
		if (chapterHeading.match(line) or sectionHeading.match(line) or line_num == num_lines-1) and textBuffer:

			# whether we've got a chapter or a section, we need to create the "title" element
			wholeTitle = textBuffer[0].rstrip()
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
			revised_buffer = fix_footnotes(textBuffer, directory_prepend)
			graphics_revised_buffer = fix_image_links(revised_buffer, directory_prepend)

			myOutput.writelines(graphics_revised_buffer)
			myOutput.close()
			#empty the buffer
			textBuffer = []

		if(lastlineHolder):
			textBuffer.append(lastlineHolder)
		
		lastlineHolder = line


	sourceStream.close()
	summaryFile.close()

def fix_footnotes(textBuffer_array, footnote_prefix):
	# of course, now that I have to loop through the entire text buffer twice, I could completely
	# rewrite the above...but not now
	new_text_buffer = []

	# so, I have to find and rewrite both the format and the innards of the footnote links
	# Using a simple #endnotes doesn't work for GitBook file structure
	footnote_format = re.compile("(.*)(\^\[)(\d+)(\]\(#)(.*)(\)\^)(.*)")
	#newline_remnant = re.compile("(.*)(\\\n)")

	for line in textBuffer_array:

		if footnote_format.match(line):
			# instead of rewriting in a separate function, just get the match object and use it here
			footnote_matchObj = footnote_format.match(line)
			line = footnote_matchObj.group(1)+"<sup>["+footnote_matchObj.group(3)+"]("+footnote_prefix+"endnotes/README.html)</sup>"

		# while we're at it, we might as well get real newlines into our footnote sections
		line = re.sub(r"\\\n", "\n\n", line)

		new_text_buffer.append(line)

	return new_text_buffer

def fix_image_links(textBuffer_array, graphics_prepend):
	# placeholder for edited text; need to rewrite any image links to point to 
	# top level of GitBook
	new_text_buffer = []

	# look for the structure of a graphics link
	# "(![.*?])(\(graphics)(.*?\))(.*)"
	graphics_link = re.compile("(!\[.*?\])(\(graphics)(.*?\))")
	#newline_remnant = re.compile("(.*)(\\\n)")


	for line in textBuffer_array:

		if graphics_link.match(line):
			# instead of rewriting in a separate function, just get the match object and use it here
			#print(line)
			graphics_matchObj = graphics_link.match(line)
			line = graphics_matchObj.group(1)+"("+graphics_prepend+"graphics"+graphics_matchObj.group(3)
			#print(line)
			

		# while we're at it, we might as well get real newlines into our footnote sections
		#line = re.sub(r"\\\n", "\n\n", line)

		new_text_buffer.append(line)

	return new_text_buffer	


def formatTitle(aLine):
	# remove digits and punctuation from chapter/section title, make it lowercase and split it on spaces
	#title_adds = re.compile("(.*?)({.*?})")
	#title_matchObj = title_adds.match(aLine)
	#if(title_matchObj):
#		aLine = title_matchObj.group(1)
	theTitleArray = re.sub('[\'!@#$&.:1234567890,]', '',aLine).lower().split()

	# join the first four "words" of the title together with underscores
	theTitle = "_".join(theTitleArray[0:3])

	return theTitle  


main()          
    
