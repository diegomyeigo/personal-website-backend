from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500/survey/index.html"])

@app.route('/api/test')
def test():
    return {"message": "Successful test"}

@app.route("/api/survey", methods=["POST"])
def submit_survey():
    data = request.get_json()

    print(data)

    return {
        "success": True,
        "message": "Received!"
    }

if __name__ == '__main__':
    app.run(debug=True)