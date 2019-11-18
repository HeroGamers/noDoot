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
    Invite_Channel = CharField()

    class Meta:
        database = db


async def add_user(userid, name, bot):
    try:
        User.create(UserID=userid, DiscordTag_at_Verification=name, Captcha_text="", Verification_Date="",
                    Verified=False, Invite_Channel="")
    except IntegrityError as e:
        await logger.log("DB Notice: ID Already Used! - " + str(e), bot, "DEBUG")


def remove_user(userid):
    query = User.delete().where(User.UserID == userid)
    query.execute()


def isUserVerified(userid):
    query = User.select().where((User.UserID.contains(str(userid))) & (User.Verified == True))
    if query.exists():
        return True
    return False


def verify_user(userid):
    date = datetime.datetime.now()
    query = User.update(Verified=True, Verification_Date=date).where(User.UserID == userid)
    query.execute()


def unverify_user(userid):
    query = User.update(Verified=False).where(User.UserID == userid)
    query.execute()


def add_captcha(userid, captchatext):
    query = User.update(Captcha_text=captchatext).where(User.UserID == userid)
    query.execute()


def get_captcha(userid):
    query = User.select().where(User.UserID == userid)
    try:
        return query[0].Captcha_text
    except IndexError:
        return "No Captcha"


def add_invite(userid, channelid):
    query = User.update(Invite_Channel=channelid).where(User.UserID == userid)
    query.execute()


def get_invite_channel(userid):
    query = User.select().where(User.UserID == userid)
    try:
        return query[0].Invite_Channel
    except IndexError:
        return ""


def count_verified_users():
    query = User.select().where(User.Verified == True).count()
    return query


def create_tables():
    with db:
        db.create_tables([User])


create_tables()
