from flask import Flask, request
from joblib import load
import pandas as pd
import os

application = Flask(__name__)
clases = {1: 'No hay bicicletas disponibles', 2: 'Menos de 5 bicicletas', 3: 'Más de 5 bicicletas'}
clf_rf = load('static/modelo_predictor_estatus.joblib')
opciones_dia = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sábado', 'domingo']
id_estaciones = list(range(1, 481))
x_vars = ['nombre_dia', 'id', 'fracc_dia', 'fecha_dt']


@application.route('/')
def index():
    params = request.args
    if not params:
        params = dict()

    hora = int(params.get('hora', 5))
    minuto = int(params.get('minuto', 0))
    fracc_dia = hora * 12 + int(minuto / 5)
    dia = params.get('dia', 'lunes')
    if hora < 5 or hora > 23:
        return {'error': 'Hora fuera de rango'}
    if minuto < 0 or minuto > 59:
        return {'error': 'minuto fuera de rango'}
    if dia not in opciones_dia:
        return {'error': f'dia mal especificado. Opciones validas son: {opciones_dia}'}

    punto = dict(fracc_dia=fracc_dia, nombre_dia=dia, id=id_estaciones, fecha_dt=0)
    query = pd.DataFrame(punto)[x_vars]
    query['estatus'] = clf_rf.predict(query)
    query['texto'] = query['estatus'].map(clases)
    output = dict()
    output['estatus'] = query[['id', 'estatus', 'texto']].to_dict(orient='records')
    output['dia'] = dia
    output['hora'] = hora
    output['minuto'] = minuto
    return output


if __name__ == '__main__':
    if 'Windows' in os.getenv('OS', default=''):
        application.run(debug=True)
    else:
        application.run(host='0.0.0.0', port=80)
