<template>
  <footer class="site-footer">
    <!-- Cam kết dịch vụ ở đầu footer -->
    <div class="footer-features">
      <div class="container">
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="1" y="3" width="15" height="13"></rect>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                <circle cx="5.5" cy="18.5" r="2.5"></circle>
                <circle cx="18.5" cy="18.5" r="2.5"></circle>
              </svg>
            </div>
            <div>
              <h4>Giao hàng hỏa tốc</h4>
              <p>Nhận hàng trong 2H nội thành, toàn quốc 1-3 ngày</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 4 23 10 17 10"></polyline>
                <polyline points="1 20 1 14 7 14"></polyline>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
            </div>
            <div>
              <h4>Đổi trả 30 ngày</h4>
              <p>Đổi size, đổi mẫu dễ dàng và hoàn toàn miễn phí</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div>
              <h4>100% Chính hãng</h4>
              <p>Chất liệu cao cấp, bảo đảm chất lượng tuyệt đối</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <div>
              <h4>AI Stylist 24/7</h4>
              <p>Trợ lý thông minh tư vấn outfit và size theo vóc dáng</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Nội dung chính của footer (4 cột) -->
    <div class="container footer-main">
      <div class="footer-grid">
        <!-- Cột 1: Giới thiệu Fashion Store -->
        <div class="footer-col about-col">
          <div class="footer-logo">
            <div class="footer-logo-icon">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <path d="M16 10a4 4 0 0 1-8 0"></path>
              </svg>
            </div>
            <span class="footer-logo-text">FASHION STORE</span>
          </div>
          <p class="about-desc">
            <strong>Fashion Store</strong> là thương hiệu và hệ thống bán lẻ thời trang thông minh hiện đại, đem đến cho giới trẻ những thiết kế thanh lịch, trẻ trung và bắt kịp xu hướng thời trang quốc tế.
          </p>
          <p class="about-desc">
            Tích hợp công nghệ <strong>AI Stylist</strong> hỗ trợ tư vấn chọn đồ, phối đồ và giải đáp thắc mắc của khách hàng mọi lúc, mọi nơi.
          </p>
          <div class="social-links">
            <a href="#" class="social-btn" title="Facebook">Facebook</a>
            <a href="#" class="social-btn" title="Instagram">Instagram</a>
            <a href="#" class="social-btn" title="TikTok">TikTok</a>
            <a href="#" class="social-btn" title="Zalo">Zalo</a>
          </div>
        </div>

        <!-- Cột 2: Các Brand thời trang liên kết -->
        <div class="footer-col">
          <h3 class="col-title">Thương hiệu & Bộ sưu tập</h3>
          <ul class="footer-links">
            <li><RouterLink to="/products">Lumia Signature</RouterLink></li>
            <li><RouterLink to="/products">Zara Collection</RouterLink></li>
            <li><RouterLink to="/products">Uniqlo LifeWear</RouterLink></li>
            <li><RouterLink to="/products">H&M Trend</RouterLink></li>
            <li><RouterLink to="/products">Routine Studio</RouterLink></li>
            <li><RouterLink to="/products">Coolmate Essentials</RouterLink></li>
            <li><RouterLink to="/products">Thời trang Công sở Smart Casual</RouterLink></li>
            <li><RouterLink to="/products">Streetwear Năng động</RouterLink></li>
          </ul>
        </div>

        <!-- Cột 3: Hỗ trợ khách hàng -->
        <div class="footer-col">
          <h3 class="col-title">Hỗ trợ khách hàng</h3>
          <ul class="footer-links">
            <li><a href="#promos">Mã giảm giá & Khuyến mãi</a></li>
            <li><RouterLink to="/orders">Tra cứu đơn hàng online</RouterLink></li>
            <li><a href="#" @click.prevent="alertHelp('Hướng dẫn chọn size: Quý khách vui lòng chat với AI Stylist hoặc xem chi tiết ở từng sản phẩm!')">Bảng hướng dẫn chọn size chuẩn</a></li>
            <li><a href="#" @click.prevent="alertHelp('Chính sách đổi trả: Miễn phí đổi trả trong vòng 30 ngày kể từ ngày nhận hàng với sản phẩm còn nguyên tem mác.')">Chính sách đổi trả & Hoàn tiền</a></li>
            <li><a href="#" @click.prevent="alertHelp('Chính sách giao hàng: Miễn phí vận chuyển cho đơn hàng từ 500.000đ. Giao hàng toàn quốc.')">Chính sách giao hàng & Kiểm hàng</a></li>
            <li><a href="#" @click.prevent="alertHelp('Phương thức thanh toán: Hỗ trợ Tiền mặt khi nhận hàng (COD) và Chuyển khoản ngân hàng an toàn.')">Hướng dẫn thanh toán & Bảo mật</a></li>
            <li><a href="#" @click.prevent="alertHelp('Câu hỏi thường gặp: Quý khách có thể bấm biểu tượng Chat AI Stylist ở góc phải màn hình để được giải đáp tức thì 24/7!')">Câu hỏi thường gặp (FAQ)</a></li>
          </ul>
        </div>

        <!-- Cột 4: Thông tin liên hệ -->
        <div class="footer-col">
          <h3 class="col-title">Thông tin liên hệ</h3>
          <div class="contact-item">
            <div class="contact-icon">📍</div>
            <div>
              <strong>Showroom TP.HCM:</strong>
              <p>Tầng 3, Fashion Center, 180 Hai Bà Trưng, Quận 1, TP. Hồ Chí Minh</p>
            </div>
          </div>

          <div class="contact-item">
            <div class="contact-icon">🏢</div>
            <div>
              <strong>Chi nhánh Hà Nội:</strong>
              <p>88 Phố Huế, Quận Hai Bà Trưng, Hà Nội</p>
            </div>
          </div>

          <div class="contact-item">
            <div class="contact-icon">📞</div>
            <div>
              <strong>Hotline chăm sóc khách hàng:</strong>
              <p><a href="tel:19006868" class="hotline">1900 6868</a> (8:30 - 22:00)</p>
            </div>
          </div>

          <div class="contact-item">
            <div class="contact-icon">✉️</div>
            <div>
              <strong>Email liên hệ:</strong>
              <p><a href="mailto:hotro@fashionstore.vn">hotro@fashionstore.vn</a></p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bản quyền & thanh toán ở chân trang -->
    <div class="footer-bottom">
      <div class="container footer-bottom-inner">
        <p class="copyright">
          © {{ year }} <strong>FASHION STORE AI</strong>. Tất cả các quyền được bảo lưu. Thiết kế & phát triển cho trải nghiệm mua sắm thông minh.
        </p>
        <div class="payment-methods">
          <span class="payment-tag">COD</span>
          <span class="payment-tag">Chuyển khoản</span>
          <span class="payment-tag">VNPAY</span>
          <span class="payment-tag">Momo</span>
          <span class="payment-tag">Visa / Master</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()

function alertHelp(message) {
  alert(message)
}
</script>

<style scoped>
.site-footer {
  background: #201c18;
  color: #e5ded6;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 4rem;
}

/* Cam kết dịch vụ */
.footer-features {
  background: #171411;
  padding: 2.2rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(201, 147, 66, 0.15);
  color: var(--accent-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-item h4 {
  margin: 0 0 0.2rem;
  font-size: 0.98rem;
  font-weight: 700;
  color: #ffffff;
}

.feature-item p {
  margin: 0;
  font-size: 0.82rem;
  color: #a89f94;
  line-height: 1.35;
}

/* Lưới footer 4 cột */
.footer-main {
  padding: 3.5rem 0 2.5rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1.1fr 1.2fr;
  gap: 2.5rem;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.footer-logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--accent-gold);
  color: #171411;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-logo-text {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #ffffff;
}

.about-desc {
  font-size: 0.88rem;
  line-height: 1.6;
  color: #b5aba0;
  margin: 0 0 0.8rem;
}

.about-desc strong {
  color: #ffffff;
}

.social-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1.2rem;
}

.social-btn {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  font-size: 0.78rem;
  color: #d1c7bc;
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: all 0.2s ease;
}

.social-btn:hover {
  background: var(--accent-gold);
  color: #171411;
  border-color: var(--accent-gold);
}

.col-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1.2rem;
  letter-spacing: 0.02em;
  position: relative;
  padding-bottom: 0.5rem;
}

.col-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 36px;
  height: 2px;
  background: var(--accent-gold);
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.footer-links a {
  color: #aea397;
  font-size: 0.88rem;
  transition: color 0.2s ease;
}

.footer-links a:hover {
  color: #ffffff;
  padding-left: 4px;
}

.contact-item {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.86rem;
}

.contact-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.contact-item strong {
  display: block;
  color: #ffffff;
  margin-bottom: 0.15rem;
}

.contact-item p {
  margin: 0;
  color: #aea397;
  line-height: 1.4;
}

.hotline {
  color: var(--accent-gold);
  font-size: 1.1rem;
  font-weight: 800;
}

/* Bottom copyright */
.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1.5rem 0;
  font-size: 0.84rem;
  color: #8c8276;
}

.footer-bottom-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.copyright {
  margin: 0;
}

.copyright strong {
  color: #d1c7bc;
}

.payment-methods {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.payment-tag {
  background: rgba(255, 255, 255, 0.06);
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #c4b9ad;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
}

@media (max-width: 640px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .footer-bottom-inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
