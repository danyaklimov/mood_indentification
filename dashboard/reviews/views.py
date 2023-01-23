import json

import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from reviews.models import Metrics
from reviews.serializers import MetricsSerializer

from reviews.models import Review

API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
headers = {"Authorization": f"Bearer {'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'}"}


def query(request, payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


class ClassifyReview(APIView):
    def get(self, request, format=None):
        outputs = query(request, Review.objects.get(user=request.user).content)
        metric = Metrics(
            review=Review.objects.get(user=request.user),
            negative_rate=outputs[0][0]['score'],
            neutral_rate=outputs[0][1]['score'],
            positive_rate=outputs[0][2]['score']
        )
        metric.save()
        return Response(outputs)




# output = query({
#     "inputs": "I like you. I love you",
# })


class MetricsViewSet(ModelViewSet):
    queryset = Metrics.objects.all()
    serializer_class = MetricsSerializer
