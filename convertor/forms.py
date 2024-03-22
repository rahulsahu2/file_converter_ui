# forms.py

from django import forms
from .models import ReceiptFile

class ReceiptFileForm(forms.ModelForm):
    file = forms.FileField(required=False)
    class Meta:
        model = ReceiptFile
        fields = ['file']
