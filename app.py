import base64, io, os
import streamlit as st
import anthropic
from PIL import Image

st.set_page_config(page_title="Dénicheur CarPlay", page_icon="🚗")
st.title("🚗 Dénicheur d'écran CarPlay")

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT = """Voici une photo de l'intérieur de ma voiture.
1. Identifie la marque, le modèle et l'année probable (et dis-moi ton niveau de certitude).
2. Repère l'emplacement et le format de l'autoradio actuel (simple DIN, double DIN, taille).
3. Cherche sur AliExpress un écran Android / CarPlay compatible avec ce modèle.
4. Privilégie les vendeurs avec de bons avis (note élevée, beaucoup de ventes).
5. Donne-moi 3 options max : nom, prix approximatif, points forts, points faibles, lien.
Si tu n'es pas sûr de la compatibilité, dis-le clairement."""

photo = st.file_uploader("Photo de l'intérieur", type=["jpg", "jpeg", "png"])
extra = st.text_input("Précision (optionnel)", placeholder="ex : Clio 4 de 2016")

if photo and st.button("Chercher"):
    img = Image.open(photo).convert("RGB")
    img.thumbnail((1600, 1600))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    data = base64.standard_b64encode(buf.getvalue()).decode()

    content = [
        {"type": "image", "source": {"type": "base64",
                                     "media_type": "image/jpeg", "data": data}},
        {"type": "text", "text": PROMPT + (f"\nPrécision : {extra}" if extra else "")},
    ]
    messages = [{"role": "user", "content": content}]

    with st.spinner("Recherche en cours..."):
        for _ in range(5):
            resp = client.messages.create(
                model="claude-sonnet-5-5",
                max_tokens=2000,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=messages,
            )
            if resp.stop_reason != "pause_turn":
                break
            messages = [messages[0], {"role": "assistant", "content": resp.content}]

    st.markdown("".join(b.text for b in resp.content if b.type == "text"))
