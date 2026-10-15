# 4 Nền tảng AWS và Git đã chuẩn bị

| Hạng mục | Kết quả ghi nhận |
| --- | --- |
| VPC và subnet | Tái sử dụng default VPC vpc-01cefe25cf51f1293 (172.31.0.0/16).<br>A: subnet-0dd4e6a728f1a7476, us-east-1a, 172.31.16.0/20.<br>B: subnet-039825a0b49e43f75, us-east-1b, 172.31.32.0/20. |
| Route ra Internet | Main route table rtb-02f08db969e7a3be8 có route 0.0.0.0/0 tới igw-033330f9a6a5ae975, trạng thái Active. |
| bg-alb-sg | Đã tạo sg-0b2f0910bab760484. Inbound TCP 80/8080 từ IP máy demo 171.250.165.238/32. Outbound TCP 8080 tới bg-task-sg đã lưu thành công. |
| bg-task-sg | Đã tạo sg-09c234bb4a8e6fbcf. Inbound TCP 8080 từ bg-alb-sg; outbound HTTPS 443 tới 0.0.0.0/0. |
| Tags | Đã điền Project=ecs-bluegreen-demo và Owner=khoa-dat ở form tạo hai SG. |
| Git và minh chứng | Repository có branch main và remote origin trỏ tới toilacongkhoa/Final-cloud-computing. |

[Quay lại mục lục báo cáo tuần 1](README.md)
