from flask import Flask, Response

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world() -> str:
    """   
    This method sends a generic welcome message.

    :return: welcome message
    :rtype: str
   """
    return "Hola mundo, TFG entornos eficientes CI/CD!"

@app.route('/user_welcome/')
@app.route("/user_welcome/<string:username>", methods=['GET'])
def hello_world_user(username: str=None) -> str:
    """   
    This method sends a custom welcome message based on the parameter.

    :param username: user's name.
    :type username: str
    :return: custom welcome message
    :return: Error 400, username not found.
    :rtype: str
    """
    if username is None:
        return "Error 400: Parámetro <username> no proporcionado", 400
    
    return f"Hola {username}, bienvenido a TFG entornos eficientes CI/CD!"