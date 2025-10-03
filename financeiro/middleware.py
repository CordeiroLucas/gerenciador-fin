from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser


class UserFilterMiddleware(MiddlewareMixin):
    """
    Middleware para filtrar automaticamente dados por usuário logado
    """
    
    def process_request(self, request):
        """
        Adiciona informações do usuário ao request para facilitar filtragem
        """
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            # Adicionar método helper para filtrar por usuário
            def filter_by_user(queryset):
                """Helper para filtrar queryset pelo usuário logado"""
                if hasattr(queryset.model, 'usuario'):
                    return queryset.filter(usuario=request.user)
                return queryset
            
            request.filter_by_user = filter_by_user
        
        return None
