import os

import jsonschema
import openai
from chalice import Chalice, Response

app = Chalice(app_name="chalice-commentary-editor")
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
        },
    },
    "required": ["commentary", "rule", "context"],
}


@app.route("/", methods=["POST"])
def commentary():
    # Validate JSON
    try:
        input_data = app.current_request.json_body
        jsonschema.validate(instance=input_data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        # Return error message
        return Response(body={"error": str(err)}, status_code=400)

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
    return {"commentary": response}


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
