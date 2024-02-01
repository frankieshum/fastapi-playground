from pydantic import BaseModel, PastDatetime

class Company(BaseModel):
    company_id: str
    name: str
    industry: str
    email_address: str
    modified_datetime: PastDatetime
