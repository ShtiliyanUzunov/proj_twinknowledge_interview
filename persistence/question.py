from sqlalchemy.orm import declarative_base
from sqlalchemy import text, Enum, Integer, String, Date, Text, Column

Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    show_number = Column("Show Number", Integer, nullable=False)
    air_date = Column("Air Date", Date, nullable=False)
    round = Column("Round", Enum("Jeopardy!", "Double Jeopardy!", "Final Jeopardy!", name="round_enum"), nullable=False)
    category = Column("Category", String(255), nullable=False)
    value = Column("Value", Integer, nullable=True)
    question = Column("Question", Text, nullable=False)
    answer = Column("Answer", Text, nullable=False)