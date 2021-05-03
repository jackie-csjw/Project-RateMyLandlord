"""
This file defines the database models
"""

from .common import db, Field, auth, T
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_username():
    return auth.current_user.get('username') if auth.current_user else None

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


db.define_table(
    'renter_account',
    # TODO_complete: define the fields that are in the json.
    Field('account_username', default=get_username),
    # Field('account_password', requires=IS_NOT_EMPTY()), # get from auth.user
    Field('account_type', default='renter'),
    Field('account_email', default=get_user_email),
)

db.renter_account.account_type.readable = db.renter_account.account_type.writable = False
db.renter_account.account_username.readable = db.renter_account.account_username.writable = False


db.define_table(
    'landlord_account',
    # TODO_complete: define the fields that are in the json.
    Field('account_username', default=get_username),
    Field('account_first_name', requires=IS_NOT_EMPTY(error_message=T('Please enter a name'))),
    Field('account_last_name', requires=IS_NOT_EMPTY(error_message=T('Please enter a name'))),
    # Field('account_password', requires=IS_NOT_EMPTY()), # get from auth.user
    Field('account_type', default='landlord'),
    Field('account_email', default=get_user_email),
)

db.landlord_account.account_type.readable = db.landlord_account.account_type.writable = False
db.landlord_account.account_username.readable = db.landlord_account.account_username.writable = False

db.define_table(
    'reviews',
    # TODO_complete: define the fields that are in the json.
    Field('reviews_renters_username', 'reference renter_account', default=get_username),
    Field('reviews_landlord_first_name', 'reference landlord_account'),
    Field('reviews_landlord_last_name', 'reference landlord_account'),
    Field('reviews_contents', requires=IS_NOT_EMPTY(error_message=T('Review cannot be empty'))),
    Field('reviews_score_overall', default='0'),
    Field('reviews_score_responsiveness', default='0'),
    Field('reviews_score_friendliness', default='0'),
    Field('reviews_property_address', requires=IS_NOT_EMPTY(error_message=T('Property Address Required'))),
    Field('thumbs_up', default='0'),
    Field('thumbs_down', defualt='0'),
)

db.reviews.reviews_username.readable = db.reviews.reviews_username.writable = False
db.reviews.thumbs_up.readable = db.reviews.thumbs_up.writable = False
db.reviews.thumbs_down.readable = db.reviews.thumbs_down.writable = False


db.define_table(
    'review_replies',
    Field('reply', requires=IS_NOT_EMPTY(error_message=T('Reply cannot be empty'))),
    # Field('username', 'reference account', default=get_username),
    Field('review_id', 'reference reviews'),
)


db.commit()
