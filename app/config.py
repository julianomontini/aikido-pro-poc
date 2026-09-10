"""App configuration.

TODO (DAST-2): decide how DEBUG / detailed error pages behave once this app
is deployed (Render), and how SECRET_KEY is set there. See
REQUIREMENTS.md#DAST-2 before filling this in -- the choice you make here,
and later un-make as a fix, is the exercise.
"""
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")

    # TODO (DAST-2): set this appropriately (and differently) for local dev
    # vs. the deployed environment. Ships as False/unset -- secure by
    # default -- until you deliberately introduce the misconfiguration
    # described in REQUIREMENTS.md#DAST-2.
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # TODO (SEC-1): see REQUIREMENTS.md#SEC-1 -- add one obviously-fake
    # credential-shaped constant somewhere plausible (here is a fine place)
    # to exercise secrets scanning, then remove it again once it's been
    # flagged and confirm the finding clears.
