from typing import Dict, Any

class ZohoNormalizer:
    """
    Transforms raw Zoho CRM objects into AVENOR-AI Canonical Entities.
    Ensures Zoho-specific field names never leak.
    """
    
    @staticmethod
    def normalize_company(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Zoho Account to CanonicalCompany format."""
        return {
            "source": "zoho",
            "source_id": raw.get("id"),
            "domain": raw.get("Website"),
            "name": raw.get("Account_Name"),
            "industry": raw.get("Industry"),
            "employee_count": int(raw.get("Employees", 0)) if raw.get("Employees") else None,
            "annual_revenue": float(raw.get("Annual_Revenue", 0.0)) if raw.get("Annual_Revenue") else None,
            "created_at": raw.get("Created_Time"),
            "updated_at": raw.get("Modified_Time")
        }

    @staticmethod
    def normalize_contact(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Zoho Contact to CanonicalContact format."""
        
        # Zoho encapsulates lookup fields as a dict {"name": "...", "id": "..."}
        account = raw.get("Account_Name") or {}
        
        return {
            "source": "zoho",
            "source_id": raw.get("id"),
            "email": raw.get("Email"),
            "first_name": raw.get("First_Name"),
            "last_name": raw.get("Last_Name"),
            "job_title": raw.get("Title"),
            "phone": raw.get("Phone"),
            "associated_company_id": account.get("id"), 
            "created_at": raw.get("Created_Time"),
            "updated_at": raw.get("Modified_Time")
        }

    @staticmethod
    def normalize_opportunity(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Zoho Deal to CanonicalOpportunity format."""
        
        account = raw.get("Account_Name") or {}
        owner = raw.get("Owner") or {}
        
        return {
            "source": "zoho",
            "source_id": raw.get("id"),
            "name": raw.get("Deal_Name"),
            "amount": float(raw.get("Amount", 0.0)) if raw.get("Amount") else None,
            "stage": raw.get("Stage"),
            "pipeline": raw.get("Pipeline"), 
            "close_date": raw.get("Closing_Date"),
            "owner_id": owner.get("id"),
            "associated_company_id": account.get("id"),
            "created_at": raw.get("Created_Time"),
            "updated_at": raw.get("Modified_Time")
        }
        
    @staticmethod
    def normalize_lead(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Zoho Lead to CanonicalLead format."""
        
        return {
            "source": "zoho",
            "source_id": raw.get("id"),
            "email": raw.get("Email"),
            "first_name": raw.get("First_Name"),
            "last_name": raw.get("Last_Name"),
            "company_name": raw.get("Company"),
            "status": raw.get("Lead_Status"), 
            "created_at": raw.get("Created_Time"),
            "updated_at": raw.get("Modified_Time")
        }
