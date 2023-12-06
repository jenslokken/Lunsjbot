import requests
from bs4 import BeautifulSoup
import sys
import os
from threading import Thread
import datetime
import time
import chompjs


def generate_menu():
    menu_path = "https://tullin.munu.shop/meny"

    page = requests.get(menu_path)
    soup = BeautifulSoup(page.content, "html.parser")

    script = soup.findAll("script")
    j = script[1].text[42:-3]
    # j = j.replace("\\u0022", "'")
    j = j.split("JSON.parse(")[-1][1:]
    j = j.replace("\\u0022", '"')
    j = j.replace("\\u003C", "<")
    j = j.replace("\\u003E", ">")
    j = j.replace('\\\\"', "'")

    js = chompjs.parse_js_object(j)
    js = js["general"]["staticPages"][-1]["body"]

    new_soup = BeautifulSoup(js, "html.parser")
    out = new_soup.get_text(separator=" ").replace("\\n", "").replace("\\r", "")
    return out


token = os.environ.get("TOKEN")


def send_message(message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    myobj = {
        "channel": "kxo-lunsjboten",
        "text": message,
    }

    x = requests.post(url, headers=headers, json=myobj)
    print("Status Code", x.status_code)


# openai_utils.py
import openai
import os


def load_api_keys():
    # """Loads API keys from .env file"""
    API_KEY_1 = os.environ.get("AZURE_OPENAI_KEY")
    return API_KEY_1


def select_api_key(model):
    # """Selects the appropriate API key based on model"""
    API_KEY_1 = load_api_keys()

    if model == "gpt-3.5-turbo":
        return API_KEY_1
    else:
        raise ValueError("Invalid model specified.")


def generate_openai_response(
    prompt, model="gpt-3.5-turbo", temperature=0.7, num_responses=1
):
    # """Generates a response from OpenAI's GPT model"""
    openai.api_key = select_api_key(model)
    openai.api_type = "azure"
    openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-07-01-preview"
    messages = [{"role": "user", "content": prompt}]
    responses = []
    for _ in range(num_responses):
        response = openai.ChatCompletion.create(
            engine="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )
        responses.append(response.choices[0].message["content"])
    return responses if num_responses > 1 else responses[0]


send_message(
    "Dagens meny i kantinen er:lunch-train::drum_with_drumsticks::drum_with_drumsticks::"
)

# print(generate_openai_response("Kan du hente ut hovedrett, vegetar og suppe fra denne html-filen? Jeg vil ha det på formatet {'Hovedrett':'', 'Vegetar':'', 'Suppe': ''} \n" + SOUP[-8000:]))
time.sleep(3)
message = ""
menu = generate_openai_response(
    'Kan du hente ut en json på dette formatet fra denne teksten? {dag: {"hovedrett":, "vegetar": , "Suppe: }} og rette eventuelle skrivefeil?'
    + generate_menu()
    + "\n Hvis det ikke er en hovedrett, så setter du vegetarretten som hovedrett og dropper å ha vegetar"
)

week = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]

today = datetime.date.today().weekday()
menu = chompjs.parse_js_object(menu)
# menu = eval(menu)
try:
    day_menu = menu[week[today]]
except:
    week = list(map(str.lower, week))
    day_menu = menu[week[today]]

message = ""

for key, value in day_menu.items():
    if not value:
        continue
    try:
        if value[-1] != ".":
            value += "."
    except:
        pass
    line = key.capitalize() + ": " + value.capitalize() + "\n"
    message += line

send_message(message)
sys.exit()
