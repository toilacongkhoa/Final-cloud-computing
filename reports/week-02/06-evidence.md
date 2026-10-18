# 6 Minh chứng

![Hình 1 Kết quả kiểm thử Node.js trước triển khai](../../evidence/week-02/01-nodejs-tests-pass.png)

![Hình 2 Push thành công hai image v1 và v2](../../evidence/week-02/02-ecr-push-blue-green.png)

![Hình 3 Hai tags trên ECR Console](../../evidence/week-02/03-ecr-image-tags.png)

![Hình 4 ALB Active và hai tags đúng](../../evidence/week-02/04-alb-active-project-owner-tags.png)

![Hình 5 Hai listeners HTTP 80 và 8080 trỏ Blue ban đầu](../../evidence/week-02/05-alb-listeners-blue.png)

![Hình 6 Task definition Blue revision 1 ACTIVE và LabRole](../../evidence/week-02/06-ecs-blue-task-definition.png)

![Hình 7 Cluster Fargate được tạo thành công](../../evidence/week-02/07-ecs-cluster-created.jpg)

![Hình 8 Service ACTIVE sử dụng controller CODE_DEPLOY](../../evidence/week-02/08-ecs-service-code-deploy.jpg)

![Hình 9 Blue running một task và target healthy](../../evidence/week-02/09-blue-running-target-healthy.jpg)

![Hình 10 Hai task Blue và Green chạy đúng revision](../../evidence/week-02/10-ecs-blue-green-tasks.jpg)

![Hình 11 CloudWatch nhận log Blue và Green](../../evidence/week-02/11-cloudwatch-blue-green-logs.jpg)

![Hình 12 Deployment group dùng LabRole và hai target groups](../../evidence/week-02/12-codedeploy-labrole-configuration.jpg)

![Hình 13 Canary chuyển 10 phần trăm traffic sang Green](../../evidence/week-02/13-codedeploy-canary-10-percent.jpg)

![Hình 14 Deployment Succeeded và hoàn tất các lifecycle events](../../evidence/week-02/14-codedeploy-succeeded.jpg)

![Hình 15 Service cuối phiên dùng Green revision 2](../../evidence/week-02/15-ecs-green-service-succeeded.jpg)

![Hình 16 Target group Green có một healthy và không unhealthy](../../evidence/week-02/16-green-target-healthy.jpg)

[Quay lại mục lục báo cáo tuần 2](README.md)
