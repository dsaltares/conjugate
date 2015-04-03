import logging
from bs4 import BeautifulSoup

class VerbixParser:
	def parse(self, document):
		try:
			translation = self.__get_translation(document)
			translation['modes'] = self.__get_modes(document)

			return translation
		except Exception as e:
			logging.error('Error parsing document: {0}'.format(e.strerror))

	def get_infinitive(self, language, document):
		soup = BeautifulSoup(document, 'html5')

		for a_element in soup.select('li > a'):
			if a_element['href'].find('D1=%s&'%language) != -1:
				return a_element.string

	def __get_translation(self, document):
		soup = BeautifulSoup(document, 'html5')

		return {
			'name': soup.h1.string.replace('\n', '').split(':')[1].replace(' ', ''),
			'meanings': self.__get_english(soup),
		}

	def __get_english(self, soup):
		meanings = []
		meaning_blocks = soup.find_all('div', {'class': 'trfloatmeaning'})[:-1]

		for meaning_block in meaning_blocks:
			description = meaning_block.h3.string.lower()
			link = meaning_block.a.string

			meanings.append({
				'eng': link.string,
				'description': description
			})

		return meanings

	def __get_modes(self, document):
		document = self.__cleanse_document(document)
		soup = BeautifulSoup(document, 'html5')
		modes = soup.find_all('div', {'class': 'column'})
		return [self.__get_mode(mode) for mode in modes if mode is not None]

	def __cleanse_document(self, document):
		start_tag = '<!-- #BeginEditable "Full_width_text" -->'
		end_tag = '<!-- #EndEditable -->'

		start_idx = document.rindex(start_tag)
		end_idx = document.index(end_tag)

		document = document[start_idx:end_idx].replace('<br>', '').replace('\n', '')

		return '<html><body><div>' + document + '</div></body></html>'

	def __get_mode(self, mode_element): 
		try:
			return {
				'name': self.__get_mode_name(mode_element),
				'tenses': self.__get_tenses(mode_element)
			}
		except Exception as e:
			logging.error('Error processing mode: {0}'.format(e.strerror))

	def __get_mode_name(self, mode_element):
		return self.__process_str(mode_element.h3.get_text())

	def __get_tenses(self, mode_element):
		tenses = []
		current_tense = None

		for block in mode_element.select('td > p'):
			try:
				for element in block.children:
					if element.name is None:
						continue

					if element.name == 'b':
						tense_name = self.__process_str(element.string)
						current_tense = self.__create_tense(tense_name)
						tenses.append(current_tense)
					elif element.name == 'font':
						pronoun = self.__process_str(element.span.string)

						if current_tense is None:
							current_tense = self.__create_tense('')
							tenses.append(current_tense)

						conjugation = self.__create_conjugation(pronoun)
						current_tense['conjugations'].append(conjugation)
					elif element.name == 'span':
						option = self.__process_str(element.string)

						if len(option) < 1:
							continue

						if current_tense is None:
							current_tense = self.__create_tense('')
							tenses.append(current_tense)

						if len(current_tense['conjugations']) == 0:
							conjugation = self.__create_conjugation('')
							current_tense['conjugations'].append(conjugation)
						
						current_tense['conjugations'][-1]['options'].append(option)
			except Exception as e:
				logging.error('Error processing block: {0}'.format(e.strerror))

		return [tense for tense in tenses if len(tense['conjugations']) > 0]

	def __create_tense(self, name):
		return {
			'name': name,
			'conjugations': []
		}

	def __create_conjugation(self, name):
		return {'name': name, 'options': []}

	def __process_str(self, str):
		return str.replace('\n', ' ').replace(':', '').lstrip().rstrip()