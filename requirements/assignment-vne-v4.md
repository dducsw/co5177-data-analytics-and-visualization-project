# BÀI TẬP LỚN MÔN HỌC
## Nền tảng lập trình cho phân tích và trực quan dữ liệu

- **Giảng viên:** Lê Thành Sách  
- **Học kỳ:** 261 | **Năm học:** 2026–2027  

---

### Lịch sử phiên bản (Version History)

| Version | Release Date | Update Summary |
| :--- | :--- | :--- |
| **v1.0** | 03 Nov 2025 | Initial release for Semester 1, Academic Year 2025–2026. |
| **v3.0** | 04 Sep 2026 | Updated for Semester 261, Academic Year 2026–2027. |
| **v4.0** | 14 Sep 2026 | Semester 261: group registration, GitHub Pages submission, multimodal scale, and 10-point creativity rubric. |

> **Note:** The latest version will be available on the course LMS.

---

## Mục lục
- [1. Mục tiêu](#1-mục-tiêu)
- [2. Mẫu tham khảo (Samples)](#2-mẫu-tham-khảo-samples)
- [3. Chia nhóm và lựa chọn tập dữ liệu](#3-chia-nhóm-và-lựa-chọn-tập-dữ-liệu)
  - [3.1 Quy định chung](#31-quy-định-chung)
  - [3.2 Khối lượng theo quy mô nhóm](#32-khối-lượng-theo-quy-mô-nhóm)
- [4. Ràng buộc đối với tập dữ liệu](#4-ràng-buộc-đối-với-tập-dữ-liệu)
  - [4.1 Nguyên tắc chung](#41-nguyên-tắc-chung)
  - [4.2 Dữ liệu bảng (Tabular)](#42-dữ-liệu-bảng-tabular)
  - [4.3 Dữ liệu văn bản (Text)](#43-dữ-liệu-văn-bản-text)
  - [4.4 Dữ liệu ảnh (Image) — Yêu cầu chi tiết](#44-dữ-liệu-ảnh-image--yêu-cầu-chi-tiết)
  - [4.5 Dữ liệu đa phương thức (Text–Image)](#45-dữ-liệu-đa-phương-thức-textimage)
- [5. Cấu trúc nội dung thực hiện](#5-cấu-trúc-nội-dung-thực-hiện)
- [6. Quy cách nộp bài](#6-quy-cách-nộp-bài)
  - [6.1 Landing page (trang giới thiệu chung)](#61-landing-page-trang-giới-thiệu-chung)
  - [6.2 Trang từng bài tập lớn con](#62-trang-từng-bài-tập-lớn-con)
  - [6.3 Báo cáo PDF và video](#63-báo-cáo-pdf-và-video)
  - [6.4 Notebook](#64-notebook)
  - [6.5 Hạn nộp](#65-hạn-nộp)
- [7. Thang điểm đánh giá (Evaluation Rubric)](#7-thang-điểm-đánh-giá-evaluation-rubric)
  - [7.1 Cách lấy 10 điểm sáng tạo, mở rộng và trình bày](#71-cách-lấy-10-điểm-sáng-tạo-mở-rộng-và-trình-bày)

---

## 1. Mục tiêu

Bài tập lớn nhằm giúp sinh viên:
- Vận dụng kiến thức về lập trình Python, hướng đối tượng (OOP) và các thư viện phổ biến: `NumPy`, `Pandas`, `Matplotlib`, `Seaborn`, `OpenCV`, `Scikit-learn`.
- Áp dụng quy trình hoàn chỉnh của phân tích dữ liệu: thu thập, tiền xử lý, EDA (*Exploratory Data Analysis*), trực quan hóa và huấn luyện mô hình học máy.
- Làm quen với nhiều loại dữ liệu khác nhau: **Tabular**, **Text**, **Image**, **Multimodal**, **Time series**.

---

## 2. Mẫu tham khảo (Samples)

Sinh viên được khuyến khích tham khảo các ví dụ sẵn có trên GitHub của giảng viên, minh họa toàn bộ quy trình từ phân tích dữ liệu, trực quan đến mô hình học máy:
- [Exploratory Data Analysis (EDA)](https://ltsach.github.io/AILearningHub/01_Data_Analysis/01_EDA/)
- [Machine Learning](https://ltsach.github.io/AILearningHub/02_Machine_Learning/)
- [Text Classification](https://ltsach.github.io/AILearningHub/04_Natural_Language_Processing/text_classification/)
- [Image Classification](https://ltsach.github.io/AILearningHub/03_Computer_Vision/)

*Sinh viên nên dựa theo cấu trúc và tinh thần của các ví dụ này để hoàn thiện bài tập lớn.*

---

## 3. Chia nhóm và lựa chọn tập dữ liệu

### 3.1 Quy định chung
Sinh viên có thể làm cá nhân hoặc theo nhóm **2–3 người**.

Tệp đăng ký dưới đây dùng để đăng ký nhóm gồm 2–3 sinh viên cùng thực hiện các bài tập của học phần Nền tảng lập trình cho phân tích và trực quan dữ liệu:  
👉 [Tệp đăng ký nhóm và landing page](https://docs.google.com/spreadsheets/d/1Uuc3o8Py17MNIcSf3qfz2ZQCIfzMDFv29KDu3I2peVI/edit?gid=1146533447#gid=1146533447)

**Các bước đăng ký nhóm:**
1. Các bạn có thể tự chọn thành viên nhóm ngoài giờ học.
2. Chọn tên nhóm — không được trùng với tên của các nhóm đã đăng ký — và nhập tên nhóm cho tất cả thành viên vào trang tính `GroupRegistration`. *Khuyến nghị:* tên nhóm nên ngắn gọn và có ý nghĩa.
3. Mỗi nhóm điền đường dẫn đến trang giới thiệu (landing page) của nhóm vào trang tính `GroupLink`.

Mỗi nhóm cần lựa chọn tập dữ liệu theo các ràng buộc nêu ở phần sau và điền thông tin đầy đủ trong tệp đăng ký.

### 3.2 Khối lượng theo quy mô nhóm
- **Sinh viên cá nhân:** Thực hiện **2 loại dữ liệu**
  - 1 bài bắt buộc: **Tabular**.
  - 1 bài tự chọn: **Text**, **Image**, **Multimodal** hoặc **Time series**.
- **Nhóm 2–3 người:** Thực hiện **3 loại dữ liệu**
  - Bắt buộc 1 bài về **Tabular**.
  - Bắt buộc 1 bài về **Text**.
  - 1 bài tự chọn trong: **Image**, **Multimodal** hoặc **Time series**.
- **Khuyến khích sử dụng các mô hình cơ bản của Scikit-learn.** Nếu áp dụng học sâu (*Deep Learning*), sinh viên có thể:
  - Tham khảo code mẫu trong các liên kết GitHub ở trên.
  - Xem các phần trích đặc trưng hoặc huấn luyện như các hàm sẵn có, không cần tìm hiểu chi tiết kiến trúc bên trong.

---

## 4. Ràng buộc đối với tập dữ liệu

### 4.1 Nguyên tắc chung
- Các nhóm nên hạn chế chọn trùng tập dữ liệu. Nếu trùng, các nhóm sẽ được chấm song song và so sánh độ sáng tạo, khác biệt trong cách tiếp cận.

### 4.2 Dữ liệu bảng (Tabular)
- Có ít nhất **2000 samples** và tối thiểu **10 cột**.
- Dữ liệu cần có missing values để thực hành thống kê và xử lý thiếu dữ liệu.
- Bao gồm các cột categorical để áp dụng kỹ thuật encoding.
- Bao gồm các cột numerical để áp dụng kỹ thuật scaling.
- Ưu tiên các tập dữ liệu có độ khó cao: *imbalanced data, outliers, ...*

### 4.3 Dữ liệu văn bản (Text)
- Có ít nhất **2000 samples**.
- Với sinh viên Việt Nam, khuyến khích sử dụng tập dữ liệu tiếng Việt.
- Sinh viên tự thu thập dữ liệu (*crawling*) để tạo tập riêng sẽ được đánh giá cao.

### 4.4 Dữ liệu ảnh (Image) — Yêu cầu chi tiết
- **Quy mô:** Tối thiểu **5000 ảnh** (tổng), ít nhất **3 lớp** (đối với classification).
- **Độ phân giải:** Khuyến nghị ảnh có cạnh ngắn $\ge$ 128 px; nếu nhỏ hơn, cần nêu rõ lý do và cách xử lý (resize, padding).
- **Tập dữ liệu:** **KHÔNG chấp nhận toy datasets** (ví dụ: *MNIST*, *Fashion-MNIST*, *CIFAR-10*) cho bài chính. Các tập này chỉ dùng để minh hoạ pipeline (không tính là dataset chính).
- **Pretrained bắt buộc (nếu dùng DL):** Sử dụng mô hình pretrained (ví dụ: *ResNet50*, *MobileNetV3*, *ViT-B/16*) theo một trong các cách:
  - *Feature extractor:* freeze backbone, trích đặc trưng $\rightarrow$ huấn luyện classifier nông.
  - *Fine-tuning nhẹ:* unfreeze một vài tầng cuối, learning rate nhỏ.  
  *(Sinh viên có thể coi mô hình như hàm sẵn dùng; không yêu cầu hiểu chi tiết kiến trúc bên trong).*
- **Split:** Nêu rõ cách chia train/val/test; tránh rò rỉ dữ liệu (*data leakage*).
- **Augmentation:** Áp dụng hợp lý (*horizontal flip, random crop/resize, color jitter, normalization...*) và giải thích mục tiêu.
- **Bài toán mở rộng:** Nếu làm *detection, segmentation, pose estimation, action recognition, re-identification, crowd counting, depth estimation, hoặc 3D reconstruction*, yêu cầu:
  - Dữ liệu cần có annotation định dạng chuẩn hoặc tự thiết kế hợp lý, có thể sử dụng các chuẩn phổ biến như:
    - *COCO, VOC, YOLO, LabelMe, Cityscapes, KITTI, MPII, OpenImages*, hoặc định dạng JSON/CSV/XML tự thiết kế miễn hợp lý.
  - Nếu tự gán nhãn, cần mô tả công cụ sử dụng (VD: *LabelImg, CVAT, Roboflow, VGG Annotator...*) và cách đảm bảo chất lượng nhãn.
  - Báo cáo cần mô tả cấu trúc thư mục, ví dụ: `images/`, `labels/`, `annotations.json`, và số lượng mẫu mỗi lớp.
- **OpenCV (tuỳ chọn):** Có thể dùng để trích đặc trưng thủ công (*SIFT, HOG, ORB, GLCM, LBP, v.v.*) nhằm đối chiếu với hướng pretrained.

### 4.5 Dữ liệu đa phương thức (Text–Image)
Nếu chọn multimodal thay cho một bài Text và một bài Image, mỗi thành phần phải đạt quy mô tương đương bài đơn phương thức. Không được dùng tập toy chỉ để minh họa.
- **Thành phần văn bản:** Ít nhất **2000 cặp** (hoặc 2000 văn bản gắn với ảnh). Khuyến khích tiếng Việt; tự thu thập được tính ở phần sáng tạo nếu có kết quả chạy được.
- **Thành phần ảnh:** Tối thiểu **5000 ảnh**, ít nhất **3 lớp** nếu là phân loại, cạnh ngắn khuyến nghị $\ge$ 128 px. Không chấp nhận *MNIST*, *Fashion-MNIST*, *CIFAR-10* làm tập chính.
- **Mỗi mẫu phải gắn text với đúng ảnh** (không ghép ngẫu nhiên). Nêu cách chia train/val/test để không rò rỉ cùng một ảnh hoặc cùng một văn bản sang nhiều tập.

---

## 5. Cấu trúc nội dung thực hiện

Bài tập lớn được thực hiện dưới dạng `.ipynb`, chạy trực tiếp trên **Google Colab**. Mỗi loại dữ liệu được trình bày trong một file riêng biệt.

1. **Mô tả tập dữ liệu:**
   - Sử dụng Markdown để mô tả thông tin tổng quan.
   - Dùng Plotly, Matplotlib hoặc Seaborn để trực quan dữ liệu.
2. **Chuẩn bị dữ liệu:**
   - Tiền xử lý bằng NumPy hoặc Pandas.
   - Xử lý missing values, outliers, ...
   - Encoding dữ liệu dạng categorical.
   - Scaling dữ liệu dạng numerical.
   - Chia dữ liệu thành train, validation và test.
3. **Phân tích và mô hình hóa:**
   - Huấn luyện mô hình bằng Scikit-learn.
   - So sánh kết quả giữa các mô hình hoặc tham số khác nhau.
4. **Tổng kết và mở rộng:**
   - Đánh giá kết quả qua độ chính xác, biểu đồ, confusion matrix, ...
   - Trình bày nhận xét, hạn chế và đề xuất hướng mở rộng.

---

## 6. Quy cách nộp bài

Bài làm phải được công bố trên **GitHub Pages**. Link landing page (trang giới thiệu chung của nhóm) được ghi vào sheet `GroupLink`. Notebook, video và các file khác được liên kết từ landing page; không thay thế trang này.  
👉 [Tệp đăng ký nhóm và landing page](https://docs.google.com/spreadsheets/d/1Uuc3o8Py17MNIcSf3qfz2ZQCIfzMDFv29KDu3I2peVI/edit?gid=1146533447#gid=1146533447)

### 6.1 Landing page (trang giới thiệu chung)
Mỗi nhóm duy trì một landing page công khai trên GitHub Pages. Trang này phải có đủ các nhóm thông tin sau:

- **Thông tin môn học:**
  - Trường: Đại học Bách Khoa – ĐHQG-HCM.
  - Khoa: Khoa Khoa học và Kỹ thuật Máy tính.
  - Tên học phần: Nền tảng lập trình cho phân tích và trực quan dữ liệu.
  - Học kỳ 261, năm học 2026–2027.
  - Giảng viên: Lê Thành Sách.
- **Thông tin nhóm:**
  - Tên nhóm (trùng khớp sheet `GroupRegistration`).
  - Danh sách thành viên: họ tên, MSSV, vai trò hoặc phần đóng góp chính của từng người.
  - Link GitHub của thành viên nếu có (không tạo link giả).
  - Link kho mã nguồn (repository) của nhóm.
- **Mục lục các bài tập lớn con:**
  - Landing page phải có link rõ ràng đến từng bài tập lớn con tương ứng từng loại dữ liệu nhóm thực hiện (Tabular, Text, Image, Multimodal hoặc Time series).
  - Mỗi bài con là một trang (hoặc mục) riêng, không gộp chung vào một trang dài không mục lục.

### 6.2 Trang từng bài tập lớn con
Mỗi trang bài con phải có:
- Tên bài và loại dữ liệu.
- Tên nhóm và danh sách thành viên.
- Mô tả bài toán và tập dữ liệu.
- Link notebook (GitHub và/hoặc Google Colab chạy được Run all).
- Link file PDF report của bài đó.
- Link video trình bày trên YouTube.

### 6.3 Báo cáo PDF và video
- Mỗi bài tập lớn con có một PDF report tóm tắt cách làm và kết quả, và một video trình bày (khuyến nghị 5–10 phút).
- Video ở chế độ Public hoặc Unlisted. Nhóm tự kiểm tra link trước khi nộp.
- Gợi ý tiêu đề video: `[Tên nhóm] – [Loại dữ liệu] – Nền tảng lập trình`.
- Cuối khóa, một thành viên đại diện nộp thêm báo cáo PDF tổng hợp lên LMS, tên file:
  ```text
  <groupname>-report.pdf
  ```
  *Ví dụ:* nhóm DataViz nộp `DataViz-report.pdf`. Tên nhóm phải trùng sheet `GroupRegistration`. PDF trên LMS không thay thế landing page và các link video.

### 6.4 Notebook
- Mỗi loại dữ liệu là một file `.ipynb` riêng.
- File phải chạy hoàn chỉnh (**Run all**) trên Google Colab, không lỗi.
- Notebook có phần Markdown giải thích quy trình, biểu đồ và kết quả.

### 6.5 Hạn nộp
- Landing page, các trang bài con (kèm PDF và video) và file PDF trên LMS được hoàn thành đúng hạn cuối khóa.
- Link landing page phải được điền vào `GroupLink` trước hạn đăng ký do giảng viên thông báo trên LMS.

---

## 7. Thang điểm đánh giá (Evaluation Rubric)

| STT | Thành phần đánh giá | Trọng số (%) |
| :---: | :--- | :---: |
| 1 | Chất lượng và hoàn thiện các notebook (`.ipynb`) | 50% |
| 2 | Báo cáo, giải thích, trình bày Markdown | 20% |
| 3 | Video demo và khả năng trình bày | 15% |
| 4 | Tính sáng tạo, mở rộng, và trình bày có kết luận | 10% |
| 5 | Hình thức nộp (GitHub Pages, landing page, PDF và video từng bài, PDF LMS) | 5% |
| | **Tổng cộng** | **100%** |

### 7.1 Cách lấy 10 điểm sáng tạo, mở rộng và trình bày
10 điểm này không thay phần bắt buộc (notebook chạy được, EDA, mô hình, nộp bài). Chạy lại end-to-end (**Run all**) là yêu cầu bắt buộc, không cộng vào cột này.

Được điểm khi có hình hoặc bảng trả lời một câu hỏi, caption ghi kết luận, và có số liệu đối chiếu. Không cộng điểm vì đổi màu, thêm word cloud, hoặc dùng Plotly cho đẹp hơn mà không nêu được điều gì.

- **0 điểm:** Chỉ có biểu đồ bắt buộc (phân phối, missing values, cân bằng lớp, confusion matrix) và không có thí nghiệm thêm.
- **4 điểm:** Mỗi loại dữ liệu có thêm ít nhất một hình đúng câu hỏi, caption nêu kết luận.
- **7 điểm:** Hình đó có số so sánh (trước/sau xử lý, mô hình A so với B, mẫu đúng so với mẫu sai).
- **10 điểm:** Mỗi loại dữ liệu của nhóm đạt mức 7, và kết luận khớp bảng metric trong report.

**Gợi ý hình được tính (chọn, không cần làm hết):**
- **Tabular:** Target so với 2–3 feature; phân phối trước/sau scale; so sánh baseline với mô hình mở rộng (imbalance, outlier, feature importance).
- **Text:** Từ hoặc n-gram phân biệt lớp; confusion matrix kèm ví dụ bị gán sai; so TF-IDF với embedding hoặc với tập tự thu thập.
- **Ảnh:** Mẫu dự đoán sai; so traditional ML trên vector pretrained với transfer learning trên cùng test set.
- **Time series:** Split theo thời gian; dự báo so với thực tế.
- **Multimodal:** Baseline từng modality so với mô hình ghép, chỉ ra modality nào kéo chất lượng lên hoặc xuống.

Các điểm sáng tạo khác vẫn được tính nếu có kết quả chạy được và giải thích được, ví dụ tự thu thập dữ liệu, trùng dataset nhưng cách tiếp cận khác và có số đối chiếu, hoặc bài toán mở rộng (detection, segmentation, ...) đủ annotation. Đề xuất “có thể làm sau” mà không chạy thì không cộng điểm.
