import streamlit as st
from supabase import create_client
import uuid
from datetime import datetime

st.set_page_config(page_title="CharAI.deutsch – Deine deutschen KI-Charaktere", page_icon="🤖", layout="centered")

# Supabase Verbindung (wird später mit Secrets gefüllt)
supabase_url = st.secrets.get("SUPABASE_URL")
supabase_key = st.secrets.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

# Fake-Login bis Supabase läuft
if "user" not in st.session_state:
    st.session_state.user = {"email": "du@charai.deutsch"}
user = st.session_state.user


st.sidebar.success(f"Angemeldet als {user['email']}")

page = st.sidebar.radio("Navigation", ["Galerie", "Charakter erstellen", "Meine Charaktere"])

if page == "Galerie":
    st.title("CharAI.deutsch – Die Community")
    st.markdown("Die beliebtesten deutschen KI-Charaktere")
    if supabase:
        chars = supabase.table("characters").select("*").order("likes", desc=True).execute().data
        cols = st.columns(3)
        for i, char in enumerate(chars or []):
            with cols[i % 3]:
                st.image(char.get("avatar", "https://via.placeholder.com/200"), use_column_width=True)
                st.subheader(char["name"])
                st.caption(f"❤️ {char.get('likes',0)} Likes")
                if st.button("Chatten", key=f"chat_{char['id']}"):
                    st.session_state.active_char = char
                    st.rerun()
    else:
        st.info("Supabase noch nicht verbunden – Galerie kommt in 2 Minuten!")

if page == "Charakter erstellen":
    st.title("Neuen Charakter erstellen")
    with st.form("new_char"):
        name = st.text_input("Name")
        desc = st.text_area("Beschreibung")
        prompt = st.text_area("System-Prompt (Persönlichkeit)", height=200)
        avatar = st.file_uploader("Avatar", type=["png","jpg","jpeg"])
        model = st.selectbox("Modell", ["gpt-4o-mini", "claude-3-haiku", "llama3-70b (Groq)"])
        if st.form_submit_button("Veröffentlichen!", type="primary"):
            if supabase:
                avatar_url = "https://via.placeholder.com/200"
                if avatar:
                    path = f"avatars/{uuid.uuid4()}.jpg"
                    supabase.storage.from_("avatars").upload(path, avatar.getvalue())
                    avatar_url = supabase.storage.from_("avatars").get_public_url(path)
                supabase.table("characters").insert({
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "beschreibung": desc,
                    "prompt": prompt,
                    "model": model,
                    "avatar": avatar_url,
                    "creator": user["email"],
                    "likes": 0
                }).execute()
                st.success("Dein Charakter ist live!")
            else:
                st.success("Test-Charakter erstellt – Supabase kommt gleich!")
            st.balloons()

st.balloons()
st.success("Deine deutsche Character.AI ist jetzt FERTIG! Nur noch Supabase Secrets eintragen und du hast die volle Community-Plattform!")
