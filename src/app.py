from flask import Flask, request, jsonify
from sistema_recomendacion import (
    cargar_datos, recomendar_perfiles, obtener_habilidades_ofrecidas,
    calificar_habilidad, obtener_promedio_calificacion
)
import os

# Inicializa la aplicación Flask
app = Flask(__name__)

# Carga los datos al iniciar el servidor
base_path = os.path.dirname(os.path.dirname(__file__))
archivo = os.path.join(base_path, 'data', 'base_datos.xlsx')
usuarios_df, perfil_df, habilidades_df, categorias_df = cargar_datos(archivo)

# Endpoint para obtener recomendaciones de perfiles
@app.route('/recomendaciones', methods=['POST'])
def recomendaciones():
    try:
        data = request.get_json()
        app.logger.info(f'Received data: {data}')  # Log the incoming data
        habilidad_a_aprender = data.get('habilidad_a_aprender')
        dias_preferidos = data.get('dias_preferidos')
        rango_tiempo_preferido = data.get('rango_tiempo_preferido')
        
        # Genera las recomendaciones
        perfiles, resúmenes = recomendar_perfiles(perfil_df, usuarios_df, habilidad_a_aprender, dias_preferidos, rango_tiempo_preferido)
        
        # Verifica si hay resultados
        if perfiles is not None and not perfiles.empty:
            return jsonify(resúmenes), 200
        else:
            return jsonify({'error': 'No se encontraron perfiles que coincidan con los criterios.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener habilidades ofrecidas
@app.route('/habilidades_ofrecidas', methods=['GET'])
def habilidades_ofrecidas():
    try:
        habilidades = obtener_habilidades_ofrecidas(perfil_df)
        return jsonify({'habilidades': habilidades}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para calificar una habilidad
@app.route('/calificar_habilidad', methods=['POST'])
def calificar():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        skill = data.get('skill')
        rating = data.get('rating')
        tipo = data.get('tipo', 'ofrecida')

        calificar_habilidad(user_id, skill, rating, tipo)
        return jsonify({'mensaje': 'Calificación registrada exitosamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener el promedio de calificación de una habilidad
@app.route('/promedio_calificacion', methods=['GET'])
def promedio_calificacion():
    try:
        skill = request.args.get('skill')
        tipo = request.args.get('tipo', 'ofrecida')
        promedio = obtener_promedio_calificacion(skill, tipo)

        if promedio is not None:
            return jsonify({'promedio': promedio}), 200
        else:
            return jsonify({'mensaje': 'No hay calificaciones para esta habilidad.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run(debug=True)
