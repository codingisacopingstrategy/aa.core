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
function VoidMedia() { 
    return  elt = {
        _timer : null,
        _ended : false,
        get ended () { return this._ended; },

        _autoplay : false,
        get autoplay () { return this._autoplay; },
        set autoplay(val) { this._autoplay = val; },

        _duration : 0,
        get duration () { return this._duration; },
        set duration(val) { 
            if (val !== this._duration) {
                this._duration = val; 
                $(this).trigger('durationchange');
            }
        },

        _loop : false,
        get loop () { return this._loop; },
        set loop(val) { this._loop = val; },

        _paused : true,
        get paused () { return this._paused; },
        set paused(val) { this._paused = val; },

        _currentTime: 0,
        get currentTime () { return this._currentTime; },
        set currentTime(val) { this._currentTime = val; },

        // FIXME: can't find why playbackrate set value isn't persistent...
        _playbackRate: 1,
        get playbackrate () { return this._playbackRate; },
        set playbakRate(val) { 
            this._playbackRate = val; 
            $(this).trigger('ratechange');
        },

        _play: function () {
            this._currentTime += ((200 / 1000) * this._playbackRate);
            var _this = this;
            if (this._currentTime < this._duration) {
                $(this).trigger('timeupdate');
                this._timer = setTimeout(function() { _this._play() }, 200);
            } else {
                this._currentTime = this._duration;
                $(this).trigger('ended');
                if (this._loop) {
                    this._currentTime %= this._duration;
                    $(this).trigger('timeupdate');
                    this._timer = setTimeout(function() { _this._play() }, 200);
                } else {
                    this._currentTime = this._duration;
                    this.pause();
                }
            }
        },
        play: function () {
            if (this._paused) {
                this._play()
                this._paused = false;
                $(this).trigger('play');
            }
        },
        pause: function () {
            if (!this._paused) {
                clearTimeout(this._timer);
                this._paused = true;
                $(this).trigger('pause');
            }
        }, 
    }
};
