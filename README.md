1. Input data
Nguồn từ các website khác (cafeF, 24h,...): Qua quá trình crawl data. Đây là phần dữ liệu để trainning và dữ liệu được lưu trữ lại để end-user có thể tìm kiếm. File .py:
Website của team: Qua chức năng tạo mới dữ liệu. Sử dụng API insert: file .py: 
2. Xử lý data

2.1. Sử dụng Azure Databricks để làm sạch dữ liệu.
File .py: 

2.2. Tóm tắt nội dung bài báo theo từng mã chứng khoán.
Viết trên Azure Databricks.
Sử dụng OpenAI và các thành viên của team tóm tắt bài báo theo từng mã cổ phiếu và gán nhãn dữ liệu làm training set. 
Sử dung OpenAI để tóm tắt bài báo theo từng mã cổ phiếu: file .py: 

2.3. Gán nhãn dữ liệu: positive/negative/neutral:
Viết trên Azure Databricks.
Sử dụng OpenAI và các thành viên của team tóm tắt bài báo theo từng mã cổ phiếu và gán nhãn dữ liệu làm training set. 
Viết Sentiment analytics model: 
3. Lưu trữ dữ liệu
Sử dụng Azure CosmosDB để lưu trữ dữ liệu (hệ thống cloud)
Dữ liệu dạng json
Primary key: Mã chứng khoán, URL
4. API
API search: Mục đích để lấy ra thông tin Mã chứng khoán (nội dung, thời gian tạo, nhãn dán) theo yêu cầu của end-users (khoảng thời gian, mã chứng khoán hoặc nhãn dán)
Chi tiết API search: file document: /API specification.xlsx  và file .py:  /sentiment-analytics/get-stock-information/__init__.py
API insert: Mục đích để thêm mới bài báo
Chi tiết API insert: file document: /API specification.xlsx và file .py: /sentiment-analytics/insert-article-in-db/__init__.py
5. Website
Front-end:
Bao gồm 2 chức năng search data và insert data.
Sử dụng ngôn ngữ HTML/CSS: để viết front-end.
File: /Website_SA/index.html và /Website_SA/dashboard.html và /Website_SA/font-type.css
Back-end:
Mục đích để gọi API search và API insert data, kiểm tra required fields và logics kết quả.
Sử dụng ngôn ngữ javascript: để viết back-end.
File: /Website_SA/xlsx.full.min.js và /Website_SA/jszip.js và /Website_SA/action
Folder ảnh: Chứa các ảnh cho màn hình. /Website_SA/image/
Folder files: Chứa file template (trong phần insert data): /Website_SA/file/
