Tổng hợp toàn bộ lý thuyết, mô hình ML, metric nghiệp vụ và phương pháp trực quan nâng cao trong notebook:

---

### 1. Lý thuyết Dữ liệu & Bản chất bài toán (Tabular Fraud Detection)

#### 1.1 Mất cân bằng lớp cực đoan (Extreme Class Imbalance)
- **Bản chất:** Lớp gian lận ($y=1$) chỉ chiếm **~1.1%**, lớp người dùng thật ($y=0$) chiếm **~98.9%**.
- **Accuracy Paradox:** Nếu mô hình đoán 100% hồ sơ là "không gian lận", độ chính xác (Accuracy) vẫn đạt $98.9\%$, nhưng mô hình hoàn toàn vô dụng. Không bao giờ dùng Accuracy làm hàm mục tiêu hay metric chính.

#### 1.2 Trôi dạt dữ liệu theo thời gian (Temporal Shift / Concept Drift)
- Hành vi gian lận thay đổi theo tháng (thủ đoạn mới, chiến dịch tấn công mới).
- **Hệ quả:** Dữ liệu tháng sau phân phối khác tháng trước.
- **Giải pháp - Temporal Split:** Chia dữ liệu theo mốc thời gian (Tháng 0–5: Train; Tháng 6: Validation; Tháng 7: Test).
  - *Cấm kỵ:* Dùng `train_test_split` ngẫu nhiên vì gây **Lookahead Bias** (dùng dữ liệu tương lai tháng 7 để dự đoán tháng 2 $\rightarrow$ rò rỉ dữ liệu).

#### 1.3 Dữ liệu khuyết ẩn (Hidden Missing) & Kỹ thuật `_flag`
- Tập dữ liệu mã hóa giá trị thiếu dưới dạng `-1` hoặc `< 0` (ví dụ `intended_balcon_amount`, `prev_address_months_count`).
- **Missing Not At Random (MNAR):** Kẻ gian lận thường cố tình bỏ trống một số thông tin (hoặc thông tin không tồn tại do dùng danh tính giả). Việc *thiếu dữ liệu tự nó mang thông tin phân loại rủi ro*.
- **Cách xử lý:**
  1. Gán giá trị `-1` thành `np.nan`.
  2. Tạo thêm một cột cờ nhị phân `col_flag = 1` nếu thiếu, `0` nếu có.
  3. Sau đó mới impute (điền median cho mô hình tuyến tính, hoặc để LightGBM tự xử lý).

#### 1.4 Scaler: StandardScaler vs. RobustScaler
- `StandardScaler`: Chuẩn hóa theo $\frac{x - \mu}{\sigma}$. Rất nhạy cảm với giá trị ngoại lai (outliers) vì Mean ($\mu$) và Std ($\sigma$) bị outlier kéo lệch.
- `RobustScaler`: Chuẩn hóa theo Median và IQR (Interquartile Range):
  $$\tilde{x} = \frac{x - Q_2}{Q_3 - Q_1}$$
  Giữ nguyên cấu trúc phân phối, không bị phá vỡ bởi các giao dịch đột biến (như biến `velocity_6h`, `zip_count_4w`).

---

### 2. Các mô hình Machine Learning

#### 2.1 Baseline: Logistic Regression (Phạt trọng số)
- **Cơ chế:** Phân loại tuyến tính qua hàm kích hoạt Sigmoid:
  $$P(y=1|\mathbf{x}) = \sigma(\mathbf{w}^T\mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T\mathbf{x} + b)}}$$
- **Xử lý mất cân bằng qua `class_weight='balanced'`:**
  Điều chỉnh hàm mất mát Binary Cross-Entropy (Log-loss). Phạt nặng khi mô hình đoán sai mẫu thiểu số ($y=1$):
  $$w_1 = \frac{N}{2 \cdot N_1} \approx \frac{1.000.000}{2 \times 11.000} \approx 45.45$$
  Mỗi lần đoán sót một ca gian lận, mô hình bị phạt gấp ~45 lần so với đoán nhầm một ca người dùng thật.
- **Hạn chế:** Không bắt được quan hệ phi tuyến và tương tác giữa các thuộc tính (ví dụ: `housing_status` tương tác với `device_os`).

#### 2.2 Mô hình chính: LightGBM (Light Gradient Boosting Machine)
- **Bản chất:** Ensemble dạng Boosting gồm hàng nghìn cây quyết định nông (Decision Trees). Mỗi cây mới được sinh ra để học phần phần dư (residual/gradient) mà các cây trước dự đoán sai.
- **Hai cải tiến cốt lõi:**
  1. **GOSS (Gradient-based One-Side Sampling):** Giữ lại các mẫu có gradient lớn (khó học, hay đoán sai) và lấy mẫu ngẫu nhiên nhóm mẫu có gradient nhỏ (đã học tốt) $\rightarrow$ Huấn luyện nhanh gấp nhiều lần trên 1 triệu dòng mà không giảm độ chính xác.
  2. **EFB (Exclusive Feature Bundling):** Gộp các đặc trưng thưa hiếm khi cùng khác 0 lại với nhau để giảm số chiều.
- **Xử lý missing và categorical nguyên bản (Native Support):**
  - Tự động gán NaN vào nhánh tối ưu hàm mất mát nhất tại từng node rẽ nhánh.
  - Tự gom nhóm category tối ưu theo histogram gradient mà không cần mở rộng one-hot hàng trăm cột.
- **Seed Ensemble:** Chạy 3 hạt ngẫu nhiên (`SEEDS = [42, 202, 777]`) rồi lấy trung bình xác suất $\rightarrow$ giảm phương sai (variance reduction), tăng độ mượt của dự đoán.

---

### 3. Metric đánh giá chuyên biệt

```
                  Thực tế Gian lận (1)    Thực tế Hợp lệ (0)
Dự đoán Gian lận       TP (True Positive)     FP (False Positive - Chặn nhầm)
Dự đoán Hợp lệ         FN (False Negative)    TN (True Negative)
```

#### 3.1 Nhóm Metric cơ bản
- **$\text{TPR (True Positive Rate / Recall)} = \frac{TP}{TP + FN}$:** Bắt được bao nhiêu % gian lận trong thực tế?
- **$\text{FPR (False Positive Rate)} = \frac{FP}{FP + TN}$:** Bao nhiêu % khách hàng vô tội bị nghi ngờ oan?
- **$\text{Precision} = \frac{TP}{TP + FP}$:** Trong số những hồ sơ hệ thống báo gian lận, bao nhiêu % là gian lận thật?
- **$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$:** Trung bình điều hòa giữa Precision và Recall.

#### 3.2 ROC-AUC vs. PR-AUC
- **ROC-AUC (Receiver Operating Characteristic - Area Under Curve):**
  - Vẽ đường cong $\text{TPR}$ theo $\text{FPR}$ trên mọi ngưỡng $\tau \in [0, 1]$.
  - Ý nghĩa xác suất: Khả năng mô hình cho điểm một hồ sơ gian lận ngẫu nhiên cao hơn một hồ sơ bình thường ngẫu nhiên.
  - *Nhược điểm:* Khi lớp âm ($TN$) quá lớn (989.000 dòng), $FP$ tăng lớn vẫn làm $FPR = \frac{FP}{FP+TN}$ trông rất nhỏ $\rightarrow$ ROC-AUC có xu hướng quá lạc quan trên dữ liệu imbalanced.
- **PR-AUC (Precision-Recall AUC / Average Precision):**
  - Vẽ đường cong $\text{Precision}$ theo $\text{Recall}$.
  - Tập trung hoàn toàn vào lớp dương ($TP, FP, FN$), bỏ qua $TN$. Phản ánh trực diện tổn thất nghiệp vụ.

#### 3.3 Metric nghiệp vụ thực tế: $\text{TPR@FPR} \le 5\%$
- **Ràng buộc kinh doanh:** Ngân hàng không thể kiểm duyệt tất cả khách hàng. Nếu $\text{FPR} > 5\%$, đội vận hành quá tải và khách hàng phàn nàn vì bị chặn giao dịch.
- **Định nghĩa:** Đặt giới hạn ngân sách báo động giả tối đa là 5% ($\text{FPR} \le 0.05$). Tại điểm cắt này, mô hình bắt được bao nhiêu % kẻ gian lận?
- **Quy trình chọn ngưỡng (Threshold Tuning):**
  1. Quét đường cong ROC trên **Validation set (tháng 6)**, tìm ngưỡng xác suất $\tau^*$ nhỏ nhất sao cho $\text{FPR} \le 0.05$.
  2. Cố định $\tau^*$ này, chuyển sang dự đoán trên **Test set (tháng 7)**. Nếu $P(y=1|\mathbf{x}) \ge \tau^* \rightarrow$ Báo động gian lận.

---

### 4. Phương pháp Thống kê & Phân tích Nâng cao

#### 4.1 Khoảng tin cậy Bootstrap (Bootstrap Confidence Intervals)
- **Vấn đề:** Điểm metric đơn lẻ (ví dụ $\text{TPR} = 0.560$) có thể do may rủi của tập Test. Làm sao chứng minh LightGBM tốt hơn Logistic Regression thật sự?
- **Thuật toán Bootstrap (1.000 lần):**
  1. Rút mẫu có hoàn lại ($N = 100.000$) từ tập Test 1.000 lần.
  2. Tính metric cho cả 2 mô hình và tính hiệu số: $\Delta = \text{Metric}_{\text{LGBM}} - \text{Metric}_{\text{LR}}$.
  3. Lấy phân vị 2.5% và 97.5% để tạo khoảng tin cậy 95% (95% CI).
- **Kết luận thống kê:** Nếu khoảng tin cậy của $\Delta$ nằm hoàn toàn bên dương (ví dụ $\Delta\text{TPR} \in [+0.091, +0.129]$, không chứa số 0) $\rightarrow$ Khẳng định có ý nghĩa thống kê với mức ý nghĩa $\alpha = 0.05$ ($p < 0.05$).

#### 4.2 Tính công bằng & Đạo đức AI (Fairness & Bias)
- **Hiện tượng:** Chia khách hàng theo độ tuổi ($< 50$ và $\ge 50$).
- **Predictive Equality / Equalized Odds:** Khi áp dụng cùng một ngưỡng chung $\tau^*$, nhóm lớn tuổi ($\ge 50$) có tỷ lệ bị báo động nhầm (FPR) cao hơn hoặc thấp hơn nhóm trẻ tuổi.
- **Khắc phục - Group-specific Thresholding:** Chọn ngưỡng cắt riêng cho từng nhóm nhân khẩu học sao cho $\text{FPR}_{\text{trẻ}} = \text{FPR}_{\text{già}} \le 5\%$, đảm bảo không nhóm khách hàng hợp lệ nào bị đối xử bất công do thuật toán.

---

### 5. Ý nghĩa các biểu đồ trong Notebook

```
+------------------------------------+------------------------------------+
| 1. Dual-axis Trend (Plotly)        | 2. ROC & PR Curves (Matplotlib)    |
| - Cột: Số lượng hồ sơ theo tháng   | - Trục hoành: FPR (ROC) / Recall   |
| - Đường: Tỷ lệ gian lận (%)        | - Trục tung: TPR (ROC) / Precision |
| => Thấy rõ trôi dạt (Tháng 6, 7)   | => Đối đầu LightGBM vs Baseline    |
+------------------------------------+------------------------------------+
| 3. Correlation Heatmap (Seaborn)   | 4. Boxplot/Histogram Outliers      |
| - Ma trận Pearson/Spearman         | - Biểu diễn phân phối lệch phải    |
| - Đánh giá độ tương quan đơn biến  | - So sánh trước/sau khi chuẩn hóa  |
|   giữa các đặc trưng với target    |   RobustScaler                     |
+------------------------------------+------------------------------------+
```

1. **Biểu đồ xu hướng 2 trục (Plotly Dual-axis):** Trục trái là thể tích hồ sơ (volume), trục phải là % gian lận. Chứng minh tỷ lệ gian lận biến thiên bất thường qua 8 tháng (tháng 6, 7 tăng vọt).
2. **Cặp đường cong ROC và PR (ROC/PR Curves):** Đường cong LightGBM bao trùm hoàn toàn đường cong Logistic Regression ở mọi mức ngưỡng, trực quan hóa sức mạnh vượt trội.
3. **Biểu đồ phân phối có phân tầng theo nhãn (KDE / Histplot by `fraud_bool`):** Chỉ ra các biến có tính phân tách cao (ví dụ: `name_email_similarity`, `housing_status`).