1. Document.pdf
- Mô tả nội dung, chức năng của bài đề tài: Phân tích cảm xúc của mã chứng khoán theo bài báo
3. Code-crawl-and-clean-data
- Lấy dữ liệu từ nguồn cafeF và lọc dữ liệu (tin tức chứng khoán và doanh nghiệp)
5. Code-model
- SummarizeArticle2Model.ipynb: Tóm tắt nội dung bài báo theo từng mã chứng khoán: Sử dụng OpenAI và các thành viên của team tóm tắt bài báo theo từng mã cổ phiếu 
- phoBert_Training.ipynb: Training mô hình sentiment analytics để gán nhãn dữ liệu: positive/ negative/ neutral
- phoBert_Inferrence.ipynd: gán nhãn dữ liệu, chạy data thật. 
6. API specification.xlsx & sentiment-analytics
- API specification.xlsx: Mô tả chi tiết 2 API 
- sentiment-analytics: chứa code API get-stock-information (search các MCK) và API insert-article-in-db (thêm các bài viết mới vào database để model xử lý và phân tích - Sử dụng Azure CosmosDB để lưu trữ dữ liệu (hệ thống cloud))
7. Website_SA
- Front-end:
   - /Website_SA/index.html và /Website_SA/dashboard.html: để xem giao diện
   - Bao gồm 2 chức năng search data và insert data.
   - Sử dụng ngôn ngữ HTML/CSS: để viết front-end.
   - File: /Website_SA/index.html và /Website_SA/dashboard.html và /Website_SA/font-type.css
- Back-end:
   - Mục đích để gọi API search và API insert data, kiểm tra required fields và logics kết quả.
   - Sử dụng ngôn ngữ javascript: để viết back-end.
   - File: /Website_SA/xlsx.full.min.js và /Website_SA/jszip.js và /Website_SA/action
   - Folder ảnh: Chứa các ảnh cho màn hình. /Website_SA/image/
   - Folder files: Chứa file template (trong phần insert data): /Website_SA/file/
