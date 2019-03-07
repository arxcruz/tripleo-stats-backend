import datetime

from sqlalchemy import Date, func, cast
from sqlalchemy.orm import sessionmaker
from database.model import engine
from database.model import JobRun


def show_data():
    Session = sessionmaker(engine)
    session = Session()

    query = session.query(func.count().label('count'), JobRun.failure_type).group_by(
            JobRun.failure_type).all()
    # .filter(func.date(JobRun.date) == func.date((datetime.datetime.today()-datetime.timedelta(4)))).all()

    # .filter(JobRun.date == datetime.datetime.now()-datetime.timedelta(3) ).all()

    for row in query:
        print('{} - {}'.format(row.count, row.failure_type))

if __name__ == '__main__':
    show_data()
