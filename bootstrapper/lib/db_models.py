from sqlalchemy import Column, Integer, String
from .db import Base


class Template(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    # simple name of the template
    name = Column(String(50), unique=True)
    # type of the template - bootstrap or init-cfg-static.txt
    type = Column(String(32), unique=False)
    # simple description of this template
    description = Column(String(120), unique=False)
    # actual text of the jinja template
    template = Column(String(), unique=False)

    def __init__(self, name=None, description=None, type='bootstrap', template=""):
        self.name = name
        self.description = description
        self.type = type
        self.template = template

    def __repr__(self):
        return '<Template %r>' % (self.name)