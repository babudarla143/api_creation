from flask import Flask, request, jsonify, render_template
import secrets
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os

app = Flask(__name__)



FINAL_MODEL = "C:/Users/harib/Downloads/model_2.keras"
CLASS_NAMES = "C:/Users/harib/Downloads/class_names_222.npy"
INFESTATION_NAMES = "C:/Users/harib/Downloads/infestation_names_222.npy"


class_names = np.load(CLASS_NAMES, allow_pickle=True)
infestation_names = np.load(INFESTATION_NAMES, allow_pickle=True)
model = load_model(FINAL_MODEL)


def preprocess_image(img_path, img_size=(380, 380)):
    img = load_img(img_path, target_size=img_size)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array


def encoding_infestation_names(infestation_name):
    infestation_dict = {name: idx for idx, name in enumerate(infestation_names)}
    return np.array([[infestation_dict.get(infestation_name, 0)]])


API_KEYS = {}


pest_solutions = {
    "Armyworms (Spodoptera mauritia)": "Use pheromone traps, biological control (e.g., parasitoids, predators), and timely insecticide application. Maintain clean fields by removing weeds and crop residues that serve as breeding grounds. Encourage natural enemies such as birds and parasitic wasps. Avoid excessive use of nitrogen fertilizers, as they promote lush growth that attracts pests.",
    
    "Echinochloa_crus_galli": "Practice crop rotation, use pre-emergence herbicides, and maintain proper water management. Implement mechanical control like hand-pulling young weeds before seed production. Mulching and flooding techniques can suppress weed growth. Use cover crops to compete with weeds and reduce their spread.",
    
    "Green Leafhopper (Nephotettix virescens)": "Encourage natural predators like spiders, use resistant crop varieties, and apply neem-based pesticides. Avoid indiscriminate pesticide use that may kill beneficial insects. Implement light traps to monitor and control adult populations. Grow border crops like marigolds to repel leafhoppers.",
    
    "Monochoria vaginalis (Pickerelweed)": "Hand weeding, proper field drainage, and the use of selective herbicides. Use water level management techniques such as deep flooding to suppress weed emergence. Timely plowing and harrowing reduce weed seed banks in the soil. Introduce biological control agents like plant pathogens specific to pickerelweed.",
    
    "Monochoria vaginalis (Pickerelweed) Mainn": "Flooding management, hand-pulling before seed formation, and using herbicides like bentazon. Use rice-duck farming to suppress weed growth naturally. Implement mulching techniques with organic materials to inhibit seed germination. Ensure proper land leveling to avoid water stagnation, which favors weed growth.",
    
    "Rice Gundhi Bug (Leptocorisa acuta)": "Use light traps, destroy egg masses, and apply botanical pesticides like neem oil. Grow trap crops such as sorghum or millet around rice fields to attract pests away from rice. Remove weeds and grasses near fields that serve as breeding sites. Encourage natural predators like assassin bugs and spiders.",
    
    "Rice Stem Borer (Scirpophaga incertulas)": "Use Trichogramma parasitoids, pheromone traps, and avoid excessive nitrogen fertilizer. Plant resistant rice varieties that are less susceptible to infestation. Practice synchronous planting to disrupt pest life cycles. Remove and destroy infected plant parts to reduce the pest population.",
    
    "Brown Planthopper (Nilaparvata lugens)": "Use resistant rice varieties, avoid excessive nitrogen use, and introduce natural predators like spiders. Use alternate wetting and drying irrigation to discourage planthopper populations. Apply botanical pesticides such as neem oil instead of synthetic chemicals. Maintain field sanitation by removing weeds and stubbles.",
    
    "Rice Blast (Magnaporthe oryzae)": "Use resistant varieties, maintain proper field sanitation, and apply fungicides when necessary. Ensure balanced fertilization, as excess nitrogen promotes disease susceptibility. Avoid planting in shaded areas with high humidity, which favors fungal growth. Rotate rice with non-host crops like legumes to break disease cycles.",
    
    "Rice Hispa (Dicladispa armigera)": "Handpick larvae, promote biological control using parasitic wasps, and use neem-based sprays. Implement timely plowing to destroy pupae in the soil. Encourage natural enemies such as predatory beetles and birds. Maintain proper plant spacing to reduce humidity that favors pest development.",
    
    "Rice Root Knot Nematode (Meloidogyne graminicola)": "Practice crop rotation with non-host plants, maintain proper field drainage, and use nematicides. Use organic amendments like compost and neem cake to suppress nematode populations. Flood infested fields for several weeks to reduce nematode numbers. Grow resistant or tolerant rice varieties.",
    
    "False Smut (Ustilaginoidea virens)": "Use certified disease-free seeds, maintain balanced fertilization, and avoid excessive humidity in the field. Remove infected panicles before spores spread to healthy plants. Apply potassium-based fertilizers to improve plant resistance. Avoid late nitrogen applications that increase disease susceptibility.",
    
    "Sheath Blight (Rhizoctonia solani)": "Use resistant rice varieties, improve plant spacing, and apply fungicides during early infection. Avoid over-fertilization, as dense growth increases humidity and disease spread. Remove infected plant debris to reduce fungal inoculum. Use biological control agents like Trichoderma species.",
    
    "Stem Rot (Sclerotium oryzae)": "Improve soil drainage, reduce excess nitrogen application, and use biocontrol agents like Trichoderma. Apply silicon-based fertilizers to strengthen plant tissues against infection. Implement proper tillage practices to bury infected plant residues. Use crop rotation with legumes to reduce pathogen buildup in the soil."
}

@app.route("/") 
def home():
    return render_template("index.html")
    

@app.route("/api_create", methods=["POST"])
def api_creation():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Username is required"}), 400

    username = data["name"]
    api_key = secrets.token_hex(16)
    API_KEYS[username] = api_key 
    print(API_KEYS.items())

    return jsonify({
        "message": "Username is correct",
        "username": username,
        "api_key": api_key
    }), 200
    
@app.route('/api_verify', methods=['POST'])
def verify_api():
    api_keys = request.get_json()
    
    if not api_keys or "key" not in api_keys:
        return jsonify({"error": "api_key is required"}), 400

    key = api_keys['key']
    
    if key in API_KEYS.values():
        return jsonify({"message": "API key is valid"}), 200
    else:
        return jsonify({"error": "Invalid API key"}), 401
    
@app.route('/predict', methods=["POST"])
def predict():
    
    if 'image' not in request.files or 'infestation_name' not in request.form:
        return jsonify({"error": "Missing image or infestation_name"}), 400

    img_file = request.files['image']
    infestation_name = request.form['infestation_name']

    img_path = "temp.jpg"
    img_file.save(img_path)

    img_input = preprocess_image(img_path)
    infestation_input = encoding_infestation_names(infestation_name)

    predictions = model.predict([img_input, infestation_input])
    predicted_class = np.argmax(predictions, axis=1)[0]
    confidence = np.max(predictions) * 100

    
    solution = pest_solutions.get(class_names[predicted_class], "No solution available.")
    #(if predictions in pest_solutions return)
    #
    os.remove(img_path)

    return jsonify({
        "pest_solution": solution,
        "predicted_class": class_names[predicted_class],
        "confidence": f"{confidence:.2f}%"
    }) 
if __name__ == "__main__":
    app.run(debug=True)
