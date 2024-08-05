from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class UserRequest(BaseModel):
    username: str

def extract_domain(email: str) -> str:
    if "@" in email:
        return email.split("@")[1]
    return ""

@app.post("/get-user")
async def get_user(user: UserRequest):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE username = '{user.username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()

    if result:
        email_domain = extract_domain(result[1])  # Using the extract_domain function
        return {"username": result[0], "email": result[1], "domain": email_domain}
    else:
        raise HTTPException(status_code=404, detail="User not found")
