from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os
import re

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Admin:WTUOB6XURdpxnF9d@scrapingtrantor.bj3aqkm.mongodb.net/DatosEmpresas?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI)
db = client['DatosEmpresas']  

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/buscar', methods=['GET'])
def buscar_empresa():
    entrada = request.args.get('entrada')  

    if not entrada:
        return jsonify({"error": "Debe proporcionar un RUT o una razón social para buscar"}), 400

    if es_rut(entrada):
        rut = normalizar_rut(entrada)
        print(f"Detectado como RUT: {rut}")  
        filtro = {"RUT": rut} 
    else:
        razon_social = entrada
        print(f"Detectado como Razón Social: {razon_social}")  
        filtro = {"Razon Social": {"$regex": razon_social, "$options": "i"}}  

    colecciones = [f"DatosGob{anio}" for anio in range(2013, 2026)]
    resultados_totales = []

    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]

        print(f"Filtro de búsqueda: {filtro}") 
        resultados = list(coleccion.find(filtro))
        print(f"Resultados encontrados en {coleccion_nombre}: {resultados}") 

        for resultado in resultados:
            resultado["_id"] = str(resultado["_id"])  
            resultados_totales.append(resultado)

    if not resultados_totales:
        return jsonify({"message": "No se encontraron resultados para los criterios proporcionados"}), 404

    return jsonify(resultados_totales), 200
def normalizar_rut(rut):
    return rut.replace(".", "").replace(" ", "").strip()

def es_rut(texto):

    patron_rut = r"^\d{7,8}-[0-9kK]$" 
    return re.match(patron_rut, texto) is not None


if __name__ == '__main__':
    app.run(debug=True)
