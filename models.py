from peewee import (
    CharField,
    DateTimeField,
    IntegerField,  # type: ignore
    Model,
    SqliteDatabase,
)

db = SqliteDatabase("/app/data/data.db")


class User(Model):
    id = IntegerField(primary_key=True)
    telegram_id = IntegerField(unique=True)
    username = CharField(null=True)
    chat_id = IntegerField(null=True)
    last_report_date_time = DateTimeField(null=True)

    class Meta:
        database = db


def create_tables():
    with db:
        db.create_tables([User])
