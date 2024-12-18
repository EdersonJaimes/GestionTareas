import streamlit as st
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
Base = declarative_base()
DATABASE_URL = 'sqlite:///tareas.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Modelo de tarea
class Tarea(Base):
    __tablename__ = 'tareas'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    completada = Column(Boolean, default=False)

# Crear tablas en la base de datos
Base.metadata.create_all(engine)

def agregar_tarea(titulo, descripcion):
    """Agrega una nueva tarea a la base de datos."""
    session = Session()
    nueva_tarea = Tarea(titulo=titulo, descripcion=descripcion)
    session.add(nueva_tarea)
    session.commit()
    session.close()

def listar_tareas():
    """Devuelve todas las tareas de la base de datos."""
    session = Session()
    tareas = session.query(Tarea).all()
    session.close()
    return tareas

def marcar_completada(id_tarea):
    """Marca una tarea como completada en la base de datos."""
    session = Session()
    tarea = session.query(Tarea).filter_by(id=id_tarea).first()
    if tarea:
        tarea.completada = True
        session.commit()
    session.close()

def eliminar_tarea(id_tarea):
    """Elimina una tarea completada de la base de datos."""
    session = Session()
    tarea = session.query(Tarea).filter_by(id=id_tarea).first()
    
    if tarea and tarea.completada:
        session.delete(tarea)
        session.commit()
        session.close()
    else:
        session.close()

def guardar_tareas():
    """Guarda las tareas actuales en un archivo JSON."""
    tareas = listar_tareas()
    tareas_dict = [{'id': tarea.id, 'titulo': tarea.titulo, 'descripcion': tarea.descripcion, 'completada': tarea.completada} for tarea in tareas]
    with open('tareas.json', 'w') as archivo:
        json.dump(tareas_dict, archivo)

def cargar_tareas():
    try:
        with open('tareas.json', 'r') as archivo:
            tareas_dict = json.load(archivo)
            session = Session()

            # Obtiene todas las tareas actuales en la base de datos
            tareas_en_bd = session.query(Tarea).all()
            ids_en_bd = {tarea.id for tarea in tareas_en_bd}

            # Añadir solo tareas que no están en la base de datos
            for tarea_dict in tareas_dict:
                # Si la tarea no está en la base de datos, agregarla
                if tarea_dict['id'] not in ids_en_bd:
                    tarea = Tarea(
                        id=tarea_dict['id'],
                        titulo=tarea_dict['titulo'],
                        descripcion=tarea_dict['descripcion'],
                        completada=tarea_dict['completada']
                    )
                    session.add(tarea)

            session.commit()
            session.close()
    except FileNotFoundError:
        pass  # Si el archivo no existe, no hace nada

# Estilo de la interfaz
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
            font-family: 'Arial', sans-serif;
        }
        .title {
            text-align: center;
            color: #3e4e64;
            font-size: 3rem;
            padding-top: 20px;
        }
        .header {
            text-align: center;
            color: #3e4e64;
            font-size: 2rem;
            margin-top: 30px;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            text-align: center;
            font-size: 16px;
            margin-top: 10px;
            cursor: pointer;
            border-radius: 5px;
        }
        .button:hover {
            background-color: #45a049;
        }
        .button:active {
            background-color: #3e8e41;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .task-card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Interfaz
def app():
    cargar_tareas()

    st.markdown('<h1 class="title">Gestión de Tareas</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<h2 class="header">Agregar una nueva tarea</h2>', unsafe_allow_html=True)
        titulo = st.text_input("Título de la tarea")
        descripcion = st.text_area("Descripción de la tarea")
        if st.button("Agregar Tarea", key="agregar", help="Haz clic para agregar la tarea"):
            if titulo:
                agregar_tarea(titulo, descripcion)
                st.success("Tarea agregada exitosamente!")
            else:
                st.error("El título es obligatorio.")

    with col2:
        st.markdown('<h2 class="header">Lista de Tareas</h2>', unsafe_allow_html=True)
        tareas = listar_tareas()
        
        for tarea in tareas:
            with st.container():
                st.markdown(f"""
                    <div class="task-card">
                        <h4>{tarea.titulo}</h4>
                        <p>{tarea.descripcion}</p>
                        <p><strong>{'Completada' if tarea.completada else 'Pendiente'}</strong></p>
                    </div>
                """, unsafe_allow_html=True)
                
                if not tarea.completada:
                    if st.button(f"Marcar como completada {tarea.id}", key=f"completar_{tarea.id}"):
                        marcar_completada(tarea.id)
                        st.success(f"Tarea {tarea.id} marcada como completada.")

        # Sección para eliminar tareas completadas
        st.markdown('<h2 class="header">Eliminar tareas completadas</h2>', unsafe_allow_html=True)
        for tarea in tareas:
            if tarea.completada:
                if st.button(f"Eliminar {tarea.id}", key=f"eliminar_{tarea.id}"):
                    eliminar_tarea(tarea.id)  # Llama la función de eliminación
                    st.success(f"Tarea {tarea.id} eliminada.")
                    tareas = listar_tareas()  # Recarga la lista de tareas después de la eliminación
                    break  # Para recargar la lista correctamente después de eliminar

        if st.button("Guardar tareas", key="guardar", help="Guarda las tareas en un archivo"):
            guardar_tareas()
            st.success("Tareas guardadas en el archivo.")

if __name__ == "__main__":
    app()
