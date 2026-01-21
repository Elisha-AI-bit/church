from core.models import set_current_church, clear_current_church

class TenantMiddleware:
    """Detects the church from the logged-in user and sets it in thread locals"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Get the church from the user's profile
                church = request.user.profile.church
                set_current_church(church)
                request.church = church # Also attach to request for convenience
            except:
                clear_current_church()
                request.church = None
        else:
            clear_current_church()
            request.church = None

        response = self.get_response(request)
        
        # Clean up to avoid cross-request contamination
        clear_current_church()
        
        return response
