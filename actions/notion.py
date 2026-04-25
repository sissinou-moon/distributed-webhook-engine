import requests

url = "https://api.notion.com/v1/databases"

def createDatabase(page_id: str, title: str, access_token: str):
    print("Creating Notion Database... ✅")
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": page_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": title
                }
            }
        ],
        "properties": {
            "Name": {
                "title": {}
            }
        }
    }
    headers = {
        "Notion-Version": "2022-06-28",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Notion Database Created Successfully ✅")
    print(response.json())

    return response.json()
