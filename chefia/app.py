import streamlit as st
import google.generativeai as genai
import csv
from datetime import datetime

# Configuração da chave
genai.configure(api_key="AIzaSyCT-5QTvKm2jW2V8_S9zOKJUbrLcwPaaSE")

# Modelo Gemini
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuração da página
st.set_page_config(page_title="ChefIA", page_icon="🍳", layout="wide")

st.title("🍳 ChefIA: Sua Receita Inteligente")
st.markdown("Descubra receitas baseadas nos ingredientes que você tem, seu humor e o tempo disponível.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Preferências")

    st.subheader("🥦 Ingredientes disponíveis")
    ingredientes_padrao = ["Arroz", "Frango", "Tomate", "Batata", "Feijão", "Ovos", "Queijo",
                           "Macarrão", "Cebola", "Alho", "Cenoura", "Leite", "Farinha", "Manteiga"]
    ingredientes = st.multiselect("Selecione os ingredientes:", ingredientes_padrao)

    ingrediente_custom = st.text_input("➕ Adicionar ingrediente personalizado:")
    if ingrediente_custom and ingrediente_custom not in ingredientes:
        ingredientes.append(ingrediente_custom)

    st.subheader("🚫 Restrições alimentares")
    restricoes = st.multiselect("Selecione suas restrições:",
                                ["Vegetariano", "Vegano", "Sem glúten", "Sem lactose", "Sem ovos", "Sem frutos do mar"])

    st.subheader("⏱️ Tempo disponível para cozinhar")
    tempo_opcao = st.radio(
        "Quanto tempo você tem?",
        options=["Até 15 minutos", "Até 30 minutos", "Até 1 hora", "Mais de 1 hora", "Personalizado"],
        index=1
    )

    if tempo_opcao == "Personalizado":
        tempo_minutos = st.number_input(
            "Digite o tempo em minutos:",
            min_value=5,
            max_value=300,
            value=30,
            step=5
        )
        tempo_label = f"{tempo_minutos} minutos"
    else:
        tempo_label = tempo_opcao
        tempo_map = {
            "Até 15 minutos": 15,
            "Até 30 minutos": 30,
            "Até 1 hora": 60,
            "Mais de 1 hora": 90
        }
        tempo_minutos = tempo_map[tempo_opcao]

    st.subheader("😊 Contexto / Humor")
    mood = st.text_area(
        "Descreva o que você deseja:",
        placeholder="Ex: Quero algo leve para o jantar em família."
    )

    nivel_dificuldade = st.select_slider(
        "🎯 Nível de dificuldade desejado:",
        options=["Muito fácil", "Fácil", "Médio", "Difícil"],
        value="Fácil"
    )

    porcoes = st.number_input("🍽️ Número de porções:", min_value=1, max_value=20, value=2)

    botao_recomendar = st.button("🔍 Buscar Receitas", use_container_width=True)

# --- PROCESSAMENTO ---
if botao_recomendar:
    if not mood and not ingredientes:
        st.warning("⚠️ Por favor, selecione ingredientes ou descreva o que você deseja!")
    else:
        ingredientes_str = ', '.join(ingredientes) if ingredientes else "ingredientes básicos de cozinha"
        restricoes_str = ', '.join(restricoes) if restricoes else "nenhuma"

        with st.spinner("👨‍🍳 Analisando receitas..."):
            prompt = f"""
Você é um chef especialista em culinária brasileira e internacional.

Sugira exatamente 3 receitas com base nas seguintes informações:
- **Ingredientes disponíveis:** {ingredientes_str}
- **Restrições alimentares:** {restricoes_str}
- **Tempo máximo disponível para cozinhar:** {tempo_label}
- **Nível de dificuldade desejado:** {nivel_dificuldade}
- **Número de porções:** {porcoes}
- **Contexto/humor do usuário:** {mood if mood else "sem preferência específica"}

IMPORTANTE: Todas as receitas devem ser preparadas em no máximo {tempo_minutos} minutos.

Para cada receita, forneça no seguinte formato:
## 🍽️ [Nome da Receita]
- ⏱️ **Tempo de preparo:** X minutos
- 🎯 **Dificuldade:** [nível]
- 🍴 **Porções:** {porcoes}
- ✨ **Por que combina:** [frase curta explicando a escolha]
- 📋 **Ingredientes principais:** [lista rápida]
- 👨‍🍳 **Modo de preparo resumido:** [passos simples]
"""

            try:
                response = model.generate_content(prompt)

                st.success("✅ Aqui estão minhas sugestões para você:")

                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("⏱️ Tempo disponível", tempo_label)
                with col_info2:
                    st.metric("🎯 Dificuldade", nivel_dificuldade)
                with col_info3:
                    st.metric("🍽️ Porções", porcoes)

                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")

                # --- FEEDBACK ---
                st.markdown("### 💬 O que achou das sugestões?")
                col1, col2 = st.columns(2)

                def salvar_feedback(avaliacao):
                    with open("feedback.csv", "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                            mood,
                            ingredientes_str,
                            restricoes_str,
                            tempo_label,
                            nivel_dificuldade,
                            porcoes,
                            avaliacao
                        ])

                with col1:
                    if st.button("👍 Gostei", use_container_width=True):
                        salvar_feedback("Gostei")
                        st.success("Obrigado pelo feedback positivo! 😊")
                with col2:
                    if st.button("👎 Não gostei", use_container_width=True):
                        salvar_feedback("Não gostei")
                        st.info("Feedback registrado! Vamos melhorar. 🙏")

            except Exception as e:
                st.error(f"❌ Erro ao conectar com a IA: {e}")

# --- RODAPÉ ---
st.markdown("---")
st.caption("🍳 ChefIA • Powered by Google Gemini")