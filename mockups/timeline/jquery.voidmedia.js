/*
 * Copyright 2011 Alexandre Leray <http://stdin.fr/>
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Also add information on how to contact you by electronic and paper mail.
 */


/*
 *interface HTMLMediaElement : HTMLElement {
 *
 *  // error state
 *  readonly attribute MediaError error;
 *
 *  // network state
 *           attribute DOMString src;
 *  readonly attribute DOMString currentSrc;
 *  const unsigned short NETWORK_EMPTY = 0;
 *  const unsigned short NETWORK_IDLE = 1;
 *  const unsigned short NETWORK_LOADING = 2;
 *  const unsigned short NETWORK_NO_SOURCE = 3;
 *  readonly attribute unsigned short networkState;
 *           attribute DOMString preload;
 *  readonly attribute TimeRanges buffered;
 *  void load();
 *  DOMString canPlayType(in DOMString type);
 *
 *  // ready state
 *  const unsigned short HAVE_NOTHING = 0;
 *  const unsigned short HAVE_METADATA = 1;
 *  const unsigned short HAVE_CURRENT_DATA = 2;
 *  const unsigned short HAVE_FUTURE_DATA = 3;
 *  const unsigned short HAVE_ENOUGH_DATA = 4;
 *  readonly attribute unsigned short readyState;
 *  readonly attribute boolean seeking;
 *
 *  // playback state
 *           attribute double currentTime;
 *  readonly attribute double initialTime;
 *  readonly attribute double duration;
 *  readonly attribute Date startOffsetTime;
 *  readonly attribute boolean paused;
 *           attribute double defaultPlaybackRate;
 *           attribute double playbackRate;
 *  readonly attribute TimeRanges played;
 *  readonly attribute TimeRanges seekable;
 *  readonly attribute boolean ended;
 *           attribute boolean autoplay;
 *           attribute boolean loop;
 *  void play();
 *  void pause();
 *
 *  // media controller
 *           attribute DOMString mediaGroup;
 *           attribute MediaController controller;
 *
 *  // controls
 *           attribute boolean controls;
 *           attribute double volume;
 *           attribute boolean muted;
 *           attribute boolean defaultMuted;
 *
 *  // tracks
 *  readonly attribute MultipleTrackList audioTracks;
 *  readonly attribute ExclusiveTrackList videoTracks;
 *  readonly attribute TextTrack[] textTracks;
 *  MutableTextTrack addTextTrack(in DOMString kind, in optional DOMString label, in optional DOMString language);
 *};
 */


(function($) {

Math._round = Math.round;
Math.round = function(number, precision)
{
    precision = Math.abs(parseInt(precision)) || 0;
    var coefficient = Math.pow(10, precision);
    return Math._round(number*coefficient)/coefficient;
}

function voidmedia() { 
    return  elt = {
        _timer : null,
        _ended : false,
        get ended () { return this._ended; },

        _autoplay : false,
        get autoplay () { return this._autoplay; },
        set autoplay(val) { this._autoplay = val; },

        _duration : 0,
        get duration () { return this._duration; },
        set duration(val) { this._duration = val; },

        _loop : false,
        get loop () { return this._loop; },
        set loop(val) { this._loop = val; },

        _paused : true,
        get paused () { return this._paused; },
        set paused(val) { this._paused = val; },

        _currentTime: 0,
        get currentTime () { return this._currentTime; },
        set currentTime(val) { this._currentTime = val; },

        play: function () {
            this._currentTime += (350 / 1000);
            var _this = this;
            if (this._currentTime < this._duration) {
                $(this).trigger('timeupdate');
                this._timer = setTimeout(function() { _this.play() }, 350);
            } else {
                this._currentTime = this._duration;
                $(this).trigger('ended');
                if (this._loop) {
                    this._currentTime %= this._duration;
                    $(this).trigger('timeupdate');
                    this._timer = setTimeout(function() { _this.play() }, 350);
                } else {
                    this._currentTime = this._duration;
                    this.pause();
                }
            }
            this._paused = false;
        },
        pause: function () {
            clearTimeout(this._timer);
            this._paused = true;
        }, 
    }
};

var media = new voidmedia();
media.currentTime = 0;
console.log(media.currentTime);
media.currentTime = 10;
console.log(media.currentTime);

var media2 = new voidmedia();
console.log(media2.duration = 15);
media2.duration = 3;
media2.loop = true;
media2.play();

//$(media2).on('ended timeupdate', function(event) {
    //console.log(event.type);
//});
$(media2).on('timeupdate', function(event) {
    $('#time').text(Math.round(media2.currentTime, 2).toFixed(2)
                    + "/" + media2.duration);
})

$("#play").on('click', function(event) {
    media2.play();
    console.log('click')
})
$("#pause").on('click', function(event) {
    media2.pause();
    console.log('click')
})

})(jQuery);
