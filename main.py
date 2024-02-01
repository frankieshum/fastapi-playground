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
async def get_companies():
    return [
        CompanyResponse(**db_company.dict())
        for db_company
        in db.get_all_companies()
    ]

@app.get('/companies/{company_id}')
async def get_company_by_id(company_id: str):
    db_company = db.get_company_by_id(company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail=f'Company with ID "{company_id}" not found')
    return CompanyResponse(**db_company.dict())

@app.post('/companies', status_code=status.HTTP_201_CREATED)
async def create_company(company: CreateCompanyRequest):
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
async def update_company(company_id: str, company: UpdateCompanyRequest):
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
async def delete_company(company_id: str):
    db.delete_company(company_id)

@app.middleware('http')
async def format_server_errors(request: Request, call_next):
    try:
        response = await call_next(request)
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
