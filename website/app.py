from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace this with your Rasa server URL
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.form["user_message"]

    # Send the user message to the Rasa server
    rasa_response = requests.post(RASA_SERVER_URL, json={"sender": "user", "message": user_message}).json()

    # Extract the bot response from the Rasa server response
    bot_response = rasa_response[0]["text"]

    return jsonify({"bot_response": bot_response})


if __name__ == "__main__":
    app.run(port="8050", debug=True)



# @app.route('/rasa_interact', methods=['POST'])
# def rasa_interact():
#     # Get the input text data from the client
#     user_message = request.json['user_message']

#     # Replace the URL with the actual endpoint of your Rasa server
#     rasa_endpoint = 'http://localhost:5005/webhooks/rest/webhook'

#     # Prepare the payload data in the required format for Rasa
#     payload = {
#         'sender': 'user',
#         'message': user_message
#     }

#     try:
#         # Send the POST request to the Rasa server
#         response = requests.post(rasa_endpoint, json=payload)

#         # Check if the request was successful (status code 200)
#         if response.status_code == 200:
#             return jsonify(response.json())
#         else:
#             return jsonify({"error": "Failed to interact with Rasa server"}), 500

#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "Failed to connect to Rasa server"}), 500

# if __name__ == '__main__':
#     app.run(port="8050",debug=True)