from django import forms


class MultiFileInput(forms.ClearableFileInput):
	allow_multiple_selected = True


class PhotoUploadForm(forms.Form):
	images = forms.FileField(
		widget=MultiFileInput(attrs={'multiple': True}),
		required=True,
	)
