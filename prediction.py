import requests

def send_prediction_request(image_path, infestation_name):
    url="http://127.0.0.1:5000/predict"
    api_key = "b1879517199c2f6a57b2b6ffea8ee08b"
    headers = {
        "x-api-key": api_key  # API key for verification
    }
    files = {
        "image": open(image_path, "rb")  # Open image file
    }
    data = {
        "infestation_name": infestation_name  # Infestation name parameter
    }
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

#Echinochloa crus-galli (Barnyard Grass)
path = "C:/Users/harib/Downloads/eeeeee.jpeg"
infestation = "Echinochloa crus-galli (Barnyard Grass)"

res = send_prediction_request(path,infestation)
print(res)