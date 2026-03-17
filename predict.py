import torch
import pickle
import random
from transformers import BertTokenizer, BertForSequenceClassification

# LOAD MODEL
tokenizer = BertTokenizer.from_pretrained("saved_model")
model = BertForSequenceClassification.from_pretrained("saved_model")

# LOAD LABEL ENCODER
le = pickle.load(open("saved_model/label_encoder.pkl","rb"))

# ---------------- DIET GUIDES ----------------
diet_guides = {

"Balanced":{
"calories":"2000 kcal/day",
"protein":"70 g/day",
"carbohydrates":"250 g/day",
"fat":"60 g/day",
"vitamins":"Vitamin A, C, D, Iron",

"recommended_foods":[
"Brown rice","Oats","Eggs","Milk","Fruits",
"Vegetables","Almonds"
],

"foods_to_avoid":[
"Junk food","Sugary drinks"
]
},

"Low_Carb":{
"calories":"1500 kcal/day",
"protein":"90 g/day",
"carbohydrates":"80 g/day",
"fat":"70 g/day",
"vitamins":"Vitamin B, D",

"recommended_foods":[
"Eggs","Chicken","Paneer","Tofu",
"Leafy vegetables","Nuts"
],

"foods_to_avoid":[
"Rice","Bread","Pasta","Sugar"
]
},

"Low_Sodium":{
"calories":"1800 kcal/day",
"protein":"75 g/day",
"carbohydrates":"220 g/day",
"fat":"55 g/day",
"vitamins":"Vitamin C, Magnesium",

"recommended_foods":[
"Fruits","Vegetables","Oats",
"Brown rice","Lentils"
],

"foods_to_avoid":[
"Salt","Pickles","Processed food"
]
}

}

# -------- AI MEAL PLANNER --------
def generate_meal_plan(guide):

    foods = guide["recommended_foods"]
    avoid = guide["foods_to_avoid"]

    safe_foods = [f for f in foods if f not in avoid]

    if len(safe_foods) < 3:
        safe_foods = foods

    def meal():
        return random.choice(safe_foods)

    return {
        "Monday": f"{meal()} + {meal()} + {meal()}",
        "Tuesday": f"{meal()} + {meal()} + {meal()}",
        "Wednesday": f"{meal()} + {meal()} + {meal()}",
        "Thursday": f"{meal()} + {meal()} + {meal()}",
        "Friday": f"{meal()} + {meal()} + {meal()}",
        "Saturday": f"{meal()} + {meal()} + {meal()}",
        "Sunday": f"{meal()} + {meal()} + {meal()}"
    }

# ---------------- MAIN FUNCTION ----------------
def predict_diet(age, bmi, diseases, activity, gender, personalized=None,
                 include_foods=None, exclude_foods=None):

    text = f"Age {age}, Gender {gender}, BMI {bmi}, Diseases {','.join(diseases)}, Activity {activity}"

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)

    pred = torch.argmax(outputs.logits).item()
    diet = le.inverse_transform([pred])[0]

    guide = diet_guides[diet].copy()
    guide["recommended_foods"] = guide["recommended_foods"].copy()
    guide["foods_to_avoid"] = guide["foods_to_avoid"].copy()

    # ---------------- PERSONALIZATION ----------------
    if personalized == "yes":

        bmi = float(bmi)

        # Gender
        if gender == "Male":
            guide["calories"] = "2200–2800 kcal/day"
        else:
            guide["calories"] = "1600–2200 kcal/day"

        # BMI
        if bmi > 25:
            guide["calories"] = "1200–1500 kcal/day"

        # Diseases
        for d in diseases:
            if d == "Diabetes":
                guide["foods_to_avoid"] += ["Sugar"]
            elif d == "Hypertension":
                guide["foods_to_avoid"] += ["Salt"]

        # User preferences
        if include_foods:
            guide["recommended_foods"] += [f.strip() for f in include_foods.split(",")]

        if exclude_foods:
            guide["foods_to_avoid"] += [f.strip() for f in exclude_foods.split(",")]

        # Remove duplicates
        guide["recommended_foods"] = list(set(guide["recommended_foods"]))
        guide["foods_to_avoid"] = list(set(guide["foods_to_avoid"]))

        # AI Meal Plan
        guide["weekly_plan"] = generate_meal_plan(guide)
        guide["note"] = "AI Personalized Diet Plan"

    return diet, guide