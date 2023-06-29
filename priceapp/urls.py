"""В модуле прописаны urls для представлений приложения."""

from django.urls import path

from .views import (
    PrintSheetView,
    PrintSheetDelete,
    PrintSheetList,
    ProductICQUpdateView,
    ProductConfirmUpdateView,
    ProductUpdateView,
    ProductCreateView,
    MissingProductFormView,
    update_instruction_get,
)


app_name = 'priceapp'

urlpatterns = [
    path('', PrintSheetDelete.as_view(), name='printsheet_delete'),
    path('scaner/', PrintSheetView.as_view(), name='printsheet_create'),
    path('print/', PrintSheetList.as_view(), name='printsheet_print'),
    path('new-product/', ProductCreateView.as_view(), name='product_create'),
    path('update/', ProductUpdateView.as_view(), name='product_update'),
    path(
        'update/icq/',
        ProductICQUpdateView.as_view(),
        name='product_icq_update'
    ),
    path(
        'update/confirm/',
        ProductConfirmUpdateView.as_view(),
        name='product_confirm_update'
    ),
    path(
        'update/add-missing/',
        MissingProductFormView.as_view(),
        name='missingproduct_form'
    ),
    path(
        'update/instruction/',
        update_instruction_get,
        name='update_instruction'
    ),
]
