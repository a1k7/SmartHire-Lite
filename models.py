from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    title = Column(String)
    description = Column(Text)

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    resume_text = Column(Text)

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    candidate_id = Column(Integer)
    score = Column(Integer)
    decision = Column(String)
    summary = Column(Text)