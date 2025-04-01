from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define los orígenes permitidos (puedes usar "*" para permitir todos, pero es mejor especificar)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Función para conectar a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="reserva_hoteles"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Esquema para los datos de la reserva
class Reserva(BaseModel):
    id_habitacion_hotel: int
    fecha_inicio: str
    fecha_fin: str
    cant_habitaciones: int
    num_personas: int
    tipo_habitacion: str
    hotel: str

# Ver la disponibilidad de los sitios (hoteles) de acuerdo a la fecha en que desea viajar.  

# Función para verificar disponibilidad de habitaciones
def verificar_disponibilidad_habitaciones(cursor, id_habitacion_hotel, cant_habitaciones):
    cursor.execute("""
        SELECT habitaciones_disponibles 
        FROM habitaciones_hotel 
        WHERE id_habitacion_hotel = %s
    """, (id_habitacion_hotel,))
    
    habitacion = cursor.fetchone()
    
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada.")
    
    habitaciones_disponibles = habitacion["habitaciones_disponibles"]
    
    if habitaciones_disponibles < cant_habitaciones:
        raise HTTPException(status_code=400, detail="No hay suficientes habitaciones disponibles.")
    
    return habitaciones_disponibles

# Función para verificar disponibilidad de la habitación en las fechas seleccionadas
def verificar_disponibilidad_fechas(cursor, id_habitacion_hotel, fecha_inicio, fecha_fin):
    # Consultar las reservas existentes en las fechas seleccionadas
    cursor.execute("""
        SELECT SUM(cant_habitaciones) as habitaciones_reservadas
        FROM reservas 
        WHERE id_habitacion_hotel = %s AND (
            (fecha_inicio BETWEEN %s AND %s) OR 
            (fecha_fin BETWEEN %s AND %s) OR
            (fecha_inicio <= %s AND fecha_fin >= %s)
        )
    """, (id_habitacion_hotel, fecha_inicio, fecha_fin,
            fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))

    resultado = cursor.fetchone()
    
    # Obtener el número de habitaciones reservadas
    habitaciones_reservadas = resultado["habitaciones_reservadas"] if resultado["habitaciones_reservadas"] else 0
    
    # Consultar las habitaciones disponibles en el hotel
    cursor.execute("""
        SELECT habitaciones_disponibles 
        FROM habitaciones_hotel 
        WHERE id_habitacion_hotel = %s
    """, (id_habitacion_hotel,))
    
    habitacion = cursor.fetchone()
    
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada.")
    
    habitaciones_disponibles = habitacion["habitaciones_disponibles"]
    
    # Calcular cuántas habitaciones quedan disponibles
    habitaciones_disponibles_fechas = habitaciones_disponibles - habitaciones_reservadas
    
    if habitaciones_disponibles_fechas <= 0:
        raise HTTPException(status_code=400, detail="No hay habitaciones disponibles en las fechas seleccionadas.")
    
    return habitaciones_disponibles_fechas

# Ruta para realizar la validación
@app.post("/disponibilidad_hoteles/")
def disponibilidad_hoteles(reserva: Reserva):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)

        # Verificar disponibilidad de habitaciones
        habitaciones_disponibles = verificar_disponibilidad_habitaciones(cursor, reserva.id_habitacion_hotel, reserva.cant_habitaciones)

        if habitaciones_disponibles:
            # Verificar disponibilidad de las fechas seleccionadas
            habitaciones_disponibles_fechas = verificar_disponibilidad_fechas(cursor, reserva.id_habitacion_hotel, reserva.fecha_inicio, reserva.fecha_fin)

            print(habitaciones_disponibles_fechas)

            cursor.close()
            connection.close()
            return {"message": f"Hay {habitaciones_disponibles_fechas} habitaciones disponibles en las fechas seleccionadas."}
        else:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Habitación no encontrada en la base de datos.")
    else:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos.")
    

# Ver las tarifas de acuerdo al sitio, la temporada (alta, baja), el número de personas y de acuerdo al alojamiento elegido
# (estándar, premium, VIP).  

# Función para traer la información de cada habitación
def habitaciones(cursor, tipo_habitacion, hotel):
    # Obtener la tarifa, temporada, num_personas y tipo de la habitación
    cursor.execute("""
        SELECT DISTINCT th.`tipo_habitacion`,
                th.`tarifa`,
                h.`cupo_personas`
        FROM `tipo_habitaciones` th
        INNER JOIN habitaciones_hotel h
            ON h.`id_t_habitacion` = th.`id_t_habitaciones`
        INNER JOIN hoteles ho
            ON ho.`id_hotel` = h.`id_hotel`
        WHERE th.`tipo_habitacion` = %s 
            AND ho.`sede` = %s 
    """, (tipo_habitacion, hotel))
    
    habitacion = cursor.fetchone()  # Obtener un solo registro

    # Asegurar que la respuesta siempre sea una lista
    if habitacion:
        return [{
            "tipo_habitacion": habitacion["tipo_habitacion"],
            "tarifa": habitacion["tarifa"],
            "cupo_personas": habitacion["cupo_personas"]
        }]
    else:
        return []

def es_temporada_alta(fecha_inicio_str, fecha_fin_str):
    # Convertir las fechas de reserva a objetos datetime.date
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

    # Definir los rangos de temporada alta
    rangos_temporada_alta = [
        (datetime(2025, 12, 1).date(), datetime(2026, 1, 31).date()),  # Diciembre y enero
        (datetime(2025, 4, 13).date(), datetime(2025, 4, 20).date()),  # Semana Santa
        (datetime(2025, 6, 1).date(), datetime(2025, 7, 31).date())    # Junio y julio
    ]

    # Verificar si ambas fechas están dentro de al menos un rango de temporada alta
    en_temporada_alta = any(inicio <= fecha_inicio <= fin and inicio <= fecha_fin <= fin for inicio, fin in rangos_temporada_alta)

    return en_temporada_alta

# Ruta para obtener la información de las habitaciones
@app.post("/informacion_habitaciones/")
def info_habitaciones(reserva: Reserva):

    connection = get_db_connection()

    info_habitacion = []  # Lista vacía por si hay errores

    if connection:
        cursor = connection.cursor(dictionary=True)
        info_habitacion = habitaciones(cursor, reserva.tipo_habitacion, reserva.hotel)
        cursor.close()
        connection.close()

    # Es temporada alta ? 
    fecha_inicio = reserva.fecha_inicio
    fecha_fin = reserva.fecha_fin
    temporada_alta = False

    if es_temporada_alta(fecha_inicio, fecha_fin):
        temporada_alta = True
    else:
        temporada_alta = False


    # Si la lista tiene datos, accedemos al primer elemento
    if info_habitacion:
        if(temporada_alta):
            return {
                "message": f"La habitación {reserva.tipo_habitacion} tiene una tarifa de {info_habitacion[0]['tarifa']}, se encuentra en temporada alta, "
                            f"y tiene un cupo máximo de {info_habitacion[0]['cupo_personas']} personas."
            }
        else:
            return {
                "message": f"La habitación {reserva.tipo_habitacion} tiene una tarifa de {info_habitacion[0]['tarifa']}, se encuentra en temporada baja, "
                            f"y tiene un cupo máximo de {info_habitacion[0]['cupo_personas']} personas."
            }
    else:
        return {"message": "No se encontró información para la habitación solicitada."}
    

# Realizar el cálculo de la tarifa a cancelar de acuerdo al sitio, número de habitaciones que necesita utilizar, el número de
# personas, al tipo de alojamiento (estándar, premium, VIP) y a la temporada (alta, baja).

def calcular_dias_reserva(fecha_inicio, fecha_fin):
    try:
        # Convertir las cadenas de fecha a objetos datetime
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        # Calcular la diferencia entre las fechas
        diferencia = fecha_fin - fecha_inicio

        # Obtener la cantidad de días de la diferencia
        dias = diferencia.days

        return dias
    except ValueError:
        return "Formato de fecha incorrecto."
    
# Ruta para obtener la tarifa total
@app.post("/tarifa_total/")
def calcular_tarifa_total(reserva: Reserva):

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Calcular la cantidad de días
            cantidad_dias = calcular_dias_reserva(reserva.fecha_inicio, reserva.fecha_fin)

            # Reutilzar función ya hecha anteriormente
            habitaciones = habitaciones(cursor, reserva.id_habitacion_hotel)

            tarifa_habitacion = habitaciones[0]['tarifa']

            # Calcular la temporada de las fechas
            if es_temporada_alta(reserva.fecha_inicio, reserva.fecha_fin):
                temporada_alta = True
            else:
                temporada_alta = False

            # Calcular el porcentaje de aumento si es temporada alta (en este caso 30%)
            if(temporada_alta == True):
                tarifa_habitacion =  tarifa_habitacion + (tarifa_habitacion * 0.3)
            else:
                # La tarifa queda igual
                tarifa_habitacion
            
            # Cantidad de habitaciones
            cantidad_habitaciones = reserva.cant_habitaciones

            # Para calcular la tarifa se asumió que se está consultando un solo tipo de habitación
            tarifa_total = (cantidad_dias * cantidad_habitaciones) * tarifa_habitacion

            return {"tarifa_total": tarifa_total}

        except Error as e:
            raise HTTPException(status_code=500, detail=f"Error al calcular la tarifa: {e}")
        finally:
            cursor.close()
            connection.close()
    else:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos")
