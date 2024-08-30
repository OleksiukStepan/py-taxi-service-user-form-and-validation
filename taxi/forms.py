from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, RegexValidator

from taxi.models import Driver, Car


class CarCreateForm(forms.ModelForm):
    drivers = forms.ModelMultipleChoiceField(
        queryset=Driver.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = Car
        fields = "__all__"


class DriverForm(forms.ModelForm):
    cars = forms.ModelMultipleChoiceField(
        queryset=Car.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    license_number = forms.CharField(
        validators=[
            MaxLengthValidator(8),
            RegexValidator(
                regex=r"^[A-Z]{3}",
                message="The first 3 characters must be uppercase letters",
                code="invalid_first_three_characters"
            ),
            RegexValidator(
                regex=r"\d{5}$",
                message="The last 5 characters must be numbers",
                code="invalid_last_five_characters"
            )
        ]
    )

    class Meta:
        model = Driver
        fields = "__all__"

    def clean_license_number(self) -> str:
        license_number = self.cleaned_data["license_number"]
        if Driver.objects.filter(license_number=license_number).exists():
            raise ValidationError(
                "A driver with this license number already exists."
            )
        return license_number


class DriverCreateForm(DriverForm, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Driver
        fields = (
            "username", "first_name", "last_name", "email", "license_number"
        )


class DriverLicenseUpdateForm(DriverForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields.pop("cars", None)

    class Meta:
        model = Driver
        fields = ("license_number",)
