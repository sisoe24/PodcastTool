=========
Changelog
=========

Version 2.1.0
==============

[New Feature] :

- New GUI design, smaller and more compact to save on screen real estate.
- Automatic update checking.
- Info app status messages in the terminal window.
- Ability to select multiple podcast files at once instead of only one.
  This is for when, if the algorithm doesnt catch all the podcasts, the user
  can fallback manually.
- App launcher can now be saved on the dock. For more info check new folder
  **make_shortcut**.

[other] :

- The match podcast algorithm now checks for creation date instead of
  modfication date. Should be more accurate.
- Audio options are now in the new Audio window of the app.
- If podcast folder is not present on the server, app will now ask user for
  confirmation in order to create it instead of doing it automatically with
  no notice.
- New fatal error and simple error logs if app fails to start for some reason.
- Temporary included updated ``pstats.py`` and re enable profiling.
- Temporary disabled the ability to select archive html from the app. If needed
  used folder instead.

Version 2.0.1
==============

[New Feature] :

- Added minor visual cue next to the progress bar for status script.

[other] :

- Reduced the podcast splitting process from 1 min to less than 5 seconds

[bug fix] :

- App crashing because ``SortKey`` class is missing from pstats.py
  (Python3.7 Ubuntu17.10). Temporary disabled profiling function.

Version 2.0.0
==============

[New Feature] :

- Complety redesigned workflow with a new GUI window.
- Error checking for wrong code names files and folders.
- Automatic highlight of the errors with suggestion based on name approximation
- Ability to recognize podcast parts even if contains error.
- Automatic creation of podcast folder in server if missing.

