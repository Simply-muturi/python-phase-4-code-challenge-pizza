#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.get("/restaurants")
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_data = [
        restaurant.to_dict(only=("id", "name", "address"))
        for restaurant in restaurants
    ]
    return make_response(restaurant_data, 200)


@app.get("/restaurants/<int:id>")
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    return make_response(restaurant.to_dict(), 200)


@app.delete("/restaurants/<int:id>")
def delete_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    db.session.delete(restaurant)
    db.session.commit()

    return make_response("", 204)


@app.get("/pizzas")
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_data = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]
    return make_response(pizza_data, 200)


@app.post("/restaurant_pizzas")
def create_restaurant_pizza():
    data = request.get_json() or {}

    try:
        restaurant_pizza = RestaurantPizza(
            price=data.get("price"),
            pizza_id=data.get("pizza_id"),
            restaurant_id=data.get("restaurant_id"),
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return make_response({"errors": ["validation errors"]}, 400)

    return make_response(
        restaurant_pizza.to_dict(
            only=(
                "id",
                "price",
                "pizza_id",
                "restaurant_id",
                "pizza.id",
                "pizza.name",
                "pizza.ingredients",
                "restaurant.id",
                "restaurant.name",
                "restaurant.address",
            )
        ),
        201,
    )


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(port=5555, debug=True)
