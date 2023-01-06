from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
# import os

app = Flask(__name__)
# CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://udxcllujktanec:5ae9a95ef7f2841a391e79e15015dcf1b1fa22c0bc561570770b702a4373a5f4@ec2-52-203-118-49.compute-1.amazonaws.com:5432/dfhp0uqgd5l88k'

# baseddir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseddir, 'app.sqlite')

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Shoe(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    shoe_img = db.Column(db.String, unique=True)
    description = db.Column(db.String)

    def __init__(self, name, shoe_img, description):
        self.name = name
        self.shoe_img = shoe_img
        self.description = description

class ShoeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'shoe_img', 'description')

shoe_schema = ShoeSchema()
many_shoe_schema = ShoeSchema(many=True)

@app.route('/shoe/add', methods=["POST"])
def add_shoe():
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    name = post_data.get('name')
    shoe_img = post_data.get('shoe_img')
    description = post_data.get('description')
    
    if name == None:
        return jsonify('Error: Name is required')

    if description == None:
        return jsonify('Error: Description is required')

    new_shoe = Shoe(name, shoe_img, description)
    db.session.add(new_shoe)
    db.session.commit()

    return jsonify(shoe_schema.dump(new_shoe))

@app.route('/shoe/get', methods=["GET"])
def get_shoe():
    all_shoes = db.session.query(Shoe).all()
    return jsonify(many_shoe_schema.dump(all_shoes))

@app.route('/shoe/get/<id>', methods=["GET"])
def get_one_shoe(id):
    one_shoe = db.session.query(Shoe).filter(Shoe.id  == id).first()
    return jsonify(shoe_schema.dump(one_shoe))

@app.route('/shoe/edit/<id>', methods=["POST"])
def edit_shoe(id):
    if request.content_type != 'application/json':
        return jsonify('Error: Send data as json')

    put_data = request.get_json()
    name = put_data.get('name')
    shoe_img = put_data.get('shoe_img')
    description = put_data.get('description')

    edit_shoe = db.session.query(Shoe).filter(Shoe.id == id).first()

    if name != None:
        edit_shoe.name = name
    if shoe_img != None:
        edit_shoe.shoe_img = shoe_img
    if description != None:
        edit_shoe.description = description

    db.session.commit()

    return jsonify(shoe_schema.dump(edit_shoe))

@app.route('/shoe/delete/<id>', methods=["DELETE"])
def delete_shoe(id):
    delete_shoe = db.session.query(Shoe).filter(Shoe.id == id).first()
    db.session.delete(delete_shoe)
    db.session.commit()

    return jsonify('Shoe Has Been Deleted')

@app.route('/shoe/add/many', methods=["Post"])
def add_many_shoes():
    if request.content_type != "application/json":
        return jsonify("Error: Send Data as Json to Proceed")
    
    post_data = request.get_json()
    shoes = post_data.get("shoes")

    new_shoes = []

    for shoe in shoes:
        name = shoe.get('name')
        shoe_img = shoe.get('shoe_img')
        description = shoe.get('description')

        existing_shoe_check = db.session.query(Shoe).filter(Shoe.name == name).first()
        if existing_shoe_check is None:
            new_shoe = Shoe(name, shoe_img, description)
            db.session.add(new_shoe)
            db.session.commit()
            new_shoes.append(new_shoe)
        
    return jsonify(many_shoe_schema.dump(new_shoes))




if __name__ == '__main__':
    app.run(debug=True)