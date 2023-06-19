import re
from _csv import reader

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django.views import View
from django.views.generic import CreateView

from .models import (
    PrintSheet,
    Product,
    Tag,
    UpdateProduct,
    MissingProduct, Category, Country,
)
from .forms import (
    PrintSheetForm,
    PrintSheetFreeForm,
    ProductICQUpdateForm,
    ProductConfirmUpdateSet,
    FileDownloadForm,
    MissingProductFormSet,
)

before_redirect_url: str = ''
last_scan: dict = {
    'tag': {
        'size': 'big',
        'is_discount': False
    },
    'product': 'Список пуст'
}
missing_products_flag: bool = False


class PrintSheetDelete(View):
    """Стартовое представление которое очищает таблицы \
    `Ценники для печати`, `Обновляемые товары` и `Ненайденные товары`, \
    после чего перенаправляет на страницу формирования печати ценников."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос, очищает таблиц \
        и перенаправляет на страницу формирования печати.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        global last_scan
        PrintSheet.objects.all().delete()
        UpdateProduct.objects.all().delete()
        MissingProduct.objects.all().delete()
        last_scan = {
            'tag': {
                'size': 'big',
                'is_discount': False
            },
            'product': 'Список пуст'
        }
        return redirect(reverse('priceapp:printsheet_create'))


class PrintSheetView(View):
    """Представление формирует список ценников для печати."""

    tag_list = (
        {'size': 'big', 'is_discount': (False, 'false')},
        {'size': 'big', 'is_discount': (True, 'true')},
        {'size': 'small', 'is_discount': (False, 'false')},
        {'size': 'small', 'is_discount': (True, 'true')},
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос, использует две формы \
        для обработки: форма поиска по Товарам и свободная \
        форма для формирования ценников по уценки.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        form = PrintSheetForm()
        free_form = PrintSheetFreeForm()
        context = {
            'form': form,
            'free_form': free_form,
            'tag_list': self.tag_list,
            'last_scan': last_scan
        }
        return render(
            request,
            'priceapp/printsheet_form.html',
            context=context
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Метод формирует список ценников для печати, \
        обрабатывая для этого формы.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        global last_scan
        error_flag = ''
        form = PrintSheetForm(request.POST)
        free_form = PrintSheetFreeForm(request.POST)
        tag = last_scan['tag']
        discount_type = 'Акция !!!'
        if form.is_valid():
            form = form.cleaned_data
            input_line = form['input_line']
            size = form['size']
            is_discount = form['is_discount'] == 'true'
            tag = Tag.objects.get(size=size, is_discount=is_discount)
            product = (
                Product.objects.filter(
                    Q(ean=input_line) | Q(name__iexact=input_line)
                )
                .values(
                    'name',
                    'category',
                    'country',
                    'price',
                    'old_price',
                    'red_price'
                )
                .first()
            )
            if not product:
                error_flag = input_line

        if free_form.is_valid():
            form = free_form.cleaned_data
            tag = form['tag']
            product = (
                Product.objects
                .filter(name__iexact=form['name'])
                .values(
                    'name',
                    'category',
                    'country',
                    'price',
                    'old_price',
                    'red_price'
                )
                .first()
            )
            if product:
                discount_type = form['discount_type']
                name = product['name']
                if tag.size == 'small':
                    product['name'] = f'{name} {discount_type}'
                product['price'] = form['price']
                product['old_price'] = form['old_price']
                product['red_price'] = form['red_price']
            else:
                error_flag = form['name']
        last_scan['tag'] = tag
        if error_flag:
            form = PrintSheetForm(request.POST.copy())
            form.data['input_line'] = ''
            form.errors.pop('input_line')
            if free_form.is_valid():
                free_form.add_error('name', f'Товар {error_flag} не найден!')
            else:
                form.add_error('input_line', f'Товар {error_flag}\n\n не найден!')
            context = {
                'form': form,
                'free_form': free_form,
                'tag_list': self.tag_list,
                'last_scan': last_scan
            }
            return render(
                request,
                'priceapp/printsheet_form.html',
                context=context
            )
        else:
            last_scan['product'] = product['name']
            product['category'] = (
                Category.objects.only('name')
                .get(pk=product['category'])
                .name
            )
            product['country'] = (
                Country.objects.only('name')
                .get(pk=product['country'])
                .name
            )
            PrintSheet.objects.create(
                tag=tag,
                discount_type=discount_type,
                **product
            )

        return redirect(reverse('priceapp:printsheet_create'))


class PrintSheetList(View):
    """Представление формирует лист печати ценников."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос, проходит по списку \
        ценников для печати и формирует листы размером A4.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        max_height = 290
        max_width = 180
        printsheet_list = PrintSheet.objects.all()
        size_list = ['big', 'small']
        page_list = [[]]
        height = 0
        width = 0
        for size in size_list:
            tag_list = printsheet_list.filter(tag__size=size)
            for tag in tag_list:
                page_list[-1].append(tag)
                width += tag.tag.width
                if width == max_width:
                    height += tag.tag.height
                    width = 0
                if height + tag.tag.height > max_height:
                    page_list.append([])
                    height = 0
        context = {
            'page_list': page_list
        }
        return render(
            request,
            'priceapp/print_tags.html',
            context=context
        )


class ProductICQUpdateView(View):
    """Представление обрабатывает обновление цен по \
    полученной информации от руководства через ICQ."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос. В начале обработки \
        происходит удаление всех объектов в Обновляемых \
        товарах и в Ненайденных товарах.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        UpdateProduct.objects.all().delete()
        MissingProduct.objects.all().delete()
        form = ProductICQUpdateForm()
        context = {
            'form': form
        }
        return render(
            request,
            'priceapp/product_icq_update.html',
            context=context
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает post запрос. Из полученного текста \
        выделяются строки с товаром и новой ценой и формируются \
        два списка: Обновляемые товары и Ненайденные в базе \
        товары.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        global before_redirect_url, missing_products_flag
        before_redirect_url = request.path
        form = ProductICQUpdateForm(request.POST)
        update_product_list = []
        missing_product_list = []
        if form.is_valid():
            form = form.cleaned_data
            text = form['text'].split('\r\n')
            regex = r'\s{1,2}\-{1,3}\s{0,2}'
            update_list = map(lambda x: [elem.strip() for elem in re.split(regex, x)], text)
            for product in update_list:
                if len(product) == 2:
                    name, price = product
                    old_price = 0
                elif len(product) == 3:
                    name, old_price, price = product
                else:
                    continue
                product = Product.objects.filter(name=name).first()
                if product:
                    update_product_list.append(
                        UpdateProduct(
                            name=product.name,
                            price=price,
                            old_price=old_price,
                            red_price=product.red_price
                        )
                    )
                else:
                    missing_product_list.append(
                        MissingProduct(
                            name=name,
                            price=price,
                            old_price=old_price
                        )
                    )
        if missing_product_list:
            MissingProduct.objects.bulk_create(missing_product_list)
            missing_products_flag = True
        if update_product_list:
            UpdateProduct.objects.bulk_create(update_product_list)
            return redirect(reverse('priceapp:product_confirm_update'))
        return redirect(reverse('priceapp:missingproduct_form'))


class ProductUpdateView(View):
    """Представление обновляет товары из файла при поступлении \
    новой партии товара. Информацию передает руководство."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос. В начале обработки \
        происходит удаление всех объектов в Обновляемых \
        товарах и в Ненайденных товарах.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        UpdateProduct.objects.all().delete()
        MissingProduct.objects.all().delete()
        form = FileDownloadForm()
        context = {
            'form': form,
        }
        return render(
            request,
            'priceapp/product_update.html',
            context=context
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает post запрос. Из полученного файла \
        выделяются строки с товаром и информацией о цене для \
        формирования списков Обновляемых товаров и Ненайденных \
        в базе товаров.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        global before_redirect_url, missing_products_flag
        before_redirect_url = request.path
        form = FileDownloadForm(request.POST, request.FILES)
        update_product_list = []
        product_name_list = []
        missing_product_list = []
        if form.is_valid():
            file = form.cleaned_data['file'].read().strip()
            price_str = file.decode('utf-8').split('\n')[1:]
            csv_reader = reader(price_str, delimiter=';', quotechar='"')
            for row in csv_reader:
                product = Product.objects.filter(sku=row[0])
                if product:
                    product = product.first()
                    update_product = UpdateProduct(name=product.name, price=row[1], old_price=row[2])
                    if update_product.name not in product_name_list:
                        update_product_list.append(update_product)
                        product_name_list.append(product.name)
                else:
                    missing_product_list.append(
                        MissingProduct(sku=row[0], price=row[1], old_price=row[2])
                    )
        if missing_product_list:
            MissingProduct.objects.bulk_create(missing_product_list)
            missing_products_flag = True
        if update_product_list:
            UpdateProduct.objects.bulk_create(update_product_list)
            return redirect(reverse('priceapp:product_confirm_update'))
        return redirect(reverse('priceapp:missingproduct_form'))


class ProductConfirmUpdateView(View):
    """Представление обрабатывает подтверждение обновления цен."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос и передает список в виде \
        формы для проверки корректности данных.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        formset = ProductConfirmUpdateSet()
        context = {
            'formset': formset
        }
        return render(
            request,
            'priceapp/product_confirm_update.html',
            context=context
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает post запрос. Проходит по всему \
        списку полученных форм и формирует список для \
        массового обновления.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        formset = ProductConfirmUpdateSet(request.POST)
        name_list: list = []
        data_list: dict = {}
        for form in formset:
            if form.is_valid():
                form = form.cleaned_data
                name = form['name']
                name_list.append(name)
                data_list[name] = {
                    'price': form['price'],
                    'old_price': form['old_price'],
                    'red_price': form['red_price'],
                    'updated_at': form['id'].update_at
                }
        product_list = Product.objects.filter(name__in=name_list)
        for product in product_list:
            product.price = data_list[product.name]['price']
            product.old_price = data_list[product.name]['old_price']
            product.red_price = data_list[product.name]['red_price']
            product.updated_at = data_list[product.name]['updated_at']
        Product.objects.bulk_update(
            product_list,
            [
                'price',
                'old_price',
                'red_price',
                'updated_at'
            ]
        )
        UpdateProduct.objects.all().delete()
        if missing_products_flag:
            return redirect(reverse('priceapp:missingproduct_form'))
        return redirect(before_redirect_url)


class MissingProductFormView(UserPassesTestMixin, View):
    """Представление служит для добавления товаров, которые \
    не найдены в базе при обновлении."""

    def test_func(self) -> bool:
        """
        Проверяет наличие объектов в списке Ненайденых товаров.

        :return: bool.
        """
        return MissingProduct.objects.exists()

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        """
        При отсутствии Ненайденных товаров вернет пользователя на \
        страницу обновления.

        :param request: HttpRequest.
        :param args: Any.
        :param kwargs: Any.
        :return: HttpResponse.
        """
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return redirect(before_redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает get запрос. Формирует список \
        Ненайденных при обновлении товаров для заполнения \
        и создания новых Product.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        formset = MissingProductFormSet()
        context = {
            'formset': formset
        }
        return render(
            request,
            'priceapp/missingproduct_form.html',
            context=context
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Метод обрабатывает post запрос. Проверяет данные из \
        списка форм и производит массовое добавление новых \
        записей в Товары.

        :param request: HttpRequest.
        :return: HttpResponse.
        """
        formset = MissingProductFormSet(request.POST)
        product_list = []
        for form in formset:
            if form.is_valid():
                form = form.cleaned_data
                form.pop('id')
                product_list.append(Product(**form))
        Product.objects.bulk_create(product_list)
        MissingProduct.objects.all().delete()
        return redirect(reverse('priceapp:printsheet_delete'))


class ProductCreateView(CreateView):
    """Представление основано на CreateView для создания \
    новых товаров"""

    model = Product
    fields = 'sku', 'ean', 'name', 'category', 'country', 'price', 'old_price', 'red_price'
    success_url = reverse_lazy('priceapp:printsheet_delete')
