# 4 Triển khai và kết quả từng thành phần

### 4.1 Chuẩn bị image và ECR

Chạy npm.cmd test, kết quả 7 pass và 0 fail được lưu trong ảnh. Script kiểm thử Docker đã chạy tới dòng PASS Green với các kiểm tra image, healthcheck, HTTP, user không phải root và shutdown.

Repository ECR được tạo, đăng nhập thành công và push cả v1, v2. Console hiển thị hai tags và digest tương ứng. Phiên tiếp tục chỉ tái sử dụng hai image, không build/push lại.

### 4.2 Mạng và ALB

Đã kiểm tra các subnet sẵn có, chọn hai AZ khác nhau và xác nhận route Internet Gateway. Không xóa các subnet/default security group của Lab. IP máy demo thay đổi nên inbound ALB được cập nhật bằng My IP. ALB bg-alb đạt Active; listeners 80 và 8080 được xác nhận trỏ Blue trước khi triển khai Green. Hai tags Project/Owner đã được lưu đúng.

### 4.3 ECS Blue và Green

Blue revision 1 được đăng ký từ JSON với execution role LabRole và image ECR :v1. Cluster Fargate được tạo thành công. Form ECS Console hiện tại hiển thị controller ECS và các chiến lược native; vì đề tài dùng CodeDeploy, service được tạo bằng AWS CLI trong CloudShell của Console với --deployment-controller type=CODE_DEPLOY. Kết quả tạo service hiển thị ACTIVE và desired count 1.

Blue sau khởi động có running 1, pending 0, service steady state; target 172.31.32.206 healthy. Green revision 2 được tạo bằng cách giữ cấu hình Blue và đổi image sang :v2. Trong lúc deployment, Console ghi nhận hai task Running tương ứng revision 1 và 2, không phải hai service độc lập.

### 4.4 CodeDeploy chuyển Blue sang Green

Đã tạo application compute platform ECS và deployment group sử dụng LabRole, cluster/service, hai target groups và hai listeners có sẵn. AppSpec chỉ định Green revision 2, container demo-app, port 8080. Deployment d-56NWVLOBM bắt đầu khoảng 22:00 ngày 18/10/2026.

Console ghi nhận lần lượt tạo replacement task set, thiết lập test traffic route, canary 10%, chuyển 100% production traffic, chờ 1 phút và terminate original task set. Trạng thái cuối là Succeeded. Mốc ảnh cuối 22:09 ghi nhận service sử dụng revision 2, một task running, không còn pending; target group Green có một target healthy. Không cấu hình alarm hoặc automatic rollback trong phiên này, không thử tình huống deployment lỗi.

### 4.5 CloudWatch và bảng kết quả

Log group đã được tạo trước task. Sau khi ECS chạy, tab Logs hiển thị các sự kiện listening của Blue/Green và các request /health status 200, lần lượt có version 1.0.0/color blue và version 2.0.0/color green. Đây là log thật từ task chạy trên AWS; không phải dữ liệu minh họa. Không suy ra từ /health rằng mọi luồng người dùng đã được kiểm thử.

| Thành phần | Kết quả |
| --- | --- |
| Ứng dụng local | 7/7 test pass trong ảnh chuẩn bị |
| Docker | Ảnh PASS Green; hai image đã push ECR |
| ECR | Có v1, v2 và kết quả push thành công |
| ECS Fargate | Blue steady state; cuối phiên Green revision 2, running 1/pending 0 |
| ALB | Active, hai listeners; Blue healthy rồi Green 1 Healthy/0 Unhealthy |
| CodeDeploy | Canary 90/10, sau đó Green 100%; Succeeded |
| CloudWatch Logs | Có log startup và health HTTP 200 của hai phiên bản |

[Quay lại mục lục báo cáo tuần 2](README.md)
