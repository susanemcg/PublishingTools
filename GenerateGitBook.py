#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
import os
import argparse
from roman import toRoman

citation_counter = 1


# TODO: look for carriage returns in links and remove


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
			wholeTitle = re.sub("(\*)(.*?)(\*)",replace_italics, wholeTitle)

			# this deals with the way LaTeX will output titles that have been 
			# blocked from the TOC
			title_adds = re.compile("(.*?)({.*?})")
			title_matchObj = title_adds.match(wholeTitle)
			if(title_matchObj):
				wholeTitle = title_matchObj.group(1)


			titleText = formatTitle(wholeTitle)

			# if we are indeed at the last line of the file, we need to push it to the buffer *before* processing 
			if line_num == num_lines:
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

			# trying to figure out what's in corrected_buffer. Hopefully the entire file?
			really_corrected_buffer = remove_breaks(corrected_buffer)

			
			myOutput.writelines(really_corrected_buffer)
			myOutput.close()
			#empty the buffer
			textBuffer = []

		if(lastlineHolder):
			textBuffer.append(lastlineHolder)
		
		lastlineHolder = line


	sourceStream.close()
	summaryFile.close()



def replace_blocks(matchobj):
	return matchobj.group(1)+" "+matchobj.group(3)

def replace_bold(matchobj):
	return "<b>"+matchobj.group(2)+"</b>"

def replace_italics(matchobj):
	return "<em>"+matchobj.group(2)+"</em>"

def format_captions(matchobj):
	return "<span style='font-size:12px;'><em>"+matchobj.group(2)+"</em></span>"

def replace_links(matchobj):
	# 2 is text, 5 is link
	#print matchobj.group(2)
	if matchobj.group(2) != "":
		return '<a href="'+matchobj.group(5)+'">'+matchobj.group(2)+'</a>'
	else:
		return '[]('+matchobj.group(5)+')\n'

def remove_breaks(the_buffer):
	another_text_holder = []
	for num, line in enumerate(the_buffer):
		if num > 2: # this skips the title and header indicator
			if line != '\n':
				if line[-1:] == "\n":
					# e.g. everything not listed here
					another_text_holder.append(line[:-1])
				else: 
					# e.g. graphics links
					another_text_holder.append(line+"\n")
			else:
				# e.g. a clear line between grafs
				another_text_holder.append("\n\n")
		else:
			# e.g. the title and header links, which are left as-is
			another_text_holder.append(line)

	# join this stuff together into a single string, stedda an array
	concat_holder = " ".join(another_text_holder)


	concat_holder = re.sub("(\w)(\s\>\s)(\w)", replace_blocks, concat_holder)

	# using the question marks makes these 'non-greedy' which is a huge f-in help
	new_tester = re.sub("(\*\*)(.*?)(\*\*)",replace_bold, concat_holder)

	new_tester = re.sub("(\*?!\*)(.*?)(\*?!\*)",replace_italics, new_tester)

	link_fix = re.sub("(\[)(.*?)(\])(\()(.*?)(\))", replace_links, new_tester)

	caption_edit = re.sub("(<span>)(.{4,}?)(<\/span>)", format_captions, link_fix)

	return caption_edit






def fix_media(textBufferArray, directory_prepend, footnotes_roman, footnote_title, citations_title):

	text_holder = []

	footnote_format = re.compile("(.*)(\[\^)(\d+)(\])(.*)")

	citation_format = re.compile("(.*)(\[@)(.+?)(\])")

	graphics_link = re.compile("(!\[.*?\])(\(graphics)(.*?\))")

	for line in textBufferArray:

		if footnote_format.match(line):
			# instead of rewriting in a separate function, just get the match object and use it here
			footnote_iter = footnote_format.finditer(line)
			foot_holder = []
			for match in footnote_iter:
				theNumber = match.group(3)
				if footnotes_roman == "True":
					theNumber = toRoman(int(match.group(3)))
				line_frag = match.group(1)+"<sup>["+theNumber+"]("+directory_prepend+footnote_title+"/README.html)</sup>"
				foot_holder.append(line_frag)
			foot_holder.append(line[match.end():])
			line = "".join(foot_holder)

		if citation_format.match(line):
			# instead of rewriting in a separate function, just get the match object and use it here
			citation_iter = citation_format.finditer(line)
			new_holder = []
			for match in citation_iter:
				#print match.group(1)
				line_frag = match.group(1)+"<sup><a href="+directory_prepend+citations_title+"/index.html>"+str(citation_counter)+"</a></sup>"
				new_holder.append(line_frag)
				global citation_counter
				citation_counter+=1
			new_holder.append(line[match.end():])
			line = "".join(new_holder)

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
	theTitleArray = re.sub('[\'*!@#$&.:1234567890,?/]', '',aLine).lower().split()

	# join the first four "words" of the title together with underscores
	theTitle = "_".join(theTitleArray[0:4])

	return theTitle  


main()          
    
