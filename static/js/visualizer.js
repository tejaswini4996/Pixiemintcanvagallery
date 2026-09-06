// Room Visualizer State
let currentRoom = 'room_living.jpg';
let currentWallColor = '#F0EEEA';
let currentArtworkFilename = 'faceless_couple.jpg';

function setArtwork(artworkFilename, btn) {
  currentArtworkFilename = artworkFilename;
  updateActiveBtn(btn);
  updateRoomPreview();
}

function setRoom(roomFilename, btn) {
  currentRoom = roomFilename;
  updateActiveBtn(btn);
  updateRoomPreview();
}

function setWallColor(hex, btn) {
  currentWallColor = hex;
  document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  updateRoomPreview();
}

function updateActiveBtn(btn) {
  if (!btn) return;
  const parent = btn.parentElement;
  if (parent) {
    parent.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
}

function updateRoomPreview() {
  const displayImg = document.getElementById('visualizerPreviewImg');
  if (!displayImg) return;

  fetch('/api/visualize-preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_filename: currentArtworkFilename,
      room_filename: currentRoom,
      wall_color_hex: currentWallColor
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      displayImg.src = data.preview_url + '?t=' + new Date().getTime();
    }
  })
  .catch(err => console.error("Visualizer error:", err));
}
