from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class HubSpotNormalizer:
    """
    Transforms raw HubSpot objects into AVENOR-AI Canonical Entities.
    Ensures HubSpot-specific field names (e.g., hs_object_id, numemployees) never leak
    into the core Intelligence Cloud.
    """
    
    @staticmethod
    def normalize_company(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps HubSpot Company to CanonicalCompany format."""
        properties = raw.get("properties", {})
        
        # HubSpot's internal ID
        hubspot_id = raw.get("id") or properties.get("hs_object_id")
        
        return {
            "source": "hubspot",
            "source_id": hubspot_id,
            "domain": properties.get("domain"),
            "name": properties.get("name"),
            "industry": properties.get("industry"),
            "employee_count": int(properties.get("numemployees", 0)) if properties.get("numemployees") else None,
            "annual_revenue": float(properties.get("annualrevenue", 0.0)) if properties.get("annualrevenue") else None,
            "created_at": properties.get("createdate"),
            "updated_at": properties.get("hs_lastmodifieddate")
        }

    @staticmethod
    def normalize_contact(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps HubSpot Contact to CanonicalContact format."""
        properties = raw.get("properties", {})
        hubspot_id = raw.get("id") or properties.get("hs_object_id")
        
        return {
            "source": "hubspot",
            "source_id": hubspot_id,
            "email": properties.get("email"),
            "first_name": properties.get("firstname"),
            "last_name": properties.get("lastname"),
            "job_title": properties.get("jobtitle"),
            "phone": properties.get("phone"),
            "associated_company_id": properties.get("associatedcompanyid"), # Often requires associations API
            "created_at": properties.get("createdate"),
            "updated_at": properties.get("lastmodifieddate")
        }

    @staticmethod
    def normalize_deal(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Maps HubSpot Deal to CanonicalOpportunity format."""
        properties = raw.get("properties", {})
        hubspot_id = raw.get("id") or properties.get("hs_object_id")
        
        return {
            "source": "hubspot",
            "source_id": hubspot_id,
            "name": properties.get("dealname"),
            "amount": float(properties.get("amount", 0.0)) if properties.get("amount") else None,
            "stage": properties.get("dealstage"),
            "pipeline": properties.get("pipeline"),
            "close_date": properties.get("closedate"),
            "owner_id": properties.get("hubspot_owner_id"),
            "created_at": properties.get("createdate"),
            "updated_at": properties.get("hs_lastmodifieddate")
        }
