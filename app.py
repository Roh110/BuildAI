from flask import Flask, request, jsonify
from calculator import (
    calculate_workers,
    calculate_materials,
    calculate_cost,
    calculate_timeline
)
from ai_engine import get_ai_insights

app = Flask(__name__, static_folder="static", static_url_path="")

@app.route("/")
def serve_frontend():
    return app.send_static_file("index.html")

@app.route("/estimate", methods=["POST"])
def estimate():
    data = request.get_json()

    area = data.get("area")
    floors = data.get("floors")
    duration = data.get("duration")

    workers = calculate_workers(area, floors , duration)
    materials = calculate_materials(area, floors)
    cost = calculate_cost(area, floors)
    timeline = calculate_timeline(duration)

    prompt = f"""
    Area: {area} sq.ft
    Floors: {floors}
    Duration: {duration} days
    """

    ai_text = get_ai_insights(prompt)

    return jsonify({
        "calculations": {
            "workers": workers,
            "materials": materials,
            "cost": cost,
            "timeline": timeline
        },
        "ai_insights": ai_text
    })

if __name__ == "__main__":
    app.run(debug=True)