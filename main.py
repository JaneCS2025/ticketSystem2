from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional


app = FastAPI(title="Ticket System")


class TicketCreate(BaseModel):
  title: str
  description: str
  created_by: int


class TicketOut(TicketCreate):
  id: int
  status: str='open'
  category: Optional[str]=None
  priority: Optional[str]=None
  suggested_category: Optional[str] = None
  suggested_priority: Optional[str] = None
  ai_summary: Optional[str] = None
  final_category: Optional[str] = None
  final_priority: Optional[str] = None


tickets = []
next_id = 1

# @app.get('/')
# def home():
#   return {"message": "Welcome to ticket system!"}

#create a ticket
@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_tickets(payload: TicketCreate):
  global next_id
  ticket = TicketOut(id=next_id, **payload.model_dump())
  next_id +=1
  tickets.append(ticket)
  return ticket



