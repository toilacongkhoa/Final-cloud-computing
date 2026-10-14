# Minh chứng tuần 1

14 ảnh PNG gốc được sao chép nguyên vẹn từ các ảnh sinh viên cung cấp, không chỉnh sửa nội dung. Thời gian dưới đây đọc từ đồng hồ trong ảnh, ngày 10/10/2026, UTC+7. Ảnh chụp form cấu hình được phân biệt với ảnh thông báo lưu/tạo thành công.

| Ảnh | Giờ hiển thị | Nội dung và giới hạn |
| --- | --- | --- |
| [01-learner-lab.png](01-learner-lab.png) | 11:49 | AWS màu xanh; ngân sách hiển thị Used $0 of $50 |
| [02-console-region.png](02-console-region.png) | 11:51 | Console mở được, Account ID và Region us-east-1 |
| [03-iam-policy-read-denied.png](03-iam-policy-read-denied.png) | 11:56 | Lỗi iam:GetPolicy cho VocLabPolicy1; không chứng minh quyền deployment bị chặn |
| [04-default-vpc.png](04-default-vpc.png) | 12:54 | Danh sách có một default VPC; cột ID không hiển thị trong ảnh này |
| [05-subnet-ids-cidrs.png](05-subnet-ids-cidrs.png) | 12:58 | Sáu subnet Available; IDs, CIDRs và VPC |
| [06-subnet-availability-zones.png](06-subnet-availability-zones.png) | 13:00 | AZs và route table theo cùng thứ tự dòng với ảnh 05 |
| [07-route-table.png](07-route-table.png) | 13:05 | Main route table, VPC và hai route Active |
| [08-alb-inbound-form.png](08-alb-inbound-form.png) | 13:13 | Form ALB SG: TCP 80/8080 từ My IP /32 |
| [09-alb-tags-form.png](09-alb-tags-form.png) | 13:15 | Form ALB SG: Project/Owner; outbound còn trống lúc này |
| [10-alb-created.png](10-alb-created.png) | 13:16 | Tạo ALB SG thành công, ID, 2 inbound/0 outbound — trạng thái trung gian |
| [11-task-rules-tags-form.png](11-task-rules-tags-form.png) | 13:20 | Form task SG: inbound từ ALB SG, outbound HTTPS và Project/Owner |
| [12-task-created.png](12-task-created.png) | 13:21 | Tạo task SG thành công, ID, 1 inbound/1 outbound |
| [13-alb-outbound-form.png](13-alb-outbound-form.png) | 13:25 | Form ALB SG: TCP 8080 tới task SG |
| [14-alb-outbound-saved.png](14-alb-outbound-saved.png) | 13:26 | Lưu outbound ALB SG thành công; 1 outbound TCP 8080 |

Ảnh 14 là minh chứng mới nhất cho outbound ALB SG, thay cho trạng thái chưa có outbound ở ảnh 09–10. Các ảnh form tags chưa thay thế việc xem lại tab Tags trên console sau khi tạo.

Xem [báo cáo chuẩn bị nền tảng AWS và Git](../../CHUAN_BI_NEN_TANG_AWS_VA_GIT.md) và [kết quả kiểm tra Learner Lab](../../KET_QUA_KIEM_TRA_AWS_LEARNER_LAB.md). Ảnh chứa thông tin tài khoản/phiên đăng nhập phục vụ minh chứng lớp học; sinh viên rà nội dung trước khi tự công khai repository.
