# Kết quả kiểm tra AWS Learner Lab — Tuần 1

- **Đề tài:** Blue/Green deployment cho ECS với AWS CodeDeploy.
- **Ngày kiểm tra:** 10/10/2026, múi giờ UTC+7.
- **Phạm vi:** Kiểm tra khả năng truy cập lab, ngân sách hiển thị, Region, dịch vụ được phép và cấu hình IAM ban đầu.
- **Kết luận:** Hoàn thành bước kiểm tra môi trường ban đầu của tuần 1. Các thao tác triển khai và rollback chưa được kiểm chứng thực tế.

## 1. Mục đích kiểm tra

Xác nhận môi trường AWS Learner Lab hỗ trợ các dịch vụ cần cho đề tài trước khi tạo tài nguyên. Kiểm tra giúp phát hiện sớm hạn chế về Region, IAM và ngân sách để chuẩn bị triển khai phù hợp.

## 2. Tài liệu và minh chứng đã xem

Kết quả được tổng hợp từ những thông tin sinh viên đã cung cấp trong quá trình kiểm tra:

1. Ảnh trang **Launch AWS Academy Learner Lab**: trạng thái AWS màu xanh, có bộ đếm thời gian và ngân sách.
2. Ảnh **AWS Console Home**: truy cập console thành công và đang chọn N. Virginia.
3. Nội dung **Trust relationships** của `LabRole`.
4. Danh sách bảy permissions policies gắn với `LabRole`.
5. Ba ảnh lỗi khi mở `VocLabPolicy1`, `VocLabPolicy2`, `VocLabPolicy3`.
6. Nội dung **Learner Lab Readme**, ghi ngày cập nhật hướng dẫn là **24/06/2025**.

Các ảnh được chọn đã sao chép nguyên vẹn vào [thư mục minh chứng tuần 1](evidence/week-01/README.md), gồm [trạng thái Learner Lab](evidence/week-01/01-learner-lab.png), [Console và Region](evidence/week-01/02-console-region.png), [lỗi đọc VocLabPolicy1](evidence/week-01/03-iam-policy-read-denied.png) và ảnh chuẩn bị mạng/security groups. Hai ảnh lỗi VocLabPolicy2/3 cùng nội dung trust/danh sách policies đã được xem qua thông tin sinh viên cung cấp, chưa được lưu thành ảnh riêng trong repository. Khi nộp bài, minh chứng cần thể hiện Account ID, Region và thời gian theo yêu cầu giảng viên, đồng thời tránh để lộ credentials/session token.

## 3. Truy cập lab, ngân sách và Region

| Nội dung | Kết quả ghi nhận | Đánh giá |
| --- | --- | --- |
| Khởi động Learner Lab | Chấm trạng thái cạnh AWS màu xanh; bộ đếm thời gian hiển thị | Đã khởi động thành công |
| Truy cập AWS Console | Đã mở được Console Home | Đạt |
| Region đang chọn | `us-east-1` — United States (N. Virginia) | Phù hợp đề bài và giới hạn lab |
| Region được phép theo Readme | `us-east-1`, `us-west-2`, trừ ngoại lệ được nêu riêng trong tài liệu lab | Đã xác định |
| Ngân sách hiển thị trong ảnh | `Used $0 of $50` | Đã ghi nhận số liệu tại thời điểm chụp |

Theo Readme, dữ liệu ngân sách thường cập nhật mỗi **8–12 giờ**. Vì vậy, số tiền hiển thị không chứng minh toàn bộ hoạt động gần nhất chưa phát sinh chi phí.

## 4. Dịch vụ được phép sử dụng

| Dịch vụ | Xác nhận từ Readme | Áp dụng cho đề tài |
| --- | --- | --- |
| Amazon ECS | Có trong danh sách dịch vụ được phép | Chạy ứng dụng container và quản lý service/task |
| AWS Fargate | Được phép; có thể assume `LabRole` | Có thể lựa chọn cho nền tảng chạy ECS task |
| AWS CodeDeploy | Được phép; có thể assume `LabRole` | Điều phối triển khai blue/green và chuyển traffic |
| Elastic Load Balancing | Được phép; có thể assume `LabRole` | Sử dụng ALB và hai target group |
| Amazon ECR | Người dùng console có quyền ghi; `LabRole` có quyền đọc | Push image bằng quyền người dùng lab; task lấy image bằng execution role |
| Amazon CloudWatch | Có trong danh sách dịch vụ được phép | Thu thập log, metric và cấu hình alarm |
| Amazon VPC | Có trong danh sách dịch vụ được phép | Chuẩn bị mạng, subnet và security group |

Danh sách trên xác nhận dịch vụ được phép theo tài liệu của lab. Chưa kiểm thử tất cả API, quota hoặc từng thao tác tạo tài nguyên của các dịch vụ này.

## 5. Kiểm tra LabRole

### 5.1. Trust relationships

Trust policy đã cung cấp có statement với:

- `Effect`: `Allow`.
- `Action`: `sts:AssumeRole`.
- Danh sách service principals bao gồm `codedeploy.amazonaws.com`, `ecs-tasks.amazonaws.com` và `ecs.amazonaws.com`.

**Kết quả:** Trust policy có các service principals cần cho CodeDeploy và ECS task. Đây là điều kiện cho phép các dịch vụ sử dụng role; không đồng nghĩa đã chứng minh toàn bộ quyền thao tác sau khi assume role.

### 5.2. Permissions policies

Trang Permissions hiển thị bảy policies:

| Policy | Loại |
| --- | --- |
| `AmazonEC2ContainerRegistryReadOnly` | AWS managed |
| `AmazonEKSClusterPolicy` | AWS managed |
| `AmazonEKSWorkerNodePolicy` | AWS managed |
| `AmazonSSMManagedInstanceCore` | AWS managed |
| Policy có tên chứa `VocLabPolicy1` | Customer managed |
| Policy có tên chứa `VocLabPolicy2` | Customer managed |
| Policy có tên chứa `VocLabPolicy3` | Customer managed |

Permissions boundary hiển thị **not set**. Tuy nhiên, việc không có boundary không chứng minh không tồn tại các giới hạn khác của lab.

Khi mở ba policies `VocLabPolicy`, AWS trả lỗi **Access denied to iam:GetPolicy**. Thông báo xác định phiên đăng nhập `voclabs` bị một identity-based policy từ chối rõ ràng thao tác đọc policy.

**Kết quả:** Đã xác nhận danh sách policies được gắn với `LabRole`, nhưng không đọc được nội dung ba customer-managed policies. Lỗi này chỉ xác nhận hạn chế đọc IAM policy của phiên đăng nhập; không đủ để kết luận `LabRole` bị chặn triển khai ECS/CodeDeploy.

Trang role còn báo không có quyền `access-analyzer:ListPolicyGenerations` khi hiển thị chức năng tạo policy từ CloudTrail. Chức năng đó không cần cho bước chuẩn bị đề tài này.

### 5.3. Cách sử dụng role theo hướng dẫn lab

- **CodeDeploy service role:** sử dụng `LabRole`, phù hợp yêu cầu đề bài và Readme.
- **ECS task role:** chọn `LabRole` theo hướng dẫn ECS trong Readme.
- **ECS task execution role:** chọn `LabRole` theo hướng dẫn ECS trong Readme.
- **Nếu dùng EC2:** sử dụng instance profile có sẵn `LabInstanceProfile` khi cần gắn role cho instance.

Không tạo IAM user/role riêng để thay thế giới hạn của bài. Quyền `iam:PassRole` và các thao tác ECS/ELB/CloudWatch cần được xác nhận khi thực hiện cấu hình và deployment thực tế; hiện chưa có kết quả kiểm thử các thao tác này.

## 6. Giới hạn và lưu ý cho giai đoạn triển khai

- Giữ tài nguyên của bài trong Region được phép.
- Nếu chọn ECS trên EC2, tuân thủ giới hạn instance nano đến large, tối đa chín instance và 32 vCPU chạy đồng thời mỗi Region theo phần giới hạn của lab; tài nguyên EC2 do dịch vụ khác tạo cũng có thể được tính vào giới hạn.
- Với EBS, áp dụng yêu cầu chặt hơn của đề bài: tổng dung lượng không quá 100 GB, sử dụng gp2/gp3.
- Gắn tag `Project` và `Owner` cho tài nguyên hỗ trợ tag.
- Theo Readme, kết thúc phiên lab vẫn giữ lại dữ liệu và tài nguyên. Cần chủ động dừng/xóa tài nguyên tính phí của nhóm sau buổi thực hành.
- Thao tác **Reset** xóa tài nguyên và dữ liệu đã tạo nhưng không đặt lại ngân sách; không sử dụng để xử lý lỗi đọc policy.

## 7. Kết luận và công việc tiếp theo

**Hoàn thành kiểm tra môi trường ban đầu của tuần 1**, với các bằng chứng:

- Truy cập Learner Lab và AWS Console thành công.
- Region hiện tại phù hợp; đã xác định giới hạn Region.
- Đã ghi nhận ngân sách hiển thị và độ trễ cập nhật.
- Tài liệu lab cho phép ECS, Fargate, CodeDeploy, ELB, ECR và CloudWatch.
- Trust của `LabRole` có CodeDeploy và ECS task; Readme hướng dẫn sử dụng role có sẵn.
- Đã ghi nhận hạn chế đọc IAM policies và không suy diễn lỗi đó thành lỗi triển khai.

**Chưa kiểm chứng:** tạo ECS task/service, pull image và ghi log thực tế, quyền PassRole, tạo deployment group, chuyển traffic, CloudWatch alarm và rollback tự động.

Đã có [tài liệu luồng blue/green](TIM_HIEU_BLUE_GREEN.md), [sơ đồ kiến trúc](SO_DO_KIEN_TRUC.md) và [kết quả chuẩn bị nền tảng AWS/Git](CHUAN_BI_NEN_TANG_AWS_VA_GIT.md). Sinh viên điền phân công và số giờ thực tế vào [worklog tuần 1](WORKLOG_TUAN_1.md), rồi tự commit/push. Ứng dụng demo, Dockerfile và kiểm thử local là phần chuẩn bị cho triển khai tuần 2; có thể làm sớm nhưng không được trình bày là yêu cầu riêng bắt buộc của tuần 1 từ đề bài. Khi triển khai trên AWS, lưu kết quả thực tế; nếu gặp AccessDenied ở thao tác cần thiết, ghi rõ action/resource và nhờ giảng viên hoặc quản trị lab xác nhận.

## 8. Nội dung có thể dùng trong worklog tuần 1

> Đã kiểm tra môi trường AWS Learner Lab: truy cập console thành công, sử dụng Region us-east-1, ngân sách hiển thị đã dùng $0/$50. Xác nhận các dịch vụ cần cho đề tài được phép theo Readme; kiểm tra trust của LabRole cho CodeDeploy/ECS task và hướng dẫn sử dụng role. Ghi nhận tài khoản bị chặn đọc VocLabPolicy; quyền thao tác triển khai sẽ được kiểm chứng ở giai đoạn thực hiện.

Điền thành viên, thời gian và số giờ thực tế vào worklog; tài liệu này không xác nhận số giờ đã làm. Nội dung báo cáo được AI hỗ trợ tổng hợp từ minh chứng sinh viên cung cấp; sinh viên cần rà soát và giải thích được kết quả khi vấn đáp.
