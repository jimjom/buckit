
import collections
import sqlite3

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
import evernote.edam.error.ttypes as Errors
import evernote.edam.type.ttypes as Types

Macros = collections.namedtuple('Macros', 'alcohol carbs fats proteins')

class EvernoteWrapper():


	def __init__(self, db, token):
		self._dbName = db
		self._auth_token = token

		client = EvernoteClient(token=token, sandbox=False)
		self._userStore = client.get_user_store()
		self._noteStore = client.get_note_store()
		
		self._userId = str(self._userStore.getUser(self._auth_token).id)
		self._shardId = str(self._userStore.getUser(self._auth_token).shardId)

	def findNotebook(self, name):
		notebooks = self._noteStore.listNotebooks()
		for notebook in notebooks:
			if notebook.name == name:
				return notebook
		return None

	def findNotebookNotes(self, notebook):
		notefilter = NoteFilter()
		notefilter.notebookGuid = notebook.guid
		notefilter.ascending = False

		spec = NotesMetadataResultSpec()
		spec.includeTitle = True
		spec.includeCreated = True

		return self._noteStore.findNotesMetadata(self._auth_token,notefilter,0,100,spec).notes

	def moveNotebook(self, note, notebook):
		note.notebookGuid = notebook.guid
		self._noteStore.updateNote(note)

	def findTag(self, name):
		tags = self._noteStore.listTags(self._auth_token)
		for tag in tags:
			if tag.name == name:
				return tag
		return None

	def findTagNotes(self, name):
		tag = self.findTag(name)

		if tag is None:
			return None

		notefilter = NoteFilter()
		notefilter.tagGuids = [ tag.guid ]
		notefilter.ascending = False

		spec = NotesMetadataResultSpec()
		spec.includeTitle = True
		spec.includeCreated = False

		return self._noteStore.findNotesMetadata(self._auth_token,notefilter,0,100,spec).notes

	def makeNoteLink(self, title, note):
		noteGuid = str(note.guid)

		link = 'evernote:///view/'+self._userId+'/'+self._shardId+'/'+noteGuid+'/'+noteGuid+'/'
		return "<a href='"+link+"'>"+title+"</a>"

	def makeNote(self, noteTitle, noteBody, parentNotebook=None):

		nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
		nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
		nBody += "<en-note>%s</en-note>" % noteBody

		## Create note object
		ourNote = Types.Note()
		ourNote.title = noteTitle
		ourNote.content = nBody

		## parentNotebook is optional; if omitted, default notebook is used
		if parentNotebook and hasattr(parentNotebook, 'guid'):
			ourNote.notebookGuid = parentNotebook.guid

		## Attempt to create note in Evernote account
		try:
			note = self._noteStore.createNote(self._auth_token, ourNote)
		except Errors.EDAMUserException, edue:
			## Something was wrong with the note data
			## See EDAMErrorCode enumeration for error code explanation
			## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
			print "EDAMUserException:", edue
			return None
		except Errors.EDAMNotFoundException, ednfe:
			## Parent Notebook GUID doesn't correspond to an actual notebook
			print "EDAMNotFoundException: Invalid parent notebook GUID"
			return None
		## Return created note object
		return note
	
