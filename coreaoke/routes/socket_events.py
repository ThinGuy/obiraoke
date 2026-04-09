"""Socket.IO event handlers for PiKaraoke."""

import logging
import threading

from flask import Flask, request

from coreaoke.lib.current_app import get_karaoke_instance

# Track connected splash screen clients and the elected master
# Maps session ID to channel name
splash_connections: dict[str, str] = {}
master_splash_id: str | None = None

# Grace period timer: delays end_song when master disconnects,
# allowing a new master to register before the song is stopped.
pending_master_timeout: threading.Timer | None = None

# Flask app instance, set by setup_socket_events() for use in background threads.
_app: Flask | None = None


def setup_socket_events(socketio, app: Flask):
    """Register Socket.IO event handlers.

    Args:
        socketio: The SocketIO instance.
        app: The Flask application instance.
    """
    global _app
    _app = app

    @socketio.on("end_song")
    def end_song(reason: str) -> None:
        """Handle end_song WebSocket event from client.

        Args:
            reason: Reason for ending the song (e.g., 'complete', 'error').
        """
        if request.sid != master_splash_id:
            return
        k = get_karaoke_instance()
        k.playback_controller.end_song(reason)

    @socketio.on("start_song")
    def start_song() -> None:
        """Handle start_song WebSocket event when playback begins."""
        k = get_karaoke_instance()
        k.playback_controller.start_song()

    @socketio.on("clear_notification")
    def clear_notification() -> None:
        """Handle clear_notification WebSocket event to dismiss notifications."""
        k = get_karaoke_instance()
        k.reset_now_playing_notification()

    @socketio.on("register_splash")
    def register_splash(data: dict | None = None) -> None:
        """Handle splash screen registration and assign master/slave roles."""
        global master_splash_id, pending_master_timeout
        sid = request.sid
        channel = (data or {}).get("channel", "main")
        splash_connections[sid] = channel
        logging.info(f"Splash screen registered: {sid} (channel={channel})")

        if master_splash_id is None:
            if pending_master_timeout is not None:
                pending_master_timeout.cancel()
                pending_master_timeout = None
                logging.info("Cancelled pending master timeout — new master arrived")
            master_splash_id = sid
            socketio.emit("splash_role", "master", room=sid)
            logging.info(f"Master splash screen assigned: {sid}")
        else:
            socketio.emit("splash_role", "slave", room=sid)
            logging.info(f"Slave splash screen assigned: {sid}")

    @socketio.on("playback_position")
    def handle_playback_position(position: float) -> None:
        """Handle playback_position WebSocket event from the master splash screen.

        Args:
            position: Current playback position in seconds.
        """
        global master_splash_id
        sid = request.sid
        if sid == master_splash_id:
            k = get_karaoke_instance()
            k.playback_controller.now_playing_position = position
            # Broadcast position to all other splash screens (slaves)
            socketio.emit("playback_position", position, include_self=False)

    @socketio.on("credits_overlay")
    def credits_overlay() -> None:
        """Broadcast credits overlay message to all connected clients."""
        socketio.emit("credits_overlay")

    @socketio.on("credits_trigger")
    def credits_trigger() -> None:
        """Client-side trigger for credits overlay (sidebar AJAX workaround)."""
        socketio.emit("credits_overlay")

    @socketio.on("disconnect")
    def handle_disconnect() -> None:
        """Handle Socket.IO client disconnection and manage splash role handover."""
        global master_splash_id, pending_master_timeout
        sid = request.sid
        if sid in splash_connections:
            channel = splash_connections.pop(sid)
            logging.info(f"Splash screen disconnected: {sid} (channel={channel})")
            if sid == master_splash_id:
                master_splash_id = None
                logging.info("Master splash disconnected, electing new master")
                if splash_connections:
                    # Elect new master from remaining connections
                    new_master = next(iter(splash_connections))
                    master_splash_id = new_master
                    socketio.emit("splash_role", "master", room=new_master)
                    logging.info(f"New master splash elected: {new_master}")
                else:
                    # No splash screens left — start grace period before ending song
                    def _end_song_after_timeout() -> None:
                        global pending_master_timeout
                        with _app.app_context():
                            pending_master_timeout = None
                            if master_splash_id is None:
                                logging.info("Grace period expired, no new master — ending song")
                                k = get_karaoke_instance()
                                k.playback_controller.end_song("splash screen closed")

                    pending_master_timeout = threading.Timer(5.0, _end_song_after_timeout)
                    pending_master_timeout.daemon = True
                    pending_master_timeout.start()
                    logging.info("Started 5s grace period for master reconnection")
