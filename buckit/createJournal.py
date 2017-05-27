#!/usr/bin/env python

from MacrosWrapper import MacrosWrapper
from datetime import datetime, date, timedelta
import authtoken

import sys

YOGA_TEXT_FILE = "revolution-yoga.txt"
dbName = 'data.db'

evn = MacrosWrapper(db=dbName, token=authtoken.auth_token)

inbox = evn.findNotebook("Inbox")
journal = evn.findNotebook("Journal")

whenNoteLevel = int(sys.argv[1])
if whenNoteLevel == 0:
	whenNodeLevel = 2

def diff_dates(date1, date2):
	return abs(date2-date1).days

def calcTotal(total):
	return (total[0] * 4) +\
			(total[1] * 4) + \
			(total[2] * 9) + \
			(total[3] * 4)

def addDailyMantra() :
	return "<h1>Keep your hopes and dreams alive!</h1>"

def addKetoDay():
	start = date(2017,3,27)
	today = date.today()
	return "Day "+str(diff_dates(start,today))

def addYogaDay():
	start = date(2017,2,28)
	today = date.today()
	text_line = diff_dates(start,today)
	return str(getLineOfText(YOGA_TEXT_FILE,text_line))

def getLineOfText(fileName,lineNo):
	with open(fileName) as fp:
			for i, line in enumerate(fp):
				if i == lineNo:
					return line

def addYesterdayMacros(env):
	yesterday = date.today() - timedelta(1)
	result = evn.queryLogForDate(yesterday)
	total = [0, 0, 0, 0]
	for row in result:
		total[0] += row[3]
		total[1] += row[4]
		total[2] += row[5]
		total[3] += row[6]
	return ("Yesterday <b>\
			%s Total</b> |\
			%s alcohol \
			%s carbs \
			%s fats \
	%s proteins <hr/>" % (calcTotal(total), str(total[0]), str(total[1]), str(total[2]), str(total[3])))

def addDailyItems():
	return "<en-todo/>1 - Exercise <br/>\
			<en-todo/>2 - Review Inbox <br/>\
			<en-todo/>3 - Read Emails<br/>\
			<en-todo/>4 - Meditate<br/>\
			<en-todo/>5 - Read/Write<hr/>"

def addInboxItems():
	notes =  evn.findNotebookNotes(inbox)
	if notes is None:
		return "0 Inbox Notes <hr/>"
	count = len(notes)
	
	result = str(count) + " Inbox Notes<hr/><ul>"
	for note in notes:
		result += "<li>"+evn.makeNoteLink(note.title, note)+"</li>"
	return result+"</ul><br/>"

def addTagItems(tag,title):
	notes =  evn.findTagNotes(tag)
	if notes is None:
		return "0 '"+title+"' Notes<hr/><ul>"

	count = len(notes)

	result = str(count) + " '"+title+"' Notes<hr/><ul>"
	for note in notes:
		result += "<li>"+evn.makeNoteLink(note.title, note)+"</li>"
	return result+"</ul><br/>"

def addNextItems():
	return None
def addSoonItems():
	return None

#noteText = addYesterdayMacros(evn)
noteText = addDailyMantra() + "<hr/>"
noteText += addKetoDay() + "<hr/>"
#noteText = addYogaDay() + "<hr/>"
noteText += addDailyItems() 
noteText += addInboxItems() #+ "<br/>"
if whenNoteLevel > 0:
	noteText += addTagItems('1-Now', 'Now (Today)')
if whenNoteLevel > 1:
	noteText += addTagItems('2-Next','Next (This Week)')
if whenNoteLevel > 2:
	noteText += addTagItems('3-Soon','Soon (This Month)')
if whenNoteLevel > 3:
	noteText += addTagItems('4-Later','Later (This Year)')
if whenNoteLevel > 4:
	noteText += addTagItems('5-Someday','Someday')
noteText += addTagItems('Goals','Read these, everyday')

now = datetime.now()
#noteText = evn.makeNoteLink(note1.title, note1)

note2 = evn.makeNote(now.strftime("%m/%d/%y"), noteText, journal)
