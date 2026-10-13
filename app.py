# ==========================================
# DASHBOARD INTERACTIVO: REGALÍAS CON IMPACTO (CESAR 2020-2026)
# Framework: Streamlit
# ==========================================

import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Regalías con Impacto - Cesar",
    page_icon="📊",
    layout="wide"
)

# Título principal y presentación institucional
st.title("🏛️ Regalías con Impacto: Evaluación Territorial y Social (Cesar 2020-2026)")
st.markdown("""
Plataforma de evaluación ex-post y ex-ante del Sistema General de Regalías (SGR). 
Mide la **Funcionalidad Real** (caza de elefantes blancos), la **Transición Productiva (IST)** 
y el impacto directo en la reducción de la pobreza (**NBI**), fundamentado en el Enfoque de Capacidades de Amartya Sen.
""")

@st.cache_data
def cargar_datos():
    # Simulación replicando la estructura validada en el motor econométrico
    municipios_cesar = [
        ("Valledupar", "20001"), ("Aguachica", "20011"), ("Agustín Codazzi", "20013"),
        ("Bosconia", "20032"), ("Chimichagua", "20045"), ("La Paz", "20621"),
        ("San Alberto", "20770"), ("El Paso", "20250"), ("La Jagua de Ibirico", "20400")
    ]
    
    data = []
    np.random.seed(42)
    for i in range(1, 150):
        muni, divipola = municipios_cesar[np.random.randint(0, len(municipios_cesar))]
        monto = np.random.randint(1200, 30000) * 1e6
        avance = np.random.uniform(20, 100)
        estado = "Liquidado" if avance == 100 else ("En Ejecución" if avance > 50 else "Suspendido")
        funcional = 1 if (estado == "Liquidado" and np.random.rand() > 0.25) else (1 if avance > 85 else 0)
        
        data.append({
            "bpin": f"BPIN_{divipola}_{i:03d}",
            "municipio": muni,
            "divipola": divipola,
            "valor_asignado": monto,
            "funcional_real": funcional
        })
    
    df_sgr = pd.DataFrame(data)
    
    df_dane = pd.DataFrame([
        {"divipola": "20001", "nbi_inicial": 24.5, "nbi_actual": 19.8},
        {"divipola": "20011", "nbi_inicial": 32.1, "nbi_actual": 28.0},
        {"divipola": "20013", "nbi_inicial": 35.4, "nbi_actual": 31.2},
        {"divipola": "20032", "nbi_inicial": 29.8, "nbi_actual": 26.5},
        {"divipola": "20045", "nbi_inicial": 48.2, "nbi_actual": 43.1},
        {"divipola": "20621", "nbi_inicial": 28.5, "nbi_actual": 25.0},
        {"divipola": "20770", "nbi_inicial": 26.0, "nbi_actual": 22.4},
        {"divipola": "20250", "nbi_inicial": 41.0, "nbi_actual": 37.5},
        {"divipola": "20400", "nbi_inicial": 22.0, "nbi_actual": 18.2}
    ])
    
    df_master = pd.merge(df_sgr, df_dane, on='divipola', how='left')
    df_resumen = df_master.groupby(['divipola', 'municipio', 'nbi_inicial', 'nbi_actual']).agg(
        presupuesto_total=('valor_asignado', 'sum'),
        proyectos_totales=('bpin', 'count'),
        proyectos_operativos=('funcional_real', 'sum')
    ).reset_index()
    
    df_resumen['ER_m'] = df_resumen['proyectos_operativos'] / df_resumen['proyectos_totales']
    df_resumen['IST_m'] = np.random.uniform(0.15, 0.65, len(df_resumen))
    df_resumen['delta_nbi'] = df_resumen['nbi_inicial'] - df_resumen['nbi_actual']
    df_resumen['IIER_score'] = (0.5 * df_resumen['ER_m'] + 0.5 * df_resumen['IST_m']) * df_resumen['delta_nbi'] * 10
    
    return df_resumen.sort_values(by='IIER_score', ascending=False)

df = cargar_datos()

# Barra lateral (Sidebar) para filtros
st.sidebar.header("🎛️ Panel de Control y Filtros")
municipio_seleccionado = st.sidebar.selectbox(
    "Seleccione un Municipio:",
    options=["Todos los Municipios"] + list(df['municipio'].unique())
)

# Filtrado dinámico
if municipio_seleccionado != "Todos los Municipios":
    df_filtrado = df[df['municipio'] == municipio_seleccionado]
else:
    df_filtrado = df

# Métricas Principales (KPIs)
st.markdown("### 📈 Indicadores Globales del Departamento")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Presupuesto Total Analizado", value=f"${df_filtrado['presupuesto_total'].sum() / 1e9:,.2f} Mil Millones COP")
with col2:
    st.metric(label="Promedio Ejecución Real (ER_m)", value=f"{df_filtrado['ER_m'].mean() * 100:.1f}%")
with col3:
    st.metric(label="Promedio Puntaje IIER", value=f"{df_filtrado['IIER_score'].mean():.2f}")

st.markdown("---")

# Visualización de la Tabla
st.markdown("### 📋 Matriz de Evaluación por Municipio")
st.dataframe(df_filtrado[['municipio', 'presupuesto_total', 'ER_m', 'IST_m', 'delta_nbi', 'IIER_score']], use_container_width=True)

# Gráfico de barras interactivo nativo de Streamlit
st.markdown("### 📊 Comparativa de Impacto (IIER Score)")
st.bar_chart(df_filtrado.set_index('municipio')['IIER_score'])

st.markdown("---")
st.caption("Desarrollado para el Departamento del Cesar (2020-2026) | Metodología de Capacidades de Amartya Sen.")
