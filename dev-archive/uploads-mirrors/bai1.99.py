import sys

class MayTinh:
    """Lớp thực hiện các phép toán cơ bản sử dụng tư duy OOP."""
    
    def __init__(self, so_1, so_2):
        """Khởi tạo hai số hạng."""
        self.so_1 = so_1
        self.so_2 = so_2

    def tinh_tong(self):
        """Tính và trả về tổng của hai số hạng."""
        return self.so_1 + self.so_2

def nhap_so(thong_bao):
    """
    Nhập số từ bàn phím, xử lý lỗi định dạng và yêu cầu nhập lại cho đến khi đúng.
    """
    while True:
        try:
            du_lieu = input(thong_bao).strip()
            if not du_lieu:
                print("Lỗi: Bạn chưa nhập gì. Vui lòng nhập một con số.")
                continue
            return float(du_lieu)
        except ValueError:
            print("Lỗi: Định dạng không hợp lệ. Vui lòng nhập số thực hoặc số nguyên.")
        except (EOFError, KeyboardInterrupt):
            print("\nĐã thoát chương trình.")
            sys.exit()

def main():
    """Luồng chính thực thi chương trình."""
    print("--- CHƯƠNG TRÌNH TÍNH TỔNG (OOP VERSION) ---")
    
    # Nhập dữ liệu với logic kiểm tra lỗi và yêu cầu nhập lại
    val1 = nhap_so("Nhập số thứ nhất: ")
    val2 = nhap_so("Nhập số thứ hai: ")

    # Khởi tạo đối tượng từ lớp MayTinh
    phep_tinh = MayTinh(val1, val2)
    tong = phep_tinh.tinh_tong()

    # In kết quả định dạng f-string chuyên nghiệp
    print("-" * 20)
    print(f"Tổng của {val1} và {val2} là: {tong}")
    print("-" * 20)

if __name__ == "__main__":
    main()
