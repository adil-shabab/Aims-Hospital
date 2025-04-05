from django import forms
from django.core.exceptions import ValidationError
from PIL import Image

class SVGAndImageField(forms.ImageField):
    def to_python(self, data):
        file = super().to_python(data)
        if file:
            if not file.name.endswith('.svg'):
                try:
                    Image.open(file)
                except IOError:
                    raise ValidationError("Invalid image format")
        return file
