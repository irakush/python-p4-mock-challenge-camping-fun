#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def home():
    return ""


######################### CAMPERS ###########################


@app.route("/campers", methods=["GET", "POST"])
def campers():
    if request.method == "GET":
        campers = Camper.query.all()
        # add rules = ("-singups", )
        response = make_response(
            [camper.to_dict(rules=("-signups",)) for camper in campers], 200
        )
    elif request.method == "POST":
        try:
            form_data = request.get_json()

            new_camper = Camper(name=form_data["name"], age=form_data["age"])

            db.session.add(new_camper)
            db.session.commit()

            response = make_response(new_camper.to_dict(), 201)
        except ValueError:
            response = make_response({"errors": ["validation errors"]}, 400)

    return response


@app.route("/campers/<int:id>", methods=["GET", "PATCH"])
def campers_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        if request.method == "GET":
            response = make_response(camper.to_dict(), 200)
        elif request.method == "PATCH":
            try:
                form_data = request.get_json()
                for attr in form_data:
                    setattr(camper, attr, form_data[attr])

                db.session.commit()

                response = make_response(camper.to_dict(), 202)
            except ValueError:
                response = make_response({"errors": ["validation errors"]}, 400)
    else:
        response = make_response({"error": "Camper not found"}, 404)

    return response


######################### ACTIVITIES ###########################


@app.route("/activities", methods=["GET"])
def activities():
    activities = []

    for activity in Activity.query.all():
        # add rules = ("-singups", )
        activities.append(activity.to_dict(rules=("-signups",)))

    response = make_response(activities, 200)

    return response


@app.route("/activities/<int:id>", methods=["DELETE"])
def activities_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if activity:
        assoc_signups = Signup.query.filter(Signup.id == id).all()
        for assoc_signup in assoc_signups:
            db.session.delete(assoc_signup)

        db.session.delete(activity)
        db.session.commit()

        response = make_response({}, 204)

    else:
        response = make_response({"error": "Activity not found"}, 404)

    return response


######################### SIGNUPS ###########################


@app.route("/signups", methods=["POST"])
def signups():
    try:
        form_data = request.get_json()

        new_signup = Signup(
            time=form_data["time"],
            camper_id=form_data["camper_id"],
            activity_id=form_data["activity_id"],
        )

        db.session.add(new_signup)
        db.session.commit()

        response = make_response(new_signup.to_dict(), 201)
    except ValueError:
        response = make_response({"errors": ["validation errors"]}, 400)

    return response


if __name__ == "__main__":
    app.run(port=5555, debug=True)
