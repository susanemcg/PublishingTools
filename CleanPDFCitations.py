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
	arg_parser = argparse.ArgumentParser(description="Remove carriage returns and excess text in citations list from PDF.")
	arg_parser.add_argument("filename")
	arg_parser.add_argument("report_title")


	args = arg_parser.parse_args()

	# right now this only matches chapter headings denoted by 5 equals signs and section headings by 5 dashes
	# other formats for these could optionally be added, if other markdown sources are used


	# e.g. load the file passed in from the command line
	targetFile = args.filename
	report_title = args.report_title

	# strip the file extension from the target file to create target folder
	cleanfile = open(targetFile[:-3]+"_clean.txt", "w")
	cleanfile.write("Citations\n======\n\n")

	sourceStream = open(targetFile, "rU")
	sourceText = sourceStream.readlines()
	num_lines = len(sourceText)

	text_holder = []

	cite_pattern = re.compile("(\d+\.\s)")
	page_pattern = re.compile("(\d+\s"+report_title+")")
	title_pattern = re.compile("(Columbia Journalism School)")

	for line_num, line in enumerate(sourceText):
		if line_num == 0:
			text_holder.append(line[:-1])

		if cite_pattern.match(line):
			if text_holder != []:
				# if it's not empty, process and write its contents, then empty and append this line
				joined_holder = "".join(text_holder)
				fix_dash1 = re.sub("(-\s)","-", joined_holder)
				fix_dash2 = re.sub("(\s-)","-", fix_dash1)
				fix_slash1 = re.sub("(\s\/)","/", fix_dash2)
				fix_slash2 = re.sub("(\/\s)","/", fix_slash1)
				fix_colon = re.sub("https\s://","https://", fix_slash2)
				fix_com = re.sub("\s.com", ".com", fix_colon)
				cleanfile.writelines(fix_com+"\n\n")
				text_holder = []
				text_holder.append(line[:-1])
		elif not(page_pattern.match(line)) and not(title_pattern.match(line)):
			# if this isn't the start of a citation, lop off the errant carriage return
			text_holder.append(line[:-1])


	sourceStream.close()
	cleanfile.close()



main()          
    
