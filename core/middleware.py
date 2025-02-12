import requests
from django.utils.deprecation import MiddlewareMixin
from .models import Visitor

class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        location = self.get_location(ip_address)
        
        # Check if the visitor already exists
        if not Visitor.objects.filter(ip_address=ip_address).exists():
            Visitor.objects.create(ip_address=ip_address, location=location)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_location(self, ip_address):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
            data = response.json()
            if data.get('status') == 'fail':
                return 'Unknown'
            return f"{data.get('city')}, {data.get('country')}"
        except requests.exceptions.RequestException as e:
            return 'Unknown'
