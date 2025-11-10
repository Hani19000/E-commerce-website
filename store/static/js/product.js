  // Quantity buttons
  function incrementQty() {
    const input = document.getElementById('quantity');
    input.value = parseInt(input.value) + 1;
  }

  function decrementQty() {
    const input = document.getElementById('quantity');
    if (parseInt(input.value) > 1) {
      input.value = parseInt(input.value) - 1;
    }
  }

  // Thumbnail gallery
  document.querySelectorAll('.thumbnail-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.thumbnail-item').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const img = this.querySelector('img').src;
      document.getElementById('mainImage').src = img;
    });
  });

  // Tabs
  function openTab(evt, tabName) {
    const tabContent = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContent.length; i++) {
      tabContent[i].classList.remove('active');
    }
    
    const tabButtons = document.getElementsByClassName('tab-btn');
    for (let i = 0; i < tabButtons.length; i++) {
      tabButtons[i].classList.remove('active');
    }
    
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
  }

  // Wishlist toggle
  function toggleWishlist(btn) {
    btn.classList.toggle('active');
  }

  // Add to cart
  function addToCart() {
    const quantity = document.getElementById('quantity').value;
    alert(`Added ${quantity} item(s) to cart!`);
    // Ajoutez ici votre logique pour ajouter au panier
  }