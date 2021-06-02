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
import random
url_signer = URLSigner(session)


# @unauthenticated("index", "index.html") # original skeleton
@action('index')
@action.uses(db, 'index.html')
def index():
    auth = Auth(session, db, extra_fields=[
        Field('user_type', requires=IS_IN_SET("Renter", "Landlord"))
    ])
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")

    landlord_count = db(db.landlord).count()
    print(landlord_count)
    if(landlord_count > 1):
        random_landlords = random.sample(range(1, landlord_count+1), 2)
    else: # if there is only one landlord populate page with the only landlord twice
        random_landlords = [1, 1]
    print(random_landlords)

    example_landlord1 = db.landlord[random_landlords[0]]
    example_landlord1_name = example_landlord1.first_name + " " + example_landlord1.last_name
    rows1 = db(
        (db.reviews.reviews_landlordID == 1)
    ).select().first()


    example_landlord2 = db.landlord[random_landlords[1]]
    example_landlord2_name = example_landlord2.first_name + " " + example_landlord2.last_name
    rows2 = db(
        (db.reviews.reviews_landlordID == 2)
    ).select().first()

    return dict(
        message=message,
        load_reviews_url=URL('load_reviews', signer=url_signer),
        add_reviews_url=URL('add_reviews', signer=url_signer),
        delete_reviews_url=URL('delete_reviews', signer=url_signer),
        search_url=URL('search', signer=url_signer),
        example_landlord1=example_landlord1,
        example_landlord1_name=example_landlord1_name,
        example_landlord2=example_landlord2,
        example_landlord2_name=example_landlord2_name,
        rows1=rows1,
        rows2=rows2
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

@action('dashboard_landlord')
@action.uses(url_signer.verify(), db)
def dashboard_landlord():

    return dict()

@action('dashboard_user')
@action.uses(db, session, auth.user, 'dashboard_user.html')
def dashboard_user():

    return dict(
        load_reviews_url = URL('load_reviews', signer=url_signer),
        add_reviews_url = URL('add_reviews', signer=url_signer),
        delete_reviews_url = URL('delete_reviews', signer=url_signer),
    )


""" previous version
@action('reviews', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'reviews.html')
def reviews():
    
    return dict(
        load_reviews_url = URL('load_reviews', signer=url_signer),
        add_reviews_url = URL('add_reviews', signer=url_signer),
        delete_reviews_url = URL('delete_reviews', signer=url_signer),
    )
"""

@action('reviews/<landlord_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'reviews.html')
def reviews(landlord_id=None):
    assert landlord_id is not None
    landlord = db.landlord[landlord_id]
    landlord_name = landlord.first_name + " " + landlord.last_name
    
    landlordID = landlord_id
    session['landlordID'] = landlord_id
    
    rows = db(
        (db.reviews.reviews_landlordID == landlord_id)
    ).select() # as list
    
    num_rows = db(
        (db.reviews.reviews_landlordID == landlord_id)
    ).count()
    
    avg_overall = 0;
    avg_friend = 0;
    avg_resp = 0;

    for r in rows:
        #print(r.reviews_score_overall)
        avg_overall += float(r.reviews_score_overall)
        avg_friend += float(r.reviews_score_friendliness)
        avg_resp += float(r.reviews_score_responsiveness)
    
    print(avg_overall)
    print(num_rows)

    avg_overall = round(avg_overall/num_rows)
    avg_friend = round(avg_friend/num_rows)
    avg_resp = round(avg_resp/num_rows)
    
    return dict(
        avg_overall = avg_overall,
        avg_friend = avg_friend,
        avg_resp = avg_resp,
        landlordID = landlordID,
        landlord_name = landlord_name,
        load_reviews_url = URL('load_reviews', signer=url_signer),
        add_reviews_url = URL('add_reviews', signer=url_signer),
        delete_reviews_url = URL('delete_reviews', signer=url_signer),
    )

@action('add_reviews', method=["GET", "POST"])
@action.uses(url_signer.verify(), db, auth, auth.user)
def add_reviews():
    #assert landlord_id is not None
    #landlord = db.landlord.id

    renter = db(db.auth_user.email == get_user_email()).select().first()
    renter_id = renter.id if renter is not None else "Unknown"
    renter_email = renter.email
    reviews_landlordID = int(session.get('landlordID', None))
    #reviews_landlordID = request.json.get('reviews_landlordID')
    reviews_score_friendliness=int(request.json.get('reviews_score_friendliness'))
    reviews_score_responsiveness=int(request.json.get('reviews_score_responsiveness'))
    reviews_property_address=request.json.get('reviews_property_address')
    reviews_score_overall=(reviews_score_friendliness+reviews_score_responsiveness)/2
    reviews_contents=request.json.get('reviews_contents')

    id = db.reviews.insert(
        reviews_renters_id=renter_id,
        renter_email = renter_email,
        reviews_landlordID = reviews_landlordID,
        #reviews_landlordID=request.json.get('reviews_landlordID'),
        reviews_address_id=request.json.get('reviews_address_id'),
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
        reviews_landlordID = reviews_landlordID,
        renter_id=renter_id, 
        renter_email=renter_email,
        reviews_score_responsiveness=reviews_score_responsiveness,
        reviews_score_friendliness = reviews_score_friendliness,
        reviews_property_address= reviews_property_address,
        reviews_score_overall = reviews_score_overall,
        reviews_contents = reviews_contents,
    )


@action('delete_reviews')
@action.uses(url_signer.verify(), db)
def delete_reviews():
    id = request.params.get('id')
    assert id is not None
    db(db.reviews.id == id).delete()
    return "--REVIEW DELETED--"


@action('add_landlord', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_landlord.html')
def add_landlord():
    form = Form(db.landlord, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        ## CODE TO CREATE URL FOR REVIEW PAGE HERE
        redirect(URL('index')) # change this later to redirect to landlord page
    return dict(form=form)


@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    rows = db(db.landlord).select().as_list()
    # if
    results = db(db.landlord).select().as_list()
    # results = ['name']
    # results = [q + ":" + str(uuid.uuid1()) for _ in range(random.randint(2, 6))]
    return dict(results=results)


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
