from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.models import Ingredient
from playhouse.shortcuts import model_to_dict


ingredient_bp = Blueprint('ingredient_bp', __name__)

@ingredient_bp.route('/', methods=['GET', 'POST'])
def get_ingredients():
    if request.method == 'GET':
        ingredients = Ingredient.select()
        ingredient_data = [ingredient.__dict__['__data__'] for ingredient in ingredients]

        return jsonify(ingredient_data)
    elif request.method == 'POST':
        data = request.json
        ingredient = Ingredient(
            name = data['name'],
            food_type = data['food_type']
        )
        try:
            ingredient.save()
        # TODO: have more specific error handling logic
        except Exception as e:
            print(f'Error: {e}')
        return jsonify(model_to_dict(ingredient)), 201
    return ''
