from typing import Dict, Any, List

def get_client_details(client_name: str) -> Dict[str, Any]:
    """
    A mock tool to get details about a client from a CRM.

    Args:
        client_name: The name of the client.

    Returns:
        A dictionary with client details.
    """
    print(f"--- Calling get_client_details for: {client_name} ---")
    if "Global Tech" in client_name:
        return {
            "name": "Global Tech Inc.",
            "industry": "Technology",
            "size": "Large",
            "location": "San Francisco, CA",
            "past_projects": [
                {"name": "Project Alpha", "value": 500000},
                {"name": "Project Beta", "value": 750000},
            ],
            "contact_person": "Jane Doe",
            "contact_email": "jane.doe@globaltech.com"
        }
    else:
        return {
            "name": client_name,
            "error": "Client not found in CRM."
        }

def get_project_details(project_name: str) -> Dict[str, Any]:
    """
    A mock tool to get details about a project from a project management tool.

    Args:
        project_name: The name of the project.

    Returns:
        A dictionary with project details.
    """
    print(f"--- Calling get_project_details for: {project_name} ---")
    if "E-commerce" in project_name:
        return {
            "name": "New E-commerce Platform",
            "status": "In Planning",
            "budget": 1200000,
            "currency": "USD",
            "team_members": ["Alice", "Bob", "Charlie"],
            "timeline_months": 9,
            "key_features": ["Product catalog", "Shopping cart", "Payment gateway integration"]
        }
    else:
        return {
            "name": project_name,
            "error": "Project not found in project management tool."
        }
