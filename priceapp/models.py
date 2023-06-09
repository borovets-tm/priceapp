from django.db import models


class Country(models.Model):
    name = models.CharField(
        max_length=20,
        verbose_name='название страны',
        help_text='Вьетнам'
    )

    class Meta:
        ordering = 'name',
        verbose_name = 'страна производства'
        verbose_name_plural = 'страны производства'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='название категории',
        help_text='наушники'
    )

    class Meta:
        ordering = 'name',
        verbose_name = 'категория товара'
        verbose_name_plural = 'категории товаров'

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        help_text='IERM7.WW2'
    )
    ean = models.IntegerField(
        unique=True,
        verbose_name='штрихкод',
        help_text='4548736081680'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='наименование',
        help_text='IER-M7'
    )
    old_price = models.DecimalField(
        max_digits=7,
        decimal_places=0,
        verbose_name='старая цена',
        null=False,
        blank=True,
        default=0
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=0,
        verbose_name='цена',
        default=0
    )
    red_price = models.BooleanField(
        verbose_name='красный ценник',
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name='страна'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='категория'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='последнее обновление'
    )

    class Meta:
        ordering = '-updated_at', 'ean', 'sku'
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return f'({self.sku}) {self.name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='название ценника'
    )
    width = models.IntegerField(
        verbose_name='ширина'
    )
    height = models.IntegerField(
        verbose_name='высота'
    )
    size = models.CharField(
        max_length=5,
        choices=(
            ('big', 'big'),
            ('small', 'small')
        ),
        default='big',
        verbose_name='размер ценника'
    )
    is_discount = models.BooleanField(
        default=False,
        verbose_name='двойной ценник'
    )

    class Meta:
        ordering = 'is_discount', 'name'
        verbose_name = 'ценник'
        verbose_name_plural = 'ценники'

    def __str__(self):
        return f'{self.name}({self.width}*{self.height})'


class PrintSheet(models.Model):
    printed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата печати'
    )
    discount_type = models.CharField(
        max_length=40,
        null=False,
        blank=True,
        verbose_name='причина скидки',
        default='Акция !!!'
    )
    product = models.CharField(
        max_length=100,
        verbose_name='наименование',
        help_text='WF-1000XM4'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='цена',
        help_text='19990'
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=False,
        blank=True,
        verbose_name='старая цена',
        help_text='25990'
    )
    red_price = models.BooleanField(
        default=False,
        verbose_name='красная цена'
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name='страна',
        help_text='Малайзия'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='категория',
        help_text='BT наушники'
    )
    tag = models.ForeignKey(
        Tag,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='ценник'
    )

    class Meta:
        ordering = 'printed_at',
        verbose_name = 'ценник для печати'
        verbose_name_plural = 'ценники для печати'

    def __str__(self):
        return f'{self.tag} {self.product!r}'


class UpdateProduct(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='наименование'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='цена'
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='старая цена'
    )
    red_price = models.BooleanField(
        default=False,
        verbose_name='красная цена'
    )
    update_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата обновления'
    )

    class Meta:
        ordering = 'update_at',
        verbose_name = 'обновляемый товар'
        verbose_name_plural = 'список обновления'

    def __str__(self):
        return self.name


class MissingProduct(models.Model):
    sku = models.CharField(
        max_length=50,
        null=True,
        unique=True,
        help_text='IERM7.WW2'
    )
    ean = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='штрихкод',
        help_text='4548736081680'
    )
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='наименование',
        help_text='IER-M7'
    )
    old_price = models.DecimalField(
        max_digits=7,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='старая цена',
        default=0
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='цена',
        default=0
    )
    red_price = models.BooleanField(
        verbose_name='красный ценник',
        default=False
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='последнее обновление'
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='страна'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='категория'
    )

    class Meta:
        verbose_name = 'отсутствующий товар'
        verbose_name_plural = 'отсутствующие товары'

    def __str__(self):
        return self.sku
