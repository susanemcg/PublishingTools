import re
import os
import argparse
import csv
import datetime


def fix_date(date_groups):
	
	corrected_date = ""

	if date_groups.group(1) == "1":
		corrected_date = "Jan"
	elif date_groups.group(1) == "2":
		corrected_date = "Feb"
	elif date_groups.group(1) == "3":
		corrected_date = "Mar"
	elif date_groups.group(1) == "4":
		corrected_date = "Apr"
	elif date_groups.group(1) == "5":
		corrected_date = "May"
	elif date_groups.group(1) == "6":
		corrected_date = "Jun"
	elif date_groups.group(1) == "7":
		corrected_date = "Jul"
	elif date_groups.group(1) == "8":
		corrected_date = "Aug"
	elif date_groups.group(1) == "9":
		corrected_date = "Sep"
	elif date_groups.group(1) == "10":
		corrected_date = "Oct"
	elif date_groups.group(1) == "11":
		corrected_date = "Nov"
	elif date_groups.group(1) == "12":
		corrected_date = "Dec"	

	corrected_date += " "+date_groups.group(3)+", "
	if int(date_groups.group(5)) > datetime.datetime.now().year:
		corrected_date += "19"
	else:
		corrected_date += "20"

	corrected_date += date_groups.group(5)

	return corrected_date


def main():

	# create an argument parser to take commandline arguments (e.g. target filename)
	arg_parser = argparse.ArgumentParser(description="Tab-separated file to be processed into LaTeX .bib format")
	arg_parser.add_argument("filename")


	args = arg_parser.parse_args()
	# e.g. load the file passed in from the command line
	targetFile = args.filename

	# strip the file extension from the target file to create new filename
	newFileName = targetFile[:-3]

	# you know, I really shouldn't have to do this. but no one cares about "should"
	bad_date = re.compile("(\d+)(\/)(\d+)(\/)(\d+)")

	# create summary file, which will be used by Gitbook to generate the table of contents/links
	bibFile = open(newFileName+"bib", "w")

	sourceStream = open(targetFile, "rU")
	sourceText = csv.DictReader(sourceStream, delimiter='\t',fieldnames=["shortcode","type","title","author","journal","org","publisher","address","year","vol","number","URL","access_date","pgs", "chapter_title", "eds"])

	for i, row in enumerate(sourceText):
		entry_type = row['type'].lower()
		if entry_type == "bookchapter":
			entry_type = "incollection"
		if entry_type == "journal":
			entry_type = "article"

		if i > 0 and entry_type != "":
			mainBibEntry = "@"+entry_type+"{"+row['shortcode']+",\n\t"
			# if the type is "online" then we should add an organization and a url
			if entry_type == 'online':
				mainBibEntry += "title={{"+row['title']+"}},\n\t"
				mainBibEntry += "organization={"+row['org']+"},\n\t"
			# if it's an "article" we're going to default to magazine/newspaper subtype, and manually correct from there
			if entry_type == "article":
				mainBibEntry += "title={{"+row['title']+"}},\n\t"
				mainBibEntry += "journal={"+row['journal']+"},\n\t"
				if row['vol'] != "":
					mainBibEntry += "entrysubtype = {magazine},\n\t"
				else:
					mainBibEntry += "vol = {"+row['vol']+"},\n\t"
					mainBibEntry += "number = {"+row['number']+"},\n\t"
					mainBibEntry += "pages = {"+row['pgs']+"},\n\t"
			if entry_type == "incollection":
				mainBibEntry += "title = {{"+row['chapter_title']+"}},\n\t"
				mainBibEntry += "editor = {"+row['eds']+"},\n\t"
				mainBibEntry += "booktitle ={"+row['title']+"},\n\t"
			if entry_type == "inproceedings":
				mainBibEntry += "title={{"+row['title']+"}},\n\t"
				mainBibEntry += "booktitle ={"+row['org']+"},\n\t"

			# for all entries, add "year", url, and date accessed and author, just in case
			mainBibEntry += "author={"+row['author']+"},\n\t"	
			
			# dealing with bad date formats
			theDate = row['year']
			# print theDate
			if bad_date.match(theDate):
				date_obj = bad_date.match(theDate)
				theDate	= fix_date(date_obj)

			mainBibEntry += "year = {"+theDate+"},\n\t"
			mainBibEntry += "url = {"+row['URL']+"},\n\t"
			mainBibEntry += "urldate = {"+row['access_date']+"}\n\t"

			# now close it off & write it to the file
			mainBibEntry += "}\n"
			bibFile.write(mainBibEntry)

	sourceStream.close()
	bibFile.close()





main()