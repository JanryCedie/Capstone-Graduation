from rest_framework import serializers
from .models import User, Event, Participation, OTPStore

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'email', 'role', 'points', 'barangay', 'id_image', 'is_verified']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'time', 'organizer', 'points_reward', 'barangay', 'status']

class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = ['id', 'user', 'event', 'status', 'verified_at']

class OTPStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPStore
        fields = '__all__'
