def branding(request):
    """Provides dynamic branding based on the current tenant (church)"""
    church = getattr(request, 'church', None)
    
    if church:
        church_name = church.name
        # Build acronym: First letter of the church name + "CRMS"
        # Example: "Silverest Congregation" -> "SCRMS", "Lusaka" -> "LCRMS"
        first_letter = church_name[0].upper()
        acronym = f"{first_letter}CRMS"
        
        system_name = f"{church_name} Records Management System ({acronym})"
    else:
        # Default fallback
        church_name = "Silverest Congregation"
        system_name = "Silverest Congregation Records Management System (SCRMS)"
        acronym = "SCRMS"
        
    return {
        'church_name': church_name,
        'system_name': system_name,
        'system_acronym': acronym,
    }
