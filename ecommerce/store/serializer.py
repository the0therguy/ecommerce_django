class MesSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(many=False, slug_field='name', queryset=User.objects.all())
    receiver = serializers.SlugRelatedField(many=False, slug_field='name', queryset=User.objects.all())

    class Meta:
        model = msg
        fields = '__all__'
