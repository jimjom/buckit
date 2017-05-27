
import collections
import sqlite3

from EvernoteWrapper import EvernoteWrapper

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec

from datetime import datetime, date

Macros = collections.namedtuple('Macros', 'alcohol carbs fats proteins')

class MacrosWrapper(EvernoteWrapper):


	def __init__(self, db, token):
		EvernoteWrapper.__init__(self, db, token)

	def isRecipeNote(self, note):
		keyword = note.title.upper().split(",")[0]
		return keyword == 'RECIPE'

	def isMacroNoteSimplify(self, note):
		return self.isMacroNote( note, True)

	def isMacroNote(self, note, simplifyNote):
		keyword = note.title.upper().split(",")[0]
		success = False
		if keyword == 'FOOD':
			success = True
		result = self.findRecipe(keyword)
		if (self.findRecipe(keyword) != None):
			success = True
			if simplifyNote:
				macrosStr = result.alcohol + 'a' + \
					    result.carbs + 'c' + \
					    result.fats + 'f' + \
					    result.proteins + 'p'

				note.title = keyword + ',' + macrosStr
				self._noteStore.updateNote(note)
		
		return success

	def saveRecipes(self, notes, simplifyNote):
		db = sqlite3.connect(self._dbName)
		conn = db.cursor()

		for note in notes:
			title = note.title.upper().split(",")
			if len(title)!=4:
				continue
			
			name = title[3]

			if self.findRecipe(name) == None:

				macrosStr = title[1]
				macros = self.parseMacros(macrosStr)

				conn.execute(
					'insert into recipes(name, alcohol, carbs, fat, protein)\
					values (?,?,?,?,?)',
					(name, macros.alcohol, macros.carbs, macros.fats, macros.proteins))


			if simplifyNote:
				count = title[2]
				title = name + ',' + macrosStr + ',' + count
				note.title = title
				self._noteStore.updateNote(note)
		db.commit()
		db.close()

	def saveMacroLog(self, note):
		db = sqlite3.connect(self._dbName)
		conn = db.cursor()
		
		title = note.title.upper().split(",")

		name = title[0]
		macrosStr = title[1]
		macros = self.parseMacros(macrosStr)

		conn.execute(
				'insert into macrosLog(date, name, alcohol, carbs, fat, protein)\
				values (?,?,?,?,?,?)',
				(note.created,name,macros.alcohol,macros.carbs,macros.fats,macros.proteins))


		success = (conn.rowcount ==1)
		
		db.commit()
		db.close()

		return success

	def findRecipe(self, name):
		db = sqlite3.connect(self._dbName)
		conn = db.cursor()

		conn.execute('select * from recipes where name="'+name+'"')
		
		result = conn.fetchone()
		db.close()
		if result:
			return Macros(result[1], result[2], result[3], result[4])
		else:
			return None


	def parseMacros(self, macrosStr):
		if macrosStr == "":
			return None

		alcohol = macrosStr.split('A')
		if len(alcohol)==1:
			carbs = alcohol[0]
			alcohol = 0
		else:
			carbs = alcohol[1]
			alcohol = int(alcohol[0])

		carbs = carbs.split('C')
		fat = carbs[1]
		carbs = int(carbs[0])

		fat = fat.split('F')
		protein = fat[1]
		fat = int(fat[0])

		protein = int(protein.split('P')[0])

		if alcohol == fat == carbs == protein == 0:
			return None

		return Macros(alcohol=alcohol, carbs=carbs, fats=fat, proteins=protein)

	def queryLog(self):
		db = sqlite3.connect(self._dbName)
		conn = db.cursor()

		conn.execute('select rowid, * from macrosLog')
		
		result = []
		for row in conn:
			result.append(row)

		db.close()
		return result

	def queryLogForDate(self, date):
		rows = self.queryLog()
		
		result = []
		for row in rows:
			rowDate = datetime.fromtimestamp(row[1]/1000).date()
			if date == rowDate:
				result.append(row)

		return result

