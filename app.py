from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Admin:WTUOB6XURdpxnF9d@scrapingtrantor.bj3aqkm.mongodb.net/DatosEmpresas?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI)
db = client['DatosEmpresas']  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET'])
def buscar_empresa():
    razon_social = request.args.get('razon_social')
    rut = request.args.get('RUT')

    if not razon_social and not rut:
        return jsonify({"error": "Debe proporcionar una razón social o un RUT para buscar"}), 400

    if rut:
        rut = normalizar_rut(rut)  # Normalizar el RUT ingresado

    colecciones = [f"DatosGob{anio}" for anio in range(2013, 2026)]
    resultados_totales = []

    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]

        filtro = {}
        if razon_social:
            filtro["Razon Social"] = {"$regex": razon_social, "$options": "i"}
        if rut:
            filtro["RUT"] = rut  # Buscar el RUT exacto

        resultados = list(coleccion.find(filtro))
        for resultado in resultados:
            resultado["_id"] = str(resultado["_id"])  # Convertir ObjectId a string
        resultados_totales.extend(resultados)

    if not resultados_totales:
        return jsonify({"message": "No se encontraron resultados para los criterios proporcionados"}), 404

    return jsonify(resultados_totales), 200
  
def normalizar_rut(rut):
    """
    Normaliza el RUT eliminando puntos y dejando solo el guion.
    """
    return rut.replace(".", "").strip()

if __name__ == '__main__':
    app.run(debug=True)
