from typing import Dict, Any

class DynamicsNormalizer:
    """
    Transforms raw Dynamics 365 Dataverse objects into AVENOR-AI Canonical Entities.
    Ensures Dynamics-specific field names (e.g., accountid, statecode) never leak.
    """
    
    @staticmethod
    def normalize_company(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Dynamics account to CanonicalCompany format."""
        
        return {
            "source": "microsoft_dynamics",
            "source_id": raw.get("accountid"),
            "domain": raw.get("websiteurl"),
            "name": raw.get("name"),
            "industry": raw.get("industrycode"), 
            "employee_count": int(raw.get("numberofemployees", 0)) if raw.get("numberofemployees") else None,
            "annual_revenue": float(raw.get("revenue", 0.0)) if raw.get("revenue") else None,
            "created_at": raw.get("createdon"),
            "updated_at": raw.get("modifiedon")
        }

    @staticmethod
    def normalize_contact(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Dynamics contact to CanonicalContact format."""
        
        return {
            "source": "microsoft_dynamics",
            "source_id": raw.get("contactid"),
            "email": raw.get("emailaddress1"),
            "first_name": raw.get("firstname"),
            "last_name": raw.get("lastname"),
            "job_title": raw.get("jobtitle"),
            "phone": raw.get("telephone1"),
            "associated_company_id": raw.get("_parentcustomerid_value"), 
            "created_at": raw.get("createdon"),
            "updated_at": raw.get("modifiedon")
        }

    @staticmethod
    def normalize_opportunity(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Dynamics opportunity to CanonicalOpportunity format."""
        
        return {
            "source": "microsoft_dynamics",
            "source_id": raw.get("opportunityid"),
            "name": raw.get("name"),
            "amount": float(raw.get("estimatedvalue", 0.0)) if raw.get("estimatedvalue") else None,
            "stage": raw.get("stepname"),
            "pipeline": raw.get("salesstagecode"), 
            "close_date": raw.get("estimatedclosedate"),
            "owner_id": raw.get("_ownerid_value"),
            "associated_company_id": raw.get("_customerid_value"),
            "created_at": raw.get("createdon"),
            "updated_at": raw.get("modifiedon")
        }
        
    @staticmethod
    def normalize_lead(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Dynamics lead to CanonicalLead format."""
        
        return {
            "source": "microsoft_dynamics",
            "source_id": raw.get("leadid"),
            "email": raw.get("emailaddress1"),
            "first_name": raw.get("firstname"),
            "last_name": raw.get("lastname"),
            "company_name": raw.get("companyname"),
            "status": raw.get("statecode"), 
            "created_at": raw.get("createdon"),
            "updated_at": raw.get("modifiedon")
        }
