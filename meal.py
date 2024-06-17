from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return render_template("index1.html")

@app.route("/generate_meal_plan", methods=["POST"])
def generate_meal_plan():
    try:
        # Retrieve form data
        time_frame = request.form.get("time_frame")
        target_calories = int(request.form.get("target_calories"))
        diet = request.form.get("diet")
        exclude = request.form.get("exclude")

        # Simulate generating meal plan (replace this with your actual generation logic)
        meal_plan = generate_meal_plan_logic(time_frame, target_calories, diet, exclude)

        # Return the meal plan as JSON
        return jsonify(meal_plan)

    except Exception as e:
        # Handle errors and return error response 
        return jsonify({"error": str(e)}), 400

def generate_meal_plan_logic(time_frame, target_calories, diet, exclude):
    # Replace this with your actual meal plan generation logic
    # This is a mock meal plan for demonstration purposes
    return {
        "meals": [
            {"title": "Meal 1", "readyInMinutes": 30, "servings": 4, "sourceUrl": "https://example.com/meal1"},
            {"title": "Meal 2", "readyInMinutes": 25, "servings": 3, "sourceUrl": "https://example.com/meal2"}
        ]
    }

if __name__ == "__main__":
    app.run(debug=True,port=9000)
