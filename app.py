import streamlit as st
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Regalías con Impacto - Cesar",
    page_icon="🏛️",
    layout="wide"
)

# Título Principal y Descripción
st.title("🏛️ Regalías con Impacto: Evaluación Multidimensional y Social (Cesar 2020-2026)")
st.markdown("""
**Plataforma de evaluación ex-post y ex-ante del Sistema General de Regalías (SGR)** fundamentada en el **Enfoque de las Capacidades de Amartya Sen**.
Integra un **Índice Multidimensional de Desarrollo Social ($IMSC_m$)** que cruza ejecución contractual, transición productiva, desempleo, educación, NBI y servicios públicos.
""")

# --- Carga de Base de Datos Multidimensional ---
@st.cache_data
def load_multidimensional_data():
    data = {
        'municipio': [
            'Valledupar', 'Aguachica', 'Agustín Codazzi', 'Bosconia', 
            'Chimichagua', 'El Paso', 'La Jagua de Ibirico', 'La Paz', 'San Alberto'
        ],
        'presupuesto_total': [
            348874000000, 180537000000, 408907000000, 20964000000, 
            28410000000, 109904000000, 194741000000, 25996900000, 25249900000
        ],
        'proyectos_totales': [42, 26, 27, 14, 16, 22, 28, 18, 12],
        'proyectos_operativos': [10, 6, 6, 2, 5, 0, 8, 4, 2],
        'proyectos_inoperativos_liquidados': [3, 1, 2, 4, 0, 7, 2, 0, 1],
        'alertas_entes_control': [1, 0, 1, 2, 0, 3, 1, 0, 0],
        'inversion_transicion': [
            119559119900, 88607559600, 130972912100, 5876209200, 
            11307180000, 54556345600, 63135032200, 16073883270, 4282383040
        ],
        # Nuevas variables socioeconómicas y del mercado laboral
        'tasa_desempleo': [14.2, 12.8, 15.5, 13.9, 18.2, 16.0, 11.4, 13.5, 12.1], # %
        'cobertura_educativa': [82.5, 78.0, 74.2, 71.5, 68.0, 70.4, 79.1, 76.5, 80.2], # %
        'delta_nbi': [4.7, 4.1, 4.2, 3.3, 5.1, 3.5, 3.8, 3.5, 3.6], # Puntos de reducción
        'acceso_servicios_publicos': [79.0, 72.5, 68.0, 65.1, 59.4, 63.0, 75.2, 70.1, 77.4] # %
    }
    df = pd.DataFrame(data)
    
    # 1. Índice de Ejecución Real y Funcional (ER_m)
    df['ER_m'] = df['proyectos_operativos'] / df['proyectos_totales']
    
    # 2. Factor de Penalización por Inoperatividad (P_m)
    df['P_m'] = (df['proyectos_inoperativos_liquidados'] / df['proyectos_totales']) + (df['alertas_entes_control'] * 0.1)
    
    # 3. Índice de Sostenibilidad y Transición Productiva (IST_m)
    df['IST_m'] = df['inversion_transicion'] / df['presupuesto_total']
    
    # 4. Índice Multidimensional de Desarrollo Social y Capacidades (IMSC_m)
    # Normalizamos el desempleo (menor desempleo es mejor) y ponderamos con educación, NBI, servicios y transición
    desempleo_norm = 1 - (df['tasa_desempleo'] / 25.0)
    educacion_norm = df['cobertura_educativa'] / 100.0
    servicios_norm = df['acceso_servicios_publicos'] / 100.0
    nbi_norm = df['delta_nbi'] / 6.0
    
    df['IMSC_score'] = (
        0.25 * df['IST_m'] + 
        0.20 * educacion_norm + 
        0.20 * servicios_norm + 
        0.15 * nbi_norm + 
        0.20 * desempleo_norm
    ) * 100 - (df['P_m'] * 15)
    
    # 5. Clasificación según la Matriz del Semáforo Multidimensional
    def clasificar_semaforo(row):
        if row['P_m'] > 0.3 or row['ER_m'] == 0:
            return 'Rojo Crítico (Elefante Blanco Contable)'
        elif row['P_m'] > 0.15 or row['IMSC_score'] < 45:
            return 'Rojo (Ineficiencia y Baja Inclusión Social)'
        elif row['IMSC_score'] < 60:
            return 'Amarillo (En Desarrollo / Alerta Social)'
        else:
            return 'Verde (Inversión Transformadora y Alto Desarrollo)'

    df['categoria_semaforo'] = df.apply(clasificar_semaforo, axis=1)
    
    return df

df = load_multidimensional_data()

# --- Barra Lateral: Filtros ---
st.sidebar.header("🎛️ Panel de Control y Filtros")
municipio_sel = st.sidebar.selectbox("Seleccione un Municipio:", ["Todos los Municipios"] + list(df['municipio']))

if municipio_sel != "Todos los Municipios":
    df_filtrado = df[df['municipio'] == municipio_sel]
else:
    df_filtrado = df

# --- Indicadores Globales ---
st.header("📊 Indicadores Globales y Multidimensionales del Departamento")
col1, col2, col3, col4 = st.columns(4)

presupuesto_total = df_filtrado['presupuesto_total'].sum()
desempleo_prom = df_filtrado['tasa_desempleo'].mean()
educacion_prom = df_filtrado['cobertura_educativa'].mean()
imsc_prom = df_filtrado['IMSC_score'].mean()

col1.metric("Presupuesto Total SGR", f"${presupuesto_total / 1e9:,.2f} Mil M.")
col2.metric("Promedio Tasa Desempleo", f"{desempleo_prom:.1f}%")
col3.metric("Promedio Cobertura Educativa", f"{educacion_prom:.1f}%")
col4.metric("Índice Multidimensional (IMSC)", f"{imsc_prom:.1f} pts")

st.markdown("---")

# --- Matriz del Semáforo Multidimensional ---
st.header("🚦 Matriz del Semáforo Multidimensional (Capacidades y Bienestar)")

def obtener_badge_semaforo(cat):
    if 'Verde' in cat:
        return '🟢 **Verde (Transformador)**'
    elif 'Amarillo' in cat:
        return '🟡 **Amarillo (Alerta Social)**'
    elif 'Rojo Crítico' in cat:
        return '🚨 **Rojo Crítico (Elefante Blanco)**'
    else:
        return '🔴 **Rojo (Ineficiencia)**'

def obtener_accion_recomendada(cat):
    if 'Verde' in cat:
        return 'Modelo de éxito. Priorizar escalabilidad y coinversión.'
    elif 'Amarillo' in cat:
        return 'Fortalecer programas de empleo juvenil y focalización educativa.'
    elif 'Rojo Crítico' in cat:
        return 'Acción correctiva urgente, auditoría y reporte a entes de control.'
    else:
        return 'Reorientar gasto de regalías hacia sectores de alto impacto social.'

df_display = df_filtrado.copy()
df_display['Semáforo'] = df_display['categoria_semaforo'].apply(obtener_badge_semaforo)
df_display['Acción Recomendada'] = df_display['categoria_semaforo'].apply(obtener_accion_recomendada)

st.dataframe(
    df_display[[
        'municipio', 'Semáforo', 'tasa_desempleo', 'cobertura_educativa', 
        'delta_nbi', 'acceso_servicios_publicos', 'IMSC_score', 'Acción Recomendada'
    ]].rename(columns={
        'municipio': 'Municipio',
        'tasa_desempleo': 'Desempleo (%)',
        'cobertura_educativa': 'Educación (%)',
        'delta_nbi': 'Reducción NBI',
        'acceso_servicios_publicos': 'Servicios Púb. (%)',
        'IMSC_score': 'Puntaje IMSC'
    }),
    use_container_width=True
)

st.markdown("---")

# --- Gráficos Comparativos Multivariables ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("🎓 Cobertura Educativa vs. Desempleo (%)")
    st.bar_chart(data=df_filtrado.set_index('municipio')[['cobertura_educativa', 'tasa_desempleo']])

with col_graf2:
    st.subheader("📈 Índice Multidimensional de Desarrollo (IMSC)")
    st.bar_chart(data=df_filtrado.set_index('municipio')['IMSC_score'])

# --- Detalle Teórico ---
with st.expander("ℹ️ Ver fundamentación multivariable del Enfoque de Capacidades"):
    st.markdown("""
    * **Desarrollo Humano (Amartya Sen):** La infraestructura y las regalías dejan de ser un fin contable y se evalúan en función de si generan empleos dignos, mejoran la educación y reducen las privaciones sociales.
    * **Variables Integradas:** Tasa de desempleo local, cobertura educativa neta, reducción de Necesidades Básicas Insatisfechas (NBI) y acceso efectivo a servicios públicos domiciliarios.
    """)
