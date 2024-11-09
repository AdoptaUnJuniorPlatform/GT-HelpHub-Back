import pandas as pd
import openpyxl
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cargar_datos(archivo_datos):
    try:
        excel_data = pd.ExcelFile(archivo_datos)
        usuarios_df = excel_data.parse('Users')
        perfil_df = excel_data.parse('Profile')
        habilidades_df = excel_data.parse('Habilities')
        categorias_df = excel_data.parse('Categories')
        logging.info("Datos cargados correctamente.")
        return usuarios_df, perfil_df, habilidades_df, categorias_df
    except Exception as e:
        logging.error(f"Error al cargar los datos: {e}")
        return None, None, None, None

# Obtener habilidades ofrecidas
def obtener_habilidades_ofrecidas(perfil_df):
    habilidades_ofrecidas = perfil_df['offeredHabilities'].dropna().unique()
    return habilidades_ofrecidas.tolist()

# Filtrar perfiles en base a criterios
def filtrar_perfiles(perfil_df, habilidad_a_aprender, dias_preferidos, rango_tiempo_preferido):
    filtros = pd.Series([True] * len(perfil_df))
    if habilidad_a_aprender:
        filtros &= perfil_df['category'].str.contains(habilidad_a_aprender, case=False, na=False)
    if dias_preferidos:
        filtros &= perfil_df['selectedDays'].str.contains(dias_preferidos, case=False, na=False)
    if rango_tiempo_preferido:
        filtros &= perfil_df['preferredTimeRange'].str.contains(rango_tiempo_preferido, case=False, na=False)
    
    return perfil_df[filtros]

# Generar resúmenes de usuarios
def generar_resumenes_usuarios(usuarios_df, perfil_df, perfiles_coincidentes):
    resúmenes_usuarios = []
    for idx in perfiles_coincidentes.index:
        info_usuario = usuarios_df.loc[usuarios_df.index[idx]].to_dict()
        resumen_usuario = {
            "nombre": info_usuario['nameUser'],
            "apellido": info_usuario['surnameUser'],
            "ubicación": perfil_df.loc[idx, 'location'],
            "descripción": perfil_df.loc[idx, 'description'],
            "foto_perfil": perfil_df.loc[idx, 'profilePicture'],
            "habilidades_interesadas": perfil_df.loc[idx, 'interestedHabilities']
        }
        resúmenes_usuarios.append(resumen_usuario)
    return resúmenes_usuarios

# Sistema de calificación de habilidades
ratings_df = pd.DataFrame(columns=['user_id', 'skill', 'rating', 'type'])

def calificar_habilidad(user_id, skill, rating, tipo='ofrecida'):
    global ratings_df
    if not (1 <= rating <= 5):
        logging.warning("La calificación debe estar entre 1 y 5.")
        return

    nueva_calificacion = {'user_id': user_id, 'skill': skill, 'rating': rating, 'type': tipo}
    ratings_df = ratings_df.append(nueva_calificacion, ignore_index=True)
    logging.info(f"Calificación de {rating} para la habilidad '{skill}' registrada.")

def obtener_promedio_calificacion(skill, tipo='ofrecida'):
    calificaciones_filtradas = ratings_df[(ratings_df['skill'] == skill) & (ratings_df['type'] == tipo)]
    return calificaciones_filtradas['rating'].mean() if not calificaciones_filtradas.empty else None

# Notificaciones automáticas
def enviar_notificacion(email, mensaje):
    logging.info(f"Notificación enviada a {email}: {mensaje}")

def registrar_perfil(nuevo_perfil, usuarios_df, perfil_df):
    nuevo_perfil_df = pd.DataFrame([nuevo_perfil])
    perfil_df = pd.concat([perfil_df, nuevo_perfil_df], ignore_index=True)
    notificar_intereses(nuevo_perfil, usuarios_df, perfil_df)
    logging.info("Perfil registrado y notificaciones enviadas.")
    return perfil_df

def notificar_intereses(nuevo_perfil, usuarios_df, perfil_df):
    for _, usuario in usuarios_df.iterrows():
        for habilidad in nuevo_perfil['offeredHabilities']:
            if habilidad in usuario['interestedHabilities']:
                mensaje = f"Se ha registrado un nuevo perfil que ofrece habilidades de: {habilidad}"
                enviar_notificacion(usuario['email'], mensaje)

    for _, perfil_existente in perfil_df.iterrows():
        for habilidad in perfil_existente['offeredHabilities']:
            if habilidad in nuevo_perfil['interestedHabilities']:
                mensaje = f"Un perfil existente ofrece una habilidad que te interesa: {habilidad}"
                enviar_notificacion(nuevo_perfil['email'], mensaje)

# Función principal de recomendación
def recomendar_perfiles(perfil_df, usuarios_df, habilidad_a_aprender=None, dias_preferidos=None, rango_tiempo_preferido=None):
    perfiles_coincidentes = filtrar_perfiles(perfil_df, habilidad_a_aprender, dias_preferidos, rango_tiempo_preferido)
    resúmenes_usuarios = generar_resumenes_usuarios(usuarios_df, perfil_df, perfiles_coincidentes)
    return perfiles_coincidentes, resúmenes_usuarios

# Código para ejecutar y probar el sistema de forma genérica
if __name__ == '__main__':
    archivo_datos = 'data/base_datos.xlsx'
    usuarios_df, perfil_df, _, _ = cargar_datos(archivo_datos)
    
    if usuarios_df is not None and perfil_df is not None:
        habilidad_a_aprender = input("Ingrese la habilidad que desea aprender: ")
        dias_preferidos = input("Ingrese los días preferidos (opcional): ")
        rango_tiempo_preferido = input("Ingrese el rango de tiempo preferido (opcional): ")

        perfiles, resúmenes = recomendar_perfiles(perfil_df, usuarios_df, habilidad_a_aprender, dias_preferidos, rango_tiempo_preferido)
        
        if perfiles is not None:
            print(f'Cantidad de perfiles recomendados: {len(perfiles)}')
            print(resúmenes)
    else:
        print("Error al cargar los datos.")
