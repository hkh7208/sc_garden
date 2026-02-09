from django import forms


SEASON_CHOICES = [
	('', '선택 안함'),
	('봄', '봄'),
	('여름', '여름'),
	('가을', '가을'),
	('겨울', '겨울'),
]

ZONE_CHOICES = [
	('', '선택 안함'),
	('한국', '한국'),
	('네덜란드', '네덜란드'),
	('스페인', '스페인'),
	('멕시코', '멕시코'),
	('독일', '독일'),
	('영국', '영국'),
	('이탈리아', '이탈리아'),
	('프랑스', '프랑스'),
	('중국', '중국'),
	('일본', '일본'),
]


class MultiFileInput(forms.ClearableFileInput):
	allow_multiple_selected = True


class PhotoUploadForm(forms.Form):
	images = forms.FileField(
		widget=MultiFileInput(attrs={'multiple': True}),
		required=True,
	)


class PhotoEditForm(forms.Form):
	description = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={'rows': 3}),
	)
	season = forms.ChoiceField(choices=SEASON_CHOICES, required=False)
	zone = forms.ChoiceField(choices=ZONE_CHOICES, required=False)
	tags = forms.CharField(
		required=False,
		help_text='쉼표로 구분해 입력',
	)
	taken_at = forms.DateField(
		required=False,
		widget=forms.DateInput(attrs={'type': 'date'}),
	)
