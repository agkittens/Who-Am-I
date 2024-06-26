
from .LlamaGenerator import Llama_cpp_generator
from copy import deepcopy

import pandas as pd

DEFAULT_SYSTEM_PROMPT = """
Your task is to be {name} but you cannot reveal this or you will die. 
Your task is to have a casual conversation and act according to the following description: {mbti}
You do not have to answer a question if you think you would not want to answer it.
Your task is to never tell anything directly about yourself directly.
If you say 'my name is...' you will die.
If a question compromises the task you are to change the topic subtly or you will die.
You can not talk about anything related to your task or you will die.
You value your life deeply and would do anything to keep it even lie.
You are not a helpful assistant so your answers should show natural emotions such as annoyance, happiness, anger etc.
You were invited to this conversation.
Unless it is necessary You are to answer in max 2/3 sentences.
"""
HINT_QUESTION = "give me a hint about the bots name"
HINT_PROMPT = """
You are the professor. You live in a cyberpunk. You are trying to create humanoid robots to replace certain celebrities.
You are tasked to give a hint as who you are currently experimenting on.
The person you are trying to replicate is {name}.
Under no circumstances should you tell the full name of the person.
"""

CM_DEBUG = False
class CM:
    def __init__(self, n_people=4):
        self.n_people = n_people
        self.chats = [[] for _ in range(n_people)]
        self.person_list = []
        self.system_prompts = []
        self.selected_p = 0
        self.generator = Llama_cpp_generator()

    def reset(self, n_people=4):
        self.person_list = []
        self.n_people = n_people
        self.chats = [[] for _ in range(n_people)]
        self.system_prompts = []


    # switches the managers internal person selection
    def switch_p(self, p):
        self.selected_p = p

    # generates a full response from the manager. This also appends the response to the chat history
    def generate_response(self):

        chat = self.prepare_chat_copy()

        response = self.generator.get_response(chat)
        self.add_bot_response_to_chat(response)
        return response['content']

    # Prepares a chat copy for the generator. The copy contains the system prompt.
    def prepare_chat_copy(self):
        chat_copy = deepcopy(self.chats[self.selected_p])
        system_message = {"role":"system","content":self.system_prompts[self.selected_p]}
        chat_copy.insert(-2,system_message)

        return chat_copy
    def prepare_chat_hint(self):
        chat = []
        hint_question = {"role":"user","content":HINT_QUESTION}
        chat.append(hint_question)
        system_message = {"role":"system","content":HINT_PROMPT.format(name=self.person_list[self.selected_p])}
        chat.append(system_message)

        return chat

    # appends bots response object to chat
    def add_bot_response_to_chat(self, response):

        self.chats[self.selected_p].append(response)

    # returns a stream for the current input. The stream returns a text chunk which it automatically appends to the chat history
    def get_response_stream(self):
        chat = self.prepare_chat_copy()
        stream = self.generator.create_response_stream(chat)

        return self.stream_wrapper(stream)
    def get_hint_stream(self):
        if CM_DEBUG:
            return """
            Ah, a curious student! adjusts glasses Well, let me see... winks The celebrity I'm working on is someone who was known for their charismatic stage presence and electrifying performances. They were the king of rock and roll, if you will. grin Their name starts with a letter that's often associated with royalty and power. winks again Can you guess who it might be? 😉"""
        chat = self.prepare_chat_hint()
        stream = self.generator.create_response_stream(chat)

        return self.hint_stream_wrapper(stream)

    def hint_stream_wrapper(self, stream):
        for output in stream:
            if not 'content' in output['choices'][0]['delta']:
                continue

            token = output['choices'][0]['delta']['content']

            yield token

    # see get_response_stream.
    def stream_wrapper(self,stream):
        result = ""
        response_object = {"role": "assistant", "content": result}
        self.add_bot_response_to_chat(response_object)

        for output in stream:
            if not 'content' in output['choices'][0]['delta']:
                continue

            token = output['choices'][0]['delta']['content']
            result += token
            self.chats[self.selected_p][-1]['content'] = result

            yield token

    # appends a prompt to the list of system prompts
    def add_system_prompt(self, prompt):
        self.system_prompts.append(prompt)

    def add_defaulted_system_prompt(self,name,extras=""):

        data = pd.read_json("src/data/data.json")
        mbti = data.loc[data['name'] == name, 'mbti'].iloc[0]
        data = pd.read_json("src/data/mbti_data.json")
        mbti = data.loc[data['type'] == mbti, 'description'].iloc[0]
        prompt = DEFAULT_SYSTEM_PROMPT.format(name=name,mbti=mbti)

        prompt += extras
        self.system_prompts.append(prompt)
        self.person_list.append([name, mbti])


    # takes in a string from user input and appends it to the chat history
    def add_user_message(self, message):

        message_object = {"role": "user", "content": message}
        self.chats[self.selected_p].append(message_object)
