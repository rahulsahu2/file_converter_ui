from django.db import models

# Create your models here.
class ReceiptFile(models.Model):
    """Model for storing receipt file"""
    file = models.FileField(upload_to='receipts/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    converted_csv = models.FileField(upload_to='receipts/converted_csv/', null=True, blank=True)
    status = models.CharField(max_length=100, default="Failed To convert")    

    def __str__(self):
        return self.file.name
    
class PDFFile(models.Model):
    file = models.FileField(upload_to='receipts/')
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.file.name

class ConvertedFile(models.Model):
    pdf_file = models.OneToOneField(PDFFile, on_delete=models.CASCADE)
    csv_file = models.FileField(upload_to='receipts/converted_csv/')
    timestamp = models.DateTimeField(auto_now_add=True)
