import streamlit as st
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Regalías del Carbón con Impacto - Cesar",
    page_icon="⛏️",
    layout="wide"
)

# Título Principal y Descripción orientada al Carbón y Transición
st.title("⛏️ Regalías del Carbón con Impacto: Evaluación Territorial y Social (Cesar 2020-2026)")
st.markdown("""
**Plataforma de evaluación ex-post y ex-ante del Sistema General de Regalías (SGR)** fundamentada en el **Enfoque de las Capacidades de Amartya Sen**. 
Diseñada para evaluar el rendimiento de los recursos provenientes de la **minería del carbón**, detectar elefantes blancos, medir la **Transición Productiva ($IST_m$)** hacia economías diversificadas (agroindustria, turismo y energías renovables) y su impacto real en la reducción del NBI del DANE en el departamento del Cesar.
""")

# --- Carga de Datos Oficiales del Proyecto (Regalías Mineras) ---
@st.cache_data
def load_project_data():
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
        # Inversión orientada a la descarbonización y transición productiva
        'inversion_transicion': [
            119559119900, 88607559600, 130972912100, 5876209200, 
            11307180000, 54556345600, 63135032200, 16073883270, 4282383040
        ],
        'eficiencia_contractual': [0.75, 0.82, 0.70, 0.55, 0.88, 0.40, 0.78, 0.80, 0.85],
        'delta_nbi': [4.7, 4.1, 4.2, 3.3, 5.1, 3.5, 3.8, 3.5, 3.6] # Retorno Social del Capital (RSC)
    }
    df = pd.DataFrame(data)
    
    # 1. Índice de Ejecución Real y Funcional (ER_m)
    df['ER_m'] = df['proyectos_operativos'] / df['proyectos_totales']
    
    # 2. Factor de Penalización por Inoperatividad (P_m)
    df['P_m'] = (df['proyectos_inoperativos_liquidados'] / df['proyectos_totales']) + (df['alertas_entes_control'] * 0.1)
    
    # 3. Índice de Sostenibilidad y Transición Municipal (IST_m) - Reconversión de la renta minera
    df['IST_m'] = df['inversion_transicion'] / df['presupuesto_total']
    
    # 4. Índice de Impacto y Eficiencia Real (IIER_m)
    df['IIER_score'] = (0.4 * df['eficiencia_contractual'] + 0.6 * df['ER_m']) * df['delta_nbi'] * 10 - (df['P_m'] * 5)
    
    # 5. Matriz del Semáforo Oficial
    def clasificar_semaforo(row):
        if row['P_m'] > 0.3 or row['ER_m'] == 0:
            return 'Rojo Crítico (Elefante Blanco Minero)'
        elif row['P_m'] > 0.15 or row['eficiencia_contractual'] < 0.6:
            return 'Rojo (Ineficiencia Contractual)'
        elif row['ER_m'] < 0.35:
            return 'Amarillo (En Ejecución / Alerta de Gestión)'
        else:
            return 'Verde (Inversión Transformadora Post-Carbón)'

    df['categoria_semaforo'] = df.apply(clasificar_semaforo, axis=1)
    
    return df

df = load_project_data()

# --- Barra Lateral: Filtros ---
st.sidebar.header("🎛️ Panel de Control y Filtros")
municipio_sel = st.sidebar.selectbox("Seleccione un Municipio:", ["Todos los Municipios"] + list(df['municipio']))

if municipio_sel != "Todos los Municipios":
    df_filtrado = df[df['municipio'] == municipio_sel]
else:
    df_filtrado = df

# --- Indicadores Globales ---
st.header("📊 Indicadores Globales de Regalías Mineras (Cesar 2020-2026)")
col1, col2, col3, col4 = st.columns(4)

presupuesto_total = df_filtrado['presupuesto_total'].sum()
er_promedio = df_filtrado['ER_m'].mean() * 100
iier_promedio = df_filtrado['IIER_score'].mean()
ist_promedio = df_filtrado['IST_m'].mean() * 100

col1.metric("Presupuesto Regalías SGR", f"${presupuesto_total / 1e9:,.2f} Mil M.")
col2.metric("Funcionalidad Real (ER_m)", f"{er_promedio:.1f}%")
col3.metric("Puntaje IIER Promedio", f"{iier_promedio:.2f}")
col4.metric("Transición Post-Carbón (IST_m)", f"{ist_promedio:.1f}%")

st.markdown("---")

# --- Matriz del Semáforo Oficial ---
st.header("🚦 Matriz del Semáforo: Evaluación de la Renta Minera")

def obtener_badge_semaforo(cat):
    if 'Verde' in cat:
        return '🟢 **Verde (Transformador)**'
    elif 'Amarillo' in cat:
        return '🟡 **Amarillo (Alerta)**'
    elif 'Rojo Crítico' in cat:
        return '🚨 **Rojo Crítico (Elefante Blanco)**'
    else:
        return '🔴 **Rojo (Ineficiencia)**'

def obtener_accion_recomendada(cat):
    if 'Verde' in cat:
        return 'Modelo exitoso de diversificación económica. Priorizar escalabilidad.'
    elif 'Amarillo' in cat:
        return 'Monitoreo técnico preventivo frente a la dependencia extractiva.'
    elif 'Rojo Crítico' in cat:
        return 'Reporte a Entes de Control e intervención urgente de obras inconclusas.'
    else:
        return 'Ajuste administrativo por retrasos contractuales severos.'

df_display = df_filtrado.copy()
df_display['Semáforo'] = df_display['categoria_semaforo'].apply(obtener_badge_semaforo)
df_display['Acción Recomendada'] = df_display['categoria_semaforo'].apply(obtener_accion_recomendada)

st.dataframe(
    df_display[[
        'municipio', 'Semáforo', 'ER_m', 'IST_m', 'delta_nbi', 
        'P_m', 'IIER_score', 'Acción Recomendada'
    ]].rename(columns={
        'municipio': 'Municipio',
        'ER_m': 'Ejecución Real (ER_m)',
        'IST_m': 'Transición Post-Carbón (IST_m)',
        'delta_nbi': 'Impacto Social (Δ NBI)',
        'P_m': 'Penalización (P_m)',
        'IIER_score': 'Puntaje IIER'
    }),
    use_container_width=True
)

st.markdown("---")

# --- Gráficos Comparativos ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Comparativa de Impacto (IIER_m)")
    st.bar_chart(data=df_filtrado.set_index('municipio')['IIER_score'])

with col_graf2:
    st.subheader("🌾 Inversión en Transición Productiva (IST_m)")
    st.bar_chart(data=df_filtrado.set_index('municipio')['IST_m'])

# --- Marco Teórico ---
with st.expander("ℹ️ Ver fundamentación sobre la Renta Minera y el Enfoque de Capacidades"):
    st.markdown("""
    * **El Reto del Post-Carbón:** Los ingresos por regalías mineras en el departamento del Cesar exigen una transformación estructural para evitar la maldición de los recursos naturales.
    * **Transición Productiva ($IST_m$):** Evalúa qué porcentaje de los recursos de regalías se destina efectivamente a diversificar la economía hacia la agroindustria, el turismo sostenible y las energías renovables, mejorando las capacidades humanas de largo plazo según Amartya Sen.
    """)
