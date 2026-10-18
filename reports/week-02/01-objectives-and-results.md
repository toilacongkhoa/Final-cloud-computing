# 1 Mục tiêu và kết quả tuần 2

Tuần 2 tập trung triển khai các chức năng lõi trên AWS Learner Lab và ghi nhận kết quả từng thành phần. Đề tài sử dụng ECR để lưu image, ECS Fargate để chạy ứng dụng, Application Load Balancer để định tuyến, CodeDeploy để chuyển Blue sang Green và CloudWatch Logs để lưu log ứng dụng.

Kết quả triển khai thực tế: Blue đã chạy ổn định với một target healthy; Green được đăng ký bằng task definition revision 2 và triển khai qua CodeDeploy. Deployment d-56NWVLOBM đạt Succeeded, chuyển 100% production traffic sang task set Green và hoàn tất thu hồi task set Blue. ECS service sau triển khai có 1 task running, 0 pending, sử dụng ecs-bluegreen-demo:2; target group Green có 1 Healthy, 0 Unhealthy. Đây là kết quả quan sát trên AWS Console, không phải mô phỏng local.

[Quay lại mục lục báo cáo tuần 2](README.md)
