<template>
  <div class="admin-layout">
    <!-- PANEL BÊN TRÁI: MENU QUẢN TRỊ VIÊN -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <RouterLink to="/" class="sidebar-brand">
          <div class="brand-badge-icon">AI</div>
          <div class="brand-info">
            <span class="brand-title">FASHION STORE</span>
            <span class="brand-role">👑 Quản Trị Hệ Thống</span>
          </div>
        </RouterLink>
      </div>

      <div class="admin-user-card">
        <div class="user-avatar">{{ auth.user?.full_name?.charAt(0) || 'A' }}</div>
        <div class="user-details">
          <strong>{{ auth.user?.full_name || 'Admin Quản Trị' }}</strong>
          <small>{{ auth.user?.email || 'admin@fashion.vn' }}</small>
        </div>
      </div>

      <!-- Danh sách Menu các chức năng -->
      <nav class="sidebar-nav">
        <button
          v-for="item in menuItems"
          :key="item.key"
          class="nav-item-btn"
          :class="{ active: currentSection === item.key }"
          @click="currentSection = item.key"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <RouterLink to="/" class="btn-sidebar-link">
          <span>🛍️ Xem trang cửa hàng</span>
        </RouterLink>
        <button class="btn-sidebar-link text-danger" @click="handleLogout">
          <span>🚪 Đăng xuất quản trị</span>
        </button>
      </div>
    </aside>

    <!-- KHU VỰC NỘI DUNG CHÍNH (MAIN ADMIN CONTENT) -->
    <main class="admin-main">
      <!-- 1. DASHBOARD / TỔNG QUAN -->
      <section v-if="currentSection === 'dashboard'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">📊 Tổng quan hệ thống (Dashboard)</h1>
            <p class="page-desc">Theo dõi các chỉ số kinh doanh, đơn hàng mới, sản phẩm bán chạy và tình trạng chatbot AI.</p>
          </div>
          <button class="btn secondary" @click="loadAllData">
            🔄 Làm mới số liệu
          </button>
        </div>

        <!-- Thẻ thống kê số liệu -->
        <div class="stats-overview-grid">
          <div class="stat-box clickable" @click="currentSection = 'orders'">
            <div class="stat-icon-wrapper bg-blue">📦</div>
            <div class="stat-meta">
              <span class="stat-label">Tổng đơn hàng</span>
              <strong class="stat-number">{{ dashboard.orders || 0 }}</strong>
              <span class="stat-sub">Bấm để xem đơn hàng</span>
            </div>
          </div>

          <div class="stat-box clickable" @click="currentSection = 'products'">
            <div class="stat-icon-wrapper bg-green">👗</div>
            <div class="stat-meta">
              <span class="stat-label">Sản phẩm thời trang</span>
              <strong class="stat-number">{{ dashboard.products || 0 }}</strong>
              <span class="stat-sub">Bấm để quản lý sản phẩm</span>
            </div>
          </div>

          <div class="stat-box clickable" @click="currentSection = 'categories'">
            <div class="stat-icon-wrapper bg-orange">📂</div>
            <div class="stat-meta">
              <span class="stat-label">Danh mục sản phẩm</span>
              <strong class="stat-number">{{ categories.length || 0 }}</strong>
              <span class="stat-sub">Bấm để xem danh mục</span>
            </div>
          </div>

          <div class="stat-box">
            <div class="stat-icon-wrapper bg-purple">💰</div>
            <div class="stat-meta">
              <span class="stat-label">Tổng doanh thu</span>
              <strong class="stat-number text-accent">{{ formatPrice(dashboard.revenue || 0) }}</strong>
              <span class="stat-sub">Đơn hàng không bị hủy</span>
            </div>
          </div>
        </div>

        <!-- Bảng đơn hàng gần đây trên Dashboard -->
        <div class="dashboard-recent-grid">
          <div class="panel">
            <div class="panel-header-row">
              <h3>Đơn hàng mới nhất</h3>
              <button class="btn secondary btn-sm" @click="currentSection = 'orders'">Xem tất cả đơn</button>
            </div>
            <AdminDataTable
              :columns="dashboardOrderColumns"
              :rows="orders.slice(0, 5)"
              :loading="loading"
              emptyText="Chưa có đơn hàng nào."
              @reload="loadOrders"
            >
              <template #cell-status="{ value }">
                <span class="status-pill" :class="value">{{ formatStatus(value) }}</span>
              </template>
              <template #cell-total="{ value }">
                <strong>{{ formatPrice(value) }}</strong>
              </template>
            </AdminDataTable>
          </div>

          <div class="panel">
            <div class="panel-header-row">
              <h3>Sản phẩm nổi bật (Featured)</h3>
              <button class="btn secondary btn-sm" @click="currentSection = 'products'">Quản lý sản phẩm</button>
            </div>
            <div class="featured-list">
              <div v-for="item in featuredProducts" :key="item.id" class="featured-item-row">
                <img :src="item.images?.[0] || 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'" />
                <div class="f-info">
                  <strong>{{ item.name }}</strong>
                  <small class="muted">{{ item.category_name }} · {{ formatPrice(item.sale_price || item.price) }}</small>
                </div>
                <span class="badge-tag">Hot</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Lịch sử hoạt động tổng quát -->
        <AdminActivityLog :logs="activityLogs" title="Lịch sử hoạt động toàn hệ thống" @clear="clearLogs" />
      </section>

      <!-- 2. QUẢN LÝ DANH MỤC SẢN PHẨM -->
      <section v-else-if="currentSection === 'categories'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">📂 Quản lý danh mục sản phẩm</h1>
            <p class="page-desc">Tạo và quản lý các danh mục thời trang (Áo, Quần, Váy, Áo khoác, Giày dép, Phụ kiện...).</p>
          </div>
          <div class="action-buttons">
            <button class="btn" @click="openCreateCategoryModal">
              ➕ Thêm mới
            </button>
          </div>
        </div>

        <!-- Bảng danh mục với filter từng cột -->
        <div class="panel mb-4">
          <AdminDataTable
            :columns="categoryColumns"
            :rows="categories"
            :loading="loading"
            emptyText="Chưa có danh mục nào."
            @reload="loadCategories"
          >
            <template #cell-is_active="{ value }">
              <span class="badge-status" :class="value ? 'active' : 'inactive'">
                {{ value ? 'Đang hoạt động' : 'Tạm ẩn' }}
              </span>
            </template>

            <template #cell-actions="{ row }">
              <div class="table-actions">
                <button class="btn-action-edit" @click="openEditCategoryModal(row)" title="Chỉnh sửa">
                  ✏️ Sửa
                </button>
                <button class="btn-action-delete" @click="handleDeleteCategory(row)" title="Xóa danh mục">
                  🗑️ Xóa
                </button>
              </div>
            </template>
          </AdminDataTable>
        </div>

        <!-- Lịch sử hoạt động danh mục -->
        <AdminActivityLog
          :logs="getSectionLogs('category')"
          title="Lịch sử thao tác Danh mục sản phẩm"
          @clear="clearLogs"
        />
      </section>

      <!-- 3. QUẢN LÝ SẢN PHẨM -->
      <section v-else-if="currentSection === 'products'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">👗 Quản lý sản phẩm thời trang</h1>
            <p class="page-desc">Thêm mới, chỉnh sửa thông tin, giá bán, màu sắc, size và quản lý tồn kho sản phẩm.</p>
          </div>
        </div>

        <!-- Bảng sản phẩm với filter từng cột -->
        <div class="panel mb-4">
          <input
            ref="productImportInput"
            type="file"
            accept=".csv,.json,text/csv,application/json"
            hidden
            @change="handleProductImport"
          />
          <AdminDataTable
            :columns="productColumns"
            :rows="products"
            :loading="loading"
            emptyText="Chưa có sản phẩm nào."
            @reload="loadProducts"
          >
            <template #toolbar-actions>
              <button
                class="btn secondary btn-sm"
                type="button"
                :disabled="importingProducts"
                title="Import sản phẩm từ file CSV hoặc JSON"
                @click="openProductImport"
              >
                {{ importingProducts ? '⏳ Đang import...' : '📥 Import' }}
              </button>
              <button class="btn btn-sm" type="button" @click="openCreateProductModal">
                ➕ Thêm mới
              </button>
            </template>

            <template #cell-image="{ row }">
              <img
                :src="row.images?.[0] || 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'"
                class="table-thumb"
              />
            </template>

            <template #cell-name="{ row }">
              <div class="table-product-name">
                <strong>{{ row.name }}</strong>
                <small v-if="row.is_featured" class="tag-featured">Nổi bật</small>
              </div>
            </template>

            <template #cell-price="{ row }">
              <div>
                <strong>{{ formatPrice(row.sale_price || row.price) }}</strong>
                <small v-if="row.sale_price" class="old-price-sub">{{ formatPrice(row.price) }}</small>
              </div>
            </template>

            <template #cell-actions="{ row }">
              <div class="table-actions">
                <button class="btn-action-edit" @click="openEditProductModal(row)" title="Chỉnh sửa">
                  ✏️ Sửa
                </button>
                <button class="btn-action-delete" @click="handleDeleteProduct(row)" title="Xóa sản phẩm">
                  🗑️ Xóa
                </button>
              </div>
            </template>
          </AdminDataTable>
        </div>

        <!-- Lịch sử hoạt động sản phẩm -->
        <AdminActivityLog
          :logs="getSectionLogs('product')"
          title="Lịch sử thao tác Sản phẩm"
          @clear="clearLogs"
        />
      </section>

      <!-- 4. QUẢN LÝ ĐƠN HÀNG -->
      <section v-else-if="currentSection === 'orders'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">📦 Quản lý đơn hàng khách mua</h1>
            <p class="page-desc">Theo dõi thông tin người nhận, danh sách món hàng và cập nhật tiến độ giao hàng.</p>
          </div>
        </div>

        <!-- Bảng đơn hàng với filter từng cột -->
        <div class="panel mb-4">
          <AdminDataTable
            :columns="orderColumns"
            :rows="orders"
            :loading="loading"
            emptyText="Chưa có đơn hàng nào."
            @reload="loadOrders"
          >
            <template #cell-id="{ value }">
              <strong>#{{ String(value).slice(-6).toUpperCase() }}</strong>
            </template>

            <template #cell-customer="{ row }">
              <div>
                <strong>{{ row.shipping_address?.full_name || 'Khách vãng lai' }}</strong>
                <small class="d-block muted">{{ row.shipping_address?.phone }}</small>
              </div>
            </template>

            <template #cell-items_count="{ row }">
              <span>{{ row.items?.length || 0 }} món</span>
            </template>

            <template #cell-total="{ value }">
              <strong class="text-accent">{{ formatPrice(value) }}</strong>
            </template>

            <template #cell-status="{ row }">
              <select
                :value="row.status"
                class="status-dropdown"
                :class="row.status"
                @change="handleUpdateOrderStatus(row.id, $event.target.value)"
              >
                <option v-for="st in statusList" :key="st.key" :value="st.key">
                  {{ st.label }}
                </option>
              </select>
            </template>

            <template #cell-actions="{ row }">
              <div class="table-actions">
                <button class="btn-action-view" @click="openOrderDetailModal(row)">
                  👁️ Chi tiết
                </button>
              </div>
            </template>
          </AdminDataTable>
        </div>

        <!-- Lịch sử hoạt động đơn hàng -->
        <AdminActivityLog
          :logs="getSectionLogs('order')"
          title="Lịch sử cập nhật Đơn hàng"
          @clear="clearLogs"
        />
      </section>

      <!-- 5. QUẢN LÝ KHUYẾN MÃI -->
      <section v-else-if="currentSection === 'promotions'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">🎁 Quản lý mã khuyến mãi & Voucher</h1>
            <p class="page-desc">Tạo mã ưu đãi giảm giá theo phần trăm hoặc số tiền cố định cho khách hàng.</p>
          </div>
          <div class="action-buttons">
            <button class="btn" @click="openCreatePromoModal">
              ➕ Thêm mới
            </button>
          </div>
        </div>

        <!-- Bảng khuyến mãi -->
        <div class="panel mb-4">
          <AdminDataTable
            :columns="promoColumns"
            :rows="promotions"
            :loading="loading"
            emptyText="Chưa có mã khuyến mãi nào."
            @reload="loadPromotions"
          >
            <template #cell-code="{ value }">
              <span class="code-badge">{{ value }}</span>
            </template>

            <template #cell-discount="{ row }">
              <strong>
                {{ row.discount_type === 'percent' ? `${row.discount_value}%` : formatPrice(row.discount_value) }}
              </strong>
            </template>

            <template #cell-is_active="{ value }">
              <span class="badge-status" :class="value ? 'active' : 'inactive'">
                {{ value ? 'Đang hiệu lực' : 'Đã hết hạn' }}
              </span>
            </template>

            <template #cell-actions="{ row }">
              <div class="table-actions">
                <button class="btn-action-delete" @click="handleDeletePromo(row)">
                  🗑️ Xóa
                </button>
              </div>
            </template>
          </AdminDataTable>
        </div>

        <!-- Lịch sử hoạt động khuyến mãi -->
        <AdminActivityLog
          :logs="getSectionLogs('promo')"
          title="Lịch sử thao tác Mã khuyến mãi"
          @clear="clearLogs"
        />
      </section>

      <!-- 6. QUẢN LÝ THÔNG TIN CỬA HÀNG -->
      <section v-else-if="currentSection === 'store_info'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">🏪 Quản lý thông tin cửa hàng</h1>
            <p class="page-desc">Cấu hình địa chỉ showroom, hotline CSKH, email liên hệ, chính sách đổi trả và vận chuyển.</p>
          </div>
          <button class="btn" @click="saveStoreInfo">
            💾 Lưu thông tin cửa hàng
          </button>
        </div>

        <div class="panel form-grid-panel mb-4">
          <form class="store-info-form" @submit.prevent="saveStoreInfo">
            <div class="form-row-2">
              <div class="field">
                <label>Tên cửa hàng / Thương hiệu *</label>
                <input v-model="storeForm.name" placeholder="FASHION STORE AI" required />
              </div>
              <div class="field">
                <label>Hotline chăm sóc khách hàng *</label>
                <input v-model="storeForm.hotline" placeholder="1900 6868" required />
              </div>
            </div>

            <div class="form-row-2">
              <div class="field">
                <label>Email liên hệ *</label>
                <input v-model="storeForm.email" type="email" placeholder="hotro@fashionstore.vn" required />
              </div>
              <div class="field">
                <label>Giờ mở cửa phục vụ</label>
                <input v-model="storeForm.working_hours" placeholder="8:30 - 22:00 tất cả các ngày" />
              </div>
            </div>

            <div class="field">
              <label>Địa chỉ Showroom chính</label>
              <input v-model="storeForm.address" placeholder="Tầng 3, Fashion Center, 180 Hai Bà Trưng, Quận 1, TP.HCM" />
            </div>

            <div class="field">
              <label>Chính sách đổi trả & hoàn tiền</label>
              <textarea v-model="storeForm.return_policy" rows="3" placeholder="Quy định đổi trả hàng trong 30 ngày..." />
            </div>

            <div class="field">
              <label>Chính sách vận chuyển & kiểm tra hàng</label>
              <textarea v-model="storeForm.shipping_policy" rows="3" placeholder="Miễn phí ship đơn từ 500k, đồng kiểm trước khi nhận..." />
            </div>

            <div class="field">
              <label>Khẩu hiệu / Giới thiệu ngắn</label>
              <textarea v-model="storeForm.description" rows="2" placeholder="Hệ thống thời trang thông minh tích hợp AI Stylist..." />
            </div>

            <div v-if="storeSuccessMessage" class="alert-success">
              {{ storeSuccessMessage }}
            </div>
          </form>
        </div>

        <!-- Lịch sử hoạt động cửa hàng -->
        <AdminActivityLog
          :logs="getSectionLogs('store')"
          title="Lịch sử cập nhật Thông tin cửa hàng"
          @clear="clearLogs"
        />
      </section>

      <!-- 7. QUẢN LÝ DỮ LIỆU CHO CHATBOT -->
      <section v-else-if="currentSection === 'chatbot'" class="section-content fade-up">
        <div class="page-top-bar">
          <div>
            <h1 class="page-title">🤖 Quản lý dữ liệu Chatbot AI Stylist</h1>
            <p class="page-desc">Quản lý các câu hỏi thường gặp (FAQs), đồng bộ dữ liệu Vector DB (ChromaDB) và xem nhật ký hội thoại của khách.</p>
          </div>
          <div class="action-buttons">
            <button class="btn" @click="openCreateFaqModal">
              ➕ Thêm mới
            </button>
            <button class="btn btn-reindex" :disabled="reindexing" @click="handleReindex">
              {{ reindexing ? '⏳ Đang đồng bộ...' : '⚡ Đồng bộ dữ liệu AI (ChromaDB)' }}
            </button>
          </div>
        </div>

        <!-- Thông báo Reindex -->
        <div v-if="reindexResult" class="reindex-result-box panel">
          <strong>Thông báo AI Core:</strong> {{ reindexResult }}
        </div>

        <!-- Bảng danh sách FAQ -->
        <div class="panel mb-4">
          <h3 class="sub-section-title">Danh sách câu hỏi thường gặp (FAQs)</h3>
          <AdminDataTable
            :columns="faqColumns"
            :rows="faqs"
            :loading="loading"
            emptyText="Chưa có câu hỏi FAQ nào."
            @reload="loadFaqs"
          >
            <template #cell-question="{ value }">
              <strong>❓ {{ value }}</strong>
            </template>

            <template #cell-actions="{ row }">
              <div class="table-actions">
                <button class="btn-action-delete" @click="handleDeleteFaq(row)">
                  🗑️ Xóa
                </button>
              </div>
            </template>
          </AdminDataTable>
        </div>

        <!-- Bảng nhật ký hội thoại Chatbot -->
        <div class="panel mb-4">
          <h3 class="sub-section-title">Nhật ký hội thoại gần đây của khách hàng</h3>
          <AdminDataTable
            :columns="chatLogColumns"
            :rows="chatLogs"
            :loading="loading"
            emptyText="Chưa có nhật ký hội thoại nào."
            @reload="loadChatLogs"
          />
        </div>

        <!-- Lịch sử thao tác chatbot -->
        <AdminActivityLog
          :logs="getSectionLogs('chatbot')"
          title="Lịch sử thao tác Chatbot & Kiến thức"
          @clear="clearLogs"
        />
      </section>
    </main>

    <!-- ==================== CÁC MODAL FORM TƯƠNG ỨNG ==================== -->

    <!-- MODAL 1: THÊM / SỬA DANH MỤC -->
    <AdminModal
      :show="showCategoryModal"
      :title="editingCategory ? 'Chỉnh sửa danh mục' : 'Thêm danh mục mới'"
      icon="📂"
      @close="showCategoryModal = false"
    >
      <form @submit.prevent="submitCategoryForm" id="catForm">
        <div class="field">
          <label>Tên danh mục *</label>
          <input v-model="categoryForm.name" placeholder="Ví dụ: Áo Nam & Nữ" required />
        </div>
        <div class="field">
          <label>Mã đường dẫn (Slug) *</label>
          <input v-model="categoryForm.slug" placeholder="ao-nam-nu" required />
        </div>
        <div class="field">
          <label>Mô tả danh mục</label>
          <textarea v-model="categoryForm.description" rows="3" placeholder="Áo sơ mi công sở, áo thun phong cách..." />
        </div>
      </form>
      <template #footer>
        <button class="btn secondary" type="button" @click="showCategoryModal = false">Hủy</button>
        <button class="btn" form="catForm" type="submit">
          {{ editingCategory ? 'Lưu thay đổi' : 'Tạo danh mục' }}
        </button>
      </template>
    </AdminModal>

    <!-- MODAL 2: THÊM / SỬA SẢN PHẨM -->
    <AdminModal
      :show="showProductModal"
      :title="editingProduct ? 'Chỉnh sửa sản phẩm' : 'Thêm sản phẩm thời trang mới'"
      icon="👗"
      maxWidth="720px"
      @close="showProductModal = false"
    >
      <form @submit.prevent="submitProductForm" id="prodForm">
        <div class="form-row-2">
          <div class="field">
            <label>Tên sản phẩm thời trang *</label>
            <input v-model="productForm.name" placeholder="Áo Sơ Mi Oxford Premium" required />
          </div>
          <div class="field">
            <label>Danh mục *</label>
            <select v-model="productForm.category_id" required>
              <option disabled value="">Chọn danh mục</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
        </div>

        <div class="form-row-3">
          <div class="field">
            <label>Giá niêm yết (VNĐ) *</label>
            <input v-model.number="productForm.price" type="number" placeholder="389000" required />
          </div>
          <div class="field">
            <label>Giá khuyến mãi (VNĐ)</label>
            <input v-model.number="productForm.sale_price" type="number" placeholder="329000" />
          </div>
          <div class="field">
            <label>Số lượng tồn kho</label>
            <input v-model.number="productForm.stock" type="number" placeholder="50" />
          </div>
        </div>

        <div class="form-row-2">
          <div class="field">
            <label>Màu sắc (Cách nhau dấu phẩy)</label>
            <input v-model="productForm.colorsStr" placeholder="Trắng, Đen, Xanh Pastel" />
          </div>
          <div class="field">
            <label>Kích cỡ (Cách nhau dấu phẩy)</label>
            <input v-model="productForm.sizesStr" placeholder="S, M, L, XL" />
          </div>
        </div>

        <div class="field">
          <label>Link hình ảnh sản phẩm (URL)</label>
          <input v-model="productForm.imageUrl" placeholder="https://images.unsplash.com/photo-..." />
        </div>

        <div class="field">
          <label>Mô tả chi tiết sản phẩm *</label>
          <textarea v-model="productForm.description" rows="3" placeholder="Chất liệu cotton cao cấp, chống nhăn, thoáng mát..." required />
        </div>

        <div class="field checkbox-field">
          <label class="checkbox-label">
            <input type="checkbox" v-model="productForm.is_featured" />
            <span>Đánh dấu sản phẩm <strong>Nổi bật (Featured)</strong> hiển thị ở trang chủ</span>
          </label>
        </div>
      </form>
      <template #footer>
        <button class="btn secondary" type="button" @click="showProductModal = false">Hủy</button>
        <button class="btn" form="prodForm" type="submit">
          {{ editingProduct ? 'Lưu sản phẩm' : 'Thêm sản phẩm' }}
        </button>
      </template>
    </AdminModal>

    <!-- MODAL 3: THÊM KHUYẾN MÃI -->
    <AdminModal
      :show="showPromoModal"
      title="Tạo mã khuyến mãi mới"
      icon="🎁"
      @close="showPromoModal = false"
    >
      <form @submit.prevent="submitPromoForm" id="promoForm">
        <div class="form-row-2">
          <div class="field">
            <label>Mã Voucher (Code) *</label>
            <input v-model="promoForm.code" placeholder="VÍ DỤ: FASHION2026" required />
          </div>
          <div class="field">
            <label>Tiêu đề khuyến mãi *</label>
            <input v-model="promoForm.title" placeholder="Giảm giá 15% mùa hè" required />
          </div>
        </div>

        <div class="form-row-2">
          <div class="field">
            <label>Loại giảm giá *</label>
            <select v-model="promoForm.discount_type">
              <option value="percent">Giảm theo Phần trăm (%)</option>
              <option value="fixed">Giảm theo Số tiền (VNĐ)</option>
            </select>
          </div>
          <div class="field">
            <label>Mức giảm *</label>
            <input v-model.number="promoForm.discount_value" type="number" placeholder="15" required />
          </div>
        </div>

        <div class="field">
          <label>Đơn hàng tối thiểu áp dụng (VNĐ)</label>
          <input v-model.number="promoForm.min_order_value" type="number" placeholder="200000" />
        </div>

        <div class="field">
          <label>Mô tả chi tiết voucher</label>
          <textarea v-model="promoForm.description" rows="2" placeholder="Áp dụng cho mọi khách hàng đặt online..." />
        </div>
      </form>
      <template #footer>
        <button class="btn secondary" type="button" @click="showPromoModal = false">Hủy</button>
        <button class="btn" form="promoForm" type="submit">Tạo mã ưu đãi</button>
      </template>
    </AdminModal>

    <!-- MODAL 4: THÊM CÂU HỎI FAQ -->
    <AdminModal
      :show="showFaqModal"
      title="Thêm câu hỏi FAQ cho Chatbot"
      icon="❓"
      @close="showFaqModal = false"
    >
      <form @submit.prevent="submitFaqForm" id="faqForm">
        <div class="field">
          <label>Câu hỏi của khách hàng *</label>
          <input v-model="faqForm.question" placeholder="Ví dụ: Cửa hàng có chính sách đổi trả như thế nào?" required />
        </div>
        <div class="field">
          <label>Câu trả lời của cửa hàng *</label>
          <textarea v-model="faqForm.answer" rows="4" placeholder="Cửa hàng hỗ trợ đổi trả miễn phí trong 30 ngày..." required />
        </div>
      </form>
      <template #footer>
        <button class="btn secondary" type="button" @click="showFaqModal = false">Hủy</button>
        <button class="btn" form="faqForm" type="submit">Lưu câu hỏi FAQ</button>
      </template>
    </AdminModal>

    <!-- MODAL 5: XEM CHI TIẾT ĐƠN HÀNG -->
    <AdminModal
      :show="showOrderModal"
      :title="`Chi tiết đơn hàng #${selectedOrder?.id?.slice(-6)?.toUpperCase() || ''}`"
      icon="📦"
      maxWidth="700px"
      @close="showOrderModal = false"
    >
      <div v-if="selectedOrder" class="order-detail-view">
        <div class="order-detail-header">
          <div>
            <span class="muted">Ngày đặt:</span>
            <strong>{{ formatDate(selectedOrder.created_at) }}</strong>
          </div>
          <div>
            <span class="muted">Trạng thái:</span>
            <span class="status-pill" :class="selectedOrder.status">
              {{ formatStatus(selectedOrder.status) }}
            </span>
          </div>
        </div>

        <div class="order-detail-section">
          <h4>Thông tin người nhận</h4>
          <p>
            <strong>{{ selectedOrder.shipping_address?.full_name }}</strong> · {{ selectedOrder.shipping_address?.phone }}<br />
            {{ selectedOrder.shipping_address?.address }}, {{ selectedOrder.shipping_address?.district ? selectedOrder.shipping_address.district + ', ' : '' }}{{ selectedOrder.shipping_address?.city }}
          </p>
          <p v-if="selectedOrder.shipping_address?.note" class="muted">
            <em>Ghi chú: {{ selectedOrder.shipping_address.note }}</em>
          </p>
        </div>

        <div class="order-detail-section">
          <h4>Danh sách sản phẩm trong đơn</h4>
          <div class="order-items-table">
            <div v-for="(it, i) in selectedOrder.items" :key="i" class="order-item-detail-row">
              <div>
                <strong>{{ it.name }}</strong>
                <small v-if="it.color || it.size" class="muted d-block">
                  Màu: {{ it.color }} · Size: {{ it.size }}
                </small>
              </div>
              <div>x {{ it.quantity }}</div>
              <div><strong>{{ formatPrice(it.price * it.quantity) }}</strong></div>
            </div>
          </div>
        </div>

        <div class="order-detail-footer">
          <span class="muted">Phương thức: {{ selectedOrder.payment_method === 'cod' ? 'Thanh toán khi nhận hàng (COD)' : 'Chuyển khoản' }}</span>
          <div class="order-total-highlight">
            <span>Tổng thanh toán:</span>
            <strong>{{ formatPrice(selectedOrder.total) }}</strong>
          </div>
        </div>
      </div>
      <template #footer>
        <button class="btn" type="button" @click="showOrderModal = false">Đóng</button>
      </template>
    </AdminModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminActivityLog from '../components/admin/AdminActivityLog.vue'
import AdminDataTable from '../components/admin/AdminDataTable.vue'
import AdminModal from '../components/admin/AdminModal.vue'
import { adminApi, chatApi, orderApi, productApi } from '../services'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const currentSection = ref('dashboard')
const loading = ref(false)

// Menu danh sách bên trái
const menuItems = [
  { key: 'dashboard', label: 'Dashboard', icon: '📊' },
  { key: 'categories', label: 'Quản lý danh mục', icon: '📂' },
  { key: 'products', label: 'Quản lý sản phẩm', icon: '👗' },
  { key: 'orders', label: 'Quản lý đơn hàng', icon: '📦' },
  { key: 'promotions', label: 'Quản lý khuyến mãi', icon: '🎁' },
  { key: 'store_info', label: 'Quản lý thông tin shop', icon: '🏪' },
  { key: 'chatbot', label: 'Dữ liệu Chatbot AI', icon: '🤖' },
]

// Dữ liệu quản trị
const dashboard = ref({})
const categories = ref([])
const products = ref([])
const orders = ref([])
const promotions = ref([])
const faqs = ref([])
const chatLogs = ref([])
const productImportInput = ref(null)
const importingProducts = ref(false)

// Trạng thái modal
const showCategoryModal = ref(false)
const editingCategory = ref(null)
const categoryForm = reactive({ name: '', slug: '', description: '' })

const showProductModal = ref(false)
const editingProduct = ref(null)
const productForm = reactive({
  name: '',
  category_id: '',
  price: 299000,
  sale_price: null,
  stock: 50,
  colorsStr: 'Đen, Trắng',
  sizesStr: 'S, M, L, XL',
  imageUrl: '',
  description: '',
  is_featured: false,
})

const showPromoModal = ref(false)
const promoForm = reactive({
  code: '',
  title: '',
  discount_type: 'percent',
  discount_value: 15,
  min_order_value: 0,
  description: '',
})

const showFaqModal = ref(false)
const faqForm = reactive({ question: '', answer: '', category: 'general' })

const showOrderModal = ref(false)
const selectedOrder = ref(null)

const storeForm = reactive({
  name: 'FASHION STORE AI',
  hotline: '1900 6868',
  email: 'hotro@fashionstore.vn',
  address: 'Tầng 3, Fashion Center, 180 Hai Bà Trưng, Quận 1, TP.HCM',
  working_hours: '8:30 - 22:00 tất cả các ngày trong tuần',
  description: 'Hệ thống thời trang cao cấp tích hợp trợ lý ảo AI Stylist tư vấn 24/7',
  return_policy: 'Miễn phí đổi trả trong 30 ngày đối với sản phẩm còn nguyên tem mác.',
  shipping_policy: 'Miễn phí vận chuyển cho đơn hàng từ 500.000đ. Đồng kiểm cùng shipper.',
})
const storeSuccessMessage = ref('')
const reindexing = ref(false)
const reindexResult = ref('')

// Lịch sử hoạt động
const activityLogs = ref(JSON.parse(localStorage.getItem('fs_admin_logs') || '[]'))

function addLog(section, type, title, description) {
  const newLog = {
    id: Date.now(),
    section,
    type,
    title,
    description,
    user: auth.user?.full_name || 'Admin',
    timestamp: new Date().toISOString(),
  }
  activityLogs.value.unshift(newLog)
  if (activityLogs.value.length > 50) activityLogs.value.pop()
  localStorage.setItem('fs_admin_logs', JSON.stringify(activityLogs.value))
}

function getSectionLogs(section) {
  return activityLogs.value.filter((l) => l.section === section)
}

function clearLogs() {
  activityLogs.value = []
  localStorage.removeItem('fs_admin_logs')
}

// Columns definition for AdminDataTable
const categoryColumns = [
  { key: 'name', label: 'Tên danh mục', sortable: true },
  { key: 'slug', label: 'Đường dẫn (Slug)', sortable: true },
  { key: 'description', label: 'Mô tả tóm tắt' },
  { key: 'is_active', label: 'Trạng thái', width: '150px', filterType: 'select', filterOptions: [{ label: 'Đang hoạt động', value: 'true' }, { label: 'Tạm ẩn', value: 'false' }] },
  { key: 'actions', label: 'Thao tác', width: '160px', filterable: false, align: 'center' },
]

const productColumns = computed(() => [
  { key: 'image', label: 'Ảnh', width: '70px', filterable: false },
  { key: 'name', label: 'Tên sản phẩm', sortable: true },
  {
    key: 'category_name',
    label: 'Danh mục',
    sortable: true,
    filterType: 'searchable-select',
    filterOptions: categories.value.map((c) => ({ label: c.name, value: c.name })),
  },
  { key: 'price', label: 'Giá bán', sortable: true, width: '150px' },
  { key: 'stock', label: 'Tồn kho', sortable: true, width: '100px', align: 'center' },
  { key: 'actions', label: 'Thao tác', width: '160px', filterable: false, align: 'center' },
])

const orderColumns = [
  { key: 'id', label: 'Mã đơn', width: '120px', sortable: true },
  { key: 'customer', label: 'Khách hàng', sortable: true },
  { key: 'items_count', label: 'Số món', width: '90px', align: 'center', filterable: false },
  { key: 'total', label: 'Tổng tiền', width: '140px', sortable: true },
  {
    key: 'status',
    label: 'Trạng thái',
    width: '180px',
    filterType: 'select',
    filterOptions: [
      { label: 'Chờ xác nhận', value: 'pending' },
      { label: 'Đã duyệt đơn', value: 'confirmed' },
      { label: 'Đang giao hàng', value: 'shipping' },
      { label: 'Giao thành công', value: 'completed' },
      { label: 'Đã hủy đơn', value: 'cancelled' },
    ],
  },
  { key: 'actions', label: 'Thao tác', width: '110px', filterable: false, align: 'center' },
]

const dashboardOrderColumns = [
  { key: 'id', label: 'Mã đơn' },
  { key: 'total', label: 'Tổng tiền' },
  { key: 'status', label: 'Trạng thái' },
]

const promoColumns = [
  { key: 'code', label: 'Mã Voucher', width: '160px', sortable: true },
  { key: 'title', label: 'Tiêu đề khuyến mãi', sortable: true },
  { key: 'discount', label: 'Mức giảm', width: '140px' },
  { key: 'is_active', label: 'Trạng thái', width: '150px' },
  { key: 'actions', label: 'Thao tác', width: '110px', filterable: false, align: 'center' },
]

const faqColumns = [
  { key: 'question', label: 'Câu hỏi FAQ', sortable: true },
  { key: 'answer', label: 'Câu trả lời của shop' },
  { key: 'actions', label: 'Thao tác', width: '110px', filterable: false, align: 'center' },
]

const chatLogColumns = [
  { key: 'question', label: 'Câu hỏi của khách' },
  { key: 'answer', label: 'Phản hồi từ AI Stylist' },
]

const statusList = [
  { key: 'pending', label: '⏳ Chờ xác nhận' },
  { key: 'confirmed', label: '✔️ Đã duyệt đơn' },
  { key: 'shipping', label: '🚚 Đang giao hàng' },
  { key: 'completed', label: '🎉 Giao thành công' },
  { key: 'cancelled', label: '❌ Đã hủy đơn' },
]

const statusMap = {
  pending: 'Chờ xác nhận',
  confirmed: 'Đã duyệt đơn',
  shipping: 'Đang giao hàng',
  completed: 'Giao thành công',
  cancelled: 'Đã hủy đơn',
}

const featuredProducts = computed(() => {
  return products.value.filter((p) => p.is_featured).slice(0, 5)
})

function formatPrice(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value || 0)
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('vi-VN') : '—'
}

function formatStatus(status) {
  return statusMap[status] || status
}

function handleLogout() {
  auth.logout()
  router.push('/')
}

// ================= API LOADERS =================
async function loadAllData() {
  loading.value = true
  try {
    const [dash, catRes, prodRes, ordRes, promoRes, faqRes, logRes, storeRes] = await Promise.all([
      adminApi.dashboard(),
      productApi.categories({ active_only: false }),
      adminApi.products({ page_size: 100 }),
      orderApi.adminOrders(),
      productApi.promotions({ active_only: false }),
      chatApi.faqs(),
      chatApi.chatLogs(),
      chatApi.storeInfo().catch(() => ({ data: null })),
    ])

    dashboard.value = dash.data || {}
    categories.value = catRes.data || []
    products.value = prodRes.data.items || []
    orders.value = ordRes.data || []
    promotions.value = promoRes.data || []
    faqs.value = faqRes.data || []
    chatLogs.value = logRes.data || []

    if (storeRes?.data) {
      Object.assign(storeForm, storeRes.data)
    }
  } catch (error) {
    console.error('Lỗi tải dữ liệu admin:', error)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const { data } = await productApi.categories({ active_only: false })
  categories.value = data || []
}

async function loadProducts() {
  const { data } = await adminApi.products({ page_size: 100 })
  products.value = data.items || []
}

function parseCsvProducts(text) {
  const rows = []
  let row = []
  let field = ''
  let insideQuotes = false

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index]
    if (character === '"') {
      if (insideQuotes && text[index + 1] === '"') {
        field += '"'
        index += 1
      } else {
        insideQuotes = !insideQuotes
      }
    } else if (character === ',' && !insideQuotes) {
      row.push(field)
      field = ''
    } else if ((character === '\n' || character === '\r') && !insideQuotes) {
      row.push(field)
      if (row.some((value) => value.trim())) rows.push(row)
      row = []
      field = ''
      if (character === '\r' && text[index + 1] === '\n') index += 1
    } else {
      field += character
    }
  }

  if (insideQuotes) throw new Error('File CSV có dấu ngoặc kép chưa đóng.')
  row.push(field)
  if (row.some((value) => value.trim())) rows.push(row)
  if (rows.length < 2) throw new Error('File CSV không có dữ liệu sản phẩm.')

  const headers = rows[0].map((header, index) => {
    const normalized = header.trim().replace(/^\uFEFF/, '').toLowerCase()
    if (!normalized) throw new Error(`Cột thứ ${index + 1} chưa có tên.`)
    return normalized
  })
  return rows.slice(1).map((values) => Object.fromEntries(
    headers.map((header, index) => [header, values[index] || '']),
  ))
}

function parseImportList(value) {
  if (Array.isArray(value)) return value
  if (value === null || value === undefined || value === '') return []
  const text = String(value).trim()
  if (text.startsWith('[')) {
    const parsed = JSON.parse(text)
    if (!Array.isArray(parsed)) throw new Error('Danh sách phải là một mảng.')
    return parsed
  }
  return text.split(/[;,|]/).map((item) => item.trim()).filter(Boolean)
}

function parseImportNumber(value, fieldName, required = false) {
  if ((value === null || value === undefined || value === '') && !required) return null
  const number = Number(String(value).replace(/[\s,₫]/g, ''))
  if (!Number.isFinite(number)) throw new Error(`Giá trị ${fieldName} không hợp lệ.`)
  return number
}

function parseImportBoolean(value, fallback = false) {
  if (value === null || value === undefined || value === '') return fallback
  return ['true', '1', 'yes', 'có', 'co'].includes(String(value).trim().toLowerCase())
}

function buildProductImportPayload(record) {
  const values = Object.fromEntries(
    Object.entries(record).map(([key, value]) => [key.trim().toLowerCase(), value]),
  )
  const name = String(values.name || '').trim()
  if (!name) throw new Error('Thiếu tên sản phẩm (name).')

  const categoryValue = String(values.category_id || values.category_name || values.category || '').trim()
  const category = categories.value.find((item) =>
    item.id === categoryValue || item.name.toLowerCase() === categoryValue.toLowerCase(),
  )
  if (!category) throw new Error(`Không tìm thấy danh mục "${categoryValue || '(trống)'}".`)

  return {
    name,
    slug: values.slug ? String(values.slug).trim() : undefined,
    description: String(values.description || ''),
    price: parseImportNumber(values.price, 'price', true),
    sale_price: parseImportNumber(values.sale_price, 'sale_price'),
    category_id: category.id,
    images: parseImportList(values.images || values.image_url),
    colors: parseImportList(values.colors),
    sizes: parseImportList(values.sizes),
    variants: parseImportList(values.variants),
    tags: parseImportList(values.tags),
    stock: parseImportNumber(values.stock || 0, 'stock', true),
    is_featured: parseImportBoolean(values.is_featured),
    is_active: parseImportBoolean(values.is_active, true),
  }
}

function openProductImport() {
  productImportInput.value?.click()
}

async function handleProductImport(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  importingProducts.value = true
  try {
    if (categories.value.length === 0) await loadCategories()
    const content = await file.text()
    let records
    if (file.name.toLowerCase().endsWith('.json')) {
      const parsed = JSON.parse(content)
      records = Array.isArray(parsed) ? parsed : parsed.products
      if (!Array.isArray(records)) throw new Error('JSON phải là danh sách sản phẩm hoặc có trường products.')
    } else {
      records = parseCsvProducts(content)
    }

    let imported = 0
    const failures = []
    for (const [index, record] of records.entries()) {
      try {
        await productApi.create(buildProductImportPayload(record))
        imported += 1
      } catch (error) {
        failures.push(`Dòng ${index + 2}: ${error.response?.data?.detail || error.message}`)
      }
    }

    if (imported > 0) {
      addLog('product', 'import', 'Import sản phẩm', `Đã thêm ${imported} sản phẩm từ file ${file.name}`)
      await loadProducts()
    }
    const summary = `Đã import ${imported}/${records.length} sản phẩm.`
    alert(failures.length ? `${summary}\n${failures.slice(0, 5).join('\n')}` : summary)
  } catch (error) {
    alert(error.response?.data?.detail || error.message || 'Không thể đọc file sản phẩm.')
  } finally {
    importingProducts.value = false
  }
}

async function loadOrders() {
  const { data } = await orderApi.adminOrders()
  orders.value = data || []
}

async function loadPromotions() {
  const { data } = await productApi.promotions({ active_only: false })
  promotions.value = data || []
}

async function loadFaqs() {
  const { data } = await chatApi.faqs()
  faqs.value = data || []
}

async function loadChatLogs() {
  const { data } = await chatApi.chatLogs()
  chatLogs.value = data || []
}

// ================= CRUD CATEGORY =================
function openCreateCategoryModal() {
  editingCategory.value = null
  Object.assign(categoryForm, { name: '', slug: '', description: '' })
  showCategoryModal.value = true
}

function openEditCategoryModal(cat) {
  editingCategory.value = cat
  Object.assign(categoryForm, {
    name: cat.name,
    slug: cat.slug,
    description: cat.description || '',
  })
  showCategoryModal.value = true
}

async function submitCategoryForm() {
  try {
    if (editingCategory.value) {
      await productApi.updateCategory(editingCategory.value.id, { ...categoryForm })
      addLog('category', 'update', `Cập nhật danh mục: ${categoryForm.name}`, `Đã cập nhật thông tin danh mục`)
    } else {
      await productApi.createCategory({ ...categoryForm })
      addLog('category', 'create', `Thêm mới danh mục: ${categoryForm.name}`, `Tạo danh mục mới thành công`)
    }
    showCategoryModal.value = false
    await loadCategories()
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi lưu danh mục')
  }
}

async function handleDeleteCategory(cat) {
  if (confirm(`Bạn có chắc chắn muốn xóa danh mục "${cat.name}" không?`)) {
    try {
      await productApi.deleteCategory(cat.id)
      addLog('category', 'delete', `Xóa danh mục: ${cat.name}`, `Đã xóa danh mục khỏi hệ thống`)
      await loadCategories()
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa danh mục')
    }
  }
}

// ================= CRUD PRODUCT =================
function openCreateProductModal() {
  editingProduct.value = null
  Object.assign(productForm, {
    name: '',
    category_id: categories.value[0]?.id || '',
    price: 299000,
    sale_price: null,
    stock: 50,
    colorsStr: 'Đen, Trắng',
    sizesStr: 'S, M, L, XL',
    imageUrl: '',
    description: '',
    is_featured: false,
  })
  showProductModal.value = true
}

function openEditProductModal(prod) {
  editingProduct.value = prod
  Object.assign(productForm, {
    name: prod.name,
    category_id: prod.category_id,
    price: prod.price,
    sale_price: prod.sale_price,
    stock: prod.stock || 50,
    colorsStr: (prod.colors || []).join(', '),
    sizesStr: (prod.sizes || []).join(', '),
    imageUrl: prod.images?.[0] || '',
    description: prod.description || '',
    is_featured: Boolean(prod.is_featured),
  })
  showProductModal.value = true
}

async function submitProductForm() {
  const payload = {
    name: productForm.name,
    category_id: productForm.category_id,
    price: Number(productForm.price),
    sale_price: productForm.sale_price ? Number(productForm.sale_price) : null,
    stock: Number(productForm.stock) || 0,
    colors: productForm.colorsStr.split(',').map((s) => s.trim()).filter(Boolean),
    sizes: productForm.sizesStr.split(',').map((s) => s.trim()).filter(Boolean),
    images: productForm.imageUrl ? [productForm.imageUrl] : [],
    description: productForm.description,
    is_featured: productForm.is_featured,
  }

  try {
    if (editingProduct.value) {
      await productApi.update(editingProduct.value.id, payload)
      addLog('product', 'update', `Cập nhật sản phẩm: ${payload.name}`, `Giá: ${formatPrice(payload.price)} · Tồn kho: ${payload.stock}`)
    } else {
      await productApi.create(payload)
      addLog('product', 'create', `Thêm mới sản phẩm: ${payload.name}`, `Giá niêm yết: ${formatPrice(payload.price)}`)
    }
    showProductModal.value = false
    await loadProducts()
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi lưu sản phẩm')
  }
}

async function handleDeleteProduct(prod) {
  if (confirm(`Bạn có chắc chắn muốn xóa sản phẩm "${prod.name}" không?`)) {
    try {
      await productApi.remove(prod.id)
      addLog('product', 'delete', `Xóa sản phẩm: ${prod.name}`, `Đã gỡ sản phẩm khỏi danh sách`)
      await loadProducts()
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa sản phẩm')
    }
  }
}

// ================= CRUD ORDER =================
async function handleUpdateOrderStatus(id, newStatus) {
  try {
    await orderApi.updateOrderStatus(id, newStatus)
    addLog('order', 'status', `Đổi trạng thái đơn #${id.slice(-6).toUpperCase()}`, `Chuyển sang: ${formatStatus(newStatus)}`)
    await loadOrders()
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi cập nhật trạng thái')
  }
}

function openOrderDetailModal(order) {
  selectedOrder.value = order
  showOrderModal.value = true
}

// ================= CRUD PROMOTIONS =================
function openCreatePromoModal() {
  Object.assign(promoForm, {
    code: '',
    title: '',
    discount_type: 'percent',
    discount_value: 15,
    min_order_value: 0,
    description: '',
  })
  showPromoModal.value = true
}

async function submitPromoForm() {
  try {
    await productApi.createPromotion({
      code: promoForm.code.toUpperCase().trim(),
      title: promoForm.title,
      discount_type: promoForm.discount_type,
      discount_value: Number(promoForm.discount_value),
      min_order_value: Number(promoForm.min_order_value) || 0,
      description: promoForm.description,
      is_active: true,
    })
    addLog('promo', 'create', `Tạo voucher: ${promoForm.code}`, `Mức giảm: ${promoForm.discount_value}${promoForm.discount_type === 'percent' ? '%' : 'đ'}`)
    showPromoModal.value = false
    await loadPromotions()
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi tạo mã khuyến mãi')
  }
}

async function handleDeletePromo(promo) {
  if (confirm(`Xóa mã khuyến mãi "${promo.code}"?`)) {
    try {
      await productApi.deletePromotion(promo.id)
      addLog('promo', 'delete', `Xóa voucher: ${promo.code}`, `Đã xóa mã khuyến mãi`)
      await loadPromotions()
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa mã')
    }
  }
}

// ================= CRUD STORE INFO =================
async function saveStoreInfo() {
  try {
    await chatApi.updateStoreInfo({ ...storeForm })
    storeSuccessMessage.value = '✓ Đã cập nhật và lưu thông tin cửa hàng thành công!'
    addLog('store', 'update', 'Cập nhật thông tin cửa hàng', `Showroom: ${storeForm.address}`)
    setTimeout(() => {
      storeSuccessMessage.value = ''
    }, 4000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi lưu thông tin shop')
  }
}

// ================= CRUD CHATBOT & FAQ =================
function openCreateFaqModal() {
  Object.assign(faqForm, { question: '', answer: '', category: 'general' })
  showFaqModal.value = true
}

async function submitFaqForm() {
  try {
    await chatApi.createFaq({ ...faqForm })
    addLog('chatbot', 'create', `Thêm câu hỏi FAQ: ${faqForm.question}`, `Đã lưu câu trả lời cho Chatbot AI`)
    showFaqModal.value = false
    const { data } = await chatApi.faqs()
    faqs.value = data || []
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi lưu câu hỏi FAQ')
  }
}

async function handleDeleteFaq(faq) {
  if (confirm(`Xóa câu hỏi FAQ này?`)) {
    try {
      await chatApi.deleteFaq(faq.id)
      addLog('chatbot', 'delete', `Xóa câu hỏi FAQ: ${faq.question}`, `Đã gỡ FAQ khỏi hệ thống`)
      const { data } = await chatApi.faqs()
      faqs.value = data || []
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa FAQ')
    }
  }
}

async function handleReindex() {
  reindexing.value = true
  reindexResult.value = ''
  try {
    const { data } = await chatApi.reindex()
    reindexResult.value = `✓ Đồng bộ thành công! Đã nạp ${data.indexed_documents} tài liệu sản phẩm & FAQ vào Vector Store ChromaDB.`
    addLog('chatbot', 'update', 'Đồng bộ dữ liệu Vector DB', `Đã đánh chỉ mục ${data.indexed_documents} tài liệu`)
  } catch {
    reindexResult.value = 'Lỗi đồng bộ dữ liệu. Vui lòng kiểm tra lại dịch vụ AI Core.'
  } finally {
    reindexing.value = false
  }
}

onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
  background: #f4efe7;
}

/* SIDEBAR BÊN TRÁI */
.admin-sidebar {
  background: #1c1915;
  color: #f7f2ea;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding-bottom: 1.2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1.2rem;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.brand-badge-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--accent-gold);
  color: #171411;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.06em;
}

.brand-role {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #c4b9ad;
}

.admin-user-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.06);
  padding: 0.75rem 0.9rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--accent);
  color: #ffffff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-details strong {
  font-size: 0.88rem;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-details small {
  font-size: 0.72rem;
  color: #a89f94;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Sidebar Nav */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.nav-item-btn {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: #aea397;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.nav-item-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  transform: translateX(3px);
}

.nav-item-btn.active {
  background: var(--accent);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(17, 75, 67, 0.4);
}

.nav-icon {
  font-size: 1.15rem;
}

.nav-label {
  flex: 1;
}

.sidebar-footer {
  padding-top: 1.2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-sidebar-link {
  display: flex;
  align-items: center;
  padding: 0.65rem 0.8rem;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #c4b9ad;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-sidebar-link:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
}

.text-danger {
  color: #ff8a80 !important;
}

.text-danger:hover {
  background: rgba(255, 82, 82, 0.15) !important;
}

/* MAIN CONTENT */
.admin-main {
  padding: 2.2rem;
  overflow-y: auto;
}

.section-content {
  max-width: 1300px;
  margin: 0 auto;
}

.page-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 700;
  margin: 0 0 0.35rem;
  color: var(--ink);
}

.page-desc {
  margin: 0;
  color: var(--muted);
  font-size: 0.95rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

/* Stats Overview Grid */
.stats-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.4rem;
  margin-bottom: 2rem;
}

.stat-box {
  background: #ffffff;
  border-radius: var(--radius);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  transition: all 0.25s ease;
}

.stat-box.clickable {
  cursor: pointer;
}

.stat-box.clickable:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
  border-color: var(--accent);
}

.stat-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
}

.bg-blue { background: #e3f2fd; color: #1976d2; }
.bg-green { background: #e8f5e9; color: #2e7d32; }
.bg-orange { background: #fff3e0; color: #f57c00; }
.bg-purple { background: #ede7f6; color: #673ab7; }

.stat-meta {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--muted);
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--ink);
  line-height: 1.2;
}

.stat-sub {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 0.2rem;
}

.text-accent {
  color: var(--accent);
}

/* Dashboard Recent Grid */
.dashboard-recent-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.panel-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--line);
}

.panel-header-row h3 {
  font-family: var(--font-display);
  font-size: 1.4rem;
  margin: 0;
}

.featured-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.featured-item-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.6rem;
  border-radius: 8px;
  background: var(--bg);
}

.featured-item-row img {
  width: 44px;
  height: 52px;
  object-fit: cover;
  border-radius: 6px;
}

.f-info {
  flex: 1;
}

.f-info strong {
  display: block;
  font-size: 0.9rem;
}

.badge-tag {
  background: var(--accent);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
}

.sub-section-title {
  font-family: var(--font-display);
  font-size: 1.35rem;
  margin: 0 0 1rem;
}

.mb-4 {
  margin-bottom: 2rem;
}

/* Table Elements */
.table-thumb {
  width: 44px;
  height: 54px;
  object-fit: cover;
  border-radius: 6px;
  background: var(--bg-deep);
}

.table-product-name {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.tag-featured {
  display: inline-block;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  width: fit-content;
}

.old-price-sub {
  color: var(--muted);
  text-decoration: line-through;
  font-size: 0.78rem;
  margin-left: 0.4rem;
}

.code-badge {
  background: var(--accent-light);
  color: var(--accent);
  font-family: monospace;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.88rem;
}

.badge-status {
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.badge-status.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge-status.inactive {
  background: var(--danger-soft);
  color: var(--danger);
}

.status-dropdown,
.status-pill {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.82rem;
  border: 1px solid var(--line-strong);
  outline: none;
}

.status-dropdown.pending, .status-pill.pending { background: #fff8e1; color: #b78103; }
.status-dropdown.confirmed, .status-pill.confirmed { background: #e1f5fe; color: #0277bd; }
.status-dropdown.shipping, .status-pill.shipping { background: #e8f5e9; color: #2e7d32; }
.status-dropdown.completed, .status-pill.completed { background: var(--accent-light); color: var(--accent); }
.status-dropdown.cancelled, .status-pill.cancelled { background: var(--danger-soft); color: var(--danger); }

.table-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-action-edit,
.btn-action-delete,
.btn-action-view {
  border: 1px solid var(--line-strong);
  background: #ffffff;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action-edit:hover { background: #e3f2fd; color: #1976d2; border-color: #1976d2; }
.btn-action-delete:hover { background: var(--danger-soft); color: var(--danger); border-color: var(--danger); }
.btn-action-view:hover { background: var(--accent-light); color: var(--accent); border-color: var(--accent); }

/* Forms in Modals & Pages */
.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.checkbox-field {
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.form-grid-panel {
  background: #ffffff;
  padding: 2.2rem;
}

.alert-success {
  padding: 0.9rem 1.2rem;
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
  border-radius: 10px;
  font-weight: 600;
  margin-top: 1rem;
}

.btn-reindex {
  background: var(--accent-gold);
  color: #171411;
  font-weight: 700;
}

.btn-reindex:hover {
  background: #b58133;
}

.reindex-result-box {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
  padding: 1rem 1.4rem;
  margin-bottom: 1.5rem;
}

/* Order Detail View */
.order-detail-header {
  display: flex;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.2rem;
}

.order-detail-section {
  margin-bottom: 1.4rem;
}

.order-detail-section h4 {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  color: var(--accent);
}

.order-items-table {
  background: var(--bg);
  padding: 0.8rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.order-item-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
}

.order-detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.order-total-highlight strong {
  font-size: 1.3rem;
  color: var(--accent);
  margin-left: 0.5rem;
}

@media (max-width: 1024px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }
  .admin-sidebar {
    height: auto;
    position: static;
  }
  .dashboard-recent-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .form-row-2, .form-row-3 {
    grid-template-columns: 1fr;
  }
  .admin-main {
    padding: 1.2rem;
  }
}
</style>
