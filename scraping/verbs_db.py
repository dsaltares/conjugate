import MySQLdb as mdb
import logging

class VerbsDB:
	def __init__(self, host, user, password, database):
		self.__con = mdb.connect(
			host,
			user,
			password,
			database,
			use_unicode=True,
			charset="utf8"
		)

	def build(self):
		self.delete()

		try:
			cur = self.__con.cursor()
			cur.execute(
				'''CREATE TABLE verbs (
					lang VARCHAR(10) NOT NULL,
					verb VARCHAR(25) NOT NULL,
					conjugations LONGTEXT NOT NULL,
					PRIMARY KEY (lang, verb))'''
			)

			self.__con.commit()

			cur.execute(
				'''CREATE TABLE translations (
					lang VARCHAR(10) NOT NULL,
					verb VARCHAR(25) NOT NULL,
					english VARCHAR(25) NOT NULL,
					description VARCHAR(100),
					PRIMARY KEY (lang, verb, english))'''
			)

			self.__con.commit()
			cur.close()
				
		except Exception as e:
			logging.error(u'Failed to build database: {0}'.format(str(e)))
			return False
		
		return True

	def delete(self):
		try:
			cur = self.__con.cursor()
			cur.execute('DROP TABLE IF EXISTS translations')
			cur.execute('DROP TABLE IF EXISTS verbs')
			self.__con.commit()
			cur.close()
		except Exception as e:
			logging.error(u'Failed to drop database tables: {0}'.format(str(e)))
			return False
		
		return True

	def insert_verb(self, lang, verb, conjugations):
		return (
			self.__insert_verb(lang, verb, conjugations) or
			self.__udpdate_verb(lang, verb, conjugations)
		)

	def get_verb(self, lang, verb):
		try:
			cur = self.__con.cursor()
			cur.execute(
				u'SELECT conjugations FROM verbs WHERE lang = %s AND verb = %s',
				(lang, verb)
			)

			conjugations = None

			if cur.rowcount > 0:
				conjugations = cur.fetchone()[0]

			cur.close()

			return conjugations
		except Exception as e:
			logging.error(u'Failed to get verb %s from database: %s' % (verb, str(e)))

	def get_verbs(self, lang):
		try:
			cur = self.__con.cursor()
			cur.execute(
				u'SELECT verb FROM verbs WHERE lang = %s',
				(lang)
			)

			verbs = [row['verb'] for row in cur.fetchall() ]
			cur.close()

			return verbs

		except Exception as e:
			logging.error(u'Failed to get verbs from database: %s' % (str(e)))

	def insert_translation(self, lang, verb, english, description):
		return (
			self.__insert_translation(lang, verb, english, description) or
			self.__udpdate_translation(lang, verb, english, description)
		)

	def __insert_verb(self, lang, verb, conjugations):
		try:
			cur = self.__con.cursor()
			cur.execute(
				u'INSERT INTO verbs (lang, verb, conjugations) VALUES (%s, %s, %s)',
				(lang, verb, conjugations)
			)
			self.__con.commit()
			cur.close()
		except mdb.IntegrityError:
			return False
		except Exception as e:
			logging.error(u'Failed to insert verb %s into database: %s' % (verb, str(e)))
			return False
		
		return True

	def __udpdate_verb(self, lang, verb, conjugations):
		try:
			cur = self.__con.cursor()
			cur.execute(
				u'UPDATE verbs SET conjugations = %s WHERE lang = %s AND verb = %s',
				(conjugations, lang, verb)
			)
			self.__con.commit()
			cur.close()
		except Exception as e:
			logging.error(u'Failed to update verb %s in database: %s' % (verb, str(e)))
			return False
		
		return True

	def __insert_translation(self, lang, verb, english, description):
		try:
			cur = self.__con.cursor()
			cur.execute(
				u'INSERT INTO translations (lang, verb, english, description) VALUES (%s, %s, %s, %s)',
				(lang, verb, english, description)
			)
			self.__con.commit()
			cur.close()
		except mdb.IntegrityError:
			return False
		except Exception as e:
			logging.error(u'Failed to insert translation for %s into database: %s' % (verb, str(e)))
			return False
		
		return True

	def __udpdate_translation(self, lang, verb, english, description):
		try:
			cur = self.__con.cursor()
			cur.execute(
				u'UPDATE translations SET description = %s WHERE lang = %s AND verb = %s AND english = %s',
				(description, lang, verb, english)
			)
			self.__con.commit()
			cur.close()
		except Exception as e:
			logging.error(u'Failed to update translations for %s in database: %s' % (verb, str(e)))
			return False
		
		return True