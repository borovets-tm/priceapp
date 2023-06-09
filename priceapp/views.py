import re
from _csv import reader

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from django.views import View
from django.views.generic import CreateView

from .models import PrintSheet, Product, Tag, UpdateProduct, MissingProduct
from .forms import (
    PrintSheetForm,
    PrintSheetFreeForm,
    ProductICQUpdateForm,
    ProductConfirmUpdateSet,
    FileDownloadForm,
    MissingProductFormSet,
)

before_redirect_url: str = ''


class PrintSheetDelete(View):
    """
    Представление удаляет все экземпляры моделей PrintSheet, UpdateProduct и MissingProduct и перенаправляет
    представление printsheet_create.

    :param `request`: Параметр запроса — это экземпляр класса HttpRequest, представляющий HTTP-запрос, сделанный клиентом
    серверу. Он содержит информацию о запросе, такую как используемый метод HTTP, запрошенный URL-адрес и любые данные,
    отправленные в запросе.
    :type `request`: HttpRequest
    :return: ответ перенаправления HTTP на URL-адрес, указанный именем представления «printsheet_create» в пространстве
    имен «priceapp».
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        PrintSheet.objects.all().delete()
        UpdateProduct.objects.all().delete()
        MissingProduct.objects.all().delete()
        return redirect(reverse('priceapp:printsheet_create'))


class PrintSheetView(View):
    """
    Представление отображает форму для сканирования товаров и добавления новых товаров в список для печати ценников.

    :param `request`: Объект HTTP-запроса, содержащий метаданные о выполняемом запросе.
    :type `request`: HttpRequest
    :return: Представление возвращает объект HttpResponse.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        form = PrintSheetForm()
        free_form = PrintSheetFreeForm()
        last_scan = (
            PrintSheet.objects
            .select_related('tag')
            .last()
        )
        tag_list = (
            {'size': 'big', 'is_discount': (False, 'false')},
            {'size': 'big', 'is_discount': (True, 'true')},
            {'size': 'small', 'is_discount': (False, 'false')},
            {'size': 'small', 'is_discount': (True, 'true')},
        )
        context = {
            'form': form,
            'free_form': free_form,
            'tag_list': tag_list,
            'last_scan': last_scan
        }
        return render(
            request,
            'priceapp/printsheet_form.html',
            context=context
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PrintSheetForm(request.POST)
        free_form = PrintSheetFreeForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            input_line = form.get('input_line')
            size = form.get('size')
            is_discount = form.get('is_discount') == 'true'
            if input_line.isdigit():
                product = Product.objects.get(ean=input_line)
            else:
                product = (
                    Product.objects.filter(name__iexact=input_line)
                    .select_related('category', 'country')
                    .first()
                )
            if product:
                tag = Tag.objects.get(size=size, is_discount=is_discount)
                PrintSheet.objects.create(
                    tag=tag,
                    product=product.name,
                    category=product.category,
                    country=product.country,
                    price=product.price,
                    old_price=product.old_price,
                    red_price=product.red_price
                )
        if free_form.is_valid():
            form = free_form.cleaned_data
            product = (
                Product.objects
                .filter(name__iexact=form['name'])
                .select_related('country', 'category')
                .first()
            )
            tag = form['tag']
            discount_type = form['discount_type']
            name = product.name
            if tag.size == 'small':
                name = f'{name} {discount_type}'
            price = form['price']
            old_price = form['old_price']
            red_price = form['red_price']
            PrintSheet.objects.create(
                tag=tag,
                product=name,
                category=product.category,
                country=product.country,
                price=price,
                old_price=old_price,
                red_price=red_price,
                discount_type=discount_type
            )

        return redirect(reverse('priceapp:printsheet_create'))


class PrintSheetList(View):
    """
    Представление создает список ценников для печати на основе их размера и упорядочивает их на страницах, разбивая на
    листы форматом А4.

    :param `request`: Параметр запроса — это экземпляр класса HttpRequest, представляющий HTTP-запрос, сделанный клиентом
    серверу. Он содержит информацию о запросе, такую как используемый метод HTTP, запрошенный URL-адрес и любые данные,
    отправленные в запросе. Представление использует этот параметр для генерации соответствующего ответа.
    :type `request`: HttpRequest
    :return: Функция `PrintSheetList` возвращает ответ HTTP, который отображает шаблон с именем
    `'priceapp/print_tags.html'`. Контекст, передаваемый шаблону, включает в себя список списков с именем page_list,
    который содержит объекты PrintSheet, разделенные для печати и организованные на странице в зависимости от
    их ширины и высоты.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        max_height = 290
        max_width = 180
        printsheet_list = PrintSheet.objects.all().select_related('tag')
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
    """
    Представление обрабатывает обновление цен на продукты полученные в виде текста и перенаправляет на страницу
    подтверждения.

    :param `request`: Параметр запроса — это экземпляр класса HttpRequest, представляющий входящий HTTP-запрос от
    клиента. Он содержит информацию о запросе, такую как метод HTTP, заголовки и тело. Представление использует этот
    параметр для обработки запроса и создания соответствующего ответа.
    :type `request`: HttpRequest
    :return: Если форма действительна, представление перенаправляется на URL-адрес, указанный в функции «reverse» с
    именем «priceapp:product_confirm_update». Если форма недействительна, представление отображает шаблон
    `priceapp/product_icq_update.html` с контекстом формы.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        UpdateProduct.objects.all().delete()
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
        global before_redirect_url
        before_redirect_url = request.path
        form = ProductICQUpdateForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            text = form['text'].split('\r\n')
            regex = r'\s{1,2}\-{1,3}\s{0,2}'
            update_list = map(lambda x: [elem.strip() for elem in re.split(regex, x)], text)
            for product in update_list:
                if len(product) == 2:
                    product, price = product
                    old_price = 0
                elif len(product) == 3:
                    product, old_price, price = product
                else:
                    return redirect(reverse('priceapp:product_icq_update'))
                product = Product.objects.filter(name=product).first()
                UpdateProduct.objects.update_or_create(
                    name=product.name,
                    price=price,
                    old_price=old_price,
                    red_price=product.red_price
                )

        return redirect(reverse('priceapp:product_confirm_update'))


class ProductConfirmUpdateView(View):
    """
    Представление обновляет информацию о продукте после подтверждения пользователем и перенаправляет на указанный
    URL-адрес.

    :param `request`: Параметр запроса — это экземпляр класса HttpRequest, представляющий HTTP-запрос, полученный
    Django. Он содержит информацию о запросе, такую как метод HTTP (GET, POST и т. д.), заголовки и любые данные,
    которые были отправлены с запросом.
    :type `request`: HttpRequest
    :return: Представление возвращает ответ HTTP, либо перенаправление на URL-адрес, либо отображаемый HTML-шаблон с
    контекстом, содержащим набор форм. Конкретный URL-адрес для перенаправления зависит от значения переменной
    `before_redirect_url`, которая не показана во фрагменте кода.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
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
        formset = ProductConfirmUpdateSet(request.POST)
        for form in formset:
            if form.is_valid():
                form = form.cleaned_data
                name = form['name']
                price = form['price']
                old_price = form['old_price']
                red_price = form['red_price']
                updated_at = form['id'].update_at
                Product.objects.filter(name=name).update(
                    price=price,
                    old_price=old_price,
                    red_price=red_price,
                    updated_at=updated_at
                )
        if before_redirect_url == '/update/' and MissingProduct.objects.count() > 0:
            return redirect(reverse('priceapp:missingproduct_form'))
        return redirect(before_redirect_url)


class ProductUpdateView(View):
    """
    Представление обрабатывает обновление цен на продукты из файла CSV и перенаправляет на страницу подтверждения.

    :param `request`: Параметр запроса — это экземпляр класса HttpRequest, представляющий входящий HTTP-запрос от клиента.
    Он содержит информацию о запросе, такую как метод HTTP, заголовки и тело. Представление использует этот параметр для
    обработки запроса и создания соответствующего ответа.
    :type `request`: HttpRequest
    :return: Представление возвращает HTTP-перенаправление на URL-адрес, указанный обратным поиском URL-адреса
    product_confirm_update.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        UpdateProduct.objects.all().delete()
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
        global before_redirect_url
        before_redirect_url = request.path
        form = FileDownloadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file'].read().strip()
            price_str = file.decode('utf-8').split('\n')[1:]
            csv_reader = reader(price_str, delimiter=';', quotechar='"')
            for row in csv_reader:
                product = Product.objects.filter(sku=row[0])
                if product:
                    product = product.first()
                    UpdateProduct.objects.update_or_create(name=product.name, price=row[1], old_price=row[2])
                else:
                    MissingProduct.objects.update_or_create(sku=row[0], price=row[1], old_price=row[2])

        return redirect(reverse('priceapp:product_confirm_update'))


class MissingProductFormView(View):
    """
    Представление отображает форму для создания отсутствующих продуктов и обрабатывает отправку данных формы путем
    создания новых объектов Product.

    :param `request`: Объект HTTP-запроса, который содержит информацию о текущем запросе, такую как пользовательский
    агент, запрошенный URL-адрес и любые отправленные данные.
    :type `request`: HttpRequest
    :return: Метод `post` возвращает ответ перенаправления HTTP на URL-адрес, указанный функцией `reverse`, с аргументом
    `'priceapp:printsheet_delete'`.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
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
        formset = MissingProductFormSet(request.POST)
        for form in formset:
            if form.is_valid():
                form = form.cleaned_data
                form.pop('id')
                Product.objects.create(**form)

        return redirect(reverse('priceapp:printsheet_delete'))


# Приведенный ниже код определяет класс ProductCreateView, который создает новые объекты Product.
class ProductCreateView(CreateView):
    model = Product
    fields = 'sku', 'ean', 'name', 'category', 'country', 'price', 'old_price', 'red_price'
