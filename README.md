# Hippo Product Journal — clean rebuild

A lightweight Flask + SQLite product release journal with English, Russian and Uzbek interface language switching.

## Windows quick start
1. Install Python 3.10+ and enable **Add Python to PATH**.
2. Extract this folder somewhere local.
3. Double-click `run.bat` (internet is needed for first-time installation of Flask).
4. The browser opens at http://127.0.0.1:5000.
5. On first run, create the single administrator account in the setup screen. Use a unique password of at least 12 characters.
6. Sign in; open **Admin studio** to create, edit, publish or archive release notes.

## Access model
- Public pages are read-only and show only published releases.
- Only one administrator account is supported. There is no public registration and no user-management screen.
- Passwords are stored as Werkzeug password hashes, never as plaintext.
- Admin POST actions use CSRF tokens; the login has basic throttling.
- Database is local in `hippo_journal.db`.

## Language
Choose EN / RU / UZ in the top-right language selector. The interface strings and publishing guide are translated. Release content is authored by the admin; write it in the languages you need.

## Important
This is a local development build, not yet a production deployment. For public internet hosting, set a persistent random `SECRET_KEY`, use HTTPS, configure a production WSGI server and back up the SQLite database. Do not expose the development server directly to the internet.


## Separate access
- Public release journal: `/`
- Private admin sign-in: `/admin` (redirects to login when signed out)
- Admin workspace: `/studio` (requires the administrator session)
- No admin link is shown to public visitors.
- Only the single administrator created during setup can create, edit, publish, archive, or delete releases.
- Language preference EN/RU/UZ is stored in the session. The admin interface labels are localized as well.
