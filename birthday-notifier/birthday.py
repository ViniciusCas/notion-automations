import requests
import os
import pprint
from datetime import datetime
import pytz
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage


load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


local_tz = pytz.timezone("America/Sao_Paulo")
dt_local = datetime.now(local_tz)


def post_request(url, params):
  """
  Send a POST request to the Notion API.
  Args:
      url (str): The URL to send the request to.
      params (dict): The parameters to include in the request.
  Returns:
      dict: The response from the Notion API or None if the request fails.
  Raises:
      Exception: If the request fails.     
  """
  
  headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
  }

  try:
    res = requests.post(url, headers=headers, json=params)
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return None
  
  if res.status_code != 200:
      print(f"Error: {res.status_code}")
      print(res.text)
      return None
    
  return res.json()


def get_database_id():
  """
  Get the database ID from the Notion API.
  Returns:
      str: The database ID or None if not found.
  Raises:
      Exception: If the request fails.
  """
  
  
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
  """
  Get the birthdays for today from the Notion database. 
  Returns:
      list: A list of dictionaries containing names and emails of people with birthdays today.
  Raises:
      Exception: If the request fails.  
  """
  
  database_id = get_database_id()
  if not database_id:
      return []
    
  url = f"https://api.notion.com/v1/databases/{database_id}/query"

  params = {
    "filter": {
        "property": "Aniversário",
        "rich_text": {
            "equals": dt_local.strftime("%d/%m")
        }
    }
  }

  data = post_request(url, params)["results"]
  
  birthdays_today = []
  for result in data:
      properties = result["properties"]
      
      birthday = properties["Aniversário"]["formula"]["string"].split("/")
      person_birth = properties["Data de nascimento"]["date"]["start"]
      
      person_birth = datetime.strptime(person_birth, '%Y-%m-%d').date()
      
      if int(birthday[0]) == dt_local.day and int(birthday[1]) == dt_local.month:
        name = properties["Nome"]["title"][0]["text"]["content"]
        email = properties["Email"]["email"]
        
        age = dt_local.year - person_birth.year
        
        person = {
          name: {
            "email": email, 
            "age": age
            }
          }
        

        birthdays_today.append(person)
  
  pprint.pp(birthdays_today)

  return birthdays_today

def send_email(to, subject, body):
    """
    Send an email using SMTP.
    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
  
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
  """
  Send birthday messages to the email addresses of people with birthdays today.
  Args:
      birthdays (list): A list of dictionaries containing names and emails of people with birthdays today.
  """
  
  for birthday in birthdays:
    for name, infos in birthday.items():
      subject = f"🎉 Feliz Aniversário, {name}!"
      
      body= f""" \b
        Olá, {name},
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
    