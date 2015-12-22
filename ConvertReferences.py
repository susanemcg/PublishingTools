import re
import os
import argparse
from roman import toRoman

citation_counter = 1

def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="HTML file to be corrected for web publishing")
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

	file_leader = targetFile[:-5]

	myOutput = open(file_leader+"_clean.html", "w")
	
	sourceStream = open(targetFile, "rU")
	sourceText = sourceStream.readlines()
	num_lines = len(sourceText)


	for line_num, line in enumerate(sourceText):
	
			corrected_buffer = fix_media(line, footnotes_roman, footnote_title, citations_title)

			myOutput.writelines(corrected_buffer)
			

	myOutput.close()
	sourceStream.close()



def fix_media(text_line, footnotes_roman, footnote_title, citations_title):

	line = text_line

	footnote_format = re.compile("(.*?)(\[\^)(\d+)(\])(.*?)")
	if footnotes_roman == "True":
		footnote_format = re.compile("(.*?)(\[\^)(\w+)(\])(.*?)")

	citation_format = re.compile("(.*?)(\[@)(.+?)(\])(.*?)")
	#("(.*)(\[@)(.+?)(\])")


	if footnote_format.match(line):
		# instead of rewriting in a separate function, just get the match object and use it here
		footnote_iter = footnote_format.finditer(line)
		newline_holder = []
		for match in footnote_iter:
			theNumber = match.group(3)
			line_frag = match.group(1)+"<sup><a href=#"+footnote_title+">"+theNumber+"</a></sup>"
			newline_holder.append(line_frag)
		newline_holder.append(line[match.end():])
		line = "".join(newline_holder)

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
    
