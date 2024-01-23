from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
import csv


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    coffee_rating = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("Cafe Location", validators=[DataRequired()])
    map_url = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    can_take_calls = StringField('Can take calls')
    coffee_rating = SelectField("Coffee Rating", choices=["☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"], validators=[DataRequired()])
    has_wifi = SelectField("Wifi Strength Rating", choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"], validators=[DataRequired()])
    has_sockets = SelectField("Power Socket Availability", choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"], validators=[DataRequired()])
    submit = SubmitField('Submit')


class DeleteForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# all Flask routes below
@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    cafe_list = []
    for cafe in all_cafes:
        new_cafe = {"id": cafe.id,
                    "name": cafe.name,
                    "map_url": cafe.map_url,
                    "img_url": cafe.img_url,
                    "location": cafe.location,
                    "has_wifi": cafe.has_wifi,
                    "has_sockets": cafe.has_sockets,
                    "can_take_calls": cafe.can_take_calls,
                    "coffee_rating": cafe.coffee_rating,
                    "coffee_price": cafe.coffee_price}
        cafe_list.append(new_cafe)
    return render_template("index.html", cafes=cafe_list)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_cafe = Cafe(
            name=form.cafe.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            coffee_price=form.coffee_price.data,
            coffee_rating=form.coffee_rating.data
        )
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route("/cafes", methods=['GET', 'POST'])
def cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    cafe_list = []
    for cafe in all_cafes:
        new_cafe = {"id": cafe.id,
                    "name": cafe.name,
                    "map_url": cafe.map_url,
                    "img_url": cafe.img_url,
                    "location": cafe.location,
                    "has_wifi": cafe.has_wifi,
                    "has_sockets": cafe.has_sockets,
                    "can_take_calls": cafe.can_take_calls,
                    "coffee_rating": cafe.coffee_rating,
                    "coffee_price": cafe.coffee_price}
        cafe_list.append(new_cafe)
    return render_template('cafes.html', cafes=cafe_list)


@app.route("/update-price/<int:cafe_id>", methods=["GET", "PATCH"])
def update_price(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)

    if cafe is None:
        return jsonify({"error": f"Cafe with ID {cafe_id} not found"}), 404

    if request.method == "PATCH":
        new_price = request.form.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify({"message": "Coffee price updated successfully"})


@app.route("/report-closed", methods=["GET", "POST"])
def delete_cafe():
    form = DeleteForm()
    if form.validate_on_submit():
        name = form.cafe.data
        cafe = db.session.query(Cafe).filter(Cafe.name == name).first()

        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify({"message": "Cafe deleted successfully"}), 200
        else:
            return jsonify({"message": "Cafe not found"}), 404
    return render_template('delete.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, port=5002)


