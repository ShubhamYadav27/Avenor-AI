from typing import Dict, Any
from datetime import datetime

class PipedriveNormalizer:
    """
    Transforms raw Pipedrive CRM objects into AVENOR-AI Canonical Entities.
    Ensures Pipedrive-specific field names never leak.
    """
    
    @staticmethod
    def normalize_company(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Pipedrive Organization to CanonicalCompany format."""
        
        return {
            "source": "pipedrive",
            "source_id": str(raw.get("id")),
            "domain": None, # Often stored in custom fields in Pipedrive
            "name": raw.get("name"),
            "industry": None,
            "employee_count": raw.get("people_count"),
            "annual_revenue": None,
            "created_at": raw.get("add_time"),
            "updated_at": raw.get("update_time")
        }

    @staticmethod
    def normalize_contact(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Pipedrive Person to CanonicalContact format."""
        
        org_id = raw.get("org_id")
        associated_company_id = str(org_id.get("value")) if isinstance(org_id, dict) else str(org_id) if org_id else None
        
        # Pipedrive returns emails and phones as list of dicts: [{"value": "a@b.com", "primary": True}]
        email_list = raw.get("email", [])
        primary_email = next((e.get("value") for e in email_list if e.get("primary")), email_list[0].get("value") if email_list else None)
        
        phone_list = raw.get("phone", [])
        primary_phone = next((p.get("value") for p in phone_list if p.get("primary")), phone_list[0].get("value") if phone_list else None)
        
        name = raw.get("name", "")
        parts = name.split(" ", 1)
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""
        
        return {
            "source": "pipedrive",
            "source_id": str(raw.get("id")),
            "email": primary_email,
            "first_name": first_name,
            "last_name": last_name,
            "job_title": None,
            "phone": primary_phone,
            "associated_company_id": associated_company_id, 
            "created_at": raw.get("add_time"),
            "updated_at": raw.get("update_time")
        }

    @staticmethod
    def normalize_opportunity(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Pipedrive Deal to CanonicalOpportunity format."""
        
        org_id = raw.get("org_id")
        associated_company_id = str(org_id.get("value")) if isinstance(org_id, dict) else str(org_id) if org_id else None
        
        user_id = raw.get("user_id")
        owner_id = str(user_id.get("id")) if isinstance(user_id, dict) else str(user_id) if user_id else None
        
        return {
            "source": "pipedrive",
            "source_id": str(raw.get("id")),
            "name": raw.get("title"),
            "amount": float(raw.get("value", 0.0)) if raw.get("value") else None,
            "stage": str(raw.get("stage_id")),
            "pipeline": str(raw.get("pipeline_id")), 
            "close_date": raw.get("expected_close_date"),
            "owner_id": owner_id,
            "associated_company_id": associated_company_id,
            "created_at": raw.get("add_time"),
            "updated_at": raw.get("update_time")
        }
        
    @staticmethod
    def normalize_lead(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps Pipedrive Lead to CanonicalLead format."""
        
        # In Pipedrive, leads are usually pre-deal states connected to a Person or Org
        return {
            "source": "pipedrive",
            "source_id": str(raw.get("id")),
            "email": None, # Attached to Person
            "first_name": raw.get("title"), 
            "last_name": None,
            "company_name": None,
            "status": "Lead", 
            "created_at": raw.get("add_time"),
            "updated_at": raw.get("update_time")
        }
