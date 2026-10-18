# Final-cloud-computing

Đề tài: Blue/Green deployment cho ECS với AWS CodeDeploy trên AWS Learner Lab.

Ứng dụng demo cơ bản dùng Node.js thuần + HTML/CSS: một trang hiển thị Blue/Green, `/health` để ALB kiểm tra và `/version` để xem JSON. Không cần database hoặc thư viện ngoài.

## Cấu trúc thư mục

```text
Final-cloud-computing/
├── app/                            # Mã ứng dụng
│   ├── src/server.js               # HTTP server và các endpoint
│   ├── public/                     # HTML và CSS
│   ├── releases/                   # Blue v1 / Green v2
│   └── tests/                      # Kiểm thử HTTP
├── infra/                          # Cấu hình triển khai
│   ├── docker/                     # Dockerfile và script kiểm thử container
│   └── aws/                        # Template task definition và AppSpec
├── docs/                           # Hướng dẫn chạy và bàn giao AWS
├── reports/week-01/                # Báo cáo, worklog và sơ đồ Tuần 1
├── evidence/week-01/               # Ảnh minh chứng Tuần 1
├── package.json                    # Lệnh chạy/kiểm thử, không có dependency
└── .dockerignore                   # Chỉ đưa mã ứng dụng vào build context
```

## Chạy nhanh

Cần Node.js 22 trở lên. Chạy từ gốc repo, không cần `npm install`:

```powershell
npm run start:blue
```

Mở http://localhost:8080. Nhấn Ctrl+C rồi chạy `npm run start:green` để thử Green trên cùng cổng. Nếu PowerShell chặn `npm.ps1`, dùng `npm.cmd`.

```powershell
npm test
```

## Tài liệu

- [Chạy local, kiểm thử và Docker](docs/local-development.md).
- [Cấu hình và bàn giao AWS](docs/aws-handoff.md).
- [Kết quả kiểm thử trước bàn giao](docs/pre-handoff-checks.md).
- [Báo cáo Tuần 1](reports/week-01/README.md).

Trước khi triển khai AWS, điền ARN LabRole, URI image ECR và ARN task definition vào các file mẫu trong `infra/aws/`. Hiện đã kiểm thử ứng dụng và Docker trên máy; phần triển khai Learner Lab thực hiện theo hướng dẫn trong `docs/aws-handoff.md`.
