# intro_page.py
import streamlit as st

class IntroPage:
    """Class to render the initial introduction page of the HY4RES platform."""

    def __init__(self):
        pass

    def render(self):
        st.markdown(
            "<h1 style='text-align:center'>Welcome to the HY4RES Decision Support Tool</h1>",
            unsafe_allow_html=True
        )

        intro_text = """
        <div style="
            background-color:#2f3e46;
            padding:22px;
            border-radius:14px;
            color:white;
            box-shadow:0 4px 10px rgba(0,0,0,0.18);
            line-height:1.6;
            font-size:16px;
        ">
        <strong>English:</strong> This platform provides decision support for local energy management in the <strong>Comunidad de Regantes del Valle Inferior del Guadalquivir (Seville, Spain)</strong>. It consists of three SESSIONS: ENERGY PERFORMANCE, LIFE CYCLE IMPACT, and ENERGY RESOURCE OPTIMIZATION. Currently it uses historical data, but in the future it will integrate forecast energy demand and solar generation up to 7 days ahead.<br><br>
        
        <strong>Español:</strong> Esta plataforma proporciona apoyo a la toma de decisiones para la gestión energética local en la <strong>Comunidad de Regantes del Valle Inferior del Guadalquivir (Sevilla, España)</strong>. Consta de tres SECCIONES: DESEMPEÑO ENERGÉTICO, LIFE CYCLE IMPACT y OPTIMIZACIÓN DE RECURSOS ENERGÉTICOS. Actualmente utiliza datos históricos, pero en el futuro podrá incorporar predicciones de demanda y producción solar hasta 7 días adelante.<br>
        
        <strong>Português:</strong> Esta plataforma fornece apoio à tomada de decisões para a gestão energética local na <strong>Comunidad de Regantes del Valle Inferior del Guadalquivir (Sevilha, Espanha)</strong>. Consta de três SESSÕES: DESEMPENHO ENERGÉTICO, LIFE CYCLE IMPACT e OTIMIZAÇÃO DE RECURSOS ENERGÉTICOS. Atualmente utiliza dados históricos, mas no futuro poderá incorporar previsões de demanda e produção solar de até 7 dias.<br>
        
        <strong>Français:</strong> Cette plateforme fournit un soutien à la prise de décision pour la gestion énergétique locale dans la <strong>Comunidad de Regantes del Valle Inferior del Guadalquivir (Séville, Espagne)</strong>. Elle se compose de trois SECTIONS : PERFORMANCE ÉNERGÉTIQUE, LIFE CYCLE IMPACT et OPTIMISATION DES RESSOURCES ÉNERGÉTIQUES. Actuellement, elle utilise des données historiques, mais à la future, elle pourra intégrer des prévisions de demande et de production solaire jusqu'à 7 jours à l'avance.

        </div>
        """
        st.markdown(intro_text, unsafe_allow_html=True)
