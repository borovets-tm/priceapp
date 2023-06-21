"""
Модуль хранит в себе формы для работы приложения.

Помимо обычных форм. В модуле используется объявление форм-сетов.
"""

from django import forms
from django.forms import modelformset_factory

from .models import Tag, UpdateProduct, MissingProduct


# Formset используется при подтверждении обновления цен Товаров.
ProductConfirmUpdateSet = modelformset_factory(
    UpdateProduct,
    fields=('name', 'price', 'old_price', 'red_price')
)


# FormSet используется для добавления всех Товаров, ненайденных в БД при
# обновлении.
MissingProductFormSet = modelformset_factory(
    MissingProduct,
    fields=(
        'sku',
        'ean',
        'name',
        'category',
        'country',
        'price',
        'old_price',
        'red_price'
    )
)


class PrintSheetForm(forms.Form):
    """Форма для сканирования штрихкодов с упаковок товаров и передачи \
    информации об используемом макете ценников."""

    input_line = forms.CharField(
        max_length=100,
        label='Штрихкод/Название'
    )
    size = forms.CharField(
        max_length=5,
        widget=forms.HiddenInput()
    )
    is_discount = forms.CharField(
        max_length=5,
        widget=forms.HiddenInput()
    )


class PrintSheetFreeForm(forms.Form):
    """Форма для добавления в Лист печати ценников товаров по уценки."""

    name = forms.CharField(
        label='Наименование',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'WF-1000XM4',
                'type': 'text',
                'style': 'min-height: 30px; height: 30px;'
            }
        )
    )
    old_price = forms.DecimalField(
        label='Старая цена',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': '19990',
                'type': 'text',
                'style': (
                    'min-width: 150px; width:150px; '
                    'min-height: 30px; height: 30px'
                )
            }
        )
    )
    price = forms.DecimalField(
        label='Цена',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': '15990',
                'type': 'text',
                'style': (
                    'min-width: 150px; width:150px; '
                    'min-height: 30px; height: 30px'
                )
            }
        )
    )
    discount_type = forms.CharField(
        label='Причина скидки',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Без упаковки',
                'value': 'Акция !!!',
                'type': 'text',
                'style': 'min-height: 30px; height: 30px'
            }
        )
    )
    red_price = forms.BooleanField(
        label='Красный ценник',
        widget=forms.CheckboxInput(
            attrs={
                'class': 'toggle',
                'type': 'checkbox',
                'style': (
                    'min-width: 50px; width: 50px; '
                    'min-height: 30px; height: 30px;'
                )
            }
        ),
        required=False
    )
    tag = forms.ModelChoiceField(
        label='Размер ценника',
        queryset=Tag.objects.filter(is_discount=True),
        widget=forms.Select(
            attrs={
                'class': 'form-input',
                'type': 'text',
                'style': 'min-height: 30px; height: 30px'
            },
        )
    )


class ProductICQUpdateForm(forms.Form):
    """Форма для обновления цен из текстовой информации, полученной по \
    средствам мессенджера ICQ."""

    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-text-update-icq',
                'cols': 40,
                'rows': 15
            }
        ),
        label='Вставьте текст из ICQ со списком товаров и цен.'
    )


class FileDownloadForm(forms.Form):
    """Форма для обновления цен из файла при новой поставке."""

    file = forms.FileField()
