/* ================================================================
   CricketZone – Main JavaScript
   ================================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Auto-dismiss alerts after 5 seconds ── */
  setTimeout(function () {
    document.querySelectorAll('.alert.fade.show').forEach(function (el) {
      var inst = bootstrap.Alert.getInstance(el);
      if (inst) inst.close();
      else el.classList.remove('show');
    });
  }, 5000);

  /* ── Smooth scroll for anchor links ── */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── Purchase form: live price calculation ── */
  var qtyInput  = document.getElementById('qtyInput');
  var totalQtyEl = document.getElementById('totalQty');
  var totalPrEl  = document.getElementById('totalPrice');
  if (qtyInput && totalPrEl) {
    qtyInput.addEventListener('input', function () {
      var qty   = Math.max(1, parseInt(this.value) || 1);
      var price = parseFloat(this.dataset.price || 0);
      if (totalQtyEl) totalQtyEl.textContent = qty;
      totalPrEl.textContent = '₹' + (price * qty).toLocaleString('en-IN');
    });
  }

  /* ── Admin sidebar toggle ── */
  var toggle  = document.getElementById('sidebarToggle');
  var sidebar = document.getElementById('adminSidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('collapsed');
    });
  }

  /* ── Product card: prevent hover issue on touch devices ── */
  if ('ontouchstart' in window) {
    document.querySelectorAll('.cz-product-card').forEach(function (card) {
      card.addEventListener('click', function (e) {
        if (!this.classList.contains('touched')) {
          e.preventDefault();
          this.classList.add('touched');
          /* add hover class to show back */
          this.style.setProperty('--hover-active', '1');
        }
      });
    });
  }

  /* ── Scroll-triggered fade-in for product sections ── */
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.cz-product-card, .feature-card, .stat-card').forEach(function (el) {
    el.classList.add('fade-on-scroll');
    observer.observe(el);
  });

  /* ── Thumbnail switcher on product detail ── */
  document.querySelectorAll('.detail-thumb').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      document.querySelectorAll('.detail-thumb').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      var mainImg = document.querySelector('.detail-main-img');
      if (mainImg) {
        var newSrc = this.src.replace('w=80&h=60', 'w=600&h=500');
        mainImg.style.opacity = '0';
        setTimeout(function () {
          mainImg.src = newSrc;
          mainImg.style.opacity = '1';
        }, 200);
      }
    });
  });

});

/* ── Add fade-on-scroll CSS inline (avoids extra stylesheet call) ── */
var style = document.createElement('style');
style.textContent = `
  .fade-on-scroll { opacity: 0; transform: translateY(24px); transition: opacity .55s ease, transform .55s ease; }
  .fade-on-scroll.visible { opacity: 1; transform: translateY(0); }
  .detail-main-img { transition: opacity .2s ease, transform .4s ease; }
`;
document.head.appendChild(style);