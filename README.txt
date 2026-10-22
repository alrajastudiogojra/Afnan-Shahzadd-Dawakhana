AFNAN SHAHZAD DAWAKHANA - OFFLINE WINDOWS SOFTWARE
=================================================

Features
--------
- English Windows desktop interface
- Patient name, mobile, address, disease/problem
- Automatically assigned token numbers (001, 002, 003...)
- Token numbering starts again at 001 for each Sunday/week
- Local patient database; search by patient name or mobile number
- Print a new slip or reprint a selected saved patient's slip
- 80mm / approximately 3-inch thermal receipt layout

Important
---------
This is an offline starter version. Patient data is stored locally in:
%LOCALAPPDATA%\AfnanDawakhana\afnan_dawakhana.db

Back up that folder regularly. If Windows is reinstalled or the computer is replaced,
copy the database file to the new computer and restore it to the same folder.

Run from Python
---------------
1. Install Python 3 for Windows from python.org. During setup, tick "Add Python to PATH".
2. Extract this folder.
3. Double-click run_app.bat.

Build a standalone EXE
----------------------
1. Open Command Prompt in this folder.
2. Run: build_exe.bat
3. The EXE will be created in the dist folder.

Printing
--------
The app opens a local HTML slip in your default browser and opens the print dialog.
Choose your 80mm / 3-inch thermal printer. Set paper width to 80mm (or the printer's
closest supported size), margins to minimum/default, and turn off headers and footers
in the browser print dialog if shown. Printer driver options vary by model.

Token behavior
--------------
The token number is based on the most recent Sunday date. It is 001 again on a new
Sunday and increments for each patient saved during that Sunday-based week. This is
designed for Sunday clinic sessions.

Clinic details configured in this version:
Afnan Shahzad Dawakhana
Near Mand Barfi Shop, Tehsil Office Road, Gojra
Every Sunday: 09:00 AM - 04:00 PM
For more info: 0333-7676293
