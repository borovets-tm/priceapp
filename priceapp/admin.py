from django.contrib import admin

from .models import Tag, PrintSheet, Product, Category, Country


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'name', 'size', 'is_discount', 'width', 'height'
    list_display_links = 'name',


@admin.register(PrintSheet)
class PrintSheetAdmin(admin.ModelAdmin):
    list_display = 'printed_at', 'name', 'tag', 'discount_type_view'
    list_display_links = 'printed_at',
    fieldsets = (
        (None, {
            'fields': ('category', 'country', 'name', )
        }),
        ('Информация о цене', {
            'fields': ('price', 'old_price', 'red_price', 'discount_type')
        }),
        ('Ценник', {
            'fields': ('tag', )
        })
    )

    def get_queryset(self, request):
        return PrintSheet.objects.select_related('tag')

    def discount_type_view(self, obj: PrintSheet) -> str:
        if obj.tag.is_discount:
            return obj.discount_type
        return ''


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'sku', 'ean', 'name', 'category', 'price', 'red_price', 'updated_at'
    list_display_links = 'sku', 'ean', 'name'
    search_fields = 'sku', 'ean', 'name'
    list_filter = 'category',
    fieldsets = (
        (None, {
            'fields': ('sku', 'ean', 'name'),
        }),
        ('Дополнительная информация', {
            'fields': ('category', 'country'),
            'classes': ('wide',),
            'description': 'Информация о категории и стране производители'
        }),
        ('Информация о цене', {
            'fields': ('price', 'old_price', 'red_price'),
            'classes': ('wide',),
            'description': 'Текущая и предыдущая(если доступна, иначе 0) цена'
        })
    )

    def get_queryset(self, request):
        return Product.objects.select_related('country', 'category')


class ProductTabularInline(admin.TabularInline):
    model = Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name',
    list_display_links = 'name',
    inlines = [
        ProductTabularInline,
    ]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = 'name',
    list_display_links = 'name',
    inlines = [
        ProductTabularInline,
    ]
