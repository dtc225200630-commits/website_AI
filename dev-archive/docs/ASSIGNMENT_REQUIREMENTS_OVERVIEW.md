# Thong tin bai tap va quy tac cham diem
## Quy tac cham diem (theo man hinh cham bai)
- Cong thuc: Cu phap + Yeu cau + Cau truc + Phan tich + Test (moi muc toi da 20, tong 100)
- Muc LLM chi ho tro nhan xet, khong cong vao tong diem
- Cac thanh phan diem (bang evaluation_sessions):
  - syntax_score (Cu phap)
  - requirement_score (Yeu cau)
  - structure_score (Cau truc)
  - code_analysis_score (Phan tich)
  - test_score (Test)
  - llm_score (LLM - khong tinh tong)

## Bai tap 1
- Tieu de: Viet chuong trinh cong 2 so
- Mo ta: Nhap 2 so va in ra tong
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Co dung input() (trong so: 10.00)
2. Co phep cong (trong so: 10.00)
3. Co print() (trong so: 10.00)

### Test cases
1. Input: 2
3 -> Output: 5 (trong so: 10.00)
2. Input: 10
20 -> Output: 30 (trong so: 10.00)
3. Input: 7
8 -> Output: 15 (trong so: 10.00)

## Bai tap 2
- Tieu de: Tinh dien tich hinh tron
- Mo ta: Nhap ban kinh r va tinh dien tich S = 3.14 * r * r
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Su dung hang so PI = 3.14 (trong so: 10.00)
2. Co ep kieu float cho ban kinh (trong so: 10.00)

### Test cases
1. Input: 5 -> Output: 78.5 (trong so: 10.00)
2. Input: 2 -> Output: 12.56 (trong so: 10.00)
3. Input: 4 -> Output: 50.24 (trong so: 10.00)

## Bai tap 3
- Tieu de: Kiem tra so chan le
- Mo ta: Nhap mot so nguyen n, in ra "Chan" hoac "Le"
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Su dung toan tu % (trong so: 10.00)
2. Su dung cau truc if...else (trong so: 10.00)
3. Su dung toan tu % (trong so: 10.00)
4. Su dung cau truc if...else (trong so: 10.00)

### Test cases
1. Input: 4 -> Output: Chan (trong so: 10.00)
2. Input: 7 -> Output: Le (trong so: 10.00)
3. Input: 100 -> Output: Chan (trong so: 10.00)

## Bai tap 4
- Tieu de: Vong lap in day so
- Mo ta: Nhap n, in cac so tu 1 den n bang vong lap for
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Su dung vong lap for (trong so: 10.00)
2. Su dung ham range() (trong so: 10.00)
3. Su dung vong lap for (trong so: 10.00)
4. Su dung ham range() (trong so: 10.00)

### Test cases
1. Input: 5 -> Output: 1
2
3
4
5 (trong so: 10.00)
2. Input: 3 -> Output: 1
2
3 (trong so: 10.00)
3. Input: 7 -> Output: 1
2
3
4
5
6
7 (trong so: 10.00)

## Bai tap 5
- Tieu de: Kiem tra so nguyen to
- Mo ta: Nhap mot so n, kiem tra n co phai so nguyen to khong. In "Yes" neu la nguyen to, "No" neu khong
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Code phai co ham kiem tra nguyen to (trong so: 5.00)
2. Input la so nguyen tu stdin (trong so: 5.00)
3. Output "Yes" hoac "No" dung theo logic (trong so: 5.00)
4. Xu ly edge case: n <= 1 (trong so: 5.00)

### Test cases
1. Input: 7 -> Output: Yes (trong so: 10.00)
2. Input: 4 -> Output: No (trong so: 10.00)
3. Input: 2 -> Output: Yes (trong so: 10.00)

## Bai tap 6
- Tieu de: Tinh giai thua
- Mo ta: Nhap so n, tinh n! (giai thua) va in ket qua
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Phai dung vong lap hoac de quy tinh giai thua (trong so: 5.00)
2. Input la so nguyen duong (trong so: 5.00)
3. Output la ket qua giai thua (trong so: 5.00)
4. Xu ly n = 0 (ket qua = 1) (trong so: 5.00)

### Test cases
1. Input: 5 -> Output: 120 (trong so: 10.00)
2. Input: 3 -> Output: 6 (trong so: 10.00)
3. Input: 0 -> Output: 1 (trong so: 10.00)

## Bai tap 7
- Tieu de: Dao nguoc chuoi
- Mo ta: Nhap mot chuoi ky tu, in chuoi do theo thu tu nguoc
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Code phai dao nguoc chuoi dau vao (trong so: 5.00)
2. Input tu stdin (trong so: 5.00)
3. Output chuoi dao nguoc (trong so: 5.00)
4. Khong dung thu vien reverse co san (trong so: 5.00)

### Test cases
1. Input: hello -> Output: olleh (trong so: 10.00)
2. Input: abc -> Output: cba (trong so: 10.00)
3. Input: Python -> Output: nohtyP (trong so: 10.00)





## Bai tap 9
- Tieu de: Kiem tra Palindrome
- Mo ta: Kiem tra xem chuoi co phai Palindrome (doi xung) khong. In "Yes" hoac "No"
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Phai so sanh chuoi voi chuoi dao nguoc (trong so: 5.00)
2. Input tu stdin (trong so: 5.00)
3. Output "Yes" hoac "No" (trong so: 5.00)
4. Xu ly ca chu hoa lan thuong (trong so: 5.00)

### Test cases
1. Input: racecar -> Output: Yes (trong so: 10.00)
2. Input: hello -> Output: No (trong so: 10.00)
3. Input: A -> Output: Yes (trong so: 10.00)

## Bai tap 10
- Tieu de: Sap xep day so
- Mo ta: Nhap n so, sap xep theo thu tu tang dan va in ket qua
- Han nop: 2026-12-30 23:59:00
- Ngon ngu: Python

### Yeu cau
1. Phai cai dat thuat toan sap xep (trong so: 5.00)
2. Input: so luong n, roi n so (trong so: 5.00)
3. Output: day so sap xep tang dan (trong so: 5.00)
4. Xu ly dung voi so am va so 0 (trong so: 5.00)

### Test cases
1. Input: 4\n3\n1\n4\n2 -> Output: 1 2 3 4 (trong so: 10.00)
2. Input: 3\n5\n2\n8 -> Output: 2 5 8 (trong so: 10.00)
3. Input: 5\n-3\n0\n5\n-1\n2 -> Output: -3 -1 0 2 5 (trong so: 10.00)

