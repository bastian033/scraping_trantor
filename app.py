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
    if not razon_social:
        return jsonify({"error": "Debe proporcionar una razon social para buscar"}), 400

    colecciones = [f"DatosGob{anio}" for anio in range(2013, 2026)]
    resultados_totales = []

    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]
        resultados = list(coleccion.find({"Razon Social": {"$regex": razon_social, "$options": "i"}}))
        for resultado in resultados:
            resultado["_id"] = str(resultado["_id"])  
        resultados_totales.extend(resultados)

    if not resultados_totales:
        return jsonify({"message": "No se encontraron resultados para la razón social proporcionada"}), 404

    return jsonify(resultados_totales), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  
    app.run(host='0.0.0.0', port=port, debug=True)
