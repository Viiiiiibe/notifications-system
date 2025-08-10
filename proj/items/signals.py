from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Item

channel_layer = get_channel_layer()


@receiver(pre_save, sender=Item)
def item_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_save_owner_id = sender.objects.get(pk=instance.pk).owner_id
            instance._pre_save_name = sender.objects.get(pk=instance.pk).name
        except sender.DoesNotExist:
            instance._pre_save_owner_id = None
            instance._pre_save_name = None
    else:
        instance._pre_save_owner_id = None
        instance._pre_save_name = None


@receiver(post_save, sender=Item)
def item_post_save(sender, instance, created, **kwargs):
    # собираем сообщение
    obj = instance
    message = {
        'type': 'item.changed',
        'id': obj.pk,
        'name': obj.name,
        'status': obj.status,
        'owner_id': obj.owner_id,
        'created': created,
    }

    # если сменился владелец — уведомляем старого владельца (если был) и нового
    old_owner_id = getattr(instance, '_pre_save_owner_id', None)
    new_owner_id = obj.owner_id

    if old_owner_id and old_owner_id != new_owner_id:
        payload = {
            'message': {'title': 'Ownership changed', 'text': f'Item "{obj.name}" передан другому пользователю.'}}
        async_to_sync(channel_layer.group_send)(f'admin_user_{old_owner_id}',
                                                {'type': 'notify', 'message': payload['message']})

    # уведомить нового владельца (и текущего владельца при обычном изменении)
    payload = {'message': {'title': 'Item updated', 'text': f'Item "{obj.name}" изменён.'}}
    async_to_sync(channel_layer.group_send)(f'admin_user_{new_owner_id}',
                                            {'type': 'notify', 'message': payload['message']})

    # уведомить суперюзеров
    super_payload = {'message': {'title': 'Item updated (admin)', 'text': f'Item "{obj.name}" (id={obj.pk}) изменён.'}}
    async_to_sync(channel_layer.group_send)('admin_superusers', {'type': 'notify', 'message': super_payload['message']})
