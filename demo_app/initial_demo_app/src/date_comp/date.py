from flask import Flask

app = Flask(__name__)

@app.route("/todo", methods=['GET'])
def to_do() -> str:
    """to do"""
    return "to do"
