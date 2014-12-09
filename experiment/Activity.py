__author__ = 'ugonzjo'


from meta import Base
from sqlalchemy import Column, Integer, String, DateTime

import pandas as pd

class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, index=True)
    xml_qno = Column(Integer)
    handedin = Column(DateTime)
    chapter_id = Column(Integer, index=True)
    section_id = Column(Integer,  index=True)
    objective_id = Column(Integer,  index=True)
    exercise_id = Column(Integer)
    got_correct = Column(Integer)
    kc = Column(String, index=True)

    def __init__(self,  qno, handedin, student_id,  chapter, section, objective, exercise,  got_correct, kc):
        self.xml_qno = qno
        self.handedin = handedin
        self.user_id = student_id
        self.chapter_id = chapter
        self.section_id = section
        self.objective_id = objective
        self.exercise_id = exercise
        if  not (got_correct == 1 or got_correct == 0 or got_correct==-1):
            raise RuntimeError("got_correct should be 0,1 or -1 for the last Activity of a stream")
        self.got_correct = got_correct
        self.kc = kc

    @staticmethod
    def get_columns():
        columns = [Activity.id,  Activity.xml_qno, Activity.handedin, Activity.user_id, Activity.chapter_id, Activity.section_id, Activity.objective_id, Activity.exercise_id,  Activity.got_correct, Activity.kc]
        return columns
    @staticmethod
    def get_dataframe(session,  filter_columns=[], limit_number_of_rows=None ):
        columns = Activity.get_columns()
        query = session.query( *columns).filter(*filter_columns)

        if limit_number_of_rows != None:
            query = query.limit(limit_number_of_rows)

        data = query.all()
        columns = [column['name'] for column in query.column_descriptions]

        if len(data) != 0:
            return pd.DataFrame(data, columns=columns)
        else:
            return Activity.get_empty_dataframe()

    @staticmethod
    def get_empty_dataframe():
        columns = Activity.get_columns()
        return pd.DataFrame(columns=[x.name for x in columns])






    #def __repr__(self):
    #    return '<Book %r>' % self.