/*
 * Copyright 2014-2018 Jiří Janoušek <janousek.jiri@gmail.com>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

'use strict';

(function (Nuvola) {
  var player = Nuvola.$object(Nuvola.MediaPlayer)

  var PlaybackState = Nuvola.PlaybackState
  var PlayerAction = Nuvola.PlayerAction
  var PlayerRepeat = Nuvola.PlayerRepeat
  var _ = Nuvola.Translate.gettext

  // Define rating options - 5 states with state id 0-5 representing 0-5 stars
  var ratingOptions = [
    // stateId, label, mnemo_label, icon, keybinding
    [0, _('Rating: 0 stars'), null, null, null, null],
    [1, _('Rating: 1 star'), null, null, null, null],
    [2, _('Rating: 2 stars'), null, null, null, null],
    [3, _('Rating: 3 stars'), null, null, null, null],
    [4, _('Rating: 4 stars'), null, null, null, null],
    [5, _('Rating: 5 stars'), null, null, null, null]
  ]
  // Add new radio action named ``rating`` with initial state ``3`` (3 stars)
  var ACTION_RATING = 'rating'
  Nuvola.actions.addRadioAction('playback', 'win', ACTION_RATING, 3, ratingOptions)

  var WebApp = Nuvola.$WebApp()

  WebApp._onInitWebWorker = function (emitter) {
    Nuvola.WebApp._onInitWebWorker.call(this, emitter)
    var state = document.readyState
    if (state === 'interactive' || state === 'complete') {
      this._onPageReady()
    } else {
      document.addEventListener('DOMContentLoaded', this._onPageReady.bind(this))
    }
  }

// Page is ready for magic
  WebApp._onPageReady = function () {
    // Add extra actions
    var actions = []
    for (var i = 0; i <= 5; i++) {
      actions.push(ACTION_RATING + '::' + i)
    }
    player.addExtraActions(actions)

    Nuvola.actions.connect('ActionActivated', this)
    player.connect('RatingSet', this)

    this.update()
  }

  // Extract data from the web page
  WebApp.update = function () {
    var elms = this._getElements()
    var state
    if (elms.pause) {
      state = PlaybackState.PLAYING
    } else if (elms.play) {
      state = PlaybackState.PAUSED
    } else {
      state = PlaybackState.UNKNOWN
    }

    var track = {
      title: Nuvola.queryText('#track-title'),
      artist: Nuvola.queryText('#track-artist'),
      album: Nuvola.queryText('#track-album'),
      artLocation: Nuvola.queryAttribute('#track-cover', 'src', (src) => (
        src ? window.location.href.substring(0, window.location.href.lastIndexOf('/') + 1) + src : null
      )),
      length: Nuvola.queryText('#timetotal'),
      rating: null
    }

    var rating = document.getElementById('rating')
    var stars = 0
    if (rating) {
      for (; stars < rating.childNodes.length; stars++) {
        if (rating.childNodes[stars].src.includes('star_border_white')) {
          break
        }
      }
      track.rating = stars / 5.0
    }

    player.setTrack(track)
    player.setTrackPosition(Nuvola.queryText('#timeelapsed'))
    player.updateVolume(Nuvola.queryAttribute('#volume-mark', 'aria-valuenow', (volume) => volume / 100))
    player.setPlaybackState(state)
    player.setCanGoPrev(!!elms.prev)
    player.setCanGoNext(!!elms.next)
    player.setCanPlay(!!elms.play)
    player.setCanPause(!!elms.pause)
    player.setCanRate(state !== PlaybackState.UNKNOWN)
    player.setCanSeek(state !== PlaybackState.UNKNOWN && elms.progressbar)
    player.setCanChangeVolume(!!elms.volumebar)

    var repeat = this._getRepeat()
    var shuffle = this._getShuffle()

    player.setCanRepeat(repeat !== null)
    player.setRepeatState(repeat)
    player.setCanShuffle(shuffle !== null)
    player.setShuffleState(shuffle)
    Nuvola.actions.updateEnabledFlag(ACTION_RATING, state !== PlaybackState.UNKNOWN)
    Nuvola.actions.updateState(ACTION_RATING, stars)

    // Schedule the next update
    setTimeout(this.update.bind(this), 500)
  }

  WebApp._getRepeat = function () {
    var elm = this._getElements().repeat
    if (!elm) {
      return null
    }
    if (elm.firstChild.src.endsWith('ic_repeat_one_48px.svg')) {
      return PlayerRepeat.TRACK
    }
    return elm.classList.contains('btn-info') ? PlayerRepeat.PLAYLIST : PlayerRepeat.NONE
  }

  WebApp._getShuffle = function () {
    var elm = this._getElements().shuffle
    return elm ? elm.classList.contains('btn-info') : null
  }

  WebApp._setRepeat = function (repeat) {
    while (this._getRepeat() !== repeat) {
      Nuvola.clickOnElement(this._getElements().repeat)
    }
  }

  WebApp._onActionActivated = function (emitter, name, param) {
    var elms = this._getElements()
    switch (name) {
      case PlayerAction.TOGGLE_PLAY:
        if (elms.play) {
          Nuvola.clickOnElement(elms.play)
        } else {
          Nuvola.clickOnElement(elms.pause)
        }
        break
      case PlayerAction.PLAY:
        Nuvola.clickOnElement(elms.play)
        break
      case PlayerAction.PAUSE:
      case PlayerAction.STOP:
        Nuvola.clickOnElement(elms.pause)
        break
      case PlayerAction.PREV_SONG:
        Nuvola.clickOnElement(elms.prev)
        break
      case PlayerAction.NEXT_SONG:
        Nuvola.clickOnElement(elms.next)
        break
      case PlayerAction.REPEAT:
        this._setRepeat(param)
        break
      case PlayerAction.SHUFFLE:
        Nuvola.clickOnElement(elms.shuffle)
        break
      case ACTION_RATING:
        this._setRating(param)
        break
      case PlayerAction.CHANGE_VOLUME:
        Nuvola.clickOnElement(elms.volumebar, param, 0.5)
        break
      case PlayerAction.SEEK:
        var total = Nuvola.parseTimeUsec(Nuvola.queryText('#timetotal'))
        if (param > 0 && param <= total) {
          Nuvola.clickOnElement(elms.progressbar, param / total, 0.5)
        }
        break
    }
  }

  WebApp._onRatingSet = function (emitter, rating) {
    var stars
    if (rating < 0.1) {
      stars = 0
    } else if (rating < 0.3) {
      stars = 1
    } else if (rating < 0.5) {
      stars = 2
    } else if (rating < 0.7) {
      stars = 3
    } else if (rating < 0.9) {
      stars = 4
    } else if (rating < 1.1) {
      stars = 5
    } else {
      stars = 0
    }
    this._setRating(stars)
  }

  WebApp._setRating = function (stars) {
    var elm = document.getElementById('rating-change')
    if (elm) {
      if (stars === 0) {
        var rating = document.getElementById('rating')
        if (rating) {
          for (stars = 0; stars < rating.childNodes.length; stars++) {
            if (rating.childNodes[stars].src.includes('star_border_white')) {
              break
            }
          }
        }
      }
      if (stars > 0 && stars < 6) {
        Nuvola.clickOnElement(elm.childNodes[stars - 1])
      }
    }
  }

  WebApp._getElements = function () {
    var elms = {
      play: document.getElementById('pp'),
      pause: null,
      next: document.getElementById('next'),
      prev: document.getElementById('prev'),
      repeat: document.getElementById('repeat'),
      shuffle: document.getElementById('shuffle'),
      progressbar: document.getElementById('progressbar'),
      volumebar: document.getElementById('volume-bar')
    }
    for (var key in elms) {
      if (elms[key] && elms[key].disabled) {
        elms[key] = null
      }
    }
    if (elms.play && elms.play.firstChild && elms.play.firstChild.src.includes('pause')) {
      elms.pause = elms.play
      elms.play = null
    }
    return elms
  }

  WebApp.start()
})(this)  // function(Nuvola)
