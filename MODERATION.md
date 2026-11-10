# T7: Moderator Login and Approval Queue

## Setup

After installing dependencies and configuring the database, run:

    python manage.py migrate
    python manage.py setup_moderators

The setup command creates or updates the Moderators group with
view and change permissions for Posts. It can be run repeatedly.

## Moderator accounts

Using a superuser account in Django admin:

1. Create a user with their own password.
2. Enable Active and Staff status.
3. Leave Superuser status disabled.
4. Assign the user to the Moderators group.
5. Leave individual user permissions empty.

## Reviewing posts

Log in at /admin/ and open Posts.
Filter by Pending Review and open posts to read their details.
Select pending posts and choose the approve or reject action.

Bulk actions change only pending posts.
Success messages report the number changed.
If nothing changes, a warning appears.
Post history records the moderator and action.

The change permission also allows editing post fields and status
through the individual post form.

## Manual validation

Passed locally:
- Login, logout, and incorrect-password handling.
- Nonstaff users blocked from admin.
- Staff without post permissions blocked from Posts.
- Moderator blocked from user management.
- Post details and status filters.
- Individual and bulk approval/rejection.
- Mixed selections change only pending posts.
- Warning when no posts change.
- Status persistence after logging out and back in.
- Moderator actions recorded in post history.

## Public-page integration

Public post lists and detail views must restrict results to
status="approved". This remains to be implemented and tested
when public pages are connected.
