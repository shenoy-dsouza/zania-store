from rest_framework import generics, status
from rest_framework.response import Response
from store.orders.serializers import OrderSerializer
from store.orders.utils.order_processing import process_order
from rest_framework.serializers import ValidationError
from store.exceptions import BaseException
from store import error_codes
from store.orders.models import Order


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except BaseException as e:
            return Response(
                {
                    "status": "error",
                    "code": e.get_error_code(),
                    "message": str(e),
                    "errors": e.get_errors(),
                },
                e.get_http_status_code(),
            )

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            order = process_order(serializer.validated_data["products"])

            return Response(
                {
                    "status": "success",
                    "message": "Order placed successfully.",
                    "order_id": order.id,
                    "total_price": order.total_price,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response(
                {
                    "errors": e.detail,
                    "code": error_codes.VALIDATION_ERROR,
                },
                status.HTTP_400_BAD_REQUEST,
            )

        except BaseException as e:
            return Response(
                {
                    "status": "error",
                    "code": e.get_error_code(),
                    "message": str(e),
                    "errors": e.get_errors(),
                },
                e.get_http_status_code(),
            )
