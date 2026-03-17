from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # valor por defecto
    page_size_query_param = 'page_size'  # permite especificar el tamaño en la URL
    max_page_size = 100  # límite superior opcional
