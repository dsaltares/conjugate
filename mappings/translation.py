from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Translation(Base):
    __tablename__ = 'translations'

    lang = Column(String(10), primary_key=True)
    verb = Column(String(25), primary_key=True)
    english = Column(String(25), primary_key=True)
    description = Column(String(100))

    def __repr__(self):
        return "<Translation(lang='%s', verb='%s', english='%s'>" % (self.lang, self.verb, self.english)