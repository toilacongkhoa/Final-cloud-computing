# Bàn giao cấu hình AWS — Tuần 2

Các bước đưa ứng dụng lên ECR, chạy Blue trên ECS và cập nhật Green qua CodeDeploy. Thay các giá trị `<...>` trong file mẫu bằng thông tin từ Learner Lab của nhóm.

## Các giá trị cần thống nhất

| Mục | Giá trị |
| --- | --- |
| Region | `us-east-1` |
| Project / Owner | `ecs-bluegreen-demo` / `khoa-dat` |
| Container name | `demo-app`, phải khớp ECS service, task definition và AppSpec |
| Container / target group port | HTTP `8080` |
| Target group type | `ip` |
| ALB listeners dự kiến | Production HTTP `80`, test HTTP `8080` |
| Health check | `/health`, success code `200`, traffic port |
| ECS service | Fargate, desired count 1, controller `CODE_DEPLOY` |
| Task | Linux X86_64, CPU 256, memory 512 MiB |
| Log group đề xuất | `/ecs/ecs-bluegreen-demo` |
| Canary theo thiết kế | `CodeDeployDefault.ECSCanary10Percent5Minutes` |

VPC/subnet/SG đã ghi trong [báo cáo nền tảng](../reports/week-01/04-aws-and-git-foundation.md). Kiểm tra lại đúng Account/Region: tài nguyên có thể đã được dọn, IP máy demo có thể đã đổi.

## 1. Xác minh quyền

Người phụ trách Lab xác minh LabRole có trust và quyền phù hợp cho ECS task execution và CodeDeploy, bao gồm quyền pass role cần thiết. Ảnh lỗi `iam:GetPolicy` Tuần 1 chưa chứng minh điều này. Không tạo IAM user/role mới. Nếu quyền bị giới hạn, ghi lại lỗi và làm rõ với GVHD.

Người viết ứng dụng không cần AWS credentials để chạy local. Người có phiên Lab hợp lệ thực hiện các bước AWS. Không đưa credentials/session token lên Git.

## 2. Build và push ECR

Build hai image theo [hướng dẫn local](local-development.md). Người phụ trách AWS cung cấp ECR repository URI thật. Các lệnh dưới đây yêu cầu ECR repository đã tạo, Docker engine chạy và AWS CLI có credentials tạm thời hợp lệ của đúng Lab:

```powershell
$ecrUri = '<ECR_REPOSITORY_URI>'
$ecrRegistry = $ecrUri.Split('/')[0]
aws sts get-caller-identity
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ecrRegistry
docker tag ecs-bluegreen-demo:v1 "${ecrUri}:v1"
docker tag ecs-bluegreen-demo:v2 "${ecrUri}:v2"
docker push "${ecrUri}:v1"
docker push "${ecrUri}:v2"
```

Dừng khi có lỗi. Không ghi đè tag đã dùng cho demo; khi sửa mã, tạo tag mới và task definition revision mới. Có thể dùng image digest để cố định image chính xác.

## 3. Task definition và bản Blue

Copy `infra/aws/task-definition.template.json` vào `infra/aws/generated/blue-task.json` (tạo thư mục generated nếu chưa có; Git bỏ qua thư mục này). Thay:

- `<VERIFIED_LAB_ROLE_ARN>` bằng ARN LabRole đã xác minh.
- `<ECR_IMAGE_URI_WITH_TAG_OR_DIGEST>` bằng URI image Blue `:v1` thực tế.

Tạo trước log group `/ecs/ecs-bluegreen-demo`, gắn tags và chọn retention, chẳng hạn 7 ngày. Template không tự tạo log group. Execution role cần quyền lấy image từ ECR và ghi log. Ứng dụng không gọi AWS API nên không khai báo task role riêng.

```powershell
aws ecs register-task-definition --cli-input-json file://infra/aws/generated/blue-task.json --region us-east-1
```

Lưu ARN có revision từ kết quả. Người phụ trách AWS tạo service từ revision Blue, controller `CODE_DEPLOY`, gắn target group A, chọn subnet/SG trong network configuration của service. Subnet/SG không nằm trong task definition. Với public subnet + IGW và không có NAT/endpoints, bật public IP cho task để ra Internet trực tiếp bằng IPv4.

Đợi task chạy, target healthy; kiểm tra `/`, `/health`, `/version` qua ALB production listener.

## 4. AppSpec và bản Green

1. Copy template task definition, đổi image thành Green `:v2`, đăng ký revision mới và lưu ARN.
2. Copy `infra/aws/appspec.template.yaml` vào `infra/aws/generated/appspec-green.yaml`, thay `<REGISTERED_TASK_DEFINITION_ARN_WITH_REVISION>` bằng ARN revision Green.
3. Người phụ trách AWS tạo CodeDeploy application compute platform ECS và deployment group, liên kết cluster/service, hai target group, listeners và LabRole đã xác minh. Chọn canary như thiết kế.
4. Tạo deployment bằng AppSpec đã điền. Có thể nhập nội dung AppSpec trực tiếp bằng lựa chọn revision tương ứng của CodeDeploy Console. AppSpec không tự tạo application/deployment group.
5. Khi test listener trỏ tới Green, kiểm tra địa chỉ ALB cổng 8080; theo dõi deployment events và phản hồi production tới khi chuyển Green hoàn tất.

Sau lần tạo service đầu tiên, triển khai phiên bản mới qua CodeDeploy theo đề tài. Tỷ lệ canary áp dụng cho traffic; mẫu ít request không bảo đảm quan sát đúng 10%.

## 5. Minh chứng và kết thúc buổi

- Image Blue/Green trên ECR với tag/digest; task revisions và task chạy.
- Target healthy, website qua ALB, `/health` trả 200.
- CodeDeploy thành công và production đổi Blue → Green.
- Tags đã lưu; ảnh/CLI có Account ID, Region, thời gian.
- Worklog ghi công việc, người thực hiện và giờ thực tế; nộp nội dung báo cáo trực tiếp trên website môn học.

Ghi ngân sách/chi phí, dọn tài nguyên dự án theo yêu cầu. Giảm desired count về 0 chưa dừng chi phí ALB; người phụ trách AWS cần dọn tài nguyên tính phí liên quan. Không xóa default VPC/subnet hoặc tài nguyên bài khác.

## Tài liệu AWS

- [Task definition Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html).
- [AppSpec ECS](https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorial-ecs-create-appspec-file.html).
- [CodeDeploy blue/green ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-bluegreen.html).
- [Task execution role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html).
