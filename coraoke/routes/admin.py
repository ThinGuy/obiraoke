"""Admin routes for system control and authentication."""

import datetime
import logging
import os
import sys
import threading
import time

import flask_babel
from flask import flash, jsonify, make_response, redirect, url_for
from flask_smorest import Blueprint
from marshmallow import Schema, fields

from coraoke.karaoke import Karaoke
from coraoke.lib.current_app import get_admin_password, get_karaoke_instance, is_admin
from coraoke.lib.youtube_dl import get_youtubedl_version, upgrade_youtubedl

_ = flask_babel.gettext

admin_bp = Blueprint("admin", __name__)


class AuthForm(Schema):
    admin_password = fields.String(load_default="", metadata={"description": "Admin password"})
    next = fields.String(
        load_default="/", metadata={"description": "URL to redirect to after login"}
    )


def delayed_halt(cmd: int, k: Karaoke):
    time.sleep(1.5)
    k.queue_manager.queue_clear()
    k.stop()
    if cmd == 0:
        sys.exit()
    if cmd == 1:
        if os.environ.get("SNAP"):
            logging.warning("shutdown is unavailable in snap confinement")
            return
        os.system("shutdown now")
    if cmd == 2:
        if os.environ.get("SNAP"):
            logging.warning("reboot is unavailable in snap confinement")
            return
        os.system("reboot")


@admin_bp.route("/update_ytdl")
def update_ytdl():
    """Update yt-dlp to the latest version."""
    if os.environ.get("SNAP"):
        return jsonify({"error": "yt-dlp updates are handled by snap refresh"}), 503

    k = get_karaoke_instance()

    def update_youtube_dl():
        time.sleep(3)
        k.youtubedl_version = upgrade_youtubedl()

    if is_admin():
        flash(
            # MSG: Message shown after starting the youtube-dl update.
            _("Updating youtube-dl! Should take a minute or two... "),
            "is-warning",
        )
        th = threading.Thread(target=update_youtube_dl)
        th.start()
    else:
        # MSG: Message shown after trying to update youtube-dl without admin permissions.
        flash(_("You don't have permission to update youtube-dl"), "is-danger")
    return redirect(url_for("info.info"))


@admin_bp.route("/library_stats")
def library_stats():
    """Return song count for the admin dashboard."""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    k = get_karaoke_instance()
    return jsonify({"song_count": len(k.song_manager.songs)})


@admin_bp.route("/sync_library")
def sync_library():
    """Trigger a background library scan."""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    k = get_karaoke_instance()
    started = k.sync_library()
    if started:
        return jsonify({"status": "started"})
    return jsonify({"status": "already_syncing"})


@admin_bp.route("/quit")
def quit():
    """Exit the PiKaraoke application."""
    k = get_karaoke_instance()
    if is_admin():
        # MSG: Message shown after quitting pikaraoke.
        msg = _("Exiting coraoke now!")
        flash(msg, "is-danger")
        k.send_notification(msg, "danger")
        th = threading.Thread(target=delayed_halt, args=[0, k])
        th.start()
    else:
        # MSG: Message shown after trying to quit pikaraoke without admin permissions.
        flash(_("You don't have permission to quit"), "is-danger")
    return redirect(url_for("home.home"))


@admin_bp.route("/shutdown")
def shutdown():
    """Shut down the host system."""
    if os.environ.get("SNAP"):
        return jsonify(error="shutdown is unavailable in snap confinement"), 503
    k = get_karaoke_instance()
    if is_admin():
        # MSG: Message shown after shutting down the system.
        msg = _("Shutting down system now!")
        flash(msg, "is-danger")
        k.send_notification(msg, "danger")
        th = threading.Thread(target=delayed_halt, args=[1, k])
        th.start()
    else:
        # MSG: Message shown after trying to shut down the system without admin permissions.
        flash(_("You don't have permission to shut down"), "is-danger")
    return redirect(url_for("home.home"))


@admin_bp.route("/reboot")
def reboot():
    """Reboot the host system."""
    if os.environ.get("SNAP"):
        return jsonify(error="reboot is unavailable in snap confinement"), 503
    k = get_karaoke_instance()
    if is_admin():
        # MSG: Message shown after rebooting the system.
        msg = _("Rebooting system now!")
        flash(msg, "is-danger")
        k.send_notification(msg, "danger")
        th = threading.Thread(target=delayed_halt, args=[2, k])
        th.start()
    else:
        # MSG: Message shown after trying to reboot the system without admin permissions.
        flash(_("You don't have permission to Reboot"), "is-danger")
    return redirect(url_for("home.home"))


@admin_bp.route("/auth", methods=["POST"])
@admin_bp.arguments(AuthForm, location="form")
def auth(form):
    """Authenticate as admin."""
    admin_password = get_admin_password()
    p = form["admin_password"]
    next_url = form["next"]

    # Validate next_url to prevent open redirect vulnerabilities
    if not next_url.startswith("/"):
        next_url = "/"

    if p == admin_password:
        resp = make_response(redirect(next_url))
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=90)
        resp.set_cookie("admin", admin_password, expires=expire_date)
        # MSG: Message shown after logging in as admin successfully
        flash(_("Admin mode granted!"), "is-success")
    else:
        resp = make_response(redirect(url_for("admin.login", next=next_url)))
        # MSG: Message shown after failing to login as admin
        flash(_("Incorrect admin password!"), "is-danger")
    return resp


@admin_bp.route("/logout")
def logout():
    """Log out of admin mode."""
    resp = make_response(redirect(url_for("info.info")))
    resp.set_cookie("admin", "")
    # MSG: Message shown after logging out as admin successfully
    flash(_("Logged out of admin mode!"), "is-success")
    return resp
