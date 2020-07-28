from django.core.management.base import BaseCommand, CommandError
from django_comments.models import Comment
from molo.profiles.models import UserProfile, SecurityAnswer
from molo.forms.models import MoloFormSubmission
from wagtail.core.models import Site


class Command(BaseCommand):
    help = ('Accepts site ids and removes associated users and '
            'user-generated content')
    commit = False
    comment_count = 0
    submissions_count = 0
    sec_answer_count = 0

    def add_arguments(self, parser):
        parser.add_argument('site_ids', nargs='+', type=int)

        parser.add_argument(
            '--commit',
            action='store_true',
            help='Commit the changes rather than just showing them.',
        )

    def handle(self, *args, **options):
        if options['commit']:
            self.commit = True

        for site_id in options['site_ids']:
            try:
                site = Site.objects.get(pk=site_id)
            except Site.DoesNotExist:
                raise CommandError('Site "%s" does not exist' % site_id)

            profiles = self.get_user_profiles(site)
            self.stdout.write(
                'Found %s profiles for site %s' % (profiles.count(), site_id))
            staff_count = 0

            for profile in profiles.iterator():
                # Don't delete anything for staff members
                if profile.user.is_staff or profile.user.is_superuser:
                    staff_count += 1
                    continue

                self.remove_comments(profile.user)
                self.remove_form_submissions(profile.user)
                self.remove_security_question_answers(profile)

                if self.commit:
                    user = profile.user
                    profile.delete()
                    user.delete()

            self.stdout.write('Found %s staff profiles' % staff_count)
            self.stdout.write('Found %s comments' % self.comment_count)
            self.stdout.write(
                'Found %s form submissions' % self.submissions_count)
            self.stdout.write(
                'Found %s security question answers' % self.sec_answer_count)

            if self.commit:
                self.stdout.write('All (non-staff) content deleted.')

    def get_user_profiles(self, site):
        profiles = UserProfile.objects.filter(site=site)
        return profiles

    def remove_comments(self, user):
        comments = Comment.objects.filter(user=user)
        self.comment_count += comments.count()

        if self.commit:
            comments.delete()

    def remove_form_submissions(self, user):
        submissions = MoloFormSubmission.objects.filter(user=user)
        self.submissions_count += submissions.count()

        if self.commit:
            submissions.delete()

    def remove_security_question_answers(self, profile):
        answers = SecurityAnswer.objects.filter(user=profile)
        self.sec_answer_count += answers.count()

        if self.commit:
            answers.delete()
