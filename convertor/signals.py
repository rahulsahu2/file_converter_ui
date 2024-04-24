

import os
import pandas as pd
from datetime import *
from django.conf import settings
from django.http import JsonResponse
from .models import ConvertedFile,PDFFile


def check_file_type(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.pdf' : return "PDF"
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']: return "IMAGE"
    else: return "UNKNOWN"

def convert_file(file_data,x1,y1,x2,y2):
    try:
        import os
        instance = PDFFile.objects.create(file=file_data)
        file_type = check_file_type(instance.file.name)

        if file_type == "PDF":
            try:
                import os
                import pdfplumber
                def extract_table_from_pdf(input_path, x1, y1, x2, y2, page_number=0):
                    with pdfplumber.open(input_path) as pdf:
                        if page_number < len(pdf.pages):
                            page = pdf.pages[page_number]
                            crop_region = (x1, y1, x2, y2)
                            table = page.crop(crop_region).extract_table()
                            return table
                leftMargin, bottomMargin, rightMargin, topMargin = x1, y1, x2, y2
                extracted_table = extract_table_from_pdf(file_data, leftMargin, bottomMargin, rightMargin, topMargin)
                df = pd.DataFrame(extracted_table)

                import os           
                file_name = os.path.basename(instance.file.path)
                file_name = file_name.replace(".pdf", "")
                
                converted_csv = os.path.join(settings.MEDIA_ROOT, 'receipts', 'converted_csv')
                csv_filename = f"{file_name}.csv"
                csv_file_path = f"{csv_filename}"
                csv_file_path = os.path.join(converted_csv, f'{csv_filename}')
                csv_downloading_path = '/' + os.path.join(*csv_file_path.split('/')[-3:])            
                
                # Convert to CSV format
                df.to_csv(csv_file_path, index=False)
                
                # Save the converted CSV file to storage
                converted_file_instance = ConvertedFile.objects.create(
                    pdf_file=instance,
                    csv_file=csv_downloading_path
                )
                converted_file_instance.save()

                # return JsonResponse({"success":"success"}, status=200)  
                return JsonResponse({'pdf_file_path': instance.file.url, 'csv_file_path': converted_file_instance.csv_file.url, 'timestamp': converted_file_instance.timestamp}, status=200)  
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)               
        elif file_type == "IMAGE":
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


"""
# invoice1.pdf
leftMargin = 8
bottomMargin = 145
rightMargin = 840
topMargin = 260

# invoice2.pdf   # single array  #BUGG
leftMargin = 8
bottomMargin = 145
rightMargin = 820
topMargin = 410

# invoice3.pdf
leftMargin = 8
bottomMargin = 200
rightMargin = 820
topMargin = 300

# invoice4.pdf   #single row all data column seperate
leftMargin = 18
bottomMargin = 220
rightMargin = 570
topMargin = 620

# invoice5.pdf   #single row all data column seperate
leftMargin = 8
bottomMargin = 238
rightMargin = 580
topMargin = 575

#invoice6.pdf
leftMargin = 15
topMargin = 350
bottomMargin = 145
rightMargin = 680

# invoice8.pdf
leftMargin = 8
bottomMargin = 140
rightMargin = 792
topMargin = 400

#invoice9.pdf
leftMargin = 0
topMargin = 710
rightMargin = 590
bottomMargin = 200
"""