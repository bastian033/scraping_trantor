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
    """
    Endpoint para buscar empresas por razón social o RUT.
    """
    razon_social = request.args.get('razon_social')
    rut = request.args.get('RUT')

    # Validar que al menos uno de los parámetros esté presente
    if not razon_social and not rut:
        return jsonify({"error": "Debe proporcionar una razón social o un RUT para buscar"}), 400

    # Normalizar el RUT si se proporciona
    if rut:
        rut = normalizar_rut(rut)  # Normalizar el RUT ingresado
        print(f"RUT normalizado: {rut}")  # Depuración

    # Definir las colecciones a buscar
    colecciones = [f"DatosGob{anio}" for anio in range(2013, 2026)]
    resultados_totales = []

    # Iterar sobre las colecciones y buscar coincidencias
    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]

        # Construir el filtro dinámicamente
        filtro = {}
        if razon_social:
            filtro["Razon Social"] = {"$regex": razon_social, "$options": "i"}  # Búsqueda insensible a mayúsculas
        if rut:
            filtro["RUT"] = rut  # Buscar el RUT exacto

        print(f"Filtro de búsqueda: {filtro}")  # Depuración

        # Realizar la búsqueda en la colección
        resultados = list(coleccion.find(filtro))
        print(f"Resultados encontrados en {coleccion_nombre}: {resultados}")  # Depuración

        # Convertir ObjectId a string y agregar resultados a la lista total
        for resultado in resultados:
            resultado["_id"] = str(resultado["_id"])  # Convertir ObjectId a string
            resultados_totales.append(resultado)

    # Si no se encontraron resultados, devolver un mensaje adecuado
    if not resultados_totales:
        return jsonify({"message": "No se encontraron resultados para los criterios proporcionados"}), 404

    # Devolver los resultados encontrados
    return jsonify(resultados_totales), 200

def normalizar_rut(rut):
    return rut.replace(".", "").replace(" ", "").strip()


if __name__ == '__main__':
    app.run(debug=True)
