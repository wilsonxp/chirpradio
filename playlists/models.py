###
### Copyright 2009 The Chicago Independent Radio Project
### All Rights Reserved.
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###     http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
###

"""Datastore model for DJ Playlists."""

from auth.models import User
from djdb.models import Artist, Album, Track
from google.appengine.ext import db
from google.appengine.api.datastore_types import Key

class Playlist(db.Model):
    """A DJ playlist.
    """
    # DJ user who created the playlist
    dj_user = db.ReferenceProperty(User, required=True)
    # The type of playlist.  Possible values: 
    #
    # on-air
    #   A playlist that was recorded while broadcasting 
    #   on the air during a CHIRP radio program.
    #
    # (more possible values TBD)
    playlist_type = db.CategoryProperty(required=True, choices=('on-air',))
    # Number of tracks contained in this playlist.
    # This gets updated each time a PlaylistTrack() is saved
    track_count = db.IntegerProperty(default=0, required=True)
    # The date this playlist was established 
    # (automatically set to now upon creation)
    established = db.DateTimeProperty(auto_now_add=True)
    # The date this playlist was last modified (automatically set to now)
    modified = db.DateTimeProperty(auto_now=True)
    
    def validate(self):
        """Validate this instance before putting it to the datastore."""
        if not self.dj_user.is_dj:
            raise ValueError("User %r must be a DJ (user is: %r)" % (
                                        self.dj_user, self.dj_user.roles))
    
    def put(self, *args, **kwargs):
        self.validate()
        super(Playlist, self).put(*args, **kwargs)

class PlaylistTrack(db.Model):
    """A track in a DJ playlist."""
    # The playlist this track belongs to
    playlist = db.ReferenceProperty(Playlist, required=True)
    # Artist name if this is a freeform entry
    artist_name = db.StringProperty(required=False)
    # Reference to artist from CHIRP digital library (if exists in library)
    artist = db.ReferenceProperty(Artist, required=False)
    # Track title if this is a freeform entry
    track_title = db.StringProperty(required=False)
    # Reference to track (mp3 file) from CHIRP digital library (if exists in library)
    track = db.ReferenceProperty(Track, required=False)
    # The order at which this track appears in the playlist
    track_number = db.IntegerProperty(required=True, default=1)
    # Album title if this is a freeform entry
    album_title = db.StringProperty(required=False)
    # Reference to album from CHIRP digital library (if exists in library)
    album = db.ReferenceProperty(Album, required=False)
    # The date this playlist track was established 
    # (automatically set to now upon creation)
    established = db.DateTimeProperty(auto_now_add=True)
    # The date this playlist track was last modified (automatically set to now)
    modified = db.DateTimeProperty(auto_now=True)
    
    def __init__(self, *args, **kwargs):
        super(PlaylistTrack, self).__init__(*args, **kwargs)
        # TODO(kumar) wrap in a transaction?
        if isinstance(kwargs['playlist'], Key):
            playlist = Playlist.get(kwargs['playlist'])
        else:
            playlist = kwargs['playlist']
        track_number = playlist.track_count + 1
        playlist.track_count = track_number
        playlist.put()
        self.track_number = track_number
    
    def validate(self):
        """Validate this instance before putting it to the datastore.
        
        A track must have at least artist name and track title
        """
        if not self.track_title and not self.track:
            raise ValueError("Must set either a track_title or reference a track")
        if not self.artist_name and not self.artist:
            raise ValueError("Must set either an artist_name or reference an artist")
    
    def put(self, *args, **kwargs):
        self.validate()
        super(PlaylistTrack, self).put(*args, **kwargs)
