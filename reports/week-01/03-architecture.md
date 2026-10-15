# 3 Tìm hiểu và thiết kế kiến trúc

Blue là phiên bản hiện tại, green là bản thay thế. CodeDeploy tạo task set mới, kiểm tra health và điều chỉnh traffic qua ALB. Hai target group A/B đổi vai trò giữa các lần triển khai. Rollback theo điều kiện thất bại hoặc alarm phải được cấu hình và xác minh bằng deployment events.

Thiết kế dự kiến dùng một ECS service với controller CODE_DEPLOY, Fargate 0,25 vCPU / 512 MiB, desired count 1; hai target group loại ip, HTTP 8080. Chọn canary 10% trong năm phút, rồi chuyển phần còn lại nếu deployment tiếp tục bình thường.

```mermaid
flowchart LR
    Demo["Máy demo"]
    CodeDeploy["CodeDeploy dùng LabRole"]
    Services["ECR lưu image • CloudWatch giám sát"]

    subgraph Network["us-east-1 | Default VPC | Hai subnet ở us-east-1a và us-east-1b"]
        ALB["ALB<br/>Production 80 / Test 8080"]
        TargetA["Target group A"]
        TargetB["Target group B"]
        Current["ECS task set hiện tại"]
        Replacement["ECS task set thay thế"]

        ALB --> TargetA
        ALB --> TargetB
        TargetA --> Current
        TargetB --> Replacement
    end

    Demo --> ALB
    CodeDeploy -.-> ALB
    CodeDeploy -.-> Current
```

Hình 1  Kiến trúc blue/green dự kiến trên ECS.

[Quay lại mục lục báo cáo tuần 1](README.md)
