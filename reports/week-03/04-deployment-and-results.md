# 4 Triển khai và kết quả kiểm thử

### 4.1 Chuẩn bị

Bổ sung FAIL_HEALTH=1 để /health trả 503 và FAIL_APP=1 để / cùng /version trả 500 trong khi /health vẫn trả 200. Mặc định không bật lỗi. Chạy 9 test đều pass; build và push image week03 lên ECR, ghim image bằng digest trong task definitions. Revision 3 là bản tốt, revision 4 lỗi health, revision 5 lỗi ứng dụng.

### 4.2 Kết quả trên AWS

| Tình huống | Deployment | Kết quả quan sát |
| --- | --- | --- |
| Bản tốt | d-69JC4V9GM | Succeeded lúc 21:30; chuyển 100% traffic sang revision 3 |
| Lỗi health | d-PIW6KA9GM | Alarm bg-tg-green-unhealthy dừng deployment; rollback d-9NAW3E9GM Succeeded |
| Lỗi ứng dụng | d-W7U8H29GM | Bản lỗi nhận 10% traffic; alarm bg-tg-green-5xx dừng deployment; rollback d-1AUF3FAGM Succeeded |

Hai deployment lỗi đều có mã ALARM_ACTIVE và thông báo automatic rollback. Không bấm dừng hoặc rollback thủ công. Với lỗi health, bản mới chưa nhận production traffic; với lỗi ứng dụng, bản mới đã nhận traffic và trả 500 trước khi traffic quay về bản tốt.

### 4.3 Đo HTTP và kết luận

| Khoảng đo | Thành công | Lỗi |
| --- | --- | --- |
| Bản tốt | 891/891 | 0 |
| Lỗi health | 481/481 | 0 |
| Lỗi ứng dụng | 862/883 | 21 HTTP 500 có chủ đích |
| Sau rollback | 30/30 | 0 |

CSV và trạng thái API được lưu trong data minh chứng. Khoảng đo lỗi ứng dụng gồm thời gian baseline trước deployment. Sau rollback, service trở về bản tốt revision 3.

[Quay lại mục lục báo cáo tuần 3](README.md)
