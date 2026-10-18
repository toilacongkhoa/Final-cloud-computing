# 3 Kiến trúc và chức năng lõi

### 3.1 Ứng dụng và hai phiên bản

Ứng dụng Node.js thuần và HTML/CSS không dùng database. Blue mang phiên bản 1.0.0, Green mang phiên bản 2.0.0. Mỗi process chạy một release; image được đóng gói riêng theo tag v1 và v2. Trang / thể hiện release và hostname; /health phục vụ health check; /version trả metadata nhận diện phiên bản. Server ghi log JSON ra stdout với thời gian, đường dẫn, mã HTTP, version và color.

Dockerfile dùng Linux/amd64, user node, cổng 8080 và Docker HEALTHCHECK. Mã nguồn, Dockerfile, task definition template, AppSpec và hướng dẫn bàn giao nằm trong repository.

### 3.2 Luồng triển khai thực tế

Luồng phát hành là mã nguồn → Docker image → ECR → task definition → ECS Fargate → ALB. CodeDeploy liên kết một ECS service với hai target groups và hai listeners để tạo task set thay thế và điều chỉnh traffic. CloudWatch nhận stdout từ container qua awslogs.

Production listener HTTP 80 và test listener HTTP 8080 ban đầu cùng trỏ tới Blue. CodeDeploy được cấu hình CodeDeployDefault.ECSCanary10Percent5Minutes: chuyển 10% production traffic sang Green, giữ 5 phút rồi chuyển phần còn lại. Quan sát Console đã ghi nhận 90% original và 10% replacement, sau đó 0% original và 100% replacement. Tỷ lệ này là cấu hình traffic trên AWS.

### 3.3 Cấu hình tài nguyên

| Hạng mục | Cấu hình thực tế |
| --- | --- |
| VPC | vpc-01cefe25cf51f1293, default VPC, CIDR 172.31.0.0/16 |
| Hai public subnets | subnet-039825a0b49e43f75 tại us-east-1b và subnet-0f3d6459e489c2a8b tại us-east-1c; đã kiểm tra route 0.0.0.0/0 tới Internet Gateway |
| ALB security group | bg-alb-sg, sg-0b2f0910bab760484; inbound 80/8080 từ My IP; outbound 8080 tới task SG |
| Task security group | bg-task-sg, sg-09c234bb4a8e6fbcf; inbound 8080 từ ALB SG; outbound HTTPS 443 |
| ECR repository | 217376138299.dkr.ecr.us-east-1.amazonaws.com/ecs-bluegreen-demo, tags v1 và v2 |
| ECS cluster và service | bg-cluster / bg-service; Fargate, desired count 1, controller CODE_DEPLOY |
| Task size | Linux X86_64, awsvpc, CPU 256 units tương đương 0,25 vCPU, RAM 512 MiB |
| Container và network | demo-app:8080; hai subnet trên, task SG, public IP enabled; health-check grace period 60 giây |
| Task definitions | Blue ecs-bluegreen-demo:1; Green ecs-bluegreen-demo:2 |
| ALB và target groups | bg-alb, Internet-facing IPv4; bg-tg-blue / bg-tg-green, target type IP, HTTP 8080, health path /health, success 200 |
| CodeDeploy | Application bg-app; group bg-deployment-group; LabRole; canary 10% trong 5 phút; giữ task cũ 1 phút sau chuyển traffic |
| CloudWatch | /ecs/ecs-bluegreen-demo, awslogs stream prefix ecs, retention 1 tuần |

DNS ALB: bg-alb-453203969.us-east-1.elb.amazonaws.com. Các ARN task definition có dạng arn:aws:ecs:us-east-1:217376138299:task-definition/ecs-bluegreen-demo:1 và tương tự với revision :2.

[Quay lại mục lục báo cáo tuần 2](README.md)
