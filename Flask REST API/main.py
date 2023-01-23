from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

# CREATE SQLITE3 DATABASE:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# CREATE TABLE:
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # ability to convert into dict:
    def to_dict(self):
        final_dictionary = {}
        for each_column in self.__table__.columns:
            final_dictionary[each_column.name] = getattr(self, each_column.name)
        return final_dictionary


# ROUTING:
@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/random")
def random_page():
    cafe = db.session.query(Cafe).all()
    random_cafe = choice(cafe)
    return jsonify(
        cafe={
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
            "has_sockets": random_cafe.has_sockets,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "id": random_cafe.id,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "map_url": random_cafe.map_url,
            "name": random_cafe.name,
            "seats": random_cafe.seats
        }
    )


@app.route("/all")
def all_page():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(
        cafes=[cafe.to_dict() for cafe in all_cafes]
    )


@app.route("/search")
def search_page():
    chosen_location = request.args.get("loc")
    if chosen_location:
        loc_data = db.session.query(Cafe).filter_by(location=chosen_location)
        final_result = [item.to_dict() for item in loc_data]
        if len(final_result) > 0:
            return jsonify(
                cafe=final_result
            )
        else:
            return jsonify(
                error={
                    "Not Found": "Sorry, we don't have a cafe at that location."
                }
            )
    else:
        return "<b>Without Search Parameter</b>"


# HTTP POST - CREATE RECORD
@app.route("/add", methods=["POST"])
def add_page():
    new_cafe = Cafe(
        can_take_calls=request.json["can_take_calls"],
        coffee_price=request.json["coffee_price"],
        has_sockets=request.json["has_sockets"],
        has_toilet=request.json["has_toilet"],
        has_wifi=request.json["has_wifi"],
        img_url=request.json["img_url"],
        location=request.json["location"],
        map_url=request.json["map_url"],
        name=request.json["name"],
        seats=request.json["seats"],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(
        response={
            "success": "Successfully added the new Cafe."
        }
    )


# HTTP PUT/PATCH - UPDATE RECORD
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price_page(cafe_id):
    update_record = Cafe.query.get(cafe_id)
    if update_record:
        update_record.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(
            success={
                "Message": "Coffee price has been updated successfully!",
                "Status Code": 200
            }
        )
    else:
        return jsonify(
            error={
                "Message": "Sorry a cafe with that id was not found in the database.",
                "Status Code": 404
            }
        )


# HTTP DELETE - DELETE RECORD
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_page(cafe_id):
    my_api_key = "TommyShelby"
    user_key = request.args.get("api_key")
    if my_api_key == user_key:
        delete_record = Cafe.query.get(cafe_id)
        if delete_record:
            db.session.delete(delete_record)
            db.session.commit()
            return jsonify(
                success={
                    "Message": "Coffee Shop has been deleted successfully!",
                    "Status Code": 200
                }
            )
        else:
            return jsonify(
                error={
                    "Message": "Sorry a cafe with that id was not found in the database.",
                    "Status Code": 404
                }
            )
    else:
        return jsonify(
            error={
                "error": "Sorry, that's not allowed. Make sure you have the correct api_key!",
                "Status Code": 403
            }
        )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
