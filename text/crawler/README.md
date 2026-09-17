# Thu Thập Dữ Liệu Văn Bản (Text Crawler)
## Đề tài: Phân loại Tin tức Tài chính Tiếng Việt (Vietnamese Financial News Classification)

Tài liệu này định nghĩa mục tiêu, phạm vi và đặc tả kỹ thuật của hệ thống thu thập dữ liệu (Crawler) từ báo điện tử **VnEconomy** nhằm đáp ứng toàn diện các tiêu chí trong bài tập lớn môn học.

---

## 1. Đối chiếu mục tiêu với yêu cầu Assignment (CO5177)

| Tiêu chí Assignment | Yêu cầu bài tập lớn | Thiết kế hệ thống Crawler | Trạng thái |
| :--- | :--- | :--- | :---: |
| **Loại dữ liệu** | Dữ liệu văn bản (Text Data) | Bài báo kinh tế, tài chính tiếng Việt | Đạt |
| **Quy mô mẫu** | Tối thiểu **2.000 samples** | Mục tiêu crawl: **2.500 – 3.000 bài** (dự phòng suy hao sau deduplication và filtering) | Đạt |
| **Ngôn ngữ** | Khuyến khích sử dụng tập dữ liệu tiếng Việt | 100% tiếng Việt từ nguồn báo chính thống uy tín (**VnEconomy.vn**) | Đạt |
| **Phương thức thu thập** | Sinh viên tự thu thập (*crawling*) để tạo tập riêng được đánh giá cao | Tự động hóa pipeline crawl bằng Python (`Requests`, `BeautifulSoup` / `Playwright`) | Đạt |
| **Bài toán hạ nguồn** | Mô hình hóa học máy (Classification) | Phân loại chủ đề tin tức đa lớp (*Multi-class Topic Classification*) | Đạt |
| **Tính ứng dụng & học thuật** | Phù hợp chuẩn bài toán NLP thực tế | Tương đồng benchmark học thuật quốc tế (e.g. *ViFinClass*) | Đạt |

---

## 2. Mục tiêu kỹ thuật của Crawler

### 2.1. Mục tiêu định lượng (Quantitative Targets)
- **Tổng số lượng bài viết:** $\ge 2.500$ bài báo hợp lệ.
- **Số lượng chuyên mục (Classes):** Tối thiểu 5 chuyên mục riêng biệt.
- **Độ cân bằng dữ liệu:** Thu thập đều đặn $\approx 500 - 600$ bài/chuyên mục để giảm thiểu mất cân bằng nhãn (*Class Imbalance*).

### 2.2. Danh mục 5 chuyên mục chính thu thập (Top-level Categories)
Hệ thống thu thập dữ liệu trực tiếp theo **5 Chuyên mục Chính (Top-level Parent Categories)** trên báo điện tử **VnEconomy**:

1. **Chứng khoán** (`Stock Market`)
2. **Tài chính** (`Finance & Banking`)
3. **Bất động sản** (`Real Estate`)
4. **Thế giới** (`World Economy`)
5. **Thị trường** (`Domestic Market & Industry`)

#### Bảng cấu trúc 5 chuyên mục chính & các nhánh con trực thuộc:
| 5 Chuyên mục chính | Các nhánh con trực thuộc trên VnEconomy | Nội dung & Ranh giới nhãn |
| :--- | :--- | :--- |
| **Chứng khoán** | • `Doanh nghiệp niêm yết`, `Thị trường` *(url chứa /chung-khoan)*, `Đầu tư` *(chứng khoán)*, `Quốc tế`, `Khung pháp lý` *(chứng khoán)* | Cổ phiếu, VN-Index, thanh khoản, sàn HoSE/HNX, phân tích kỹ thuật, báo cáo tài chính doanh nghiệp niêm yết. |
| **Tài chính** | • `Ngân hàng`, `Thị trường vốn`, `Thuế`, `Bảo hiểm` *(tài chính)* | Tín dụng, lãi suất điều hành, nợ xấu, chính sách tiền tệ, thị trường trái phiếu, bảo hiểm thương mại, thuế. |
| **Bất động sản** | • `Chính sách`, `Thị trường` *(url chứa /bat-dong-san)*, `Dự án`, `Cafe BĐS`, `Tư vấn`, `Hạ tầng` | Thị trường nhà đất, quy hoạch, pháp lý đất đai, condotel, dự án, đất nền và công trình hạ tầng kỹ thuật. |
| **Thế giới** | • `Kinh tế`, `Chuyển động 24h`, `Kinh doanh` *(thế giới)* | Động thái Fed/ECB, tỷ giá USD/EUR/JPY, lạm phát Mỹ/Âu/Á, kinh tế toàn cầu và thị trường quốc tế. |
| **Thị trường** | • `Xuất nhập khẩu`, `Công nghiệp`, `Nông sản`, `Khung pháp lý` *(thị trường)* | Thị trường hàng hóa trong nước, xuất nhập khẩu nông lâm thủy sản, công nghiệp chế biến, chuỗi cung ứng. |

#### Danh mục LOẠI BỎ (Excluded Sections để triệt tiêu nhiễu dữ liệu):
Để đảm bảo chất lượng ground-truth nhãn độc lập và sạch nhất cho bài toán Text Classification, các chuyên mục sau **bị loại bỏ hoàn toàn**:
- **Kinh tế số & Kinh tế xanh**: Tách biệt, không đưa vào để giữ 5 chuyên mục độc lập rõ ràng.
- **Multimedia** (`Video`, `eMagazine`, `Infographics`): Chứa văn bản ngắn dạng chú thích ảnh/video, không đạt chuẩn văn bản tin tức.
- **Ấn phẩm** (`The Guide`, `Tạp chí kinh tế Việt Nam`, `Tư vấn Tiêu & Dùng`): Nội dung tạp chí, chuyên san PR.
- **Tiêu & Dùng** (`Du lịch`, `Sức khỏe`, `Ẩm thực`): Tin tức đời sống, tiêu dùng cá nhân, không thuộc kinh tế - tài chính.
- **Dân sinh** (`Nhân lực`, bảo hiểm xã hội): Đời sống an sinh, nhân sự lao động.
- **Doanh nghiệp** (`Doanh nhân`, `Đối thoại`, `Kết nối`): Loại bỏ để **tránh rò rỉ và trùng lặp từ vựng nghiêm trọng** (*doanh thu, lợi nhuận, CEO*) với nhóm `Doanh nghiệp niêm yết` của `Chứng khoán`.
- **Tiêu điểm**: Mục tin tổng hợp nhiều chủ đề hỗn hợp, ranh giới nhãn không rõ ràng.

### 2.3. Phương pháp gán nhãn & Cơ sở phương pháp luận (Labeling Methodology & Provenance)

#### A. Bản chất nhãn Ground-truth (Reference Labeling)
Trong bài toán này, **Ground-truth labels are derived from the editorial categories assigned by VnEconomy** (*The category assigned by VnEconomy is treated as the reference label for supervised classification*).
- Tòa soạn VnEconomy tổ chức phân tầng nội dung bài viết theo cấu trúc chuyên mục nghiệp vụ (*editorial taxonomy*):
  - **Tài chính** $\rightarrow$ *Ngân hàng, Thị trường vốn, Thuế, Bảo hiểm*
  - **Chứng khoán** $\rightarrow$ *Doanh nghiệp niêm yết, Thị trường, Đầu tư, Quốc tế, Khung pháp lý*
  - **Bất động sản** $\rightarrow$ *Chính sách, Thị trường, Dự án, Cafe BĐS, Tư vấn, Hạ tầng*
  - **Thị trường** $\rightarrow$ *Xuất nhập khẩu, Công nghiệp, Nông sản, Khung pháp lý*
  - **Thế giới** $\rightarrow$ *Kinh tế, Chuyển động 24h, Kinh doanh*
- Quy trình hình thành nhãn:
  $$\text{Bài báo gốc} \xrightarrow{\text{VnEconomy Editor}} \text{Chuyên mục gốc (raw\_category)} \xrightarrow{\text{Project Taxonomy Mapping}} \text{5 Target Classes (category)}$$
- Nhãn tham chiếu thực nghiệm (*empirical ground-truth*) được kế thừa từ quyết định biên tập của chuyên gia báo chí, có cơ sở rõ ràng, minh bạch và có thể tái lập (*reproducible*).

#### B. Đảm bảo tính kiểm toán dữ liệu (Data Provenance & Auditability)
Việc duy trì song song trường `raw_category` và trường `category` trong schema cho phép kiểm toán độc lập (*audit*):
- Ví dụ: `raw_category = "Ngân hàng"` $\rightarrow$ `category = "Tài chính"`
- Ví dụ: `raw_category = "Doanh nghiệp niêm yết"` $\rightarrow$ `category = "Chứng khoán"`
Giữ nguyên nhãn gốc giúp người đọc và giám khảo đối soát chính xác lý do từng bài báo được quy về class tương ứng, không làm mất nguồn gốc dữ liệu ban đầu.

#### C. Vai trò của chuẩn JEL (Conceptual Motivation)
Cần phân biệt rõ: **5 target classes của project là kết quả gom cụm (aggregation/mapping) từ taxonomy của VnEconomy**. Chuẩn phân loại quốc tế JEL (*Journal of Economic Literature*) và các tài liệu của BIS/IMF chỉ đóng vai trò **nền tảng động lực lý thuyết (conceptual motivation)** giúp định hình ranh giới ngữ nghĩa giữa các lĩnh vực kinh tế - tài chính, chứ không khẳng định 5 classes này chính là chuẩn JEL nguyên bản.

### 2.4. Cấu trúc dữ liệu thu thập (Schema)
Mỗi mẫu dữ liệu được lưu trữ có cấu trúc (CSV / JSON Lines) với các trường sau:

| Tên trường | Kiểu dữ liệu | Mô tả chi tiết | Mục đích sử dụng trong Pipeline |
| :--- | :--- | :--- | :--- |
| `id` | String | MD5 hash của URL | Khử trùng lặp URL (Deduplication) |
| `url` | String | Đường link bài viết gốc | Truy vết và kiểm tra xuất xứ |
| `title` | String | Tiêu đề bài báo | Feature Extraction / Phân loại tiêu đề |
| `summary` | String | Đoạn tóm tắt (Sapo) | Bổ trợ ngữ cảnh cho Text Preprocessing |
| `content` | String | Văn bản thân bài sạch (đã loại bỏ quảng cáo, tin liên quan) | Input chính cho TF-IDF / PhoBERT / ViBERT |
| `word_count` | Integer | Số từ trong bài viết (chỉ lấy bài $\ge 100$ từ) | Lọc bài viết rác, bài ảnh, infographic |
| `raw_category` | String | Chuyên mục / tiểu mục gốc do tòa soạn VnEconomy gán | Đảm bảo **Data Provenance & Auditability** (truy xuất nguồn gốc) |
| `category` | String | Project-level target label derived from VnEconomy's editorial category | **Reference / Ground-Truth Label** cho Supervised Classification |
| `published_date` | String | Thời gian xuất bản chuẩn ISO (`YYYY-MM-DD HH:MM:SS`) | Hỗ trợ chia tập **Time-based Train/Val/Test Split** |
| `published_year_month` | String | Định dạng `YYYY-MM` | Phục vụ cân bằng mẫu theo trục thời gian (Temporal Stratification) |
| `author` | String | Tên tác giả / phóng viên (nếu có) | Phân tích tác giả (EDA) |

---

## 3. Hướng dẫn chạy chương trình

### 3.1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3.2. Lệnh thu thập dữ liệu
Chạy crawler mặc định (thu thập 2.500 bài báo, 500 bài/chuyên mục):
```bash
python crawler.py
```

Tuỳ chỉnh tham số:
```bash
python crawler.py --max-total 2500 --target-per-category 500 --delay 0.3 --output-dir data
```

Tham số dòng lệnh:
- `--target-per-category`: Số lượng bài viết tối đa cho mỗi chuyên mục (mặc định: 500).
- `--max-total`: Tổng số bài báo cần thu thập (mặc định: 2500).
- `--max-per-month-category`: Số bài tối đa mỗi chuyên mục trong một tháng để cân bằng theo dòng thời gian (mặc định: 60, nhập 0 nếu tắt).
- `--delay`: Thời gian nghỉ giữa các request tính bằng giây (mặc định: 0.25).
- `--output-dir`: Thư mục lưu kết quả CSV và JSONL (mặc định: `data`).

### 3.3. Tính năng chính
- Tự động quét theo danh mục sitemap hàng tháng từ `sitemap.xml`.
- Khử trùng lặp qua mã MD5 của URL.
- Tự động cân bằng số lượng mẫu giữa 5 nhóm chuyên mục mục tiêu.
- Cơ chế Checkpoint: Lưu định kỳ sau mỗi 50 bài báo, cho phép tiếp tục cào mà không bị mất dữ liệu khi gián đoạn.

---

## 4. Căn cứ học thuật & Tài liệu tham khảo (References)

Phép gom cụm các chuyên mục nghiệp vụ của VnEconomy thành **5 Target Classes** sử dụng các tiêu chuẩn phân loại quốc tế làm **nền tảng động lực lý thuyết (conceptual motivation)** nhằm định hình ranh giới ngữ nghĩa độc lập giữa các mảng kinh tế – tài chính:

1. **Chuẩn phân loại JEL (Journal of Economic Literature Classification System) - Hiệp hội Kinh tế Hoa Kỳ (AEA):**
   - [JEL Codes Guide](https://www.aeaweb.org/econlit/jelCodes.php): Đóng vai trò tham chiếu lý thuyết để phân định các trường ngữ nghĩa:
     - **Category G1:** [General Financial Markets](https://www.aeaweb.org/econlit/jelCodes.php?view=jel#G1) *(Cơ sở lý luận cho mảng Chứng khoán / Cổ phiếu)*.
     - **Category G2:** [Financial Institutions and Services](https://www.aeaweb.org/econlit/jelCodes.php?view=jel#G2) *(Cơ sở lý luận cho mảng Tài chính – Ngân hàng – Bảo hiểm)*.
     - **Category R3:** [Real Estate Markets](https://www.aeaweb.org/econlit/jelCodes.php?view=jel#R3) *(Cơ sở lý luận cho mảng Bất động sản)*.
     - **Category F3:** [International Finance](https://www.aeaweb.org/econlit/jelCodes.php?view=jel#F3) *(Cơ sở lý luận cho mảng Kinh tế thế giới / Dòng vốn quốc tế)*.
     - **Category E & L:** [Macroeconomics / Industrial Organization](https://www.aeaweb.org/econlit/jelCodes.php?view=jel#E) *(Cơ sở lý luận cho mảng Thị trường nội địa, hàng hóa, công nghiệp)*.

2. **Benchmark phân loại tin tức tài chính trong NLP (Financial NLP Datasets):**
   - **Reuters-21578 / RCV1 Text Categorization Collection:** Bộ benchmark kinh điển trong phân loại văn bản tin tức kinh tế đa lớp (Multi-class Financial News Categorization) do UCI Machine Learning Repository phát hành: [UCI Reuters-21578 Dataset](https://archive.ics.uci.edu/dataset/137/reuters+21578+text+categorization+collection).
   - **Malo, P., et al. (2014):** *"Good debt or bad debt: Detecting semantic orientations in economic texts"*, Journal of the Association for Information Science and Technology. Nghiên cứu tiêu biểu về Financial Text Classification và việc chia tách các luồng ngữ nghĩa tài chính.

3. **Khung phân tích Macro-Financial Linkages (BIS & IMF):**
   - [Bank for International Settlements (BIS) Research](https://www.bis.org/publ/work.htm): Mô hình giám sát ổn định tài chính toàn cầu dựa trên sự tương tác giữa 5 trụ cột: *Banking, Stock Market, Real Estate, International Capital Flows/FX, và Macroeconomic Conditions*.



