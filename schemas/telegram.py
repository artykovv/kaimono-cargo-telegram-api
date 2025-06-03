from pydantic import BaseModel

class CreateClient(BaseModel):
    name: str
    number: str
    city: str
    telegram_chat_id: str
    branch_id: int