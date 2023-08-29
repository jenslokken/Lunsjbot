import requests
from bs4 import BeautifulSoup
import sys
import os
from threading import Thread
import datetime
import time


def generate_menu():
    menu_path = "https://tullin.munu.shop/meny"

    page = requests.get(menu_path)
    soup = BeautifulSoup(page.content, "html.parser")

    week = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "googleprediction"]
    menu = str(soup).lower()
    menu = menu.replace("\\u00f8", "ø" )  
    menu = menu.replace("\\u00e5", "å" )
    menu = menu.replace("\\u00e6", "æ" )
    menu = menu.replace("\\u0026amp;", "og")
    menu_list = menu.split("\\")
    day_content = [[] for _ in range(len(week))]
    day_idx = []

    for j, day in enumerate(week):
        seen_count = 0
        for i, item in enumerate(menu_list):
            if day in item:
                seen_count += 1
                if seen_count == 3 or j == (len(week) - 1):
                    day_idx.append(i)
                

    for i, day in enumerate(week[:-1]):
        start = day_idx[i]
        stop = day_idx[i + 1]
        for j in range(start, stop):
            #if menu_list[j] != "" and  "suppe" in menu_list[j].lower() or "vegetar" in menu_list[j].lower():
                #day_content[i] = [hovedrett, suppe, vegetar]ß
            menu_item = menu_list[j]
            if "u003e" in menu_item or "u00f8" in menu_item or "u00e5" in menu_item or "u00e6" in menu_item:
                try:
                    day_content[i].append(menu_item[5:])
                except:
                    print(day, "fail")
                    print(menu_item, *day_content, sep="\n")
                    sys.exit(1)

    content = []

    for day in day_content:
        new_day = ""
        for d in day:
            if not d:
                continue
            new_day += d + " "
        new_day = new_day.strip()
        content.append(new_day)

    content = content[:-1]

    output = {}

    for c in content:
        output_dict = {
            "hovedrett" : "",
            "vegetar" : "",
            "suppe" : ""
            }

        splitted = c.split()
        day = splitted[0]
        c = " ".join(splitted[1:])

        kjøtt = c.split("vegetar:")
        vegetar = kjøtt[-1].split("suppe:")
        kjøtt = kjøtt[0].strip()
        suppe = "".join(vegetar[1:]).strip()
        vegetar = vegetar[0].strip()
        output_dict["hovedrett"] = kjøtt
        output_dict["vegetar"] = vegetar
        output_dict["suppe"] = suppe
        output[day] = output_dict
    return output



token = os.environ.get('TOKEN')

week = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag"]
week_menu = generate_menu()
today = datetime.date.today().weekday()
day_menu = week_menu[week[today]]

def send_message(message):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
        }
    myobj = {
        'channel': 'kxo-lunsjbot', 
        'text': message,
        }

    x = requests.post(url, headers=headers, json = myobj)
    print("Status Code", x.status_code)


# openai_utils.py
import openai
import os


def load_api_keys():
    #"""Loads API keys from .env file"""
    API_KEY_1 = os.environ.get('OPENAI_API_KEY_1')
    return API_KEY_1

def select_api_key(model):
    #"""Selects the appropriate API key based on model"""
    API_KEY_1 = load_api_keys()

    if model == "gpt-3.5-turbo":
        return API_KEY_1
    else:
        raise ValueError("Invalid model specified.")

def generate_openai_response(prompt, model="gpt-3.5-turbo", temperature=0, num_responses=1):
    #"""Generates a response from OpenAI's GPT model"""
    openai.api_key = select_api_key(model)
    messages = [{"role": "user", "content": prompt}]
    responses = []
    for _ in range(num_responses):
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        print(response)
        responses.append(response.choices[0].message["content"])
    return responses if num_responses > 1 else responses[0]


# send_message("Dagens meny i kantinen er:lunch-train::drum_with_drumsticks::drum_with_drumsticks::")

time.sleep(3)

message = ""

for key, value in day_menu.items():
    if value[-1] != ".":
        value += "."
    line = key.capitalize() + ": " + value.capitalize() + "\n"
    message += line

message = message.strip()
print("kan du rettskrive dette?\n" + message)
try:
    text = generate_openai_response("Kan du rette alle skrivefeil i denne teksten?\n" + message)
except:
    text = message
print(text)
# send_message(text)

