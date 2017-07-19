import csv

from django import forms
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import Group


class CSVGroupCreationForm(forms.ModelForm):
    """Create group with initial users supplied via CSV file."""
    csv_file = forms.FileField(
        label=_('CSV file'),
        help_text=_('Please attach a CSV file with the first column containing'
                    ' usernames of users that you want to be added to '
                    'this group.'))

    class Meta:
        model = Group
        fields = ("name",)

    def clean_csv_file(self):
        """Read CSV file and save the users to self.initial_users."""
        csv_file = self.cleaned_data['csv_file']

        # Sniff CSV file
        try:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
        except csv.Error:
            raise forms.ValidationError(_('Uploaded file does not appear to be'
                                          ' in CSV format.'))

        csv_file.seek(0)

        # Instantiate CSV Reader
        csv_file_reader = csv.reader(csv_file, dialect)

        # Check whether file has a header
        try:
            if csv.Sniffer().has_header(csv_file.read(1024)):
                next(csv_file_reader)  # Skip the header
        except csv.Error:
            raise forms.ValidationError(_('Uploaded file does not appear to be'
                                          ' in CSV format.'))

        # Gather all usernames from the CSV file.
        usernames = set()
        for row in csv_file_reader:
            try:
                username = row[0]
            except IndexError:
                # Skip empty row
                continue
            else:
                # Skip empty username field
                if username:
                    usernames.add(username)

        if not usernames:
            raise forms.ValidationError(_('Your CSV file does not appear to '
                                          'contain any usernames.'))

        queryset = get_user_model().objects.filter(username__in=usernames)
        difference = usernames - set(queryset.values_list('username',
                                                          flat=True))
        if difference:
            raise forms.ValidationError(_('Please make sure your file contains'
                                          ' valid data. '
                                          'Those usernames do not exist: '
                                          '"%s".') % '", "'.join(difference))

        # Store users temporarily as a property so we can
        # add them when user calls save() on the form.
        self.__initial_users = queryset

    def save(self, *args, **kwargs):
        """Save the group instance and add initial users to it."""
        # Save the group instance
        group = super(CSVGroupCreationForm, self).save(*args, **kwargs)

        # Add users to the group
        group.user_set.add(*self.__initial_users)
