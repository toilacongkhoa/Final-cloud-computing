# Kết quả kiểm thử trước bàn giao — 18/10/2026

Phạm vi: ứng dụng Blue/Green, Docker images và kiểm tra tĩnh template AWS. Chưa phải biên bản triển khai thành công trên AWS Learner Lab.

## Kết quả

| Hạng mục | Kết quả |
| --- | --- |
| `npm test` trên Node.js 22.18.0 / Windows | 7/7 đạt |
| Cùng bộ kiểm thử trên Node.js 24.22.0 trong image Docker | 7/7 đạt |
| Build `ecs-bluegreen-demo:v1` (Blue) | Đạt, Linux/amd64 |
| Build `ecs-bluegreen-demo:v2` (Green) | Đạt, Linux/amd64 |
| Docker HEALTHCHECK và `/health` của hai image | Đạt, healthy và HTTP 200 |
| Trang HTML và `/version` | Đúng Blue 1.0.0 / Green 2.0.0 |
| Cache header | Có `Cache-Control: no-store` |
| User container | `node`, không phải root |
| Build context | Không đưa `.git`, báo cáo hoặc minh chứng vào `/app` |
| Dừng container bằng SIGTERM | Exit code 0 ở cả hai bản |
| Script `infra/docker/test.ps1` | Chạy đạt trên PowerShell 7 và Windows PowerShell mặc định |
| Container dùng để kiểm thử | Đã xóa sau khi kiểm thử; giữ lại hai image để bàn giao |
| Template ECS JSON / AppSpec YAML | Parse thành công; tên container/cổng khớp nhau |
| Cấu hình Fargate và tags | CPU 256, RAM 512, awsvpc, Linux X86_64, Project/Owner đúng thiết kế |
| Liên kết tương đối trong README/docs | Hợp lệ |
| `git diff --check` | Đạt |

Các kiểm thử HTTP bao gồm Blue/Green, HTML/CSS/API, query string, HEAD, 404 khi truy cập file nội bộ, 405 khi gửi method không hỗ trợ, log JSON, cấu hình khởi động không hợp lệ và URL lỗi.

Đã sửa xử lý URL sai: trả HTTP 400 và giữ server hoạt động, thay vì để lỗi parse URL làm process dừng.

Giao diện hai phiên bản đã được kiểm tra bằng trình duyệt ở các bước trước: giữ trang cơ bản, bỏ câu mô tả/phần ghi chú và bỏ viền màu trên khung theo yêu cầu.

## Chạy lại

Từ gốc repo:

```powershell
npm test
./infra/docker/test.ps1
```

Script Docker build cả hai image, tạo container với cổng localhost ngẫu nhiên và tự dọn container. Engine Docker phải hoạt động.

Để chạy bộ HTTP test bằng Node trong image (PowerShell):

```powershell
$testPath = Join-Path (Get-Location) 'app\tests'
docker run --rm --mount "type=bind,source=$testPath,target=/app/app/tests,readonly" ecs-bluegreen-demo:v1 node --test app/tests/server.test.js
```

## Phần cần người phụ trách AWS xác minh

Ba placeholder trong task definition/AppSpec được giữ nguyên có chủ đích: ARN LabRole đã xác minh, URI image ECR và ARN task definition revision. Kiểm tra tĩnh không xác nhận quyền IAM hoặc API AWS sẽ chấp nhận cấu hình trong Lab cụ thể.

Chưa kiểm thử push ECR, chạy ECS/Fargate thật, ALB health/traffic, CodeDeploy canary và rollback. Các bước này cần thực hiện trong đúng Learner Lab của nhóm theo [hướng dẫn bàn giao AWS](aws-handoff.md), rồi bổ sung minh chứng Account ID, Region và thời gian. Kết quả local/Docker không thay thế minh chứng AWS.

Codex hỗ trợ mã nguồn, cấu hình, kiểm thử và tài liệu. Sinh viên cần tự rà soát, giải thích và ghi giờ thực tế trong worklog; tài liệu này không tự ghi nhận số giờ hoặc kết quả triển khai AWS cho sinh viên.
