from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.user.models import UserDevice
from apps.user.serializers import UserMiniSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data
        user = serializer.user

        # Device info olish
        # ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        # if ip_address:
        #     ip_address = ip_address.split(',')[0]
        # else:
        #     ip_address = request.META.get('REMOTE_ADDR')
        # device_name = request.META.get('HTTP_USER_AGENT', 'Unknown')

        # UserDevice yaratish
        # UserDevice.objects.create(
        #     user=user,
        #     device_name=device_name[:255],
        #     ip_address=ip_address,
        #     refresh_token=tokens.get('refresh'),
        # )

        # User ma'lumotlari
        user_data = UserMiniSerializer(user).data

        # Response
        response_data = tokens
        response_data['user'] = user_data

        return Response(response_data)
