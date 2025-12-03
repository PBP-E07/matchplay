from rest_framework import serializers
from fields.models import Field, Facility

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name'] #

class FieldSerializer(serializers.ModelSerializer):
    # Digunakan default untuk validasi input (menerima ID: [1, 2])
    class Meta:
        model = Field
        fields = '__all__'

    # Mengubah output JSON saat data dikirim ke Flutter (GET)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        
        # Ganti list ID dengan list Object lengkap khusus untuk tampilan
        response['facilities'] = FacilitySerializer(instance.facilities.all(), many=True).data
        return response