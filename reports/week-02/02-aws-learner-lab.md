# 2 Kiểm tra AWS Learner Lab

Môi trường sử dụng Account ID 217376138299, Region us-east-1 thuộc vùng được phép. AWS CLI trong phiên chuẩn bị đã gọi STS và trả về đúng tài khoản Lab. Docker Desktop Linux engine và AWS CLI hoạt động; mốc tham chiếu cbc946e.

LabRole có ARN arn:aws:iam::217376138299:role/LabRole. Đã đọc trust relationships và thấy cả ecs-tasks.amazonaws.com và codedeploy.amazonaws.com. Task execution role và CodeDeploy service role đều sử dụng LabRole có sẵn; không tạo IAM user/role, không sửa trust policy hoặc mở rộng quyền trong phiên triển khai này. Service role hạ tầng ECS hiển thị AWSServiceRoleForECS trên Console.

Tags dùng cho tài nguyên dự án là Project=ecs-bluegreen-demo và Owner=khoa-dat.

[Quay lại mục lục báo cáo tuần 2](README.md)
