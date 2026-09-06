// Shopping Cart State
let cartItems = [];

function toggleCartDrawer() {
  const drawer = document.getElementById('cartDrawer');
  if (drawer) {
    drawer.classList.toggle('open');
  }
}

function updateCartUI() {
  const countBadge = document.getElementById('cartCount');
  const body = document.getElementById('cartBody');
  const subtotalVal = document.getElementById('cartSubtotalVal');

  let totalQty = 0;
  let totalSum = 0;

  if (cartItems.length === 0) {
    if (body) body.innerHTML = '<div style="text-align: center; color: var(--text-muted); margin-top: 3rem;">Your cart is currently empty.</div>';
    if (countBadge) countBadge.innerText = '0';
    if (subtotalVal) subtotalVal.innerText = '₹0';
    return;
  }

  let html = '';
  cartItems.forEach((item, idx) => {
    totalQty += item.qty;
    const itemTotal = item.price * item.qty;
    totalSum += itemTotal;

    const displayNote = item.hasEasel ? '🪵 Wooden Easel Stand Included' : 'Canvas Painting';

    html += `
      <div class="cart-item">
        <img src="/static/images/paintings/${item.imageFilename}" class="cart-item-img" alt="${item.title}">
        <div class="cart-item-info">
          <div style="font-weight: 600; font-size: 0.95rem;">${item.title}</div>
          <div style="font-size: 0.8rem; color: var(--accent-mint-light); margin-top: 2px;">Size: ${item.size}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${displayNote}</div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
            <div style="font-weight: 700; color: var(--accent-gold);">₹${item.price} × ${item.qty}</div>
            <button onclick="removeFromCart(${idx})" style="background: transparent; border: none; color: #ef4444; cursor: pointer; font-size: 0.8rem;">Remove</button>
          </div>
        </div>
      </div>
    `;
  });

  if (countBadge) countBadge.innerText = totalQty;
  if (body) body.innerHTML = html;
  if (subtotalVal) subtotalVal.innerText = `₹${totalSum}`;
}

function removeFromCart(index) {
  cartItems.splice(index, 1);
  updateCartUI();
}

function filterCatalog(category, btn) {
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  fetch(`/api/artworks?category=${encodeURIComponent(category)}`)
    .then(res => res.json())
    .then(data => {
      renderProductsGrid(data.artworks);
    });
}

function handleSearch() {
  const query = document.getElementById('searchInput').value;
  fetch(`/api/artworks?search=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
      renderProductsGrid(data.artworks);
    });
}

function renderProductsGrid(artworks) {
  const grid = document.getElementById('productsGrid');
  if (!grid) return;

  if (artworks.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 3rem;">No products match your search.</div>';
    return;
  }

  let html = '';
  artworks.forEach(art => {
    let priceRowsHtml = '';
    art.sizes.forEach(s => {
      priceRowsHtml += `
        <div class="price-row-item">
          <span class="price-size">${s.size}</span>
          <span class="price-val">₹${s.price}</span>
        </div>
      `;
    });

    const buttonLabel = art.has_easel ? 'Select Size & Order (Easel Stand Included)' : 'Select Size & Order';

    html += `
      <div class="product-card">
        <div class="product-img-wrap">
          <img src="/static/images/paintings/${art.image_filename}" alt="${art.title}">
          ${art.badge ? `<div class="product-badge">${art.badge}</div>` : ''}
        </div>

        <div class="product-body">
          <div class="product-category">${art.category}</div>
          <h3 class="product-title">${art.title}</h3>
          <p class="product-desc">${art.description}</p>

          <div class="product-pricing-table">
            <div class="pricing-table-title">
              <span>Size</span>
              <span>Price (INR)</span>
            </div>
            <div class="pricing-table-grid">
              ${priceRowsHtml}
            </div>
          </div>

          <div class="product-actions">
            <button class="btn-card-buy" onclick='openProductModal(${JSON.stringify(art)})'>
              ${buttonLabel}
            </button>
          </div>
        </div>
      </div>
    `;
  });

  grid.innerHTML = html;
}

// Modal Size Picker
function openProductModal(art) {
  let sizesOptionsHtml = '';
  art.sizes.forEach(s => {
    sizesOptionsHtml += `<option value="${s.size}" data-price="${s.price}">${s.size} – ₹${s.price}</option>`;
  });

  const displayNote = art.has_easel ? '<div style="background: rgba(72, 201, 176, 0.15); color: var(--accent-mint-light); border: 1px solid var(--accent-mint); padding: 0.5rem 0.8rem; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem;">🪵 Includes Handcrafted Wooden Easel Display Stand</div>' : '';

  const modalHtml = `
    <div id="productModal" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); z-index: 3000; display: flex; align-items: center; justify-content: center; padding: 2rem;">
      <div style="background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); max-width: 720px; width: 100%; overflow: hidden; display: grid; grid-template-columns: 1fr 1fr; position: relative;">
        <button onclick="closeProductModal()" style="position: absolute; top: 15px; right: 15px; background: transparent; border: none; color: white; font-size: 1.5rem; cursor: pointer; z-index: 10;">×</button>
        
        <div style="background: #000; display: flex; align-items: center; justify-content: center;">
          <img src="/static/images/paintings/${art.image_filename}" style="max-height: 380px; width: 100%; object-fit: contain;">
        </div>

        <div style="padding: 2rem; display: flex; flex-direction: column;">
          <div style="color: var(--accent-gold); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">${art.category}</div>
          <h3 style="font-family: var(--font-serif); font-size: 1.6rem; margin-bottom: 0.6rem;">${art.title}</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">${art.description}</p>
          
          ${displayNote}

          <div style="margin-bottom: 1.5rem;">
            <label style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Select Size</label>
            <select id="modalSizeSelect" class="form-control">
              ${sizesOptionsHtml}
            </select>
          </div>

          <button class="btn-primary" style="width: 100%; margin-top: auto;" onclick="addModalItemToCart(${art.id}, '${art.title}', '${art.image_filename}', ${art.has_easel})">
            Add Selected Size to Cart
          </button>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function closeProductModal() {
  const modal = document.getElementById('productModal');
  if (modal) modal.remove();
}

function addModalItemToCart(artId, title, imageFilename, hasEasel) {
  const sizeSelect = document.getElementById('modalSizeSelect');
  const selectedSize = sizeSelect.value;
  const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
  const price = parseFloat(selectedOption.getAttribute('data-price'));

  cartItems.push({
    artId: artId,
    title: title,
    imageFilename: imageFilename,
    size: selectedSize,
    price: price,
    hasEasel: hasEasel,
    qty: 1
  });

  updateCartUI();
  closeProductModal();
  toggleCartDrawer();
}

// Location-Aware Checkout Modal
function openCheckoutModal() {
  if (cartItems.length === 0) {
    alert("Your cart is empty.");
    return;
  }

  let subtotal = 0;
  cartItems.forEach(i => subtotal += i.price * i.qty);

  const modalHtml = `
    <div id="checkoutModal" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); z-index: 3500; display: flex; align-items: center; justify-content: center; padding: 2rem;">
      <div style="background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); max-width: 560px; width: 100%; padding: 2.2rem; position: relative;">
        <button onclick="closeCheckoutModal()" style="position: absolute; top: 15px; right: 15px; background: transparent; border: none; color: white; font-size: 1.5rem; cursor: pointer;">×</button>
        
        <h3 style="font-family: var(--font-serif); font-size: 1.6rem; margin-bottom: 0.4rem;">Express Delivery Checkout</h3>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.2rem;">Item Subtotal: <strong style="color: var(--accent-mint-light);">₹${subtotal}</strong></p>

        <form id="checkoutForm" onsubmit="processCheckout(event)">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" id="chkName" class="form-control" placeholder="Recipient Name" required>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Email Address *</label>
              <input type="email" id="chkEmail" class="form-control" placeholder="Order receipt destination" required>
            </div>
            <div class="form-group">
              <label>Phone Number *</label>
              <input type="tel" id="chkPhone" class="form-control" placeholder="+91 9876543210" required>
            </div>
          </div>
          <div class="form-group">
            <label>Delivery Address *</label>
            <textarea id="chkAddress" class="form-control" rows="2" placeholder="Street, Flat/House No." required></textarea>
          </div>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem;">
            <div class="form-group">
              <label>City *</label>
              <input type="text" id="chkCity" class="form-control" placeholder="City" oninput="updateLocationShippingFee()" required>
            </div>
            <div class="form-group">
              <label>State *</label>
              <input type="text" id="chkState" class="form-control" placeholder="State" oninput="updateLocationShippingFee()" required>
            </div>
            <div class="form-group">
              <label>Pincode *</label>
              <input type="text" id="chkPincode" class="form-control" placeholder="Pincode" oninput="updateLocationShippingFee()" required>
            </div>
          </div>

          <!-- Dynamic Shipping Fee Summary Box -->
          <div id="shippingSummaryBox" style="background: rgba(0,0,0,0.3); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.4rem;">
              <span style="color: var(--text-muted);">Delivery Zone:</span>
              <span id="shipZoneVal" style="font-weight: 600;">Standard Regional</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.4rem;">
              <span style="color: var(--text-muted);">Estimated Window:</span>
              <span id="shipWindowVal" style="font-weight: 600;">4-6 Business Days</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.4rem;">
              <span style="color: var(--text-muted);">Location Delivery Fee:</span>
              <span id="shipFeeVal" style="font-weight: 700; color: var(--accent-gold);">₹120</span>
            </div>
            <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 0.6rem 0;">
            <div style="display: flex; justify-content: space-between; font-size: 1.1rem; font-weight: 700;">
              <span>Total Amount:</span>
              <span id="finalTotalVal" style="color: var(--accent-mint-light);">₹${subtotal + 120}</span>
            </div>
          </div>

          <button type="submit" class="btn-primary" style="width: 100%;">Confirm Canvas Order & Generate Receipt</button>
        </form>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);
  updateLocationShippingFee();
}

function closeCheckoutModal() {
  const modal = document.getElementById('checkoutModal');
  if (modal) modal.remove();
}

function updateLocationShippingFee() {
  let subtotal = 0;
  cartItems.forEach(i => subtotal += i.price * i.qty);

  const city = document.getElementById('chkCity')?.value || '';
  const state = document.getElementById('chkState')?.value || '';
  const pincode = document.getElementById('chkPincode')?.value || '';

  fetch('/api/delivery-estimate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ city, state, pincode, total_amount: subtotal })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const est = data.estimate;
      const zoneElem = document.getElementById('shipZoneVal');
      const windowElem = document.getElementById('shipWindowVal');
      const feeElem = document.getElementById('shipFeeVal');
      const totalElem = document.getElementById('finalTotalVal');

      if (zoneElem) zoneElem.innerText = est.zone_name;
      if (windowElem) windowElem.innerText = est.delivery_window;
      
      if (feeElem) {
        feeElem.innerText = est.is_free_shipping ? 'FREE' : `₹${est.shipping_fee}`;
        feeElem.style.color = est.is_free_shipping ? 'var(--accent-mint-light)' : 'var(--accent-gold)';
      }

      const finalTotal = subtotal + est.shipping_fee;
      if (totalElem) totalElem.innerText = `₹${finalTotal}`;
    }
  });
}

function processCheckout(event) {
  event.preventDefault();

  let subtotal = 0;
  cartItems.forEach(i => subtotal += i.price * i.qty);

  const payload = {
    name: document.getElementById('chkName').value,
    email: document.getElementById('chkEmail').value,
    phone: document.getElementById('chkPhone').value,
    address: document.getElementById('chkAddress').value,
    city: document.getElementById('chkCity').value,
    state: document.getElementById('chkState').value,
    pincode: document.getElementById('chkPincode').value,
    subtotal_amount: subtotal,
    items: cartItems
  };

  fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      closeCheckoutModal();
      cartItems = [];
      updateCartUI();
      toggleCartDrawer();

      alert(`🎉 Order Confirmed!\n\nOrder ID: ${data.order_id}\nTracking Number: ${data.tracking_number}\nDelivery Zone: ${data.delivery_estimate.zone_name}\nEstimated Delivery: ${data.delivery_estimate.estimated_start} - ${data.delivery_estimate.estimated_end}\nFinal Amount: ₹${data.final_total}\n\nYou can track your shipment using your Order ID!`);
      
      const trackInput = document.getElementById('trackInput');
      if (trackInput) {
        trackInput.value = data.order_id;
        trackOrder();
      }
    }
  });
}

function submitCommissionForm(event) {
  event.preventDefault();

  const formData = new FormData();
  formData.append('name', document.getElementById('commName').value);
  formData.append('email', document.getElementById('commEmail').value);
  formData.append('phone', document.getElementById('commPhone').value);
  formData.append('art_type', document.getElementById('commType').value);
  formData.append('preferred_size', document.getElementById('commSize').value);
  formData.append('details', document.getElementById('commDetails').value);

  const photosInput = document.getElementById('commPhotos');
  if (photosInput && photosInput.files.length > 0) {
    for (let i = 0; i < photosInput.files.length; i++) {
      formData.append('photos', photosInput.files[i]);
    }
  }

  fetch('/api/commission', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      alert(`✨ Request Received!\n\n${data.message}\n\nOur team from @pixiemintcanvagallery will get in touch!`);
      document.getElementById('commissionForm').reset();
    }
  });
}
