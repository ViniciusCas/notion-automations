import requests
import os
import pprint
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

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
  
  databases = data["results"]
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
      birthday = properties["Aniversário"]["date"]["start"]
      birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
     
      birthdays_today.append({name: birthday_date})
  
  return birthdays_today

def send_message_to_email(birthdays):
  for birthday in birthdays:
    for name, date in birthday.items():
      formatted_date = date.strftime("%d %B")
      print(f"Sending email to {name} with birthday on {formatted_date}")


if __name__ == "__main__":
  birthdays = get_birthdays_today()
  if birthdays:
    send_message_to_email(birthdays)
  else:
    print("No birthdays today.")