Personalisation Module - Usage Guide for Administrators
=======================================================
To set a personalised content we must first declare segments in Wagtail's admin site.

.. contents::

Creating Segments
~~~~~~~~~~~~~~~~~
#. Please choose *Segments* section from the sidebar menu.
#. You should be able to see all already declared segments if any. Please click on the link to add a new one if there's none.

   .. image:: http://i.imgur.com/xw3uglD.png

#. Please fill the segment creation form.

   Name
       Please set a name for your segment. It won't be visible by the users on the front-end.

   Persistent
       This option is there to make sure that once users are assigned to a segment (they match a rule), they'll stay there even if they don't match the personalisation rules any more. Please be advised that it is assigned to a user session so if user logs out or logs in somewhere else, those segments will not be linked to the user any more.

   Match any
       This option makes that only one rule of the segment has to be fulfilled in order to activate the segment. If the box is unchecked, all the rules have to be met.

#. Below that you can see a list of rules assigned to a particular segment. Please add one (please see `personalisation rules <#personalisation-rules>`_ for details).
#. Save the segments. Now you can can assign content to segments (please see `assigning content to segments <#assign-content-to-segments>`_ for details).

Assign Content to Segments
~~~~~~~~~~~~~~~~~~~~~~~~~~
Currently GEM only has only one type of personalised content - surveys.

Surveys
*******
If you want to personalise existing survey, it has to be of type *Personalisable survey*. If it is not, it won't be possible and you must add a new survey of that type.

#. To add a personalised survey go to a *Explorer* (or *Pages*) → *Site* → *Surveys*.
#. When you get to the *Surveys*, click on *Add Child Page*.

   .. image:: https://i.imgur.com/3Bp5nnX.png

#. Please choose *Personalisable survey* out of the list.

   .. image:: https://i.imgur.com/W8qOmD3.png

#. Now you should be able to fill out survey as you were filling it for the default Molo/GEM surveys with a small difference.

   * You can choose a segment for the survey at the top of the page.

     * Leaving it empty will show survey to any user.
     * Selecting an option will show survey only to users that are part of the selected segment.

   * When you add a new question (form field) you can select its segment. It means that the question will be only shown to people who are part of that segment. Leaving it empty will show the field to everyone.

     .. image:: https://i.imgur.com/Rhfbo0I.png

     * It is pointless to set this option if you have set the segment for the survey already.

Personalisation Rules
~~~~~~~~~~~~~~~~~~~~~
Some of the rules can be read about in `the wagtail-personalisation documentation <https://wagtail-personalisation.readthedocs.io/en/latest/default_rules.html>`_.

GEM also has a set of the following custom rules.

Survey Submission Rule
**********************
Survey submission rule lets you segment content based on survey submissions associated with user accounts.

Options to set are:

Survey
    Please choose which survey we want to use answers from.

Field name
    What field from the survey we want to use. Please use form fields in the lower-case format and with spaces replaced with dashes. It will display the possible choices in the error messages.

Operator
    What sort of comparison we want to perform.

    Contains
        When we want to match only a small portion of the text. Won't work for choice fields.

    Equals
        Matches content exactly.

Expected response
    What response do we expect. If it is not a text field, please use error messages to guide you what content is expected.

Group Membership Rule
*********************
Only choose what group membership user should have in order to have this segment activated. You might want to read about `creating groups with CSV files <#creating-groups-with-csv-files>`_.

Comment Data Rule
*****************
There are two fields to fill in. It will search through all the comments on any content type.

Operator
    What sort of comparison is performed.

    Equals
        When we want to match the comment data exactly (case insensitive).

    Contains
        When we want to match the comment data partially (case insensitive).

Expected content
    What content do we expect in the comment.

Profile Data Rule
*****************
Profile data Rule lets you set data based on user profile data.

Field
    Choose which profile field we want to use.

Operator
    There are three main groups of operators.

    Comparison operators
        E.g. equal, not equal, less than, greater than. They will work on strings, dates, numbers, etc.

    Age operators
        E.g. of age, younger than, older than, that are used when comparing an age based on date.

    Regex (*regular expression*)
        Please do not use until you know what you are doing. It enables to define regular expression rules to enable different variations of strings and use of wild cards. Please adhere to `regular expressions documentation <https://docs.python.org/3.7/howto/regex.html#regex-howto>`_ for more information. When creating regular expressions you might want to test them using online tools such as https://regex101.com/ and selecting *Python* version.

Value
    Expected value, please adhere to guidance provided in errors when setting data so you use the right format.

Creating Groups with CSV Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you have a CSV file that has **user names** in the **first column** you can use it to create a group made out of those users. Such file can be obtained when exporting users to CSV file via *Users Export* in the admin site.

In order to create group with a CSV file please go into *Settings* and then select *CSV group creation*. There you can specify group name and upload CSV file. This system uses automatic CSV separators detection so it might occasionally get something wrong. You can try to use different separators to make it work.
