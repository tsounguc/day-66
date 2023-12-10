import os
import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)
api_key = os.environ.get("api-key", "Couldn't find api-key")

# Cafe TABLE Configuration
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

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def get_random_cafe():
    if request.method == "GET":
        with app.app_context():
            cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
            random_cafe = random.choice(cafes)
            # return jsonify(
            #     cafe={
            #         "can_take_calls": random_cafe.can_take_calls,
            #         "coffee_price": random_cafe.coffee_price,
            #         "has_sockets": random_cafe.has_sockets,
            #         "has_toilet": random_cafe.has_toilet,
            #         "has_wifi": random_cafe.has_wifi,
            #         "id": random_cafe.id,
            #         "img_url": random_cafe.img_url,
            #         "location": random_cafe.location,
            #         "map_url": random_cafe.map_url,
            #         "name": random_cafe.name,
            #         "seats": random_cafe.seats,
            #     })

            return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=['GET'])
def get_all_cafes():
    with app.app_context():
        cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search", methods=['GET'])
def search():
    with app.app_context():
        loc = request.args.get("loc")
        results = db.session.execute(db.select(Cafe).where(Cafe.location == loc))
        cafes = results.scalars().all()
        if cafes:
            return jsonify(cafes=[cafe.to_dict() for cafe in cafes]), 200
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 4040


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def post_new_cafe():
    with app.app_context():
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.form.get('new_price')
    with app.app_context():
        cafe_to_update = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe_to_update:
            cafe_to_update.coffee_price = new_price
            db.session.commit()
            return jsonify(response={"success": "Successfully updated the price."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404



# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete(cafe_id):
    with app.app_context():

        api_key_from_request = request.form.get('api-key')
        cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if api_key_from_request is api_key:
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(response={"success":f"Cafe {cafe_id} successfully deleted"}), 200
            else:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            return jsonify(error= "Sorry, that's not allowed. Make sure you have the correct api-key"),404


if __name__ == '__main__':
    app.run(debug=True)
