from django.test import TestCase

from webapp.forms import LoginForm, RegisterForm, BioForm, PostImageForm, PostForm, CommentTagForm, PostTagForm, \
    CommentForm
from webapp.models import UserProfile, Tag


class TestLoginForm(TestCase):
    def test_valid_username_password(self):
        form_data = {'username': 'testuser', 'password': 'testpassword'}
        form = LoginForm(data=form_data)
        is_valid = form.is_valid()
        assert is_valid

    def test_blank_username(self):
        form_data = {'username': '', 'password': 'testpassword'}
        form = LoginForm(data=form_data)
        is_valid = form.is_valid()
        username_errors = form.errors.get('username')
        assert is_valid is False
        assert len(username_errors) == 1
        assert 'This field is required.' in username_errors[0]

    def test_blank_password(self):
        form_data = {'username': 'testuser', 'password': ''}
        form = LoginForm(data=form_data)
        is_valid = form.is_valid()
        password_errors = form.errors.get('password')
        assert is_valid is False
        assert len(password_errors) == 1
        assert 'This field is required.' in password_errors[0]


class TestRegisterForm:
    def test_display_form(self):
        form = RegisterForm()
        assert str(form) == '<form method="post">'
        assert 'csrfmiddlewaretoken' in str(form)
        assert 'id="id_username"' in str(form)
        assert 'id="id_email"' in str(form)
        assert 'id="id_password1"' in str(form)
        assert 'id="id_password2"' in str(form)


class TestBioForm:
    def test_form_creation(self, mocker):
        mocker.patch('django.db.models.Model.save')
        form = BioForm()
        assert form.is_valid() == False

    def test_form_submission(self, mocker):
        mocker.patch('django.db.models.Model.save')
        data = {'full_name': 'John Doe', 'bio': 'Test bio', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid()
        form.save()
        assert UserProfile.objects.filter(full_name='John Doe').exists()

    def test_database_failure(self, mocker):
        mocker.patch('django.db.models.Model.save',
                     side_effect=Exception('Database connection lost'))
        data = {'full_name': 'John Doe', 'bio': 'Test bio', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid() is False

    def test_model_changes(self):
        class MockUserProfile:
            pass

        BioForm.Meta.model = MockUserProfile
        data = {'full_name': 'John Doe', 'bio': 'Test bio', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid() is False

    def test_form_validation_errors(self):
        data = {'full_name': '', 'bio': '', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid() is False
        assert 'full_name' in form.errors
        assert 'bio' in form.errors

    def test_form_fields(self):
        form = BioForm()
        assert 'full_name' in form.fields
        assert 'bio' in form.fields
        assert 'avatar' in form.fields


class TestPostImageForm:
    def test_valid_image_submission(self):
        form_data = {'image': 'valid_image.jpg'}
        form = PostImageForm(data=form_data, files=form_data)
        assert form.is_valid()

    def test_save_form_data(self):
        form_data = {'image': 'valid_image.jpg'}
        form = PostImageForm(data=form_data, files=form_data)
        assert form.is_valid()
        post_image = form.save()
        assert post_image.image.name == 'valid_image.jpg'

    def test_invalid_image_submission(self):
        form_data = {'image': 'invalid_file.txt'}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors

    def test_large_image_submission(self):
        form_data = {'image': 'large_image.jpg'}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors

    def test_image_validation(self):
        form_data = {'image': 'invalid_file.txt'}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors

    def test_empty_form_submission(self):
        form_data = {}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors


class TestPostForm:
    def test_form_save(self, mocker):
        mock_save = mocker.patch.object(PostForm, 'save')
        form_data = {'caption': 'Test caption'}
        form = PostForm(data=form_data)
        assert form.is_valid()
        form.save()
        mock_save.assert_called_once()

    def test_form_submission_with_csrf_token(self, client):
        response = client.post('/submit-form/',
                               {'caption': 'Test caption',
                                'csrfmiddlewaretoken': 'token'})
        assert response.status_code == 200

    def test_form_validation(self):
        form_data = {'caption': ''}
        form = PostForm(data=form_data)
        assert not form.is_valid()

    def test_empty_caption_field(self):
        form_data = {'caption': ''}
        form = PostForm(data=form_data)
        assert 'caption' in form.errors

    def test_caption_field_max_length(self):
        form_data = {'caption': 'a' * 201}
        form = PostForm(data=form_data)
        assert 'caption' in form.errors

    def test_invalid_data_type_for_caption_field(self):
        form_data = {'caption': 123}
        form = PostForm(data=form_data)
        assert 'caption' in form.errors


class TestPostTagForm:
    def test_valid_tag_submission(self, mocker):
        mock_tag = mocker.Mock()
        mock_tag.objects.create.return_value = mock_tag
        mocker.patch('app.forms.Tag', mock_tag)
        form_data = {'name': 'test tag'}
        form = PostTagForm(data=form_data)
        form.is_valid()
        form.save()
        mock_tag.objects.create.assert_called_once_with(name='test tag')

    def test_existing_tag_submission(self, mocker):
        mock_tag = mocker.Mock()
        mock_tag.objects.filter.return_value = [mock_tag]
        mocker.patch('app.forms.Tag', mock_tag)
        form_data = {'name': 'test tag'}
        form = PostTagForm(data=form_data)
        form.is_valid()
        form.save()
        mock_tag.objects.filter.assert_called_once_with(name='test tag')
        mock_tag.save.assert_called_once()

    def test_empty_tag_submission(self):
        form_data = {'name': ''}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_long_tag_submission(self):
        form_data = {'name': 'a' * 51}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_form_validation(self):
        form_data = {'name': 'invalid tag name'}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_special_char_tag_submission(self):
        form_data = {'name': 'test tag!@#$'}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors


class TestCommentTagForm:
    def test_valid_tag_submission(self):
        form_data = {'name': 'test_tag'}
        form = CommentTagForm(data=form_data)
        assert form.is_valid()
        tag = form.save()
        assert tag.name == 'test_tag'

    def test_existing_tag_submission(self):
        tag = Tag.objects.create(name='existing_tag')
        form_data = {'name': 'existing_tag'}
        form = CommentTagForm(data=form_data)
        assert form.is_valid()
        tag = form.save()
        assert tag == Tag.objects.get(name='existing_tag')

    def test_empty_tag_submission(self):
        form_data = {'name': ''}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_max_length_tag_submission(self):
        form_data = {'name': 'a' * 51}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_validation_error_message(self):
        form_data = {'name': ''}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'This field is required.' in form.errors['name']

    def test_invalid_character_tag_submission(self):
        form_data = {'name': 'test@tag'}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors


class TestCommentForm:
    def test_form_creation(self):
        form = CommentForm()
        assert form.is_valid() is False

    def test_form_display(self):
        form = CommentForm()
        assert 'content' in form.as_p()

    def test_empty_content_field(self):
        form = CommentForm(data={'content': ''})
        assert form.is_valid() is False

    def test_content_field_exceeds_max_length(self):
        content = 'a' * 1001
        form = CommentForm(data={'content': content})
        assert form.is_valid() is False

    def test_form_validation_errors(self):
        form = CommentForm(data={'content': ''})
        assert 'This field is required.' in form.errors['content']

    def test_form_data_saved_correctly(self):
        content = 'This is a test comment.'
        form = CommentForm(data={'content': content})
        comment = form.save()
        assert comment.content == content
