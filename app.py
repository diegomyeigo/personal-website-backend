from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/test')
def test():
    return {"message": "Successful test"}

@app.route('/api/survey', methods=["POST", "OPTIONS"])
def submit_survey():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()

    print(data)

    return {
        "success": True,
        "message": "Received!"
    }

@app.route("/api/routes")
def routes():
    return {
        "routes": [
            str(rule)
            for rule in app.url_map.iter_rules()
        ]
    }

if __name__ == '__main__':
    app.run(debug=True)