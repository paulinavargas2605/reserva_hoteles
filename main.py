from fastapi import FastAPI # , HTTPException
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    
    print("entramos aqui")

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
    
