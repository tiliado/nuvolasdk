
var Demo = {}

Demo.Icons = {
  PLAY: 'icons/ic_play_arrow_48px.svg',
  PAUSE: 'icons/ic_pause_48px.svg',
  STAR_FULL_WHITE: 'icons/ic_star_white_48dp.png',
  STAR_OUTLINE_WHITE: 'icons/ic_star_border_white_48dp.png',
  STAR_FULL_BLACK: 'icons/ic_star_24px.svg',
  STAR_OUTLINE_BLACK: 'icons/ic_star_border_24px.svg',
  REPEAT: 'icons/ic_repeat_48px.svg',
  REPEAT_ONE: 'icons/ic_repeat_one_48px.svg'
}

Demo.AlbumCovers = {
  RED: 'resources/album-red.png',
  GREEN: 'resources/album-green.png',
  BLUE: 'resources/album-blue.png',
  ORANGE: 'resources/album-orange.png',
  PURPLE: 'resources/album-purple.png'
}

Demo.Repeat = {
  NONE: 0,
  TRACK: 1,
  PLAYLIST: 2
}

Demo.Storage = {
  REPEAT: 'repeat',
  SHUFFLE: 'shuffle'
}

Demo.greenScreen = function (show) {
  document.getElementById('green-screen').style.display = show ? 'block' : 'none'
}

Demo.makeText = function (text) {
  return document.createTextNode(text)
}

Demo.makeElement = function (name, attributes, text) {
  var elm = document.createElement(name)
  attributes = attributes || {}
  for (var key in attributes) {
    elm.setAttribute(key, attributes[key])
  }
  if (text !== undefined && text !== null) {
    elm.appendChild(Demo.makeText(text))
  }
  return elm
}

Demo.RATING_TEXT = ['bad', '-', 'good']

Demo.Player = function () {
  this.playlist = document.getElementById('playlist')
  var self = this

  for (var i = 0; i < Demo.Songs.length; i++) {
    var song = Demo.Songs[i]
    var tr = Demo.makeElement('tr')
    tr.appendChild(Demo.makeElement('td', null, i + 1))
    tr.appendChild(Demo.makeElement('td', null, song.name))
    tr.appendChild(Demo.makeElement('td', null, song.artist))
    tr.appendChild(Demo.makeElement('td', null, song.album))
    var stars = Demo.makeElement('td')
    tr.appendChild(stars)
    for (var j = 0; j < song.rating; j++) {
      stars.appendChild(Demo.makeElement('img', {width: '24', src: Demo.Icons.STAR_FULL_BLACK}))
    }
    for (; j < 5; j++) {
      stars.appendChild(Demo.makeElement('img', {width: '24', src: Demo.Icons.STAR_OUTLINE_BLACK}))
    }
    tr.setAttribute('data-i', i)
    tr.style.cursor = 'pointer'
    tr.onclick = function () {
      self.setPos(this.getAttribute('data-i') * 1)
      self.play()
    }
    this.playlist.appendChild(tr)
  }

  this.elm = {
    pp: document.getElementById('pp'),
    prev: document.getElementById('prev'),
    next: document.getElementById('next'),
    status: document.getElementById('status'),
    timer: document.getElementById('timer'),
    nowplaying: document.getElementById('nowplaying'),
    coverBox: document.getElementById('cover-box'),
    cover: document.getElementById('track-cover'),
    volumeBox: document.getElementById('volume-box'),
    trackBox: document.getElementById('track-meta-box'),
    track: document.getElementById('track-title'),
    artist: document.getElementById('track-artist'),
    album: document.getElementById('track-album'),
    repeat: document.getElementById('repeat'),
    shuffle: document.getElementById('shuffle'),
    rating: document.getElementById('rating'),
    ratingChange: document.getElementById('rating-change'),
    progressbar: document.getElementById('progressbar'),
    progressmark: document.getElementById('progressmark'),
    progresstext: document.getElementById('progresstext'),
    timeelapsed: document.getElementById('timeelapsed'),
    timetotal: document.getElementById('timetotal'),
    volumeBar: document.getElementById('volume-bar'),
    volumeMark: document.getElementById('volume-mark'),
    queue: document.querySelectorAll('#playlist tr')
  }

  this.elm.progressbar.onclick = this._onProgressBarClicked.bind(this)
  this.elm.volumeBar.onclick = this._onVolumeBarClicked.bind(this)
  for (let i = 0; i < 5; i++) {
    var star = this.elm.ratingChange.childNodes[i]
    star.onmouseenter = () => {
      for (var j = 0; j <= i; j++) {
        this.elm.ratingChange.childNodes[j].src = Demo.Icons.STAR_FULL_WHITE
      }
      for (; j < 5; j++) {
        this.elm.ratingChange.childNodes[j].src = Demo.Icons.STAR_OUTLINE_WHITE
      }
    }
    star.onclick = () => { this.changeRating(i + 1) }
  }

  this.elm.prev.disabled = true
  this.elm.next.disabled = true
  this.elm.pp.onclick = this.togglePlay.bind(this)
  this.elm.prev.onclick = this.prev.bind(this)
  this.elm.next.onclick = this.next.bind(this)
  this.elm.repeat.onclick = this.toggleRepeat.bind(this)
  this.elm.shuffle.onclick = this.toggleShuffle.bind(this)
  this.setStatus(0)
  this.pos = -1
  this.timer = -1
  this.timerId = 0
  this.setVisibility(false)
  this.repeat = null
  this.setRepeat(1 * (window.localStorage.getItem(Demo.Storage.REPEAT) || 0))
  this.shuffle = null
  this.setShuffle(window.localStorage.getItem(Demo.Storage.SHUFFLE) === 'true')
}

Demo.Songs =
[
  {
    name: 'Surrender',
    artist: 'Billy Talent',
    album: 'Billy Talent II',
    cover: Demo.AlbumCovers.GREEN,
    rating: 4,
    time: 25
  },
  {
    name: 'Holiday',
    artist: 'Green Day',
    album: 'American Idiot',
    cover: Demo.AlbumCovers.RED,
    rating: 1,
    time: 8
  },
  {
    name: 'Fallen Leaves',
    artist: 'Billy Talent',
    album: 'Billy Talent II',
    cover: Demo.AlbumCovers.BLUE,
    rating: 0,
    time: 10
  },
  {
    name: 'Boten Anna',
    artist: 'Basshunter',
    album: 'LOL',
    cover: Demo.AlbumCovers.PURPLE,
    rating: 2,
    time: 5
  },
  {
    name: 'Set Your Monster Free',
    artist: 'Quiet Company',
    album: 'We Are All Where We Belong',
    cover: Demo.AlbumCovers.ORANGE,
    rating: 5,
    time: 5
  },
  {
    name: 'Come Home',
    artist: 'Morandi',
    album: 'Mindfields',
    cover: Demo.AlbumCovers.GREEN,
    rating: 3,
    time: 5
  },
  {
    name: 'Dancer in the Dark',
    artist: 'The Rasmus',
    album: 'Hide From the Sun',
    cover: Demo.AlbumCovers.RED,
    rating: 1,
    time: 5
  },
  {
    name: 'Have You Ever',
    artist: 'The Offspring',
    album: 'Americana',
    cover: Demo.AlbumCovers.GREEN,
    rating: 0,
    time: 5
  },
  {
    name: 'Pushing Me Away',
    artist: 'Linkin Park',
    album: 'Hybrid Theory',
    cover: Demo.AlbumCovers.BLUE,
    rating: 0,
    time: 5
  }
]

Demo.Player.STOPPED = 0
Demo.Player.PLAYING = 1
Demo.Player.PAUSED = 2

Demo.Player.prototype.setStatus = function (status) {
  this.status = status
  this.elm.pp.firstChild.src = status === 1 ? Demo.Icons.PAUSE : Demo.Icons.PLAY
}

Demo.Player.prototype.setPos = function (pos) {
  this.pos = pos
  var rows = document.querySelectorAll('#playlist tr')
  for (var i = 0; i < rows.length; i++) {
    rows[i].className = i === pos ? 'table-active' : ''
  }

  this.elm.prev.disabled = pos <= 0
  this.elm.next.disabled = pos < 0 || pos === Demo.Songs.length - 1
  this.timer = 5

  if (pos >= 0) {
    var track = Demo.Songs[pos]
    this.timer = track.time + 1
    this.elm.track.innerText = track.name
    this.elm.artist.innerText = track.artist
    this.elm.album.innerText = track.album
    this.elm.cover.src = track.cover
    var totaltime = track.time < 10 ? '0' + track.time : track.time
    this.elm.timetotal.innerText = '00:' + totaltime
    this.elm.timeelapsed.innerText = '00:00'
    this.elm.progressmark.style.width = 0 + '%'
    this.elm.progressmark.setAttribute('aria-valuenow', '0')
    this.setVisibility(true)
  } else {
    this.elm.track.innerText = ''
    this.elm.artist.innerText = ''
    this.elm.album.innerText = ''
    this.setVisibility(false)
  }
  this.updateRating()
}

Demo.Player.prototype.setVisibility = function (visible) {
  var visibility = visible ? 'visible' : 'hidden'
  this.elm.progressbar.style.visibility = visibility
  this.elm.timetotal.style.visibility = visibility
  this.elm.timeelapsed.style.visibility = visibility
  this.elm.trackBox.style.visibility = visibility
  this.elm.coverBox.style.visibility = visibility
  this.elm.volumeBox.style.visibility = visibility
}

Demo.Player.prototype.play = function () {
  if (this.status === Demo.Player.PAUSED) {
    this.setStatus(Demo.Player.PLAYING)
    this.timerId = setTimeout(this.tick.bind(this), 1000)
  } else if (this.status === Demo.Player.STOPPED) {
    if (this.pos < 0) {
      this.setPos(0)
    }
    this.setStatus(Demo.Player.PLAYING)
    this.startTimer()
  }
}

Demo.Player.prototype.pause = function () {
  if (this.status === Demo.Player.PLAYING) {
    this.setStatus(Demo.Player.PAUSED)
    clearTimeout(this.timerId)
    this.timerId = 0
  }
}

Demo.Player.prototype.togglePlay = function () {
  if (this.status === Demo.Player.PLAYING) {
    this.pause()
  } else {
    this.play()
  }
}

Demo.Player.prototype.next = function () {
  if (this.pos < Demo.Songs.length - 1) {
    this.setPos(this.pos + 1)
    return true
  }
  this.setPos(0)
  return true
}

Demo.Player.prototype.prev = function () {
  if (this.pos > 0) {
    this.setPos(this.pos - 1)
    return true
  }
  return false
}

Demo.Player.prototype.startTimer = function () {
  if (this.timer <= 0) { this.timer = 5 }
  this.tick()
}

Demo.Player.prototype.tick = function () {
  if (this.timer > 0) {
    this.timer--
    this.updateProgressBar()

    this.timerId = setTimeout(this.tick.bind(this), 1000)
  } else {
    if (this.next()) { this.startTimer() } else { this.reset() }
  }
}

Demo.Player.prototype.reset = function () {
  this.setPos(-1)
  this.setStatus(0)
  this.timerId = 0
}

Demo.Player.prototype.updateProgressBar = function () {
  var total = Demo.Songs[this.pos].time
  var elapsed = total - this.timer
  var percent = elapsed / total * 100
  this.elm.progressmark.setAttribute('aria-valuenow', percent)
  this.elm.progressmark.style.width = percent + '%'
  elapsed = elapsed < 10 ? '0' + elapsed : elapsed
  this.elm.timeelapsed.innerText = '00:' + elapsed
}

Demo.Player.prototype.updateRating = function () {
  var rating = this.pos >= 0 ? Demo.Songs[this.pos].rating : 0
  for (var i = 0; i < 5; i++) {
    this.elm.rating.childNodes[i].src = Demo.Icons[rating > i ? 'STAR_FULL_WHITE' : 'STAR_OUTLINE_WHITE']
  }
}

Demo.Player.prototype._onProgressBarClicked = function (event) {
  if (event.button === 0) {
    var x = event.clientX
    var rect = this.elm.progressbar.getBoundingClientRect()
    var pos = (x - rect.left) / rect.width
    var total = Demo.Songs[this.pos].time
    this.timer = total - Math.round(pos * total)
    this.updateProgressBar()
  }
}

Demo.Player.prototype._onVolumeBarClicked = function (event) {
  if (event.button === 0) {
    var x = event.clientX
    var rect = this.elm.volumeBar.getBoundingClientRect()
    var pos = (x - rect.left) / rect.width
    var percent = pos * 100
    this.elm.volumeMark.setAttribute('aria-valuenow', percent)
    this.elm.volumeMark.style.width = percent + '%'
  }
}

Demo.Player.prototype.changeRating = function (rating) {
  console.log(rating)
  var track = Demo.Songs[this.pos]
  track.rating = track.rating === rating ? 0 : rating
  this.updateRating()
  var stars = this.elm.queue[this.pos].lastChild.childNodes

  for (var i = 0; i < 5; i++) {
    stars[i].src = Demo.Icons[track.rating > i ? 'STAR_FULL_BLACK' : 'STAR_OUTLINE_BLACK']
  }
}

Demo.Player.prototype.setRepeat = function (repeat) {
  window.localStorage.setItem(Demo.Storage.REPEAT, '' + repeat)
  this.repeat = repeat
  var elm = this.elm.repeat
  switch (repeat) {
    case Demo.Repeat.TRACK:
      elm.classList.remove('btn-secondary')
      elm.classList.add('btn-info')
      elm.firstChild.src = Demo.Icons.REPEAT_ONE
      break
    case Demo.Repeat.PLAYLIST:
      elm.classList.remove('btn-secondary')
      elm.classList.add('btn-info')
      elm.firstChild.src = Demo.Icons.REPEAT
      break
    default:
      elm.classList.add('btn-secondary')
      elm.classList.remove('btn-info')
      elm.firstChild.src = Demo.Icons.REPEAT
      break
  }
}

Demo.Player.prototype.toggleRepeat = function () {
  this.setRepeat(this.repeat === Demo.Repeat.PLAYLIST ? 0 : this.repeat + 1)
}

Demo.Player.prototype.setShuffle = function (shuffle) {
  window.localStorage.setItem(Demo.Storage.SHUFFLE, shuffle ? 'true' : 'false')
  this.shuffle = shuffle
  var elm = this.elm.shuffle
  var classes = shuffle ? ['btn-info', 'btn-secondary'] : ['btn-secondary', 'btn-info']
  elm.classList.add(classes[0])
  elm.classList.remove(classes[1])
}

Demo.Player.prototype.toggleShuffle = function () {
  this.setShuffle(!this.shuffle)
}

window.player = new Demo.Player()
