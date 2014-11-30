PublishingTools
===============

Some simple, lightweight scripts for converting one document format to another.

Files:

GenerateGitbook.py (Python 2.x): Run from the command line, accepts a markdown filename as an argument, then parses it into the file/folder structure required by Gitbook. TK: adding leading digits to folder/filenames so that generating the SUMMARY.md file can be scripted as well. Also, automatically treating the first section as the main "readme" so the book's landing page isn't blank.
