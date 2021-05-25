"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
from pydal.validators import IS_IN_SET

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A

from py4web.utils.auth import Auth
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user

url_signer = URLSigner(session)


# @unauthenticated("index", "index.html") # original skeleton
@action('index')
@action.uses(db, 'index.html')
def index():
    auth = Auth(extra_fields=[
        Field('user_type', requires=IS_IN_SET("Renter", "Landlord"))
    ])
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    return dict(
        message=message,
        load_reviews_url=URL('load_reviews', signer=url_signer),
        add_reviews_url=URL('add_reviews', signer=url_signer),
        delete_reviews_url=URL('delete_reviews', signer=url_signer),
        # get_thumbs_up_url=URL('get_thumbs_up', signer=url_signer),
        # get_thumbs_down_url=URL('get_thumbs_down', signer=url_signer),
        # set_thumbs_up_url=URL('set_thumbs_up', signer=url_signer),
        # set_thumbs_down_url=URL('set_thumbs_down', signer=url_signer),
        # get_thumbs_up_list_url=URL('get_thumbs_up_list', signer=url_signer),
        # get_thumbs_down_list_url=URL('get_thumbs_down_list', signer=url_signer),
    )


@action('load_reviews')
@action.uses(url_signer.verify(), db)
def load_reviews():
    rows = db(db.reviews).select().as_list()
    email = auth.get_user()['email']
    return dict(rows=rows, email=email)


@action('add_reviews', method="POST")
@action.uses(url_signer.verify(), db, auth, auth.user)
def add_reviews():
    renter = db(db.auth_user.email == get_user_email()).select().first()
    renter_id = renter.id if renter is not None else "Unknown"
    renter_email = renter.email
    reviews_score_friendliness=int(request.json.get('reviews_score_friendliness'))
    reviews_score_responsiveness=int(request.json.get('reviews_score_responsiveness'))
    reviews_property_address=request.json.get('reviews_property_address')
    reviews_score_overall=(reviews_score_friendliness+reviews_score_responsiveness)/2
    
    id = db.reviews.insert(
        reviews_renters_id=renter_id,
        renter_email = renter_email,
        # reviews_landlord_id=request.json.get('reviews_landlord_id'),
        # reviews_address_id=request.json.get('reviews_address_id'),
        reviews_contents=request.json.get('reviews_contents'),
        reviews_score_responsiveness=request.json.get('reviews_score_responsiveness'),
        reviews_score_friendliness=request.json.get('reviews_score_friendliness'),
        reviews_property_address=request.json.get('reviews_property_address'),
        reviews_score_overall=(reviews_score_friendliness+reviews_score_responsiveness)/2,
        # thumbs_up=request.json.get('thumbs_up'),
        # thumbs_down=request.json.get('thumbs_down'),
    )
    return dict(
        id=id, 
        renter_id=renter_id, 
        renter_email=renter_email,
        reviews_score_responsiveness=reviews_score_responsiveness,
        reviews_score_friendliness = reviews_score_friendliness,
        reviews_property_address= reviews_property_address,
        reviews_score_overall = reviews_score_overall,
    )


@action('delete_reviews')
@action.uses(url_signer.verify(), db)
def delete_reviews():
    id = request.params.get('id')
    assert id is not None
    db(db.reviews.id == id).delete()
    return "--REVIEW DELETED--"

# @action("signup", method=["GET", "POST"])
# @action.uses(db, session, auth, 'signup.html')
# def signup():
#     form = Form(auth, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         # username = form.vars['reviews_username']
#         # db(db.reviews.reviews_username == username).update(username=username)
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)


# @action('add_review', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'add_review.html')
# def add_review():
#     form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         # username = form.vars['reviews_username']
#         # db(db.reviews.reviews_username == username).update(username=username)
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)


@action('reviews', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'reviews.html')
def add_review():
    
    return dict(
        load_reviews_url = URL('load_reviews', signer=url_signer),
        add_reviews_url = URL('add_reviews', signer=url_signer),
        delete_reviews_url = URL('delete_reviews', signer=url_signer),
    )


# @action('add_address', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'add_review.html')
# def add_address():
#     form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         # username = form.vars['reviews_username']
#         # db(db.reviews.reviews_username == username).update(username=username)
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)


#----------------------------------------thumbs up/down code, uncomment when ready
# @action("get_thumbs_up")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_up():
#     rows = db((db.thumbs_up.each_review == request.params.get('id')) &
#               (db.thumbs_up.rater == get_user())).select().as_list()
#     if len(rows) == 0:
#         up = 0
#     else:
#         up = int(rows[0]['up'])
#     return dict(up=up)
#
#
# @action("get_thumbs_down")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_down():
#     rows = db((db.thumbs_down.each_review == request.params.get('id')) &
#               (db.thumbs_down.rater == get_user())).select().as_list()
#     if len(rows) == 0:
#         down = 0
#     else:
#         down = int(rows[0]['down'])
#     return dict(down=down)
#
#
# @action("set_thumbs_up", method="POST")
# @action.uses(url_signer.verify(), db)
# def set_thumbs_up():
#     id = request.json.get('id')
#     up = int(request.json.get('up'))
#
#     if up == 1:
#         db.thumbs_up.update_or_insert(
#             ((db.thumbs_up.each_review == id) & (db.thumbs_up.rater == get_user())),
#             each_post=id,
#             rater=get_user(),
#             up=up
#         )
#         db((db.thumbs_down.each_review == id) & (db.thumbs_down.rater == get_user())).delete()
#     else:
#         db((db.thumbs_up.each_review == id) & (db.thumbs_up.rater == get_user())).delete()
#     return "ok"
#
#
# @action("set_thumbs_down", method="POST")
# @action.uses(url_signer.verify(), db)
# def set_thumbs_down():
#     id = request.json.get('id')
#     down = int(request.json.get('down'))
#
#     if down == 1:
#         db.thumbs_down.update_or_insert(
#             ((db.thumbs_down.each_review == id) & (db.thumbs_down.rater == get_user())),
#             each_post=id,
#             rater=get_user(),
#             down=int(request.json.get('down'))
#         )
#         db((db.thumbs_up.each_review == id) & (db.thumbs_up.rater == get_user())).delete()
#     else:
#         db((db.thumbs_down.each_review == id) & (db.thumbs_down.rater == get_user())).delete()
#     return "ok"
#
#
# @action("get_thumbs_up_list")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_up_list():
#     row_index = int(request.params.row_idx)
#     rows = db(db.thumbs_up.each_review == row_index).select().as_list()
#     list_up = []
#     for r in rows:
#         userId = r['rater']
#         row2 = db(db.auth_user.id == userId).select().as_list()
#         list_up.append(row2[0]['first_name'] + " " + row2[0]['last_name'])
#
#     final_name = ", ".join(k for k in list_up)
#     if final_name != "":
#         final_name = "Liked by " + final_name
#
#     return dict(final_name=final_name)
#
#
# @action("get_thumbs_down_list")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_down_list():
#     row_index = int(request.params.row_idx)
#     rows = db(db.thumbs_down.each_review == row_index).select().as_list()
#     list_up = []
#     for r in rows:
#         userId = r['rater']
#         row2 = db(db.auth_user.id == userId).select().as_list()
#         list_up.append(row2[0]['first_name'] + " " + row2[0]['last_name'])
#
#     final_name = ", ".join(k for k in list_up)
#     if final_name != "":
#         final_name = "Disliked by " + final_name
#     return dict(final_name=final_name)
