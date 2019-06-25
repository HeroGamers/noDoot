from peewee import SqliteDatabase, Model, CharField, DateTimeField, BooleanField, IntegrityError
import datetime
from utilities import logger

db = SqliteDatabase('./verifiedUsers.db')

class User(Model):
    UserID = CharField(unique=True)
    DiscordTag_at_Verification = CharField()
    Captcha_text = CharField()
    Verification_Date = DateTimeField()
    Verified = BooleanField()

    class Meta:
        database = db

def add_user(userid, name):
    try:
        User.create(UserID=userid, DiscordTag_at_Verification=name, Captcha_text="", Verification_Date="", Verified=False)
    except IntegrityError as e:
        logger.logDebug("DB Notice: ID Already Used! - " + str(e), "DEBUG")

def remove_user(userid):
    query = User.delete().where(User.UserID == userid)
    query.execute()

def isUserVerified(userid):
    query = User.select().where((User.UserID == userid) & (User.Verified == True))
    if query.exists():
        return True
    return False

def verify_user(userid):
    date = datetime.datetime.now()
    query = User.update(Verified=True, Verification_Date=date).where(User.UserID == userid)
    query.execute()

def add_captcha(userid, captchatext):
    query = User.update(Captcha_text=captchatext).where(User.UserID == userid)
    query.execute()

def get_captcha(userid):
    query = User.select().where(User.UserID == userid)
    return query[0].Captcha_text

def create_tables():
    with db:
        db.create_tables([User])

create_tables()
