#!/usr/bin/bash

import sys
import authtoken
from MacrosWrapper import MacrosWrapper

dbName = 'C:\Users\jepot_000\SkyDrive\python\data.db'

evn = MacrosWrapper(db=dbName, token=authtoken.auth_token)

inbox = evn.findNotebook("Inbox")
macros = evn.findNotebook("Macros")

recipeNotes = filter(evn.isRecipeNote, evn.findNotebookNotes(inbox))
evn.saveRecipes(notes=recipeNotes, simplifyNote=True)
macroNotes = filter(evn.isMacroNoteSimplify, evn.findNotebookNotes(inbox))

count = 0
for note in macroNotes:
	if evn.saveMacroLog(note):
		count = count + 1
		evn.moveNotebook(note, macros)

print ("Extraction successful, moved %d notes" % count)
