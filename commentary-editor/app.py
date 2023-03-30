import os
import openai
from flask import Flask, jsonify, request
import jsonschema

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the JSON schema
schema = {
    "type": "object",
    "properties": {
        "commentary": {"type": "string"},
        "rule": {"type": "string"},
        "context": {
            "type": "object",
            "properties": {
                "sport": {"type": "string"},
                "homeTeam": {"type": "string"},
                "awayTeam": {"type": "string"},
                "homeTeamScore": {"type": "integer", "minimum": 0},
                "awayTeamScore": {"type": "integer", "minimum": 0},
            },
            "required": [
                "sport",
                "homeTeam",
                "awayTeam",
                "homeTeamScore",
                "awayTeamScore",
            ],
        },
    },
    "required": ["commentary", "rule", "context"],
}


@app.route("/", methods=["POST"])
def commentary():
    # Validate JSON
    try:
        input_data = request.get_json()
        jsonschema.validate(instance=input_data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        # Return error message
        return jsonify({"error": str(err)}), 400

    # Parse arguments
    args = input_data
    context_args = input_data["context"]
    response = (
        openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(args, context_args),
            temperature=0.4,
            max_tokens=256,
        )
        .choices[0]
        .text.lstrip()
    )
    return jsonify(commentary=response), 200


def generate_prompt(args, context_args):
    sport = context_args.get("sport", "")
    ht = context_args.get("homeTeam", "")
    at = context_args.get("awayTeam", "")
    ht_score = context_args.get("homeTeamScore", 0)
    at_score = context_args.get("awayTeamScore", 0)
    com = args["commentary"]
    rule = args["rule"]
    return f"""rewrite the commentary using the described sentiment.
Sport: {sport}
Home team: {ht}
Away team: {at}
Home team score: {ht_score}
Away team score: {at_score}
Commentary: {com}
Sentiment: {rule}
"""


# useful resources
""" 
example JSON
{
    "commentary": "This is the commentary that you want to rewrite.",
    "rule": "This is the rule that you want to use for rewriting the commentary.",
    "context": {
        "sport": "The sport being played.",
        "homeTeam": "The name of the home team.",
        "awayTeam": "The name of the away team.",
        "homeTeamScore": 0,
        "awayTeamScore": 0
    }
}

{
  "commentary": "Attempt blocked. Luka Jovic (Real Madrid) header from the centre of the box is blocked. Assisted by Casemiro with a cross.",
  "rule": "Biased towards the home team",
  "context": {
      "sport": "football",
      "homeTeam": "Real Madrid",
      "awayTeam": "Liverpool FC",
      "homeTeamScore": 2,
      "awayTeamScore": 1
    }
}
"""
