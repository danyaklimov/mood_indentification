from rest_framework.serializers import ModelSerializer

from reviews.models import Metrics


class MetricsSerializer(ModelSerializer):
    class Meta:
        model = Metrics
        fields = '__all__'
