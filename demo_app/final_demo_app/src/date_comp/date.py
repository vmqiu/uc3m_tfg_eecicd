from flask import Flask
from datetime import datetime

app = Flask(__name__)


@app.route("/", methods=['GET'])
def get_hour() -> str:
    """   
    This returns the current hour in UTC as a string.

    :return: the current hour in %H format in UTC.
    :rtype: string
   """
    current_time = datetime.now()
    
    return str(current_time.hour)