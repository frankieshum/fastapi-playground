from redis import Redis
from models.db_models import Company
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CompaniesDb:    
    def __init__(self, db: Redis):
        self.key_prefix = 'companies:'
        self.db = db
    
    def construct_key(self, company_id: str):
        return self.key_prefix + company_id
    
    def get_all_companies(self):
        logger.info('Getting all companies in DB')
        keys = self.db.keys(self.key_prefix + '*')
        logger.debug(f'Found keys: {keys}')
        values = self.db.mget(keys)
        logger.debug(f'Retrieved {len(values)} companies in DB')
        for value in values:
            if not value:
                continue
            yield Company.model_validate_json(value)
    
    def get_company_by_id(self, company_id):
        logger.info(f'Getting company with ID "{company_id}"')
        key = self.construct_key(company_id)
        value = self.db.get(key)
        if not value:
            logger.info(f'Could not find company with ID "{company_id}"')
            return None
        logger.info(f'Retrieved company with ID "{company_id}"')
        return Company.model_validate_json(value)
    
    def create_company(self, company: Company):
        logger.info(f'Inserting company with ID "{company.company_id}"')
        key = self.construct_key(str(company.company_id))
        value = company.model_dump_json()
        self.db.set(key, value)
        logger.info(f'Finished inserting company with ID "{company.company_id}"')
        return company
    
    def update_company(self, company: Company):
        logger.info(f'Updating company with ID "{company.company_id}"')
        key = self.construct_key(company.company_id)
        value = company.model_dump_json()
        self.db.set(key, value)
        logger.info(f'Finished updating company with ID "{company.company_id}"')
        return company
    
    def delete_company(self, company_id: str):
        logger.info(f'Deleting company with ID "{company_id}"')
        key = self.construct_key(company_id)
        self.db.delete(key)
