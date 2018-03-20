# app/main/views.py

import requests
from flask import render_template, session, redirect, url_for, current_app, jsonify, request, flash, app
from flask import Flask, request
from flask import json
from .. import db
from datetime import datetime
from app.interactive import interactive
from ..models import  Catalog, Interactive, Car_type, Tour_type, User
from .. import csrf
from forms import InteractiveForm
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email
from flask import current_app
import stripe, os
from flask import current_app

stripe_keys = {
  'secret_key': 'sk_test_uxtuIOeAfAyn2AYpImH7Mjft',
  'publishable_key': 'pk_test_sRa1igLaBVBHhNtVkUPAyBAi'
}
stripe.api_key = stripe_keys['secret_key']


@interactive.route('/stripecharge', methods=['POST'])
@login_required
def stripecharge():

    id = request.form['id']
    interactive = Interactive.query.get_or_404(id)
    customer = stripe.Customer.create(
        email = current_app.config['MAIL_USERNAME'],
        source=request.form['stripeToken'])
    
    # print customer.id
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=int(interactive.total_price * 10),
        currency='usd',
        description='ByTaiwan Patment'
    )
    # print charge
    if charge['paid'] == True :
        #charge['customer'] + '-' + charge['id']
        #update paied,date
        interactive.payment_id = charge['customer'] + '-' + charge['id']
        interactive.payment_datetime = datetime.utcnow()
        interactive.payment_email = charge['source']['name']
        interactive.paied =True
        user = User.query.filter_by(id=current_user.id).first()
        send_email(charge['source']['name'], 'Pay tour ', 'interactive/email/pay', user=user, interactive=interactive)
        send_email(user.email, 'Pay tour ', 'interactive/email/pay', user=user, interactive=interactive)
        send_email(current_app.config['MAIL_USERNAME'], 'Pay tour ', 'interactive/email/pay', user=user, interactive=interactive)
        db.session.commit()
        flash('Pay ID:%s Created! Shipout ASAP.' % (charge['customer'] + '-' + charge['id']))
    return redirect(url_for('interactive.history'))

@interactive.route("/submit/<int:id>", methods=['GET'])
@login_required
def submit(id):
    
    interactive = Interactive.query.get_or_404(id)
    interactive.ordered = True
    db.session.commit()
    user = User.query.filter_by(id=current_user.id).first()
    send_email(current_app.config['MAIL_USERNAME'], 'Submit tour', 'interactive/email/submit', user=user, interactive=interactive)
    catalogs = Catalog.get_all()
    return redirect(url_for('interactive.list'))

@interactive.route("/pay/<int:id>", methods=['GET'])
@login_required
def pay(id):
    
    interactive = Interactive.query.get_or_404(id)
    catalogs = Catalog.get_all()
    return render_template('interactive/pay_tour.html',
                        catalogs=catalogs, interactive = interactive, publishkey=stripe_keys['publishable_key'] , title="Pay Tour")

@interactive.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    """Return page showing all the products has to offer"""
    form = InteractiveForm()
    if form.validate_on_submit():
        rows = Interactive.query.filter_by(userid = current_user.id, paied = False).count()
        if (rows == 5):
            flash("Your couldn't add tours more than 5 times.")
            return redirect(url_for('interactive.list'))
        interactive = Interactive(
        car_type=Car_type.query.filter_by(value=str(form.car_type.data.value)).first().id,
        tour_type=Tour_type.query.filter_by(value=str(form.tour_type.data.value)).first().id,
        tour_date=request.form.get("tour_date", ""),
        tour_guide=form.tour_guide.data,
        total_price=request.form.get('total'),
        userid = current_user.id)
        db.session.add(interactive)
        db.session.commit()
        flash('Add tour successfull.')

        return redirect(url_for('interactive.list'))
    # pre setting value
    catalogs = Catalog.get_all()
    return render_template('interactive/create_tour.html', form=form,
                            catalogs=catalogs, title="Add Tour")

@interactive.route("/remove/<int:id>", methods=['GET'])
@login_required
def remove(id):
    
    interactive = Interactive.query.get_or_404(id)
    db.session.delete(interactive)
    db.session.commit()
    return redirect(url_for('interactive.list'))
    
@interactive.route("/list", methods=['GET'])
@login_required
def list():
    
    interactives = Interactive.query.filter_by(userid = current_user.id, paied = False).order_by(Interactive.id.desc())
    catalogs = Catalog.get_all()
    return render_template('interactive/list_tour.html',
                        catalogs=catalogs, interactives = interactives, title="List Tour")


@interactive.route("/history", methods=['GET'])
@login_required
def history():
    interactives = Interactive.query.filter_by(userid=current_user.id, paied=True).order_by(Interactive.id.desc())

    catalogs = Catalog.get_all()
    return render_template('interactive/list_tour.html',
                           catalogs=catalogs, interactives=interactives, title="List Paied Tour")