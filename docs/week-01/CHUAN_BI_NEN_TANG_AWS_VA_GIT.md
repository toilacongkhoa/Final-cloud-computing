# Chuẩn bị nền tảng AWS và Git — Tuần 1

- **Đề tài:** Blue/Green deployment cho ECS với AWS CodeDeploy.
- **Ngày ghi nhận:** 10/10/2026, UTC+7.
- **Account ID:** `217376138299`.
- **Region:** `us-east-1` — N. Virginia.
- **Tags của nhóm:** `Project=ecs-bluegreen-demo`, `Owner=khoa-dat`.
- **Kết luận:** Đã chuẩn bị nền tảng mạng, kiểm tra IAM ban đầu và tổ chức tài liệu/minh chứng trong repository local. Commit và push do sinh viên thực hiện sau.

Kết quả AWS dưới đây được đối chiếu từ ảnh và thông tin sinh viên cung cấp. Không có thao tác tạo tài nguyên AWS hoặc truy vấn console mới trong bước hoàn thiện tài liệu này. Đây là kết quả chuẩn bị; chưa xác nhận ứng dụng chạy qua ALB hoặc deployment/rollback thành công.

## 1. Phạm vi và checklist

| Hạng mục | Kết quả | Minh chứng |
| --- | --- | --- |
| Truy cập Learner Lab và Console | Đã kiểm tra; sử dụng `us-east-1` | [Kết quả kiểm tra lab](KET_QUA_KIEM_TRA_AWS_LEARNER_LAB.md) |
| IAM có sẵn | Đã kiểm tra trust của `LabRole`; nội dung ba custom policies bị chặn đọc | [Kết quả IAM](KET_QUA_KIEM_TRA_AWS_LEARNER_LAB.md#5-kiểm-tra-labrole) |
| VPC và hai subnet khác AZ | Đã chọn sử dụng mạng có sẵn | Mục 2 |
| Route ra Internet | Đã xác nhận route tới Internet Gateway ở trạng thái Active | Mục 3 |
| Security group cho ALB | Đã tạo; hai inbound rules, một outbound rule sau cập nhật | Mục 4 |
| Security group cho ECS task | Đã tạo; một inbound rule và một outbound rule | Mục 4 |
| Project/Owner tags | Đã điền khi tạo hai security groups | Mục 5 |
| Git repository local và remote | Đã kiểm tra; có remote `origin` | Mục 6 |
| Tài liệu và ảnh trong dự án | Đã lưu và liên kết | [Danh mục ảnh](evidence/week-01/README.md) |
| Commit/push | Sinh viên tự thực hiện; chưa làm trong bước này | Mục 6 |

ECR, ECS service, ALB/listeners, target groups, CloudWatch và CodeDeploy là phần triển khai tiếp theo. Chưa có minh chứng tạo các tài nguyên đó trong bộ ảnh này. S3 chưa được chuẩn bị và không được đưa vào phương án hiện tại; nếu sau này chọn lưu revision trên S3 thì bổ sung cấu hình và minh chứng.

## 2. VPC và subnet được chọn

Sử dụng **default VPC có sẵn** `vpc-01cefe25cf51f1293`, mạng IPv4 `172.31.0.0/16`. Không tạo VPC hoặc subnet mới trong bước này.

Hai subnet được chọn cho cấu hình ALB/ECS ở bước triển khai:

| Vai trò | Subnet ID | Availability Zone | IPv4 CIDR |
| --- | --- | --- | --- |
| Subnet A | `subnet-0dd4e6a728f1a7476` | `us-east-1a` | `172.31.16.0/20` |
| Subnet B | `subnet-039825a0b49e43f75` | `us-east-1b` | `172.31.32.0/20` |

Ảnh danh sách cho thấy sáu subnet Available, thuộc cùng VPC và cùng route table. Hai subnet trên là lựa chọn thiết kế; chưa có ALB/ECS service để gắn subnet vào. Thông tin AZ được đối chiếu theo thứ tự dòng giữa ảnh danh sách ID/CIDR và ảnh danh sách AZ.

- [Default VPC](evidence/week-01/04-default-vpc.png).
- [Subnet IDs và CIDRs](evidence/week-01/05-subnet-ids-cidrs.png).
- [Availability Zones và route table](evidence/week-01/06-subnet-availability-zones.png).

## 3. Route table và Internet Gateway

- **Main route table:** `rtb-02f08db969e7a3be8`.
- **Internet Gateway:** `igw-033330f9a6a5ae975`.
- **VPC:** `vpc-01cefe25cf51f1293`.

| Destination | Target | Trạng thái trong ảnh |
| --- | --- | --- |
| `172.31.0.0/16` | `local` | Active |
| `0.0.0.0/0` | `igw-033330f9a6a5ae975` | Active |

Các subnet đang sử dụng route table này có route ra Internet, phù hợp phương án public subnet. Khi chạy Fargate theo thiết kế, cần cấu hình public IP cho task và kiểm tra pull image/gửi log thực tế. Route Active riêng lẻ chưa chứng minh một task kết nối được Internet.

![Route table với hai route Active](evidence/week-01/07-route-table.png)

## 4. Security groups đã tạo

Cả hai security groups thuộc VPC `vpc-01cefe25cf51f1293`.

| Tên | Security group ID | Mục đích |
| --- | --- | --- |
| `bg-alb-sg` | `sg-0b2f0910bab760484` | Gắn cho ALB ở bước triển khai |
| `bg-task-sg` | `sg-09c234bb4a8e6fbcf` | Gắn cho ECS task ENI ở bước triển khai |

### 4.1. ALB security group

| Chiều | Protocol / port | Source hoặc destination | Mục đích |
| --- | --- | --- | --- |
| Inbound | TCP 80 / HTTP | `171.250.165.238/32` — My IP lúc cấu hình | Truy cập production listener từ máy demo |
| Inbound | TCP 8080 | `171.250.165.238/32` — My IP lúc cấu hình | Truy cập test listener từ máy demo |
| Outbound | TCP 8080 | `sg-09c234bb4a8e6fbcf` — `bg-task-sg` | ALB gửi request và health check tới task |

Ảnh lúc tạo ALB SG ghi nhận **0 outbound rules**. Đây là trạng thái trung gian; ảnh cập nhật sau đó ghi nhận đã lưu thành công **1 outbound rule TCP 8080**. Destination được thể hiện ở ảnh form ngay trước khi lưu.

- [Form inbound](evidence/week-01/08-alb-inbound-form.png).
- [Tạo ALB SG thành công — trước khi bổ sung outbound](evidence/week-01/10-alb-created.png).
- [Form outbound trỏ tới task SG](evidence/week-01/13-alb-outbound-form.png).
- [Lưu outbound thành công — trạng thái mới nhất](evidence/week-01/14-alb-outbound-saved.png).

Nếu IP công cộng của máy demo thay đổi, cập nhật hai inbound rules trước khi thử truy cập.

### 4.2. ECS task security group

| Chiều | Protocol / port | Source hoặc destination | Mục đích |
| --- | --- | --- | --- |
| Inbound | TCP 8080 | `sg-0b2f0910bab760484` — `bg-alb-sg` | Nhận request và health check từ ALB |
| Outbound | TCP 443 / HTTPS | `0.0.0.0/0` | Cho phép kết nối HTTPS để lấy image và gửi log |

Form tạo task SG thể hiện rules trên; ảnh tạo thành công xác nhận ID và số lượng **1 inbound / 1 outbound**. Chưa có ảnh thử kết nối từ task đang chạy; các rules này chưa phải bằng chứng runtime hoạt động.

- [Form task rules và tags](evidence/week-01/11-task-rules-tags-form.png).
- [Tạo task SG thành công](evidence/week-01/12-task-created.png).

Không thay outbound HTTPS của task bằng rule trỏ về chính task SG. Rule TCP 8080 trỏ tới task SG được cấu hình ở **ALB SG**.

## 5. Tags và IAM

Hai form tạo security group đã điền:

| Key | Value |
| --- | --- |
| `Project` | `ecs-bluegreen-demo` |
| `Owner` | `khoa-dat` |

Minh chứng: [ALB tags](evidence/week-01/09-alb-tags-form.png), [task tags](evidence/week-01/11-task-rules-tags-form.png). Bộ ảnh chưa có tab Tags sau khi tạo; báo cáo ghi nhận giá trị đã điền ở form cùng kết quả tạo thành công. Chưa có bằng chứng gắn tags của nhóm cho default VPC/subnet/route table dùng chung.

Sử dụng `LabRole` có sẵn theo hướng dẫn lab cho CodeDeploy service role và ECS task/execution role. Không tạo hoặc chỉnh sửa IAM role trong bước này. Trust đã được kiểm tra; quyền PassRole và thao tác triển khai còn cần xác nhận khi chạy thật. Xem [báo cáo Learner Lab](KET_QUA_KIEM_TRA_AWS_LEARNER_LAB.md).

## 6. Chuẩn bị Git và tài liệu

Repository local đã được khởi tạo Git, đang ở branch `main`, có remote `origin` trỏ tới [Final-cloud-computing](https://github.com/toilacongkhoa/Final-cloud-computing). Đây là kết quả kiểm tra cấu hình local; chưa kiểm chứng quyền push hoặc trạng thái đồng bộ hiện tại với máy chủ.

| Tài liệu / thư mục | Nội dung |
| --- | --- |
| [README](README.md) | Điểm vào các tài liệu của dự án |
| [Kiểm tra Learner Lab](KET_QUA_KIEM_TRA_AWS_LEARNER_LAB.md) | Truy cập, Region, ngân sách, IAM và giới hạn |
| [Tìm hiểu blue/green](TIM_HIEU_BLUE_GREEN.md) | Luồng triển khai và rollback |
| [Sơ đồ kiến trúc](SO_DO_KIEN_TRUC.md) | Thiết kế tổng thể và nền tảng mạng đã chuẩn bị |
| Tài liệu này | Inventory mạng, security groups, tags và tình trạng Git |
| [Minh chứng tuần 1](evidence/week-01/README.md) | 14 ảnh gốc được sao chép từ ảnh sinh viên đã cung cấp |
| [Worklog tuần 1](WORKLOG_TUAN_1.md) | Mẫu ghi công việc; sinh viên điền phân công và giờ thực tế |

Giữ nguyên `.gitignore` hiện có. File hướng dẫn local `HUONG_DAN_TRIEN_KHAI.md` đang được ignore; các tài liệu được liên kết ở bảng trên không phụ thuộc vào việc đưa file đó lên Git.

**Chưa stage, commit hoặc push trong bước hoàn thiện này.** Sinh viên tự rà thay đổi, điền worklog và thực hiện commit/push. Không lưu AWS access keys, secret keys hoặc session tokens vào repository.

## 7. Bàn giao cho bước triển khai tiếp theo

Nền tảng mạng và bộ tài liệu local đã sẵn sàng. Khi thực hiện tuần 2:

1. Mở lại phiên Learner Lab, giữ Region `us-east-1`; đối chiếu các ID với console hiện tại và cập nhật My IP nếu thay đổi.
2. Chuẩn bị ứng dụng demo/Docker image, ECR và CloudWatch log group.
3. Tạo ALB với hai subnet đã chọn, dùng `bg-alb-sg`; tạo hai target groups loại `ip`, HTTP 8080.
4. Tạo ECS service với controller `CODE_DEPLOY`, task dùng `bg-task-sg` và role theo hướng dẫn lab.
5. Cấu hình CodeDeploy/AppSpec, kiểm thử baseline rồi triển khai và rollback; lưu kết quả thực tế.

Không xóa default VPC, subnet dùng chung hoặc `LabRole` khi dọn tài nguyên của nhóm. Bộ ảnh hiện tại chưa chứng minh đã dọn mọi tài nguyên tính phí trong tài khoản.

Tài liệu được AI hỗ trợ tổng hợp từ ảnh và thông tin sinh viên cung cấp. Sinh viên cần rà lại và giải thích được các cấu hình khi vấn đáp. Hoàn thành mục này không đồng nghĩa đã hoàn thành toàn bộ tuần 1 hoặc đủ số giờ worklog.
