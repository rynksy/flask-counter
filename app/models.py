from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

    @classmethod
    def get_counter(cls):
        counter = cls.query.first()
        if counter is None:
            counter = cls(count=0)
            db.session.add(counter)
            db.session.commit()
        return counter
