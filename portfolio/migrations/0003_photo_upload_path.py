from django.db import migrations, models
import portfolio.models


class Migration(migrations.Migration):
	dependencies = [
		('portfolio', '0002_photo_original_filename'),
	]

	operations = [
		migrations.AlterField(
			model_name='photo',
			name='image',
			field=models.ImageField(upload_to=portfolio.models.photo_upload_path),
		),
	]
