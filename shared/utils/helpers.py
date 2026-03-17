"""
Utility helper functions for the application
"""

def build_absolute_uri_https(request, relative_url):
    """
    Build absolute URI with HTTPS forced for production environments.
    
    This function ensures that URLs generated for media files always use HTTPS
    when the application is behind a reverse proxy (like Nginx) with SSL.
    
    Args:
        request: The Django request object
        relative_url: The relative URL path (e.g., media file URL)
    
    Returns:
        str: Absolute URL with HTTPS scheme, or None if inputs are invalid
    """
    if request and relative_url:
        uri = request.build_absolute_uri(relative_url)
        
        # Get the host to check if we're in localhost/development
        host = request.get_host().lower()
        is_local = 'localhost' in host or '127.0.0.1' in host or host.startswith('192.168.')
        
        # If not localhost, ALWAYS force HTTPS (production environment)
        if not is_local:
            uri = uri.replace('http://', 'https://')
        
        return uri
    return None
