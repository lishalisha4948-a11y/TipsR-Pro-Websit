IMPORTANT FINAL FIX
The Google Apps Script now maps values by the exact column header name.
This prevents:
- Tell us about your work from appearing in Budget
- Budget appearing in the wrong column
- Reference File appearing as a stray/new column

Use these headers in row 1:
Date & Time | Name | Mobile | Email | What do you need? | Tell us about your work | Budget | Reference File | Reference File URL | AI Summary | Status

After replacing google_apps_script.gs:
Deploy > Manage deployments > Edit > New version > Deploy.

Do NOT create a second Web App deployment if you want to keep the same URL.
