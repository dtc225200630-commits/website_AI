import sys
import logging

# Cấu hình logging để ghi lại thông tin và lỗi
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MayTinh:
    """Lớp thực hiện các phép toán cơ bản: Cộng, Trừ, Nhân, Chia."""
    
    def __init__(self, so_1, so_2):
        """Khởi tạo hai số hạng."""
        self.so_1 = so_1
        self.so_2 = so_2

    def tinh_tong(self):
        """Trả về tổng của hai số."""
        return self.so_1 + self.so_2

    def tinh_hieu(self):
        """Trả về hiệu của hai số."""
        return self.so_1 - self.so_2

    def tinh_tich(self):
        """Trả về tích của hai số."""
        return self.so_1 * self.so_2

    def tinh_thuong(self):
        """Trả về thương của hai số, xử lý lỗi chia cho 0."""
        if self.so_2 == 0:
            return "Lỗi: Không thể chia cho 0"
        return self.so_1 / self.so_2

def nhap_so(thong_bao):
    """Nhập số từ bàn phím và xử lý lỗi định dạng."""
    while True:
        try:
            du_lieu = input(thong_bao).strip()
            if not du_lieu:
                logging.error("Vui lòng nhập một số.")
                continue
            return float(du_lieu)
        except ValueError:
            logging.error("Định dạng không hợp lệ. Vui lòng nhập số.")
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)

def main():
    """Luồng chính thực thi chương trình."""
    print("--- MÁY TÍNH ĐA NĂNG (ENTERPRISE EDITION) ---")
    
    val1 = nhap_so("Nhập số thứ nhất: ")
    val2 = nhap_so("Nhập số thứ hai: ")

    # Khởi tạo đối tượng
    calc = MayTinh(val1, val2)

    # Hiển thị kết quả tất cả các phép tính
    print("\n" + "="*30)
    print(f"Số đã nhập: {val1} và {val2}")
    print(f"1. Tổng:    {calc.tinh_tong()}")
    print(f"2. Hiệu:    {calc.tinh_hieu()}")
    print(f"3. Tích:    {calc.tinh_tich()}")
    print(f"4. Thương:  {calc.tinh_thuong()}")
    print("="*30)

if __name__ == "__main__":
    main()
