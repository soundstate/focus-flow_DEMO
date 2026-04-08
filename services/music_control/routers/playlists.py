"""Playlists router for listing playlists, tracks, and focus recommendations."""

from fastapi import APIRouter

from music_control.services.playlist_service import PlaylistService

router = APIRouter()


@router.get("/")
def list_playlists():
    """Get all available playlists from YouTube Music."""
    service = PlaylistService()
    return {"playlists": service.get_playlists()}


@router.get("/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str):
    """Get tracks for a specific playlist."""
    service = PlaylistService()
    return {"playlist_id": playlist_id, "tracks": service.get_playlist_tracks(playlist_id)}


@router.get("/focus-recommendations")
def get_focus_recommendations():
    """Get playlists recommended for focus sessions based on title/description analysis."""
    service = PlaylistService()
    return {"recommendations": service.get_focus_recommendations()}
