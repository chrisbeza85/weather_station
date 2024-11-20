from django import forms
from .models import Item, Student

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'gender', 'student_number', 'email', 'phone']
