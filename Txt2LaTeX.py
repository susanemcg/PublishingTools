# This Python file uses the following encoding: utf-8

import re
import os
import argparse

# This file accepts a .txt file and outputs a .tex file of the same name.
# In the conversion it also does the following with reasonable accuracy/completeness:
#	1. Removing Tow Center for Journalism running hed/footer
#	2. Removing standalone page numbers (e.g. a line with just a number on it)
#	3. Replacing curly quotes with LaTeX quotes
#	4. Escaping dollar signs
#	5. Escaping ellipses
#	6. Properly re-formatting bulleted lists in LaTeX format
#	7. Locates footnotes and rewrites them as links to "#endnotes" OR tag passed to optional "-endnote_loc" command-line argument 
#
# Command line usage:
# 	python Txt2LaTeX.py "MyTextFile.txt" "My Running Head" -endnote_loc "endnotes_1"		


# create an argument parser to take commandline arguments (e.g. target filename)
arg_parser = argparse.ArgumentParser(description="Markdown file to be processed into Gitbook format")
arg_parser.add_argument("filename")
arg_parser.add_argument("running_hed")

# optional argument to specify the href for "endnotes", in case different/multiple
arg_parser.add_argument("-endnote_loc")

args = arg_parser.parse_args()

# e.g. load the file passed in from the command line
targetFile = args.filename

# strip the file extension from the target file to create the output filename
outputFileName = targetFile[:-3]

endNote_link = "endnotes"
if args.endnote_loc:
	endNote_link = args.endnote_loc

def main():
	# find the running hed passed in by the user and followed by a carriage return, it's a running hed, not content
	running_hed_pattern = re.compile("("+args.running_hed+")\n")
	
	# if you fina a line with just digits on it, it's a page number
	page_num_pattern = re.compile("^\d+\n")
	
	# running header/footer on current Tow reports
	tow_runner_pattern = re.compile("Columbia Journalism School | TOW CENTER FOR DIGITAL JOURNALISM\n")
	
	# this is a bit of a hack, but basically says:
	# 'if the lines starts with a capital letter and ends w/a digit, it's a running header/footer'
	# .....and: it breaks. 
	line_ends_w_pagenum = re.compile("^[A-Z].*\d$")

	# if you find a non-digit, non-dollar sign, followed by one or two digits and then a space or a paren, it's a footnote
	footnote_pattern = re.compile("([^0-9$\s])(\d{1,2})([\s)])")

	# sorry, this one is obvious
	has_bullet = re.compile("•")



	# create summary file, which will be used by Gitbook to generate the table of contents/links
	sourceStream = open(targetFile)

	sourceText = sourceStream.readlines()

	outputFile = open(outputFileName+"tex", "w")

	previousLine = ""

	for line in sourceText:

		if not (running_hed_pattern.match(line) or page_num_pattern.match(line) or tow_runner_pattern.match(line) or line_ends_w_pagenum.match(line)):
			# next two lines replace curly quotes w/LaTeX-style quotes
			edited_line = re.sub("“", "``", line)
			edited_line = re.sub("”", "''", edited_line)
			# escape $
			edited_line = re.sub("\$", "\\$", edited_line)
			# replace ellipsis with \ldots
			edited_line = re.sub("…", "\ldots ", edited_line)
			# escape % signs
			edited_line = re.sub("%", "\%", edited_line)
			
			# write footnote markup
			edited_line = footnote_pattern.sub(footnote_replace, edited_line)
			
			#replace bullets with \item in the edited line
			edited_line = re.sub("•", "\\item", edited_line)

			# if this is the last bulleted item in a list, add the closing \itemize tag, checking "raw" line values
			if has_bullet.match(previousLine) and not has_bullet.match(line):
				outputFile.write("\end{itemize}\n")
			# if this is the first bulleted item in a list, add the opening \itemize tag, checking "raw" line values
			if has_bullet.match(line) and not has_bullet.match(previousLine):
				outputFile.write("\\begin{itemize}\n")
			
			outputFile.write(edited_line)
			previousLine = line

	sourceStream.close()
	outputFile.close()

def footnote_replace(matchObj):
	return matchObj.group(1)+"^{\\href{#"+endNote_link+"}{"+matchObj.group(2)+"}}"+matchObj.group(3)

def formatTitle(aLine):
	# remove digits and punctuation from chapter/section title, make it lowercase and split it on spaces
	theTitleArray = re.sub('[!@#$&.:1234567890,]', '',aLine).lower().split()
	# join the first four "words" of the title together with underscores
	theTitle = "_".join(theTitleArray[0:3])
	return theTitle   

main()          
    