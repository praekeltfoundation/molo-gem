from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin import messages
from wagtail.wagtailadmin.utils import permission_required

from .forms import CSVGroupCreationForm


@permission_required('auth.add_group')
def create(request):
    group = Group()
    if request.method == 'POST':
        form = CSVGroupCreationForm(
            request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                _("Group '{0}' created. "
                  "Imported {1} user(s).").format(
                    group, group.user_set.count()),
                buttons=[
                    messages.button(reverse('wagtailusers_groups:edit',
                                            args=(group.id,)), _('Edit'))
                ]
            )
            return redirect('wagtailusers_groups:index')

        messages.error(request, _(
            "The group could not be created due to errors."))
    else:
        form = CSVGroupCreationForm(instance=group)

    return render(request, 'csv_group_creation/create.html', {
        'form': form
    })
