from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ValidationError as DJValidationError
from rest_framework.exceptions import ValidationError, ParseError

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(ModelViewSet):
    """
    Model Viewet hold all controles for Task API
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=True, methods=['post'], url_path='change-state')
    def transmit_view(self, request, pk=None, *args, **kwargs):
        """
        custom action responsed on change state for every instance
        if instance have done state it will return error that we cant change Done state
        """
        instance = self.get_object()
        try:
            instance.transmit()
            return super().retrieve(request, *args, **kwargs)
        except DJValidationError as e:
            raise ValidationError(e.message)

    @action(detail=True, methods=['patch', ], url_path='update-title')
    def update_title(self, request, pk=None, *args, **kwargs):
        """
        custome action responsed on change instance title only if instance state is new
        if we try to use this action when instance state not in new state it will rais error
        """
        instance = self.get_object()
        try:
            instance.update(field='title', value=request.data.get('title'))
            return super().retrieve(request, *args, **kwargs)
        except AttributeError:
            raise ParseError(f"Task {instance} isn't in New state. You can't change Attribute")

    @action(detail=True, methods=['patch', ], url_path='update-description')
    def update_desc(self, request, pk=None, *args, **kwargs):
        """
        custome action responsed on change instance description only if instance state is new
        if we try to use this action when instance state not in new state it will rais error
        """
        instance = self.get_object()
        try:
            instance.update(field='desc', value=request.data.get('desc'))
            return super().retrieve(request, *args, **kwargs)
        except AttributeError:
            raise ParseError(f"Task {instance} isn't in New state. You can't change Attribute")

    @action(detail=True, methods=['post'], url_path='add-hook')
    def add_hook(self, request, pk=None, *args, **kwargs):
        """
        custome action let user link instance with other instance only if instance curent state is in progress
        and return list of all linked tasks with this task
        """
        instance = self.get_object()
        try:
            instance.link(
                [i for i in self.get_queryset() if i.pk in self.request.data.get('hook')]
            )
            self.queryset = instance.get_linked_tasks()
            return super().list(request, *args, **kwargs)
        except AttributeError:
            raise ParseError(f"Task {instance} isn't in In Progress. You can't add linked tasks")

    @action(detail=True, methods=['get'], url_path='get-hook')
    def get_hook(self, request, pk=None, *args, **kwargs):
        """
        return list of all linked tasks with instance task only if current state is in progress
        """
        instance = self.get_object()
        try:
            self.queryset = instance.get_linked_tasks()
            return super().list(request, *args, **kwargs)
        except AttributeError:
            raise ParseError(f"Task {instance} isn't in In Progress. You can't get linked tasks")
