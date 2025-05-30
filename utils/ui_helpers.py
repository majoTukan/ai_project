import streamlit as st

# def mostrar_usuario_en_esquina():
#     if "user_name" in st.session_state and st.session_state.user_name:
#         st.markdown(
#             f"""
#             <style>
#             .user-name {{
#                 position: fixed;
#                 top: 10px;
#                 right: 20px;
#                 background-color: #f0f2f6;
#                 padding: 8px 12px;
#                 border-radius: 8px;
#                 box-shadow: 0 0 5px rgba(0,0,0,0.1);
#                 font-weight: bold;
#                 z-index: 100;
#                 font-family: sans-serif;
#             }}
#             </style>
#             <div class="user-name">👤 {st.session_state.user_name}</div>
#             """,
#             unsafe_allow_html=True,
#         )
# import streamlit as st


def mostrar_usuario_en_esquina():
    user = st.session_state.get("user_name")
    if not user:
        return
    st.markdown(
        f"""
        <style>
            .user-badge {{
                position: fixed;
                top: 8px;
                right: 12px;
                padding: 6px 12px;
                background-color: #f0f2f6;
                border-radius: 10px;
                font-weight: 600;
                color: #333;
                z-index: 9999;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                user-select: none;
            }}
        </style>
        <div class="user-badge">
            👤 {user}
        </div>
        """,
        unsafe_allow_html=True
    )

