from datetime import *
from .models import ConvertedFile,PDFFile
import os
import pdfplumber
import markdown
from django.conf import settings
from django.http import JsonResponse

# invoice8.pdf, invoice6.pdf, invoice5.pdf, invoice3.pdf, invoice1.pdf
def check_file_type(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.pdf': return "PDF"
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']: return "IMAGE"
    else: return "UNKNOWN"

def convert_file(file_data):
    try:
        import os
        instance = PDFFile.objects.create(file=file_data)
        file_type = check_file_type(instance.file.name)

        if file_type == "PDF":
            try:
                with pdfplumber.open(file_data) as pdf:
                    pdf_data = []
                    csv_data=[]
                    csv_data_main = []

                    for page in pdf.pages:
                        for table in page.extract_tables():
                            for row in table:
                                while None in row:
                                    row.remove(None)
                                pdf_data.append(row)
                    
                    print("========================")
                    for row in pdf_data:
                        if len(row) < 25 and len(row)>=14:
                            print(row)
                            csv_data.append(row)
                    print(csv_data)
            
                # Convert to CSV format
                import os           
                file_name = os.path.basename(instance.file.path)
                file_name = file_name.replace(".pdf", "")
                
                converted_csv = os.path.join(settings.MEDIA_ROOT, 'receipts', 'converted_csv')
                csv_filename = f"{file_name}.csv"
                csv_file_path = f"{csv_filename}"
                csv_file_path = os.path.join(converted_csv, f'{csv_filename}')
                csv_downloading_path = '/' + os.path.join(*csv_file_path.split('/')[-3:])            
                import csv
                with open(csv_file_path, 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    for row in csv_data:
                        writer.writerow(row)

                # Save the converted CSV file to storage
                converted_file_instance = ConvertedFile.objects.create(
                    pdf_file=instance,
                    csv_file=csv_downloading_path
                )
                converted_file_instance.save()
                return JsonResponse({'pdf_file_path': instance.file.url, 'csv_file_path': converted_file_instance.csv_file.url, 'timestamp': converted_file_instance.timestamp}, status=200)  
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)               

   
        elif file_type == "IMAGE":
            print("HELLO")
            import ssl
            import os    
            ssl._create_default_https_context = ssl._create_unverified_context

            def upload(path):
                import requests
                API_KEY = 'J8RAxOGlTP4KUq1ibooA0H88gQ99mFcO0YwV3hJa'
                url = "https://trigger.extracttable.com"
                payload = {}
                files={'input':open(path,'rb')}
                headers = { 'x-api-key': API_KEY }
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                return response.json()
            
            response = upload(instance.file.path)
#=================================================================    
            import tempfile, csv
            if(response['JobStatus'] == "Success"):
                def flatten_table(table_json):
                    flat_table = []
                    for row_key, row_data in table_json.items():
                        flat_row = [row_key] + [str(value) for value in row_data.values()]
                        flat_table.append(flat_row)
                    return flat_table
                
                import os           
                file_name = os.path.basename(instance.file.path)

                # To remove file extention with ""
                file_extension = os.path.splitext(file_name)[1].lower()
                file_name = file_name.replace(file_extension,"")
                converted_csv = os.path.join(settings.MEDIA_ROOT, 'receipts', 'converted_csv/receipts')
                csv_filename = f"{file_name}.csv"
                csv_file_path = f"{csv_filename}"
                csv_file_path = os.path.join(converted_csv, f'{csv_filename}')
                csv_downloading_path = '/' + os.path.join(*csv_file_path.split('/')[-5:])
                
                # Create a temporary file
                with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='') as temp_file:
                    temp_file_path = temp_file.name

                    # Write CSV file
                    writer = csv.writer(temp_file)
                    for table_entry in response['Tables']:
                        table_json = table_entry['TableJson']
                        flat_table = flatten_table(table_json)

                        if len(flat_table)>=8:
                        # Write table data
                            def sort_key(row):
                                return int(row[0])
                            sorted_table = sorted(flat_table, key=sort_key)
                            writer.writerows(sorted_table)

                try:
                    with open(temp_file_path, 'rb') as csv_file:
                        from django.core.files import File
                        converted_file_instance = ConvertedFile.objects.create(
                        pdf_file=instance,
                        csv_file= csv_downloading_path)
                        converted_file_instance.csv_file.save(f'{instance.file.name}.csv', File(csv_file), save=True)
                        
                        if 'message' in response:
                            message = response['message']
                        else:
                            message = 'Unknown error occurred'
                        return JsonResponse({'img_file_path': converted_file_instance.pdf_file.file.url, 'csv_file_path': converted_file_instance.csv_file.url, 'timestamp': converted_file_instance.timestamp}, status=200)
                        
                except Exception as e:
                    print(str(e))
                    return JsonResponse({'massage':str(e),'img_file_path': converted_file_instance.pdf_file.file, 'csv_file_path': converted_file_instance.csv_file.url, 'timestamp': converted_file_instance.timestamp}, status=500)  
            else:
                print(response)
                return JsonResponse({'massage':"File not found"}, status=500)  
    except Exception as e:
        print(str(e))
        return JsonResponse({'massage':str(e)}, status=500)