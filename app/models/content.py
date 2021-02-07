from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

association_table = Table(
    "contents_keywords",
    Base.metadata,
    Column("contents_id", Integer, ForeignKey("contents.id")),
    Column("keywords_id", Integer, ForeignKey("keywords.id")),
)


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(30), unique=True, index=True, nullable=False)
    filepath = Column(String(200), unique=True, nullable=False)
    count = Column(Integer, default=0, nullable=False)

    keywords = relationship(
        "Keyword", secondary=association_table, back_populates="contents"
    )


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, index=True, nullable=False)

    contents = relationship(
        "Content", secondary=association_table, back_populates="keywords"
    )
