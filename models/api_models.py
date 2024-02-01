from pydantic import BaseModel, PastDatetime

class CompanyResponse(BaseModel):
    company_id: str
    name: str
    industry: str
    email_address: str
    modified_datetime: PastDatetime    

class UpdateCompanyRequest(BaseModel):
    name: str
    industry: str
    email_address: str

class CreateCompanyRequest(BaseModel):
    name: str
    industry: str
    email_address: str
