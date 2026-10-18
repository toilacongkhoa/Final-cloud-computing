# Chạy và kiểm thử ứng dụng trên máy

Ứng dụng dùng Node.js thuần và HTML/CSS, không cần thư viện ngoài hoặc database. Một process chỉ phục vụ một phiên bản. Phiên bản được chọn lúc khởi động server.

## Chạy bằng Node.js

Cần Node.js 22 trở lên. Mở terminal tại **gốc repository**:

```powershell
npm run start:blue
```

Mở http://localhost:8080. Trang hiển thị BLUE, phiên bản 1.0.0. Nhấn Ctrl+C để dừng trước khi chạy Green trên cùng cổng:

```powershell
npm run start:green
```

Green hiển thị phiên bản 2.0.0. Không cần `npm install`: chỉ dùng module có sẵn của Node.js. Nếu PowerShell chặn `npm.ps1`, dùng `npm.cmd` thay cho `npm`.

Muốn chạy cả hai để so sánh: giữ Blue trên 8080, mở terminal thứ hai:

```powershell
$env:PORT = '8081'
npm run start:green
```

Mở http://localhost:8081. Đây là hai server local riêng, chưa có ALB và chưa chứng minh chuyển traffic bằng CodeDeploy. Để bỏ cổng tùy chỉnh trong terminal: `Remove-Item Env:PORT -ErrorAction SilentlyContinue`.

## Endpoint và mã nguồn

| Đường dẫn | Kết quả | Mục đích |
| --- | --- | --- |
| `/` | Trang HTML hiển thị phiên bản, màu, hostname | Quan sát phiên bản phục vụ trang |
| `/health` | HTTP 200, `{"status":"ok"}` | Health check của ALB |
| `/version` | JSON: service, version, color, hostname, startedAt | Xác định bản đang phản hồi |

Phản hồi đặt `Cache-Control: no-store`. Trong lúc canary, request mở `/version` có thể đến bản khác với request đã lấy trang HTML. Hostname local là tên máy; trong container là hostname container, không phải ECS task ARN.

`/health` chỉ xác nhận HTTP server ứng dụng hoạt động, không xác minh toàn bộ AWS.

| File | Vai trò |
| --- | --- |
| `app/src/server.js` | HTTP server tại `0.0.0.0:8080`, trang/API, log JSON ra stdout |
| `app/public/index.html` | Giao diện, server điền các trường `{{...}}` |
| `app/public/styles.css` | CSS cơ bản, màu theo `data-color` |
| `app/releases/blue.json` | Blue: phiên bản 1.0.0 và thông điệp |
| `app/releases/green.json` | Green: phiên bản 2.0.0 và thông điệp |
| `app/tests/server.test.js` | Kiểm thử HTTP cho cả hai phiên bản |

`APP_RELEASE` nhận `blue` hoặc `green`, mặc định `blue`. Tham số `--release` trong npm scripts được ưu tiên hơn biến môi trường. `PORT` mặc định 8080. Sửa file release cần khởi động lại server; trên AWS cần build image với tag mới và đăng ký task definition revision mới.

Chạy kiểm thử:

```powershell
npm test
```

## Chạy bằng Docker

Mở Docker Desktop và chờ Linux engine sẵn sàng. Các lệnh chạy từ **gốc repo**; dấu `.` cuối lệnh là build context.

```powershell
docker build --platform linux/amd64 -f infra/docker/Dockerfile --build-arg APP_RELEASE=blue -t ecs-bluegreen-demo:v1 .
docker build --platform linux/amd64 -f infra/docker/Dockerfile --build-arg APP_RELEASE=green -t ecs-bluegreen-demo:v2 .
docker run --rm --name bg-blue -p 8080:8080 ecs-bluegreen-demo:v1
```

Thử Green trong terminal khác:

```powershell
docker run --rm --name bg-green -p 8081:8080 ecs-bluegreen-demo:v2
```

Ứng dụng trong cả hai container nghe cổng 8080. Cổng 8081 chỉ là cổng trên máy để tránh trùng Blue. `EXPOSE` khai báo cổng; `-p` mới xuất cổng ra máy.

Image dùng Node.js 24 Alpine, chạy bằng user `node` và có Docker HEALTHCHECK tại cổng 8080. Không đổi `PORT` trong container khi dùng health check mặc định này.

Kiểm thử tự động cả hai image từ PowerShell (build, chạy container, health check, HTTP, user không phải root và dừng sạch):

```powershell
./infra/docker/test.ps1
```

Script dùng cổng localhost ngẫu nhiên và tự xóa container kiểm thử. Hai image `ecs-bluegreen-demo:v1` và `:v2` được giữ lại để bàn giao/push ECR.

Sau khi thử, dừng container:

```powershell
docker stop bg-blue bg-green
```

## Ghi nhận kết quả

Lưu kết quả chạy local và ảnh triển khai AWS theo từng tuần. Worklog ghi công việc, người thực hiện và thời gian thực tế.
