from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional


app = FastAPI(title="Ticket System")

app.add_middleware(
   CORSMiddleware,
   allow_origins=['*'],
   allow_headers=['*'],
   allow_methods=['*']
)

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

# @app.get('/tickets')
# def home():
#   return {"message": "Welcome to ticket system!"}

def find_ticket(ticket_id: int) -> TicketOut:
    for t in tickets:
      if t.id == ticket_id:
        return t
    raise HTTPException(status_code=404, detail='Ticket not found')


def fake_triage(title: str, description: str) -> dict:
   text = title + ' ' + description
   if 'bug' in text or 'crash' in text or 'error' in text:
     category = 'bug'
   elif 'payment' in text or 'billing' in text:
     category = 'payment'
   elif 'login' in text or 'password' in text:
     category = 'sso'
   else:
     category = 'general'
   if 'urgent' in text or 'critical' in text:
     priority = 'high'
   elif 'question' in text or 'how to' in text:
     priority = 'low'
   else:
      priority = 'medium'

   summary = f"User report {title}, auto-classified as {category}"

   return {'category': category, 'priority': priority, 'summary': summary}

  
#create a ticket
@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_tickets(payload: TicketCreate):
  global next_id
  ticket = TicketOut(id=next_id, **payload.model_dump())
  next_id +=1
  tickets.append(ticket)
  return ticket

@app.get('/tickets', response_model=list[TicketOut])
def list_tickets(status: Optional[str]=None, search: Optional[str]=None):
  result = tickets
  if status is not None:
    result = [t for t in result if t.status == status]
  if search:
    q = search.lower()
    result = [t for t in result if q in t.title.lower() or q in t.description.lower()]
  
  return result

#2nd step
@app.post("/tickets/{ticket_id}/triage", response_model=TicketOut)
def triage_ticket(ticket_id: int):
  ticket = find_ticket(ticket_id)
  result = fake_triage(ticket.title, ticket.description)
  ticket.suggested_category = result['category']
  ticket.suggested_priority = result['priority']
  ticket.ai_summary = result['summary']
  ticket.status = 'needs_review'
  return ticket

#3rd step
@app.post("/tickets/{ticket_id}/approve", response_model=TicketOut)
def approve_ticket(ticket_id: int):
    ticket = find_ticket(ticket_id)
    result = fake_triage(ticket.title, ticket.description)
    if ticket.status != 'needs_review':
      raise HTTPException(status_code=400, detail='Ticket has not been triaged yet')
    ticket.final_category = ticket.suggested_category
    ticket.final_priority = ticket.suggested_priority
    ticket.status = 'assigned'
    return ticket



   

