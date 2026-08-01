from typing import Dict, Any
from uuid import UUID

class SalesforceNormalizer:
    """
    Transforms raw Salesforce objects into AVENOR-AI Canonical Entities.
    Ensures Salesforce-specific field names (e.g., AccountId, StageName) never leak
    into the core Intelligence Cloud.
    """
    
    @staticmethod
    def normalize_company(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Salesforce Account to CanonicalCompany format."""
        
        # In SOQL we explicitly request these fields
        return {
            "source": "salesforce",
            "source_id": raw.get("Id"),
            "domain": raw.get("Website"),
            "name": raw.get("Name"),
            "industry": raw.get("Industry"),
            "employee_count": int(raw.get("NumberOfEmployees", 0)) if raw.get("NumberOfEmployees") else None,
            "annual_revenue": float(raw.get("AnnualRevenue", 0.0)) if raw.get("AnnualRevenue") else None,
            "created_at": raw.get("CreatedDate"),
            "updated_at": raw.get("LastModifiedDate")
        }

    @staticmethod
    def normalize_contact(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Salesforce Contact to CanonicalContact format."""
        
        return {
            "source": "salesforce",
            "source_id": raw.get("Id"),
            "email": raw.get("Email"),
            "first_name": raw.get("FirstName"),
            "last_name": raw.get("LastName"),
            "job_title": raw.get("Title"),
            "phone": raw.get("Phone"),
            "associated_company_id": raw.get("AccountId"), 
            "created_at": raw.get("CreatedDate"),
            "updated_at": raw.get("LastModifiedDate")
        }

    @staticmethod
    def normalize_opportunity(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Salesforce Opportunity to CanonicalOpportunity format."""
        
        return {
            "source": "salesforce",
            "source_id": raw.get("Id"),
            "name": raw.get("Name"),
            "amount": float(raw.get("Amount", 0.0)) if raw.get("Amount") else None,
            "stage": raw.get("StageName"),
            "pipeline": raw.get("ForecastCategoryName"), # Closest standard field without custom pipeline IDs
            "close_date": raw.get("CloseDate"),
            "owner_id": raw.get("OwnerId"),
            "associated_company_id": raw.get("AccountId"),
            "created_at": raw.get("CreatedDate"),
            "updated_at": raw.get("LastModifiedDate")
        }
