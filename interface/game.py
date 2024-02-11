import streamlit as st
import pandas as pd
from ChatManager.ChatManager import CM
def game():
    # st.session_state.window = "game"

    @st.cache_data
    def bots_num():
        return 4

    @st.cache_resource
    def get_names():
        data = pd.read_json("data.json")
        data = pd.DataFrame(data)

        names = data['name'].sample(n=4)

        return names

    @st.cache_resource
    def init_CM(names):
        cm = CM()
        for name in names:
            cm.add_defaulted_system_prompt(name)
            print(cm.system_prompts)
        return cm

    BOTS = bots_num()
    ACTIVE_BOT = 1

    # getting data
    names = get_names()
    chat, bots, guesses = st.columns([1.5,1, 0.8], gap="medium")
    cm = init_CM(names)




    with chat:
        with st.container(border=True):
            st.write(
            f'<div style="text-align: center; margin-bottom: 20px; font-size: 24px;'
            f'">Choose your fighter</div>',
            unsafe_allow_html=True)

            columns = st.columns(BOTS)

            for i in range(len(columns)):
                with columns[i]:
                    if st.button(f"Bot {i+1}", type="secondary",key=i, use_container_width=True):
                        ACTIVE_BOT = i
                        cm.switch_p(ACTIVE_BOT)


            messages = st.container(height=300, border=True)
            for message in cm.chats[cm.selected_p]:
                with messages.chat_message(message["role"]):
                    st.write(message["content"])

            if prompt := st.chat_input(placeholder="Your message"):
                messages.chat_message("user").write(prompt)
                cm.add_user_message(prompt)
                stream = cm.get_response_stream()
                # !!!!!!IMPORTANT!!!!!! Dont delete this print it doesnt work without this !!!!!!IMPORTANT!!!!!!
                print(cm.chats)
                with messages.chat_message("assistant"):
                    st.write_stream(stream)
                # st.experimental_rerun()


    with bots:
        with st.container(border=True, height=500):
            st.image("assets/temp.png", use_column_width=True)

    with guesses:
        with st.container(border=True, height=500):
            options = []
            for bot in range(BOTS):
                option = st.selectbox(
                    f"Bot {bot+1}",
                    (names),
                    index=None,
                    placeholder="Am I...",
                    key = f"bot{bot+1}")

                if 'option' not in st.session_state:
                    st.session_state.selected_option = option

                options.append(option)
        if st.button("Finish research", type="secondary", use_container_width=True):
            pass


