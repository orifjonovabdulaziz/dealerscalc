from rest_framework import viewsets, filters
from .models import Product
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        user = self.request.user
        groups = user.dealer_groups.all()

        if groups.exists():
            return Product.objects.filter(dealer_group__in=groups)
        return Product.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        groups = user.dealer_groups.all()

        if groups.count() == 1:
            serializer.save(dealer_group=groups.first())
        elif groups.exists():
            # Если несколько — используем первую, как ты просил
            serializer.save(dealer_group=groups.first())
        else:
            raise PermissionError("У пользователя нет привязанной dealer_group.")