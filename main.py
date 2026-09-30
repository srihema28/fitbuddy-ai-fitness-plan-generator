import os
import json

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
from google import genai

from database import create_database, save_user


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="FitBuddy AI Fitness Plan Generator",
    description="AI powered fitness plan generator using Gemini",
    version="1.0"
)


# --------------------------------------------------
# Static files and templates
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# Database
# --------------------------------------------------

create_database()


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "result": None
    }
)


# --------------------------------------------------
# Generate Fitness Plan
# --------------------------------------------------

@app.post("/generate", response_class=HTMLResponse)
async def generate_plan(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):

    prompt = f"""
You are FitBuddy, an AI fitness assistant.

Create a personalized 7-day fitness plan.

User Details:
Name: {name}
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}
Workout Intensity: {intensity}

Create a simple beginner-friendly plan.

For each day provide:
Day
Workout
Duration
Rest/Recovery

Also provide:
1. Nutrition Tip
2. Recovery Tip
3. Safety Note

Important:
- Do not give extreme diets.
- Do not recommend unsafe exercises.
- Keep the plan practical.
- If the user has a medical condition, recommend consulting a qualified professional.

Return the answer in clear readable text.
"""


    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        workout_plan = response.text

    except Exception as error:

        workout_plan = (
            "Unable to connect to Gemini AI.\n\n"
            f"Error: {error}"
        )


    # --------------------------------------------------
    # Nutrition tip
    # --------------------------------------------------

    nutrition_prompt = f"""
Give one short nutrition and recovery tip for a person whose goal is:

{goal}

Weight: {weight} kg
Workout intensity: {intensity}

Keep it simple and safe.
"""

    try:

        nutrition_response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=nutrition_prompt
        )

        nutrition_tip = nutrition_response.text

    except Exception:

        nutrition_tip = (
            "Stay hydrated and maintain a balanced diet."
        )


    # --------------------------------------------------
    # Save data
    # --------------------------------------------------

    user_id = save_user(
        name,
        age,
        weight,
        goal,
        intensity,
        workout_plan,
        nutrition_tip
    )


    result = {
        "id": user_id,
        "name": name,
        "age": age,
        "weight": weight,
        "goal": goal,
        "intensity": intensity,
        "plan": workout_plan,
        "nutrition": nutrition_tip
    }


    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "result": result
    }
)

# --------------------------------------------------
# Feedback API
# --------------------------------------------------

@app.post("/feedback")
async def feedback(
    feedback: str = Form(...)
):

    prompt = f"""
You are FitBuddy AI.

A user gave the following feedback about their fitness plan:

{feedback}

Create an improved workout plan based on this feedback.

Keep the plan safe, simple and practical.

Include:
- 7-day workout plan
- Workout duration
- Rest days
- One recovery tip
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return {
            "success": True,
            "updated_plan": response.text
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }


# --------------------------------------------------
# Nutrition API
# --------------------------------------------------

@app.post("/nutrition")
async def nutrition(
    goal: str = Form(...)
):

    prompt = f"""
Give a short healthy nutrition or recovery tip
for a person whose fitness goal is:

{goal}

Give only practical and safe advice.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return {
            "success": True,
            "tip": response.text
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }