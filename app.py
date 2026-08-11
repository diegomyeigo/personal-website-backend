from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/test')
def test():
    return {"message": "Successful NEW test"}

@app.route('/api/survey', methods=["POST"])
def submit_survey():
    data = request.get_json()

    print(data)

    return {
        "success": True,
        "message": "POST Received!"
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