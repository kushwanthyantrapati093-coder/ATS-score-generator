from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData

# SQLite engine
engine = create_engine('sqlite:///cv_jd_data.db')

# Metadata
metadata = MetaData()

# Table to store CV-JD comparisons
cv_table = Table(
    'cv_scores', metadata,
    Column('id', Integer, primary_key=True),
    Column('candidate_name', String),
    Column('cv_text', Text),
    Column('jd_text', Text),
    Column('score', Integer)
)

# Create table if not exists
metadata.create_all(engine)
