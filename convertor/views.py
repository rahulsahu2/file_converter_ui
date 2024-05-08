from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
import requests
import csv
import pdfplumber
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from .models import ConvertedFile,PDFFile
from datetime import *
from django.utils import timezone
from .signals import convert_file
import os
import tempfile
import tabula

BACKEND_URL = 'http://localhost:8000/media/'


def index(request):
    response = requests.get('http://localhost:8000/api/get-all')
    api_data = response.json()
    context = {
        'receipt_files':api_data["data"]
    }
    return render(request,'convert.html', context)



@csrf_exempt
def get_all_result(request):
    converted_files = ConvertedFile.objects.all().order_by('-timestamp')
    # Serialize the model instances into dictionaries
    converted_files_data = []
    for converted_file in converted_files:
        print("===================================")
        print(converted_file)
        converted = {
            'pdf_file': {
                    'id': converted_file.pdf_file.id,
                    'file': converted_file.pdf_file.file.url,
                    'timestamp': converted_file.pdf_file.timestamp.isoformat(),
                    },
                'csv_file': converted_file.csv_file.url,
                'timestamp': converted_file.timestamp.isoformat(),
                }
        converted_files_data.append(converted)            
    return JsonResponse({'status': True,'data':converted_files_data},status=200)
    #     except Exception as e:
    #         return JsonResponse({'status': False},status=200)
    # else:
    #     return JsonResponse({'error': 'Invalid request'}, status=500)


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':       
        pdf_file = request.FILES['pdf_file']
        print(pdf_file)

        leftMargin = request.POST.get("x1")
        print(leftMargin)

        bottomMargin = request.POST.get("y2")
        print(bottomMargin)

        rightMargin = request.POST.get("x2")
        print(rightMargin)
        
        topMargin = request.POST.get("y1")
        print(topMargin)

        return convert_file(pdf_file,int(leftMargin),int(bottomMargin),int(rightMargin),int(topMargin))
    
@csrf_exempt
def extract_pdf_tables(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        try:
            pdf_file = request.FILES['pdf_file']  
            # Save the uploaded PDF file to storage
            pdf_file_instance = PDFFile.objects.create(file=pdf_file)
            # Read PDF file
            with pdfplumber.open(pdf_file) as pdf:
                pdf_data = []
                csv_data=[]
                for page in pdf.pages:
                    for table in page.extract_tables():
                        for row in table:
                            while None in row:
                                row.remove(None)
                            pdf_data.append(row)
                for row in pdf_data:
                    if len(row) < 25 and len(row)>14:
                        # print(row)
                        csv_data.append(row)
                        
            # Convert to CSV format
            file_name = os.path.basename(pdf_file_instance.file.path)
            print("===========================")
            print(pdf_file_instance.file.path)
            file_name = file_name.replace(".pdf", "")
            converted_csv = os.path.join(settings.MEDIA_ROOT, 'receipts', 'converted_csv')
            csv_filename = f"{file_name}.csv"
            csv_file_path = f"{csv_filename}"
            csv_file_path = os.path.join(converted_csv, f'{csv_filename}')
            csv_downloading_path = '/' + os.path.join(*csv_file_path.split('/')[-3:])            
            # print(converted_csv,"\n",csv_filename,"\n",csv_file_path,"\n",csv_downloading_path)
            with open(csv_file_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                for row in csv_data:
                    writer.writerow(row)
            # Save the converted CSV file to storage
            converted_file_instance = ConvertedFile.objects.create(
                pdf_file=pdf_file_instance,
                csv_file=csv_downloading_path
            )
            converted_file_instance.save()
            return JsonResponse({'pdf_file_path': pdf_file_instance.file.url, 'csv_file_path': converted_file_instance.csv_file.url, 'timestamp': converted_file_instance.timestamp}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)