from django import forms


class PageEditForm(forms.Form):
    """
    Page Edit form.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '12', 'wrap': 'off'}),
        label="",
        required=False,
    )
    message = forms.CharField(
        label="Summary",
        required=False,
    )
    is_minor = forms.BooleanField(
        label="This is a minor Edit",
        required=False,
    )


class AnnotationImportForm(forms.Form):
    file = forms.FileField()
