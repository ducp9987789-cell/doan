# AGENT DEVELOPMENT & REPOSITORY HYGIENE SKILL

## 1. Tổng quan (Overview)
Tài liệu này định nghĩa các nguyên tắc bắt buộc dành cho AI Agent khi thao tác, phát triển mã nguồn, tích hợp các module AI (`ai-core`), cũng như khi thực hiện các tác vụ hỗ trợ người dùng (viết code tính năng, tạo tài liệu, xuất file báo cáo, kiểm thử và phân tích hệ thống).

---

## 2. Quy định Bảo mật Bí mật & Biến Môi trường (Zero-Secrets & Environment Security)
1. **Nghiêm cấm push file cấu hình môi trường**:
   - Tuyệt đối **KHÔNG** commit hoặc push các file chứa biến môi trường thực tế (`.env`, `.env.local`, `.env.production`, `*.env`, v.v.) lên Git repository.
   - Mọi thông tin nhạy cảm: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `JWT_SECRET_KEY`, `MONGODB_URI`, `QDRANT_API_KEY`, mật khẩu database, v.v. phải được bảo vệ và giữ cục bộ trên môi trường của người dùng.
2. **Sử dụng file mẫu `.env.example`**:
   - Khi có biến môi trường mới cần thiết lập, chỉ cập nhật vào file `.env.example` với giá trị mô phỏng/dummy (ví dụ: `your_gemini_api_key_here`).
3. **Cơ chế Gitignore**:
   - Đảm bảo file `.gitignore` ở gốc dự án luôn chứa các quy tắc loại trừ triệt để:
     ```gitignore
     .env
     .env.*
     *.env
     **/.env
     **/.env.*
     !**/.env.example
     ```

---

## 3. Quy tắc Vòng đời & Dọn dẹp File Tạm khi Tạo Tài liệu (Document Generation & Scratch Code Cleanup)
Khi người dùng sử dụng AI Agent để tạo/cập nhật các file tài liệu dạng văn bản, báo cáo (file `.docx`, `.doc`, `.txt`, `.pdf`, v.v.) mà chỉ sử dụng thông tin trong dự án để tổng hợp nội dung:

1. **Phân loại tệp tin**:
   - **Tệp tin thuộc Dự án (Project Files - BẮT BUỘC GIỮ LẠI)**:
     - Toàn bộ mã nguồn chạy ứng dụng: `backend/`, `frontend/`, `docker/`, `ai-core/`.
     - Các file cấu hình chính: `docker-compose.yml`, `package.json`, `requirements.txt`, `.gitignore`, `README.md`.
     - File tài liệu kết quả chính thức mà người dùng yêu cầu (ví dụ file báo cáo `.docx`).
   - **Tệp tin phụ trợ tạm thời (Scratch / Auxiliary Files - BẮT BUỘC XÓA SAU KHI XONG)**:
     - Các script dùng một lần được viết ra để phục vụ việc trích xuất dữ liệu, định dạng văn bản (ví dụ: các file `*.py`, `*.js` dùng `python-docx` sửa đổi văn bản, inspect docx).
     - Các file HTML/SVG trung gian tạo ra để dựng sơ đồ hoặc chụp màn hình (ví dụ: `diagram_*.html`, `test_*.js`, `render_*.js`, `cdp_capture.js`).
     - Các file backup tạm (`*.bak`), file log tạm, file nháp sinh ra trong lúc xử lý tài liệu.

2. **Nguyên tắc Dọn dẹp Tự động (Mandatory Cleanup Process)**:
   - Ngay sau khi file văn bản / tài liệu đích (`.docx`, `.txt`, `.pdf`, ...) được tạo hoặc cập nhật thành công và được xác nhận toàn vẹn:
   - AI Agent **phải chủ động rà soát và xóa bỏ toàn bộ các script, file code tạm thời** đã tạo ra để phục vụ quá trình đó.
   - Thư mục dự án phải được giữ sạch sẽ, không lưu lại code rác không phục vụ cho việc vận hành sản phẩm.

---

## 4. Quy tắc Đánh giá và Dọn dẹp File Mã Nguồn Dự án (Project Code Hygiene & Ephemeral Helper Cleanup)
Khi phát triển tính năng, tái cấu trúc (refactor) hoặc chỉnh sửa code trong dự án:

1. **Xem xét tính cần thiết và liên kết logic của mã nguồn**:
   - **File CẦN cho dự án (BẮT BUỘC GIỮ LẠI)**:
     - Các file trực tiếp tham gia vào luồng logic nghiệp vụ, kiến trúc runtime hoặc build pipeline của hệ thống.
     - Các file có liên kết phụ thuộc rõ ràng với nhau (components giao diện, router, state store, API endpoints, schemas, services, database models, AI agents/tools, test cases chính thức).
   - **File chỉ mang tính hỗ trợ hoàn thiện code chính (BẮT BUỘC XÓA SAU KHI HOÀN THÀNH)**:
     - Các file script được tạo ra tạm thời nhằm mục đích hỗ trợ việc hoàn thiện file code chính (ví dụ: script test thử nghiệm endpoint, file mock dữ liệu tạm, script chạy probe API một lần, script migration dữ liệu dùng 1 lần, script benchmark thử nghiệm).
     - **Tiêu chí xóa**: Nếu file đó không tham gia vào luồng hoạt động chính của dự án, không ảnh hưởng đến file code chính khi bị xóa, và không có bất kỳ component/module nào khác của hệ thống phụ thuộc vào nó -> **PHẢI XÓA NGAY LẬP TỨC** sau khi file code chính đã hoàn thiện và kiểm tra thành công.

2. **Nguyên tắc "Zero-Disposable Code" (Không lưu mã nguồn dùng một lần)**:
   - Không để lại các file code "mồ côi" (orphan code), file test nháp hoặc file utility dùng một lần nằm rải rác trong cây thư mục dự án.
   - Luôn đảm bảo toàn bộ mã nguồn lưu lại trong repository đều là code sản phẩm chính thức, có mục đích rõ ràng và tương tác chặt chẽ với nhau.

---

## 5. Quy trình Vận hành Chuẩn cho AI Agent (Agent Workflow Checklist)
Trước khi hoàn thành turn trả lời hoặc kết thúc bất kỳ nhiệm vụ nào, AI Agent phải thực hiện kiểm tra 4 bước:
- [ ] **Bước 1 (Secrets)**: Đảm bảo không có khóa mật (API key, token, credentials) bị lộ trong code, và không push file `.env`.
- [ ] **Bước 2 (Project Code)**: Đảm bảo các file code chính đã tích hợp đầy đủ, logic liên kết chặt chẽ; đã xóa sạch các file code tạm/script thử nghiệm sinh ra chỉ để hỗ trợ việc hoàn thiện code chính, trừ các file script/seed do chính người dùng tự thêm hoặc nhờ agent thêm.
- [ ] **Bước 3 (Document Cleanup)**: Đảm bảo nếu có tác vụ tạo tài liệu (`.docx`, `.txt`), mọi script tạm, HTML tạm và file phụ trợ phục vụ xuất tài liệu đã được dọn dẹp sạch sẽ.
- [ ] **Bước 4 (Git Status)**: Kiểm tra `git status` đảm bảo cây thư mục dự án chỉ còn đúng những file phục vụ trực tiếp cho dự án và sản phẩm bàn giao.
