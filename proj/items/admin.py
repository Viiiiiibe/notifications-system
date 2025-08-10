from django.contrib import admin
from .models import Item


class TextInputFilter(admin.SimpleListFilter):
    template = 'admin/text_input_filter.html'
    # Будет переопределено в дочерних классах
    parameter_name = None
    title = None

    def lookups(self, request, model_admin):
        return (('dummy', 'dummy'),)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(**{self.parameter_name + '__icontains': value})
        return queryset

    def value(self):
        return self.used_parameters.get(self.parameter_name)


class NameFilter(TextInputFilter):
    parameter_name = 'name'
    title = 'текстовый фильтр по названию'


class UsernameFilter(TextInputFilter):
    parameter_name = 'owner__username'
    title = 'текстовый фильтр по владельцу'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'owner', 'updated_at')
    list_filter = (NameFilter, UsernameFilter, 'status', 'owner')

    def get_queryset(self, request):
        # Ограничиваем видимость объектов
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def get_list_filter(self, request):
        # Динамически изменяем фильтры для обычных пользователей
        filters = list(super().get_list_filter(request))
        if not request.user.is_superuser:
            filters = [f for f in filters if f != 'owner']
        return filters

    def changelist_view(self, request, extra_context=None):
        # Добавляем параметры фильтров в контекст
        extra_context = extra_context or {}
        extra_context['filters_params'] = request.GET.copy()
        return super().changelist_view(request, extra_context)

    class Media:
        # WebSocket-уведомления
        js = (
            'js/admin-notifications.js',
        )
        css = {
            'all': ('css/admin-notifications.css',)
        }
