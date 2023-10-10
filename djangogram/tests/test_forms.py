from django.test import TestCase

from webapp.forms import LoginForm, RegisterForm, BioForm, PostImageForm, PostForm, CommentTagForm, PostTagForm, \
    CommentForm
from webapp.models import UserProfile, Tag


class TestLoginForm(TestCase):
    def test_valid_username_password(self):
        """
        Test case to verify the validation of a valid username and password.
        This function creates a form with the given username and password,
        and then checks if the form is valid. It asserts that the form is
        indeed valid.
        Parameters:
            self (TestCase): The test case instance.
        """
        form_data = {'username': 'testuser', 'password': 'testpassword'}
        form = LoginForm(data=form_data)
        is_valid = form.is_valid()
        assert is_valid

    def test_blank_username(self):
        """
        Test case to check if the username field is left blank.
        This test function creates a form with a blank username and a test password.
        It then checks if the form is valid and if there is an error message for the username field.
        It asserts that the form is not valid, that there is exactly one error for the username field,
        and that the error message is "This field is required."
        Parameters:
            self (TestCase): The current test case instance.
        """
        form_data = {'username': '', 'password': 'testpassword'}
        form = LoginForm(data=form_data)
        is_valid = form.is_valid()
        username_errors = form.errors.get('username')
        assert is_valid is False
        assert len(username_errors) == 1
        assert 'This field is required.' in username_errors[0]

    def test_blank_password(self):
        """
        Test case for the scenario when the password field is left blank.
        This function creates a test case for the scenario when the password field is left blank in the login form.
        It sets the form data with a blank password and verifies that the form is not valid.
        It also checks that there is exactly one password error message returned and that it contains the expected error message.
        Parameters:
        - self: The instance of the test class.
        """
        form_data = {'username': 'testuser', 'password': ''}
        form = LoginForm(data=form_data)
        is_valid = form.is_valid()
        password_errors = form.errors.get('password')
        assert is_valid is False
        assert len(password_errors) == 1
        assert 'This field is required.' in password_errors[0]


class TestRegisterForm:
    def test_display_form(self):
        """
        Test the display of the registration form.
        This function initializes a `RegisterForm` object and performs
        a series of assertions to validate the HTML representation of the form.
        The assertions check for the presence of various form elements
        (e.g., username, email, password) and ensure that the form is rendered
        with the correct method and CSRF token.
        Parameters:
            self: The current instance of the test class.
        """
        form = RegisterForm()
        assert str(form) == '<form method="post">'
        assert 'csrfmiddlewaretoken' in str(form)
        assert 'id="id_username"' in str(form)
        assert 'id="id_email"' in str(form)
        assert 'id="id_password1"' in str(form)
        assert 'id="id_password2"' in str(form)


class TestBioForm:
    def test_form_creation(self, mocker):
        """
        Test the form creation functionality.
        Parameters:
        - mocker: The mocker object used for patching.
        """
        mocker.patch('django.db.models.Model.save')
        form = BioForm()
        assert form.is_valid() == False

    def test_form_submission(self, mocker):
        """
        Test the form submission functionality.
        Parameters:
            mocker (Mock): The mocker object used for patching.
        """
        mocker.patch('django.db.models.Model.save')
        data = {'full_name': 'John Doe', 'bio': 'Test bio', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid()
        form.save()
        assert UserProfile.objects.filter(full_name='John Doe').exists()

    def test_database_failure(self, mocker):
        """
        Test the behavior of the 'test_database_failure' function when a database failure occurs.
        Args:
            mocker: The mocker object used to patch the 'save' method of the 'django.db.models.Model' class.

        """
        mocker.patch('django.db.models.Model.save', side_effect=Exception('Database connection lost'))
        data = {'full_name': 'John Doe', 'bio': 'Test bio', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid() is False

    def test_model_changes(self):
        """
        Test the changes made to the model in the BioForm.
        This function is responsible for testing the changes made to the model in the BioForm class.
        It creates a mock user profile, assigns it to the BioForm's Meta.model attribute,
         and then creates an instance of the BioForm with test data.
         The function then asserts that the form is not valid.
        """

        class MockUserProfile:
            pass

        BioForm.Meta.model = MockUserProfile
        data = {'full_name': 'John Doe', 'bio': 'Test bio', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid() is False

    def test_form_validation_errors(self):
        """
        Test the form validation errors for the given data.
        :param self: The instance of the test class.
        """
        data = {'full_name': '', 'bio': '', 'avatar': None}
        form = BioForm(data=data)
        assert form.is_valid() is False
        assert 'full_name' in form.errors
        assert 'bio' in form.errors

    def test_form_fields(self):
        """
        Test the form fields of the BioForm class.
        This function initializes an instance of the BioForm class
        and performs assertions to check if the expected fields exist in the form.
        Parameters:
        - self: The instance of the class.
        """
        form = BioForm()
        assert 'full_name' in form.fields
        assert 'bio' in form.fields
        assert 'avatar' in form.fields


class TestPostImageForm:
    def test_valid_image_submission(self):
        """
        Test the validity of an image submission.
        Parameters:
            self (object): The instance of the class.
        """
        form_data = {'image': 'valid_image.jpg'}
        form = PostImageForm(data=form_data, files=form_data)
        assert form.is_valid()

    def test_save_form_data(self):
        """
        Test the save method of the PostImageForm class.
        This function creates a test instance of the PostImageForm class with
        a valid image file and checks if the form is valid.
        Then it saves the form and asserts that the image name of the saved form matches the original image name.
        Parameters:
        - self: The instance of the test class.

        """
        form_data = {'image': 'valid_image.jpg'}
        form = PostImageForm(data=form_data, files=form_data)
        assert form.is_valid()
        post_image = form.save()
        assert post_image.image.name == 'valid_image.jpg'

    def test_invalid_image_submission(self):
        """
        Test case for invalid image submission.
        This function tests the behavior of the test_invalid_image_submission method.
        It submits an invalid image file to the server and verifies that the form is not valid
        and that the 'image' field has errors.
        Parameters:
        - self: The current instance of the test class.

        """
        form_data = {'image': 'invalid_file.txt'}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors

    def test_large_image_submission(self):
        """
        Test the submission of a large image.
        This function tests the submission of a large image by creating a form
        with a large image file and checking if the form is valid. The function
        uses the `PostImageForm` class to create the form with the provided
        image file. It then asserts that the form is not valid and that the
        'image' field is present in the form errors.
        Parameters:
        - self: The instance of the test class.
        """
        form_data = {'image': 'large_image.jpg'}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors

    def test_image_validation(self):
        """
        Test the validation of the image field in the PostImageForm.
        This function creates a test case where the 'image' field of the form is set to an invalid file name.
        It then creates an instance of the PostImageForm with the given form data and files.
        The function asserts that the form is not valid and that the 'image' field is present in the form errors.
        Parameters:
        - self: The current instance of the test class.
        """
        form_data = {'image': 'invalid_file.txt'}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors

    def test_empty_form_submission(self):
        """
        Test the behavior of submitting an empty form.
        This function tests the behavior of submitting an empty form by creating an empty
        dictionary `form_data` and passing it as the data and files parameters to the
        `PostImageForm` object. The function then asserts that the form is not valid and
        that the 'image' field is present in the form errors.
        Parameters:
        - self: The instance of the test class.
        """
        form_data = {}
        form = PostImageForm(data=form_data, files=form_data)
        assert not form.is_valid()
        assert 'image' in form.errors


class TestPostForm:
    def test_form_save(self, mocker):
        """
        Test the `save` method of the `PostForm` class.
        Parameters:
            mocker (mocker.Mock): The mocker object for patching the `save` method.
        """
        mock_save = mocker.patch.object(PostForm, 'save')
        form_data = {'caption': 'Test caption'}
        form = PostForm(data=form_data)
        assert form.is_valid()
        form.save()
        mock_save.assert_called_once()

    def test_form_submission_with_csrf_token(self, client):
        """
        Test the form submission with a CSRF token.
        This function takes two parameters:
        - `self`: an instance of the current class.
        - `client`: an instance of the client to make the POST request.
        The function performs a POST request to the '/submit-form/' URL with the following form data:
        - `caption`: a test caption.
        - `csrfmiddlewaretoken`: a CSRF token.
        The function then asserts that the response status code is 200.
        """
        response = client.post('/submit-form/', {'caption': 'Test caption', 'csrfmiddlewaretoken': 'token'})
        assert response.status_code == 200

    def test_form_validation(self):
        """
        Test the form validation functionality.
        """
        form_data = {'caption': ''}
        form = PostForm(data=form_data)
        assert not form.is_valid()

    def test_empty_caption_field(self):
        """
        Test the behavior of the function when the 'caption' field is empty.
        Args:
            self: The current instance of the test case.
        """
        form_data = {'caption': ''}
        form = PostForm(data=form_data)
        assert 'caption' in form.errors

    def test_caption_field_max_length(self):
        """
        Test case to verify that the 'caption' field in the PostForm has a maximum length of 200 characters.
        This test function creates a dictionary 'form_data' with a 'caption' key that has
        a value of a string with 201 characters.
        It then creates an instance of the PostForm class using the 'form_data' dictionary as input data.
        The function asserts that the 'caption' field is present in the form's errors attribute,
        indicating that the form validation has failed due to the length
        of the caption exceeding the maximum allowed length.
        This test case is part of the test suite for the PostForm class.
        Parameters:
        - self: The instance of the test class.
        """
        form_data = {'caption': 'a' * 201}
        form = PostForm(data=form_data)
        assert 'caption' in form.errors

    def test_invalid_data_type_for_caption_field(self):
        """
        Test case to check for invalid data type in the caption field.
        This function creates a form_data dictionary with a caption field that has a value of 123,
        which is an invalid data type.
        Then, a PostForm object is created using the form_data dictionary.
        Finally, it asserts that the 'caption' field is present in the form errors.
        This test case is designed to ensure that the form correctly handles invalid data types in the caption field.
        Parameters:
            self (TestCase): The current test case object.
        """
        form_data = {'caption': 123}
        form = PostForm(data=form_data)
        assert 'caption' in form.errors


class TestPostTagForm:
    def test_valid_tag_submission(self, mocker):
        """
        Test the submission of a valid tag in the form.
        Parameters:
        - mocker: A mock object that allows for easy testing of the function.
        Description:
        - This function tests the submission of a valid tag in the form. It creates a
          mock tag object and sets up the necessary patches and form data. It then
          validates and saves the form, and asserts that the mock tag object's
          `create` method is called with the correct parameters.
        """
        mock_tag = mocker.Mock()
        mock_tag.objects.create.return_value = mock_tag
        mocker.patch('app.forms.Tag', mock_tag)
        form_data = {'name': 'test tag'}
        form = PostTagForm(data=form_data)
        form.is_valid()
        form.save()
        mock_tag.objects.create.assert_called_once_with(name='test tag')

    def test_existing_tag_submission(self, mocker):
        """
        Test the submission of an existing tag.
        :param mocker: A mocker object for mocking dependencies.
        """
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
        """
        Test the submission of an empty tag in the form.
        This function creates a dictionary `form_data` with a single key 'name' and an empty string as its value.
        It then creates an instance of the `PostTagForm` class, passing `form_data` as the data parameter.
        The function asserts that the form is not valid and that 'name' is present in the form errors.
        Parameters:
        - self: The instance of the test class.
        """
        form_data = {'name': ''}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_long_tag_submission(self):
        """
        Test case to verify that the function handles long tag submissions correctly.
        Parameters:
            self (TestCase): The current test case object.
        """
        form_data = {'name': 'a' * 51}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_form_validation(self):
        """
        Test the form validation for the given form.
        This function creates a form with invalid data and asserts that the form is not valid.
        It then checks if the expected error message is present in the form errors.
        Parameters:
            self (object): The current instance of the test class.
        """
        form_data = {'name': 'invalid tag name'}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_special_char_tag_submission(self):
        """
        Test the submission of a special character tag.
        """
        form_data = {'name': 'test tag!@#$'}
        form = PostTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors


class TestCommentTagForm:
    def test_valid_tag_submission(self):
        """
        Test the submission of a valid tag.
        This function tests the submission of a valid tag by creating a form
        object with the required data. It then asserts that the form is valid
        and saves the form to create a new tag object. Finally, it asserts that
        the name of the created tag object is equal to the expected value.
        Parameters:
        - self: The instance of the test class.
        """
        form_data = {'name': 'test_tag'}
        form = CommentTagForm(data=form_data)
        assert form.is_valid()
        tag = form.save()
        assert tag.name == 'test_tag'

    def test_existing_tag_submission(self):
        """
        Test the submission of an existing tag.
        This function tests the functionality of submitting an existing tag through the
        CommentTagForm. It creates a new Tag object with the name 'existing_tag'. Then,
        it creates a form with the data {'name': 'existing_tag'}. The function asserts
        that the form is valid. Next, it saves the form and assigns the returned tag to
        the 'tag' variable. Finally, it asserts that the 'tag' variable is equal to the
        Tag object retrieved from the database with the name 'existing_tag'.
        Parameters:
        - self: The instance of the test case class.
        """
        tag = Tag.objects.create(name='existing_tag')
        form_data = {'name': 'existing_tag'}
        form = CommentTagForm(data=form_data)
        assert form.is_valid()
        tag = form.save()
        assert tag == Tag.objects.get(name='existing_tag')

    def test_empty_tag_submission(self):
        """
        Test the submission of an empty tag in the CommentTagForm.
        This function creates a form_data dictionary with an empty 'name' field.
        It then creates a CommentTagForm instance using the form_data.
        The function asserts that the form is not valid and that 'name' is in the form errors.
        Parameters:
        - self: the instance of the test class.
        """
        form_data = {'name': ''}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_max_length_tag_submission(self):
        """
        Test the maximum length of a tag submission in the CommentTagForm.
        This function creates a form data dictionary with a 'name' key that contains
        a string of 51 characters. It then creates a CommentTagForm object using the
        form data. The function asserts that the form is not valid and that the 'name'
        key is in the form's errors dictionary.
        Parameters:
            self (TestCase): The current test case.
        """
        form_data = {'name': 'a' * 51}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_validation_error_message(self):
        """
        Test the validation error message when the 'name' field is empty.
        This function creates a form with the 'name' field set to an empty string.
        It then checks if the form is valid. Since the 'name' field is required,
        the form should not be valid. Finally, it asserts that the error message
        'This field is required.' is present in the form's errors for the 'name' field.
        """
        form_data = {'name': ''}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'This field is required.' in form.errors['name']

    def test_invalid_character_tag_submission(self):
        """
        Test case for invalid character tag submission.
        This function tests the behavior of the CommentTagForm when an invalid character
         is included in the 'name' field of the form data.
        It verifies that the form is not valid and that the 'name' field is included in the form errors.
        Parameters:
        - self: The instance of the test case.
        """
        form_data = {'name': 'test@tag'}
        form = CommentTagForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors


class TestCommentForm:
    def test_form_creation(self):
        """
        Test the creation of a form.
        This function creates an instance of the CommentForm class and asserts that its initial
        validation state is False. This test is used to verify that the form is correctly
        initialized and that its validation behavior is as expected.
        Parameters:
            self (TestCase): The current test case.
        """
        form = CommentForm()
        assert form.is_valid() is False

    def test_form_display(self):
        """
        Test the display of the form.
        This function creates an instance of the CommentForm class
         and asserts that the 'content' field is present in the form's HTML representation.
        Parameters:
            self (object): The object instance.
        """
        form = CommentForm()
        assert 'content' in form.as_p()

    def test_empty_content_field(self):
        """
        Test the case when the content field of the CommentForm is empty.
        This function creates an instance of the CommentForm class with the 'content'
        field set to an empty string. It then asserts that the form is not valid.
        Parameters:
        - self: The instance of the test class.
        """
        form = CommentForm(data={'content': ''})
        assert form.is_valid() is False

    def test_content_field_exceeds_max_length(self):
        """
        Test if the content field exceeds the maximum length.
        This function creates a test case where the content field is set to a string
        of length 1001 characters. It then creates a CommentForm object with the
        'content' field set to the generated string. The function asserts that
        form.is_valid() returns False.
        Parameters:
            self: The instance of the test class.
        """
        content = 'a' * 1001
        form = CommentForm(data={'content': content})
        assert form.is_valid() is False

    def test_form_validation_errors(self):
        """
        Test the form validation errors for the CommentForm.
        This function creates an instance of the CommentForm with a blank 'content' field.
        It then asserts that the error message 'This field is required.' is present in the form's 'content' errors.
        Parameters:
            self (TestClass): The instance of the test class.
        """
        form = CommentForm(data={'content': ''})
        assert 'This field is required.' in form.errors['content']

    def test_form_data_saved_correctly(self):
        """
        Test if the form data is being saved correctly.
        This function creates a test comment form with the given content, and then saves it.
        It asserts that the content of the saved comment is equal to the given content.
        Args:
            self: The instance of the test case.
        """
        content = 'This is a test comment.'
        form = CommentForm(data={'content': content})
        comment = form.save()
        assert comment.content == content
