import logging
import uuid
from datetime import datetime
from redis import Redis
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from models.api_models import (CompanyResponse, CreateCompanyRequest, UpdateCompanyRequest)
from models.db_models import Company
from db import CompaniesDb

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
    
db = CompaniesDb(db=Redis(
        host='localhost',
        port=6379,
        decode_responses=True
    ))

app = FastAPI()       

@app.get('/companies')
def get_companies(industry: str | None = None) -> list[CompanyResponse]:
    companies = []
    for db_company in db.get_all_companies():
        if industry and db_company.industry.lower() != industry.lower():
            continue
        companies.append(CompanyResponse(**db_company.dict()))
    return companies

@app.get('/companies/{company_id}')
def get_company_by_id(company_id: str) -> CompanyResponse:
    db_company = db.get_company_by_id(company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail=f'Company with ID "{company_id}" not found')
    return CompanyResponse(**db_company.dict())

@app.post('/companies', status_code=status.HTTP_201_CREATED)
def create_company(company: CreateCompanyRequest) -> CompanyResponse:
    db_company = Company(
        company_id=str(uuid.uuid4()),
        name=company.name,
        industry=company.industry,
        email_address=company.email_address,
        modified_datetime=datetime.utcnow()
    )
    db_response = db.create_company(db_company)
    return CompanyResponse(**db_response.dict())

@app.put('/companies/{company_id}', status_code=status.HTTP_201_CREATED)
def update_company(company_id: str, company: UpdateCompanyRequest) -> CompanyResponse:
    db_company = Company(
        company_id=company_id,
        name=company.name,
        industry=company.industry,
        email_address=company.email_address,
        modified_datetime=datetime.utcnow()
    )
    db_response = db.update_company( db_company)
    return CompanyResponse(**db_response.dict())

@app.delete('/companies/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: str):
    db.delete_company(company_id)

@app.middleware('http')
def format_server_errors(request: Request, call_next):
    try:
        response = call_next(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error while processing request: {e}. Request: {request}', exc_info=1)
        return JSONResponse(
            status_code=500,
            content={
                'detail': 'An error occurred while processing the request'
            }
        ) 
