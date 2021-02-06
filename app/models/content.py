from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from . import Base

association_table = Table(
    "contents_keywords",
    Base.metadata,
    Column("contents_id", Integer, ForeignKey("contents.id")),
    Column("keywords_id", Integer, ForeignKey("keywords.id")),
)


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    filepath = Column(String, unique=True)
    count = Column(Integer, default=0)

    keywords = relationship(
        "Keyword", secondary=association_table, back_populates="contents"
    )


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    contents = relationship(
        "Content", secondary=association_table, back_populates="keywords"
    )
