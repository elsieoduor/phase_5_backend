from rest_framework import serializers
from .models import User
from .models import User, ChildrenOrphanage, Donation, Visit, Review
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'name', 'email', 'password', 'role']
    extra_kwargs = {
      'password':{'write_only': True}
    }

  def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
  
  def create(self, validated_data):
    password = validated_data.pop('password', None)
    instance = self.Meta.model(**validated_data)
    if password is not None:
      instance.set_password(password)
    instance.save()
    return instance


class ChildrenOrphanageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildrenOrphanage
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'