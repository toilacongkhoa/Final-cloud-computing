# 3 Tích hợp bảo mật và giám sát

### 3.1 Luồng tích hợp

Mã nguồn → Docker image → ECR → ECS task definition → CodeDeploy → ECS Fargate → ALB. Giữ một service và hai target groups luân phiên vai trò original/replacement. Listener production dùng HTTP 80, test dùng HTTP 8080. Canary chuyển 10% traffic trong 5 phút trước khi chuyển toàn bộ; task set cũ được giữ thêm 1 phút khi deployment thành công.

### 3.2 Bảo mật

ALB chỉ nhận cổng 80/8080 từ IP máy demo dạng /32; đã thay IP cũ bằng IP hiện tại để kiểm thử. Task chỉ nhận cổng 8080 từ security group của ALB, outbound HTTPS 443. Container chạy bằng user node; execution role và service role CodeDeploy dùng LabRole có sẵn. Giữ tags Project=ecs-bluegreen-demo và Owner=khoa-dat. Cấu hình demo dùng HTTP.

### 3.3 CloudWatch và automatic rollback

Log group /ecs/ecs-bluegreen-demo giữ log 7 ngày. Ứng dụng ghi JSON gồm thời gian, đường dẫn, HTTP status, version và color. Bốn alarm thuộc AWS/ApplicationELB dùng đúng dimensions LoadBalancer và TargetGroup:

| Alarm trên mỗi target group | Điều kiện | Mục đích |
| --- | --- | --- |
| bg-tg-blue-unhealthy và bg-tg-green-unhealthy | UnHealthyHostCount Maximum ≥ 1, 3/3 chu kỳ 60 giây | Phát hiện target lỗi health kéo dài |
| bg-tg-blue-5xx và bg-tg-green-5xx | HTTPCode_Target_5XX_Count Sum ≥ 5, 1/1 chu kỳ 60 giây | Phát hiện lỗi HTTP từ ứng dụng |

Cả bốn alarm được gắn vào bg-deployment-group; bật DEPLOYMENT_FAILURE và DEPLOYMENT_STOP_ON_ALARM, không bỏ qua lỗi đọc alarm. Missing data được coi là notBreaching để target group rỗng không chặn deployment; trước mỗi phép thử phải xác nhận cả bốn alarm OK. Dòng No actions trên CloudWatch chỉ nói alarm không gắn SNS/action riêng; CodeDeploy vẫn giám sát các alarm được liên kết trong deployment group.

### 3.4 Tự động hóa

week03.py kiểm tra account/controller, cấu hình alarm và rollback, đăng ký ba task definitions, tạo deployment và xuất trạng thái. Image được ghim bằng digest; bản tốt và hai bản lỗi chỉ khác biến môi trường. monitor.mjs gọi /version mỗi giây và ghi CSV cùng thống kê; đây là script tự động hóa cho hạ tầng có sẵn, chưa phải bộ IaC dựng toàn bộ tài nguyên hoặc pipeline CI/CD.

[Quay lại mục lục báo cáo tuần 3](README.md)
