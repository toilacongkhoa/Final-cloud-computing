# Minh chứng Tuần 4

## Video demo

- Video: [Xem demo Blue/Green ECS và CodeDeploy](https://drive.google.com/file/d/17kW_Dxf9iRq7HuKnb4V84pJlvBOLkvD5/view).
- Slide nghiệm thu: [Slide-Report.pdf](../../reports/week-04/Slide-Report.pdf).

## Chi phí AWS

- Ảnh mức credit trên AWS Academy Learner Lab: [learner-lab-credit-usage.png](learner-lab-credit-usage.png), hiển thị Used $16 of $50.
- Ảnh Cost and Usage: [cost-and-usage-summary.png](cost-and-usage-summary.png).
- Ảnh Cost and Usage hiển thị chi phí tháng hiện tại $14.79 và dự báo cuối tháng $16.00; đây không phải tổng chi phí toàn kỳ.
- Mức credit Learner Lab và chi phí Cost Explorer là hai số liệu riêng; không cộng hai giá trị này.

## Dọn dẹp tài nguyên

- ECS service `bg-service` đã xóa: [01-ecs-service-deleted.png](01-ecs-service-deleted.png).
- ALB `bg-alb` đã xóa: [02-alb-deleted.png](02-alb-deleted.png).
- CloudWatch alarms đã xóa: [03-cloudwatch-alarms-deleted.png](03-cloudwatch-alarms-deleted.png).
- Hai target groups đã xóa: [04-target-groups-deleted.png](04-target-groups-deleted.png).
- ECR repository `ecs-bluegreen-demo` đã xóa: [05-ecr-repository-deleted.png](05-ecr-repository-deleted.png).
- ECS cluster `bg-cluster` ở trạng thái Inactive, với 0 service và 0 task: [06-ecs-cluster-inactive-zero-tasks.png](06-ecs-cluster-inactive-zero-tasks.png). Cần xác nhận cluster đã biến mất khỏi danh sách sau khi làm mới Console.
- Security group `bg-task-sg` đã xóa: [07-task-security-group-deleted.png](07-task-security-group-deleted.png).
- Security group `bg-alb-sg` đã xóa: [08-alb-security-group-deleted.png](08-alb-security-group-deleted.png).
- CloudWatch log group `/ecs/ecs-bluegreen-demo` đã xóa; các log group Lambda còn lại không thuộc dự án: [09-project-log-group-deleted.png](09-project-log-group-deleted.png).
- EC2 Network Interfaces không còn interface trong `us-east-1`: [10-no-network-interfaces.png](10-no-network-interfaces.png).
