from __future__ import annotations

from nicegui import ui


def play_notification_sound() -> None:
    """Play a clean crisp notification sound using HTML5 Audio element."""
    ui.run_javascript("""
        try {
            const audio = new Audio('/sounds/notification.wav');
            audio.volume = 0.6;
            audio.play().catch(err => {
                console.warn('Audio play restricted by browser autoplay policy:', err);
            });
        } catch (e) {
            console.warn('Audio play failed:', e);
        }
    """)


def play_alert_sound() -> None:
    """Play an alert sound for urgent SLA."""
    ui.run_javascript("""
        try {
            const audio = new Audio('/sounds/alert.wav');
            audio.volume = 0.7;
            audio.play().catch(err => {
                console.warn('Audio play restricted by browser autoplay policy:', err);
            });
        } catch (e) {
            console.warn('Audio play failed:', e);
        }
    """)
