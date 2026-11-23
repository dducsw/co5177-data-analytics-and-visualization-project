# Reports (`reports/`)

Thư mục lưu mã nguồn LaTeX và các báo cáo PDF theo quy định của [assignment-vne-v4.md](../requirements/assignment-vne-v4.md):

- Báo cáo PDF cho từng bài tập lớn con (`tabular`, `text`, `image`).
- Báo cáo PDF tổng hợp nộp LMS: `<groupname>-report.pdf`.

## Cấu trúc thư mục

```text
reports/
├── Makefile        # Lệnh chuẩn để tạo mới, biên dịch, kiểm tra và dọn dẹp báo cáo
├── README.md       # Hướng dẫn sử dụng (cho người dùng & AI Agent)
├── starter/        # Bộ khung sạch đã cấu hình sẵn cho CO5177 (dùng để `make init`)
└── template/       # Template gốc HCMUT_Report_Template (kèm các ví dụ tham khảo)
```

## Cách sử dụng nhanh

Từ thư mục `reports/`:

1. **Khởi tạo báo cáo mới** (ví dụ `tabular`, `text`, `image`, hoặc `final`):
   ```bash
   make init NAME=tabular
   ```
   Lệnh này sao chép `reports/starter/` sang `reports/tabular/` với cấu trúc chương tách rời (`chapters/*.tex`).

2. **Biên dịch PDF**:
   ```bash
   make build TARGET=tabular
   ```
   Hoặc biên dịch kèm kiểm tra lỗi tham chiếu (`??` / undefined citations):
   ```bash
   make check TARGET=tabular
   ```
   > **Lưu ý:** Template sử dụng gói `minted` (`codespace.sty`), bắt buộc cờ `-shell-escape` và `pygmentize` (đã cấu hình sẵn trong `Makefile`).

3. **Biên dịch tự động khi sửa file (`watch`)**:
   ```bash
   make watch TARGET=tabular
   ```

4. **Dọn file tạm sau khi biên dịch**:
   ```bash
   make clean TARGET=tabular       # Chỉ xoá file tạm (.aux, .log, _minted-*)
   make distclean TARGET=tabular   # Xoá cả file tạm và report.pdf
   ```

## Quy ước dành cho AI Agent & Cộng tác viên

- **Chỉnh sửa theo module:** Giữ `report.tex` gọn nhẹ (chỉ chứa metadata bìa và `\input{chapters/...}`). Viết nội dung vào từng file trong `chapters/`.
- **Ngôn ngữ:** `hcmut-report.cls` mặc định dùng `[english]{babel}`. Nếu viết báo cáo tiếng Việt (tiêu đề Mục lục, Hình, Bảng bằng tiếng Việt), đổi dòng `\RequirePackage[english]{babel}` trong `hcmut-report.cls` của thư mục báo cáo đó sang `\RequirePackage[english,vietnamese]{babel}`.
- **Nhãn và tham chiếu chéo:**
  - Luôn đặt `\label{...}` **sau** `\caption{...}` (không đặt trước hoặc bên trong `\caption`).
  - Dùng tiền tố chuẩn: `sec:`, `subsec:`, `fig:`, `tab:`, `eq:`, `lst:`, `app:`.
  - Dùng `\Cref{...}` (từ `cleveref`) thay cho `\ref{...}`.
- **Bảng và hình:**
  - Dùng `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), tránh kẻ dọc `|`.
  - Đặt hình xuất ra từ notebook vào `figures/` trong thư mục báo cáo tương ứng và chèn bằng `\includegraphics[width=\linewidth]{figures/...}` (hoặc `max width=\linewidth` với `adjustbox`).
  - Mọi caption hình/bảng cần nêu rõ **kết luận** và **số liệu đối chiếu** khớp với kết quả thực tế trong `notebooks/` (theo rubric trong `requirements/assignment-vne-v4.md`).
- **Không tự bịa số liệu:** Mọi metric, bảng so sánh, số lượng mẫu trong báo cáo phải trích trực tiếp từ output của notebook tương ứng.
