from whitenoise.storage import CompressedManifestStaticFilesStorage


class NonStrictManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Manifest storage that doesn't raise when an entry is missing.

    Django's default ManifestStaticFilesStorage (and WhiteNoise's compressed
    variant) raise a ValueError when a file referenced in templates is not
    present in the manifest. That can cause the app to fail at runtime if
    collectstatic hasn't run yet. This subclass sets ``manifest_strict`` to
    False so the storage falls back to the unhashed original filename when a
    manifest entry is missing.
    """

    manifest_strict = False
