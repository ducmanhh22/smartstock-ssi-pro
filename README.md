# SmartStock Terminal — SSI Pro Responsive Edition

Dashboard phân tích chứng khoán có giao diện responsive cho **máy tính, máy tính bảng và điện thoại**. Chỉ dùng **SSI FastConnect** cho dữ liệu thị trường thực; Demo là dữ liệu mô phỏng có nhãn rõ. Ứng dụng **không đặt lệnh giao dịch**.

## Chạy nhanh trên Windows (VS Code)

1. Giải nén ZIP, vào VS Code → **File → Open Folder** → chọn `SmartStock_SSI_Pro` (thư mục chứa `app.py`).
2. Chọn **Terminal → New Terminal** và chạy: `py -m pip install -r requirements.txt`.
3. Chạy `py -m streamlit run app.py --server.port 8505` rồi vào `http://localhost:8505`.
4. Trong giao diện chọn **Demo (mô phỏng)** để xem đầy đủ giao diện ngay; hoặc **SSI FastConnect (thật)** → chọn mã → **Cập nhật dữ liệu**.
5. Để chạy lại cho nhanh: nhấp đúp `01_CHAY_APP.bat` sau khi đã cài thư viện, hoặc dùng `00_CAI_THU_VIEN.bat` để cài.

**Lần đầu dùng SSI:** Tạo `.env` trong cùng thư mục `app.py` bằng cách sao chép `.env.example`, rồi điền `SSI_CLIENT_ID`, `SSI_API_KEY`, `SSI_API_SECRET`. Chỉ dùng khóa **mới** đã được SSI cấp hợp lệ. `.env` không nằm trong ZIP.

## Bố cục tương thích đa thiết bị

- **Desktop:** phần nội dung rộng đến 1600px, KPI 4 cột, biểu đồ nến + panel phân tích cạnh nhau.
- **Tablet:** KPI tự chuyển 2 cột, các vùng dùng tỷ lệ khung linh hoạt.
- **Điện thoại:** KPI 2 cột (máy rất hẹp là 1 cột), biểu đồ/phân tích xếp dọc, bộ lọc nằm ngay đầu trang, danh sách mã vuốt ngang và bảng dữ liệu có thể cuộn ngang.
- Menu bên trái thu gọn tự động khi mở trên màn hình hẹp; tab phân tích cuộn ngang để không tràn trang.
- Biểu đồ sử dụng Plotly responsive, hỗ trợ chạm/zoom trên di động.

**Kiểm tra kích thước bằng Chrome PC:** nhấn `F12` → `Ctrl + Shift + M` → chọn thiết bị như iPhone 12/13 hoặc kích thước `390 × 844`, rồi tải lại trang. Thoát chế độ bằng `Ctrl + Shift + M`.

**Xem trên điện thoại thật (cùng Wi-Fi, mạng riêng tin cậy):** chạy `py -m streamlit run app.py --server.address 0.0.0.0 --server.port 8505`, trên máy tính dùng `ipconfig` xem **IPv4 Address**, rồi nhập `http://<IPv4-của-máy-tính>:8505` trên điện thoại. Nếu Windows Firewall hỏi, chỉ cho phép **Private networks**. Không mở cổng 8505 ra Internet vì app chưa có xác thực truy cập và có kết nối API.

## Các file

- `app.py`: UI responsive, biểu đồ OHLCV, RSI/MACD, bảng mã và xuất CSV.
- `ssi_data.py`: SSI FastConnect SDK, chỉ **đọc dữ liệu nến**.
- `finance.py`: xử lý nến và tính SMA5/SMA20, EMA12, RSI14, MACD, Bollinger.
- `storage.py`: lưu và đọc lịch sử SSI qua SQLite.
- `demo.py`: sinh mẫu **mô phỏng**, không phải giá thị trường.
- `.streamlit/config.toml`: theme dark mặc định.
- `tests/test_finance.py`: 8 bài kiểm thử tự động.

Chạy kiểm thử: `py -m unittest discover -s tests -v`.

## Những điều cần lưu ý

- SSI có thể trả về nến lịch sử và ứng dụng không cam kết cung cấp giá realtime.
- % biến động trong app là **trong cửa sổ nến đang chọn**, không phải % so với giá tham chiếu phiên.
- Đơn vị giá và múi giờ của nến phải được đối chiếu với quy ước dữ liệu SSI khi công bố kết quả.
- Ứng dụng phục vụ học tập/phân tích; các chỉ báo không phải lời khuyên mua bán.
- **An toàn:** API Key/Secret/Private Key từng lộ trong ảnh cần thu hồi và thay mới trên SSI. Không gửi `.env` lên mạng, GitHub hay file nộp; không chia sẻ màn hình có hiện khóa.
