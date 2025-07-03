from rest_framework import serializers

class KrediTahminSerializer(serializers.Serializer):
    no_of_dependents = serializers.IntegerField()
    education = serializers.ChoiceField(choices=["Graduate", "Not Graduate"])
    self_employed = serializers.ChoiceField(choices=["Yes", "No"])
    income_annum = serializers.FloatField()
    loan_amount = serializers.FloatField()
    loan_term = serializers.IntegerField()
    findeks_notu = serializers.IntegerField()
    residential_assets_value = serializers.FloatField()
    commercial_assets_value = serializers.FloatField()
    luxury_assets_value = serializers.FloatField()
    bank_asset_value = serializers.FloatField()
