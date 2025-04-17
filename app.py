from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['DatosEmpresas']  # Base de datos 'local'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET'])
def buscar_empresa():
    razon_social = request.args.get('razon_social')
    if not razon_social:
        return jsonify({"error": "Debe proporcionar una razon social para buscar"}), 400

    # Lista de colecciones a buscar
    colecciones = [f"DatosGob{anio}" for anio in range(2013, 2026)]
    resultados_totales = []

    # Iterar sobre cada colección y buscar
    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]
        resultados = list(coleccion.find({"Razon Social": {"$regex": razon_social, "$options": "i"}}))
        for resultado in resultados:
            resultado["_id"] = str(resultado["_id"])  # Convertir ObjectId a string para JSON
        resultados_totales.extend(resultados)

    if not resultados_totales:
        return jsonify({"message": "No se encontraron resultados para la razón social proporcionada"}), 404

    return jsonify(resultados_totales), 200

if __name__ == '__main__':
    app.run(debug=True)
