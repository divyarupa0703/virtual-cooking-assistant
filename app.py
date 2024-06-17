from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///recipe.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)

    def to_dictionary(self):
        return {"id": self.id, "name": self.name, "category": self.category}

# Routes for managing recipes
@app.route("/recipe", methods=["GET", "POST"])
def manage_recipes():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        new_recipe = Recipe(name=name, category=category)
        db.session.add(new_recipe)
        db.session.commit()
        return redirect("/recipe")

    elif request.method == "GET":
        recipes = Recipe.query.all()
        return render_template("recipes.html", recipes=recipes)

@app.route("/recipe/delete/<int:id>", methods=["POST"])
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect("/recipe")

# Other routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/voice")
def voice():
    return render_template("voiceassistant.html")

@app.route("/classic")
def classic():
    return render_template("classicmode.html")

@app.route("/suggested_recipes", methods=["POST"])
def suggested_recipes():
    try:
        if request.content_type == "application/json":
            data = request.get_json()
            transcript = data.get("transcript")
            ingredients = extract_ingredients(transcript)
        else:
            command = request.form.get("command")
            ingredients = extract_ingredients(command)

        recipes = fetch_recipes_from_api(ingredients)
        return display_recipe_titles(recipes)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/recipe_details", methods=["GET"])
def recipe_details_by_name():
    if request.method == "GET":
        try:
            recipe_name = request.args.get("recipe_name")
            recipe_id = fetch_recipe_details(recipe_name)
            instructions = fetch_recipe_instructions(recipe_id)
            return jsonify({"recipe_name": recipe_name, "instructions": instructions})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

# Helper functions
def extract_ingredients(transcript):
    if transcript:
        words = transcript.split()
        recipe_index = words.index("recipe")
        ingredients = words[recipe_index + 1:]
        return ingredients

def fetch_recipe_details(recipe_name):
    try:
        api_key = "239d300aa2114326afd1de51d554487f"
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": recipe_name,
            "apiKey": api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        recipes = response.json()

        if recipes:
            recipe_id = recipes[0]["id"]
            return recipe_id
        else:
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching recipe details:", e)
        return None

def fetch_recipe_instructions(recipe_id):
    try:
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        api_key = "239d300aa2114326afd1de51d554487f"
        params = {"apiKey": api_key}

        response = requests.get(url, params=params)
        response.raise_for_status()
        recipe_info = response.json()
        instructions = recipe_info.get("instructions")
        if instructions:
            if "<" in instructions:
                soup = BeautifulSoup(instructions, "html.parser")
                cleaned_instructions = soup.get_text(separator="\n")
                return cleaned_instructions.split("\n")
            else:
                return instructions.split("\n")
        else:
            return []
    except requests.exceptions.RequestException as e:
        print("Error fetching recipe instructions:", e)
        return []

def fetch_recipes_from_api(ingredients):
    try:
        api_key = "79f3f6a6967f448da625f1a503b055bd"
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": ",".join(ingredients),
            "apiKey": api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        recipes = response.json()
        prepared_recipes = []
        for recipe in recipes:
            title = recipe.get("title", "")
            missed_ingredients = recipe.get("missedIngredients", [])
            instructions = fetch_recipe_instructions(recipe["id"])
            preparation_time = recipe.get("readyInMinutes", 0)
            nutritional_info = fetch_nutrition_from_dish_name(recipe["title"])
            prepared_recipe = Recipe(title, missed_ingredients, instructions, preparation_time, nutritional_info)
            prepared_recipes.append(prepared_recipe)
        return prepared_recipes
    except requests.exceptions.RequestException as e:
        print("Error fetching recipes:", e)
        return []
    
def fetch_nutrition_from_dish_name(dish_name):
    try:
        api_key = "79f3f6a6967f448da625f1a503b055bd"
        endpoint = "https://api.spoonacular.com/recipes/guessNutrition"
        params = {
            "title": dish_name,
            "apiKey": api_key
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (status codes >= 400)
        nutrition_data = response.json()
        return nutrition_data
    except requests.exceptions.RequestException as e:
        print("Error fetching nutrition data:", e)
        return None
    
def extract_ingredients(command):
    # Initialize an empty list to store ingredients
    ingredients = []
    
    if command:
        words = command.split()
        if "recipe" in words:
            recipe_index = words.index("recipe")
            ingredients = words[recipe_index + 1:]
    return ingredients
    

def display_recipe_titles(recipes):
    recipe_titles = [recipe.title for recipe in recipes]
    return jsonify({"success": "Suggested Recipes", "recipe_titles": recipe_titles})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
