from django.urls import path
from .views import upload_file, extract_pdf_tables, get_all_result,index

urlpatterns = [
    path('',index),
    path("api/upload", upload_file, name="upload"),
    path('api/extract-pdf-tables', extract_pdf_tables, name='extract_pdf_tables'),
    path("api/get-all", get_all_result, name="get-all"),
]