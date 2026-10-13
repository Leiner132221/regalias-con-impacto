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
st.title("🏛️ Regalías con Impacto: Evaluación Territorial y Social (Cesar 2020-2026)")
st.markdown("""
**Plataforma de evaluación ex-post y ex-ante del Sistema General de Regalías (SGR)** fundamentada en el **Enfoque de las Capacidades de Amartya Sen**.
Mide la **Funcionalidad Real ($ER_m$)** (detección de elefantes blancos), el **Retorno Social del Capital ($RSC$)** vía variación de NBI, la **Transición Productiva ($IST_m$)** y penaliza proyectos inoperativos.
""")

# --- Carga / Generación de Datos de Ejemplo (Base de Datos Unificada) ---
@st.cache_data
def load_data():
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
        'delta_nbi': [4.7, 4.1, 4.2, 3.3, 5.1, 3.5, 3.8, 3.5, 3.6]
    }
    df = pd.DataFrame(data)
    
    # 1. Índice de Ejecución Real y Funcional (ER_m)
    df['ER_m'] = df['proyectos_operativos'] / df['proyectos_totales']
    
    # 2. Factor de Penalización por Inoperatividad (P_m)
    df['P_m'] = (df['proyectos_inoperativos_liquidados'] / df['proyectos_totales']) + (df['alertas_entes_control'] * 0.1)
    
    # 3. Índice de Sostenibilidad y Transición Municipal (IST_m)
    df['IST_m'] = df['inversion_transicion'] / df['presupuesto_total']
    
    # 4. Índice de Impacto y Eficiencia Real (IIER_m)
    df['IIER_score'] = (0.4 * df['ER_m'] + 0.6 * df['IST_m']) * df['delta_nbi'] * 10 - (df['P_m'] * 5)
    
    # 5. Clasificación según la Matriz del Semáforo
    def clasificar_semaforo(row):
        if row['P_m'] > 0.3 or row['ER_m'] == 0:
            return 'Rojo Crítico (Elefante Blanco Contable)'
        elif row['P_m'] > 0.15 or row['ER_m'] < 0.2:
            return 'Rojo (Ineficiencia Contractual)'
        elif row['ER_m'] < 0.35:
            return 'Amarillo (Alerta de Gestión)'
        else:
            return 'Verde (Inversión Transformadora)'

    df['categoria_semaforo'] = df.apply(clasificar_semaforo, axis=1)
    
    return df

df = load_data()

# --- Barra Lateral: Filtros ---
st.sidebar.header("🎛️ Panel de Control y Filtros")
municipio_sel = st.sidebar.selectbox("Seleccione un Municipio:", ["Todos los Municipios"] + list(df['municipio']))

# Filtrado de DataFrame
if municipio_sel != "Todos los Municipios":
    df_filtrado = df[df['municipio'] == municipio_sel]
else:
    df_filtrado = df

# --- Indicadores Globales ---
st.header("📊 Indicadores Globales del Departamento")
col1, col2, col3, col4 = st.columns(4)

presupuesto_total = df_filtrado['presupuesto_total'].sum()
er_promedio = df_filtrado['ER_m'].mean() * 100
iier_promedio = df_filtrado['IIER_score'].mean()
penalizacion_promedio = df_filtrado['P_m'].mean()

col1.metric("Presupuesto Total Analizado", f"${presupuesto_total / 1e9:,.2f} Mil M.")
col2.metric("Promedio Ejecución Real (ER_m)", f"{er_promedio:.1f}%")
col3.metric("Promedio Puntaje IIER", f"{iier_promedio:.2f}")
col4.metric("Factor Penalización Prom. (P_m)", f"{penalizacion_promedio:.2f}")

st.markdown("---")

# --- Matriz del Semáforo ---
st.header("🚦 Matriz del Semáforo y Clasificación de Riesgo Territorial")

def obtener_badge_semaforo(cat):
    if 'Verde' in cat:
        return '🟢 **Verde**'
    elif 'Amarillo' in cat:
        return '🟡 **Amarillo**'
    elif 'Rojo Crítico' in cat:
        return '🚨 **Rojo Crítico**'
    else:
        return '🔴 **Rojo**'

def obtener_accion_recomendada(cat):
    if 'Verde' in cat:
        return 'Proyecto modelo. Priorización para refinanciación ex-ante.'
    elif 'Amarillo' in cat:
        return 'Monitoreo técnico preventivo y auditoría de tiempos.'
    elif 'Rojo Crítico' in cat:
        return 'Reporte a entes de control (Contraloría/Procuraduría) e intervención inmediata.'
    else:
        return 'Intervención administrativa por adiciones de tiempo/presupuesto.'

df_display = df_filtrado.copy()
df_display['Semáforo'] = df_display['categoria_semaforo'].apply(obtener_badge_semaforo)
df_display['Acción Recomendada'] = df_display['categoria_semaforo'].apply(obtener_accion_recomendada)

st.dataframe(
    df_display[[
        'municipio', 'Semáforo', 'categoria_semaforo', 'ER_m', 'IST_m', 
        'P_m', 'IIER_score', 'Acción Recomendada'
    ]].rename(columns={
        'municipio': 'Municipio',
        'categoria_semaforo': 'Categoría del Marco',
        'ER_m': 'Ejecución Real (ER_m)',
        'IST_m': 'Transición Prod. (IST_m)',
        'P_m': 'Penalización (P_m)',
        'IIER_score': 'Puntaje IIER'
    }),
    use_container_width=True
)

st.markdown("---")

# --- Gráficos Comparativos ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Comparativa de Impacto (IIER Score)")
    st.bar_chart(data=df_filtrado.set_index('municipio')['IIER_score'])

with col_graf2:
    st.subheader("🌾 Índice de Transición Productiva (IST_m)")
    st.line_chart(data=df_filtrado.set_index('municipio')['IST_m'])

# --- Detalle de la Metodología Sen ---
with st.expander("ℹ️ Ver metodología del Enfoque de Capacidades y Definición de Semáforos"):
    st.markdown("""
    * **🟢 Verde (Inversión Transformadora):** Alta funcionalidad, 100% operativo y reducción constante de NBI.
    * **🟡 Amarillo (En Ejecución / Alerta de Gestión):** Avance formal continuo, sin afectación grave en campo[cite: 19].
    * **🔴 Rojo (Ineficiencia Contractual):** Adiciones presupuestales >30% y prórrogas acumuladas[cite: 19].
    * **🚨 Rojo Crítico (Elefante Blanco Contable):** Estatus DNP "Liquidado", pero con operatividad real igual a cero[cite: 19].
    """)
