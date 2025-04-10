import requests
import os
import pprint
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage


load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def post_request(url, params):
  headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
  }

  res = requests.post(url, headers=headers, json=params)
  if res.status_code != 200:
      print(f"Error: {res.status_code}")
      print(res.text)
      return None
  return res.json()


def get_database_id():
  url = "https://api.notion.com/v1/search"

  params = {
      "filter": {
          "property": "object",
          "value": "database"
      }
  }
  
  data = post_request(url, params)
  
  databases = data["resulparamsts"]
  if not databases:
      print("No databases found.")
      return None
    
  database_id = databases[0]["id"]
  return database_id


def get_birthdays_today():
  database_id = get_database_id()
  if not database_id:
      return []
    
  url = f"https://api.notion.com/v1/databases/{database_id}/query"

  params = {
      "filter": {
          "property": "Aniversariante",
          "checkbox": {
              "equals": True
          }
      }
  }

  data = post_request(url, params)["results"]
  
  birthdays_today = []
  for result in data:
      properties = result["properties"]
      
      name = properties["Nome"]["title"][0]["text"]["content"]
      email = properties["Email"]["email"]
      
      birthday = properties["Aniversário"]["date"]["start"]
      birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
      today = datetime.today().date()
      
      age = today.year - birthday_date.year

      person = {
        name: {
          "email": email, 
          "age": age
          }
        }
      
      birthdays_today.append(person)
  
  pprint.pp(  birthdays_today)

  return birthdays_today

def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print(f"✅ Email sent to {to}")

def send_message_to_email(birthdays):
  for birthday in birthdays:
    for name, infos in birthday.items():
      subject = f"🎉 Feliz Aniversário, {name}!"
      
      body= f"""Olá, {name},
Parabéns pelos {infos["age"]} anos! 🎉
Feliz aniversário! 🎂 Desejo a você um dia fantástico, cheio de alegria e risos!

Muitas felicidades, Equipe Carrossel Caipira 🎠.
      """
          
      send_email(to=infos["email"], subject=subject, body=body)



if __name__ == "__main__":
  birthdays = get_birthdays_today()
  if birthdays:
    send_message_to_email(birthdays)
  else:
    print("No birthdays today.")
    