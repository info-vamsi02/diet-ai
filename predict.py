import random

def generate_meal_plan(guide):
    foods = guide["recommended_foods"]

    def meal():
        return random.choice(foods)

    return {
        "Monday": f"{meal()} + {meal()} + {meal()}",
        "Tuesday": f"{meal()} + {meal()} + {meal()}",
        "Wednesday": f"{meal()} + {meal()} + {meal()}",
        "Thursday": f"{meal()} + {meal()} + {meal()}",
        "Friday": f"{meal()} + {meal()} + {meal()}",
        "Saturday": f"{meal()} + {meal()} + {meal()}",
        "Sunday": f"{meal()} + {meal()} + {meal()}"
    }

def predict_diet(age, bmi, diseases, activity, gender,
                 personalized=None, include_foods=None, exclude_foods=None):

    bmi = float(bmi)

    if bmi > 25:
        diet = "Low_Carb"
    elif "Hypertension" in diseases:
        diet = "Low_Sodium"
    else:
        diet = "Balanced"

    guide = {
        "calories": "2000 kcal",
        "protein": "70g",
        "carbohydrates": "250g",
        "fat": "60g",
        "vitamins": "A, B, C",
        "recommended_foods": ["Rice","Fruits","Vegetables","Eggs"],
        "foods_to_avoid": ["Junk food","Sugar"]
    }

    if personalized == "yes":
        guide["weekly_plan"] = generate_meal_plan(guide)
        guide["note"] = "AI Personalized Plan"

    return diet, guide