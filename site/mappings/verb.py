from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()

class Verb(Base):
    __tablename__ = 'verbs'


    lang = Column(String(10), primary_key=True)
    verb = Column(String(25), primary_key=True)
    conjugations = Column(String)

    def __repr__(self):
        return "<Verb(lang='%s', verb='%s'>" % (self.lang, self.verb)