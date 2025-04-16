from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['local'] 
collection = db['DatosGob2025'] 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET'])
def buscar_empresa():
    razon_social = request.args.get('razon_social')
    if not razon_social:
        return jsonify({"error": "Debe proporcionar una razon social para buscar"}), 400

    resultados = list(collection.find({"Razon Social": {"$regex": razon_social, "$options": "i"}}))
    for resultado in resultados:
        resultado["_id"] = str(resultado["_id"]) # Convertir ObjectId a string para JSON

    if not resultados:
        return jsonify({"message": "No se encontraron resultados para la razón social proporcionada"}), 404

    return jsonify(resultados), 200

if __name__ == '__main__':
    app.run(debug=True)