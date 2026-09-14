# Code Review — 2026-09-12

Findings from a full pass over the codebase (models, views, forms, templates, settings).

## Bugs (confirmed — reproduce a 500 error)

1. ~~**Property list filter crashes on bad input**~~ — **FIXED (2026-09-12)**.
   `listings/views.py`. `min_price`/`max_price` from the query string went straight into
   `price__gte=`/`price__lte=` with no validation, and a non-numeric value crashed the page
   (`curl "/properties/?min_price=abc"` → 500). Now parsed with a `_parse_price` helper that
   returns `None` on invalid input instead of raising, so the filter is just skipped.
   Re-verified: `?min_price=abc` and `?max_price=xyz` now return 200.

2. ~~**Contact page crashes on bad `?property=` param**~~ — **FIXED (2026-09-12)**.
   `pages/views.py`. `Property.objects.filter(pk=property_id)` with a non-numeric
   `property_id` threw an unhandled `ValueError` → 500. Now wrapped in `int(property_id)`
   inside a `try/except (TypeError, ValueError)`, falling back to no selected property.
   Re-verified: `curl "/contact/?property=abc"` now returns 200.

## Other issues worth knowing about

3. ~~**Contact form email failures are silently swallowed**~~ — **FIXED (2026-09-12)**.
   `pages/views.py` (`except Exception: pass`). If SES/SMTP is misconfigured (e.g. bad AWS
   creds), the user always saw "message received" but the lead never arrived and there was no
   log to notice it was broken. Now logs the exception via `logger.exception(...)` (module
   logger `pages.views`) instead of silently discarding it.

4. ~~**`DEBUG` defaults to `True`**~~ — **FIXED (2026-09-12)**. `realestate/settings.py`. If
   `DJANGO_DEBUG` was ever unset in a deployed environment, it failed open into debug mode,
   leaking stack traces/settings to visitors. Code default flipped to `False`; local dev now
   opts in explicitly via `DJANGO_DEBUG=True` in `.env` (uncommented), so nothing changes for
   this machine but a fresh/deployed environment without that `.env` line now fails safe.

5. ~~**No safeguard against multiple "primary" images per property**~~ — **FIXED (2026-09-12)**.
   `listings/models.py`. Nothing stopped an admin marking 2+ images `is_primary=True`, so
   `primary_image` picked an arbitrary one. `PropertyImage.save()` now unsets `is_primary` on
   every other image for the same property whenever one is saved as primary, so at most one
   can be primary at a time.

6. ~~**Zero test coverage**~~ — **FIXED (2026-09-12)**. Added real tests in `listings/tests.py`
   and `pages/tests.py` covering: the two previously-crashing GET-param bugs (now regression
   tests), price filtering, unique slug generation, the single-primary-image safeguard, and
   contact form submission + notification email. `manage.py test` → 7 passed.

7. **Uploaded media lives on local disk** — `realestate/settings.py:148-149`. Fine for a single
   dev box, but if this ever deploys to something like Heroku/containers with ephemeral
   filesystems, every uploaded property photo disappears on redeploy. `boto3` is already a
   dependency for SES — worth routing `MEDIA` through S3 too before going live.

## Product/UX ideas (no bug, just opportunities)

8. ~~**No keyword/text search on the properties page**~~ — **FIXED (2026-09-12)**. Added a `q`
   search box on `/properties/` (`listings/views.py`) matching title, description and address
   via `icontains`, combined with the existing structured filters.

9. ~~**City filter is free-text with no suggestions**~~ — **FIXED (2026-09-12)**. The city input
   now has an HTML `<datalist>` populated from the distinct cities of available listings, so
   typing still works but existing cities autocomplete — no dropdown lock-in, no schema change.

10. ~~**No sitemap.xml/robots.txt/meta descriptions**~~ — **FIXED (2026-09-12)**.
    - `realestate/sitemaps.py` + `/sitemap.xml` (via `django.contrib.sitemaps`): lists all
      available properties (with `lastmod`) plus the home/contact/listing pages.
    - `/robots.txt`: allows all crawling and points at the sitemap.
    - Added a `{% block meta_description %}` in `base.html`, overridden per-page (home,
      property list, property detail — built from title/city/beds/baths/description, contact).

11. ~~**No spam protection on the contact form**~~ — **FIXED (2026-09-12)**.
    - Honeypot field (`pages/forms.py` `website` field, visually hidden via `.hp-field`/`.hp-wrap`
      CSS): if a bot fills it, the submission is rejected via `clean_website()` with no visible
      error and nothing saved/sent.
    - Per-IP rate limit (`pages/views.py`): max 5 submissions/hour per `REMOTE_ADDR`, tracked via
      Django's cache framework. Note: with the default `LocMemCache` this resets on process
      restart and isn't shared across multiple worker processes — fine for now, but revisit
      (e.g. a shared Redis cache) if this ever runs behind multiple app workers.

12. ~~**Property images aren't resized/thumbnailed on upload**~~ — **FIXED (2026-09-12)**.
    `listings/models.py` `PropertyImage.save()` now downscales any newly uploaded image wider
    or taller than 1600px (Lanczos resample, JPEG quality 85, EXIF orientation corrected) before
    it's written to storage. Only triggers on new/changed uploads (checked via the file's
    `_committed` flag), not on every unrelated save, and fails open (keeps the original) if
    Pillow can't process a given file.

All items verified: full test suite passes (`manage.py test` → 12 tests), plus manual checks of
`/sitemap.xml`, `/robots.txt`, and the search/city filters against the running dev server.
