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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    return dict(message=message)

@unauthenticated("reviews", "reviews.html")
def reviews():
    form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
    return dict(form=form)

@action('add_review', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_review.html')
def add_review():
    form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We simply redirect; the insertion already happened.
        # username = form.vars['reviews_username']
        # db(db.reviews.reviews_username == username).update(username=username)
        redirect(URL('index'))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=form)


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

