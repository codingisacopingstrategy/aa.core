from django import forms


class PageEditForm(forms.Form):
    """
    Page Edit form.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '12'}),
        label="",
    )
    message = forms.CharField(
        label="Summary",
        required=False,
    )
    is_minor = forms.BooleanField(
        required=False,
        label="This is a minor Edit",
    )
