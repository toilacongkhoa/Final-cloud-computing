# Báo cáo Tuần 3

## Tích hợp giám sát CloudWatch, cấu hình Automatic Rollback và kiểm thử kịch bản sự cố cho ECS Blue/Green Deployment

- Repository: [Final-cloud-computing](https://github.com/toilacongkhoa/Final-cloud-computing).
- Báo cáo chi tiết: [Báo cáo tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/README.md).
- Báo cáo Word: [baoCaoTuan3.docx](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/baoCaoTuan3.docx).
- Worklog: [Phân công và thời lượng từng công việc](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/05-worklog.md).
- Tổng thời gian theo bảng worklog: **16 giờ, mỗi thành viên 8 giờ**.

## 1. Các commit minh chứng

- [24126e6](https://github.com/toilacongkhoa/Final-cloud-computing/commit/24126e6): Hoàn thiện giám sát CloudWatch, cấu hình automatic rollback, kiểm thử hai kịch bản lỗi (health check và HTTP 500) và hoàn thành báo cáo tuần 3.

## 2. Thành viên 1: Nguyễn Công Khoa

**MSSV: 24110254 — Tổng thời gian theo worklog: 8 giờ**

- **Kiểm tra Learner Lab, security groups và cấu hình tích hợp — 2 giờ.** Khảo sát hiện trạng tài nguyên từ tuần 2 trên AWS Learner Lab (`bg-cluster`, `bg-service`, `bg-alb`, hai target groups `bg-tg-blue`/`bg-tg-green` và `LabRole`). Tinh chỉnh security group của ECS task chỉ cho phép traffic vào cổng `8080` duy nhất từ security group của ALB, chặn toàn bộ truy cập trực tiếp từ bên ngoài; ALB chỉ mở cổng `80`/`8080` cho địa chỉ IP máy demo (`/32`). Minh chứng: [Task security group chỉ nhận traffic từ ALB](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/09-task-security-group-alb-only.jpg), [báo cáo kiểm tra Learner Lab](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/02-aws-learner-lab.md), [chi tiết bảo mật và tích hợp](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/03-integration-security-monitoring.md).

- **Cấu hình CloudWatch alarms và automatic rollback — 2 giờ.** Khởi tạo 4 CloudWatch Metric Alarms gắn với metric của Application Load Balancer theo từng target group: 2 alarm lỗi health check (`bg-tg-blue-unhealthy`, `bg-tg-green-unhealthy` theo metric `UnHealthyHostCount >= 1` trong 3 chu kỳ 60 giây) và 2 alarm lỗi 5xx (`bg-tg-blue-5xx`, `bg-tg-green-5xx` theo metric `HTTPCode_Target_5XX_Count >= 5` trong 1 chu kỳ 60 giây). Cập nhật CodeDeploy deployment group `bg-deployment-group` để kích hoạt tính năng automatic rollback cho hai sự kiện `DEPLOYMENT_FAILURE` và `DEPLOYMENT_STOP_ON_ALARM`. Minh chứng: [CodeDeploy bật automatic rollback](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/01-codedeploy-rollback-enabled.jpg), [bốn alarm CloudWatch ở trạng thái OK trước kiểm thử](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/05-cloudwatch-alarms-ok.jpg), [cấu hình chi tiết CloudWatch và rollback](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/03-integration-security-monitoring.md).

- **Triển khai bản tốt, thử lỗi health và lỗi HTTP, đối chiếu trạng thái — 2 giờ.** Thực hiện 3 đợt triển khai trên môi trường thật:
  1. Triển khai bản tốt (revision 3, deployment `d-69JC4V9GM`): hoàn thành chuyển 100% traffic sang Green thành công lúc 21:30.
  2. Kiểm thử kịch bản lỗi health check (revision 4, deployment `d-PIW6KA9GM`): cấu hình `FAIL_HEALTH=1`, alarm `bg-tg-green-unhealthy` phát hiện target lỗi và dừng deployment; CodeDeploy tự động rollback sang `d-9NAW3E9GM` thành công, lưu lượng production giữ nguyên 100% ở bản cũ không bị ảnh hưởng.
  3. Kiểm thử kịch bản lỗi ứng dụng (revision 5, deployment `d-W7U8H29GM`): cấu hình `FAIL_APP=1`, bản lỗi nhận 10% canary traffic và trả HTTP 500, alarm `bg-tg-green-5xx` kích hoạt ngay chu kỳ đầu tiên; CodeDeploy tự động dừng và rollback sang `d-1AUF3FAGM` thành công.
  Minh chứng: [Deployment bản tốt Succeeded](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/04-good-deployment-succeeded.jpg), [alarm health kích hoạt trên target group Green](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/06-health-alarm-triggered.jpg), [CodeDeploy tự rollback thành công khi lỗi health](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/07-health-automatic-rollback-succeeded.jpg), [bản lỗi nhận 10% canary traffic](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/10-bad-app-canary-10-percent.jpg), [CodeDeploy tự rollback thành công do alarm 5xx](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/11-app-automatic-rollback-succeeded.jpg).

- **Chụp ảnh Console, kiểm tra log và tập hợp minh chứng — 2 giờ.** Kiểm tra log group `/ecs/ecs-bluegreen-demo`, xác nhận log trả HTTP `503` và `500` có cấu trúc JSON; đối chiếu trạng thái phục hồi cuối của ECS cluster sau hai đợt rollback: service phục hồi ổn định về revision 3 với 1 task running, target healthy. Tổng hợp 9 ảnh chụp màn hình thực tế từ AWS Console làm minh chứng xác thực. Minh chứng: [ECS phục hồi ổn định revision 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/evidence/week-03/08-ecs-restored-after-health.jpg), [kết quả triển khai và bảng số liệu kiểm thử](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/04-deployment-and-results.md), [danh mục minh chứng Tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/06-evidence.md).

## 3. Thành viên 2: Nguyễn Tiến Đạt

**MSSV: 24110194 — Tổng thời gian theo worklog: 8 giờ**

- **Bổ sung hai chế độ lỗi có chủ đích cho ứng dụng — 2 giờ.** Cập nhật mã nguồn máy chủ Node.js hỗ trợ hai biến môi trường phục vụ kiểm chứng rollback:
  - `FAIL_HEALTH=1`: route `/health` trả về HTTP `503 Service Unavailable`, trong khi `/` và `/version` vẫn hoạt động (mô phỏng container không vượt qua health check tầng cân bằng tải).
  - `FAIL_APP=1`: route `/` và `/version` trả về HTTP `500 Internal Server Error`, nhưng `/health` vẫn trả `200 OK` (mô phỏng sự cố ứng dụng/logic nhưng tiến trình vẫn sống).
  - Mặc định hai biến mang giá trị `0` khi vận hành bình thường.
  Minh chứng: [Mã nguồn server.js cập nhật](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/app/src/server.js), [mục tiêu và kết quả tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/01-objectives-and-results.md).

- **Viết kiểm thử tách biệt health 503 và ứng dụng 500 — 1,5 giờ.** Bổ sung hai ca kiểm thử mới vào bộ test tự động của Node.js: kiểm chứng độc lập trường hợp lỗi health check trả 503 và lỗi nghiệp vụ trả 500, xác nhận server không sập và ghi nhận đúng trạng thái. Nâng quy mô kiểm thử lên `9 pass, 0 fail` (tăng từ 7 test ở tuần 2). Minh chứng: [Mã kiểm thử bổ sung](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/app/tests/server.test.js), [kịch bản kiểm thử trong package.json](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/package.json).

- **Chuẩn bị Docker image và cấu hình task definitions — 1 giờ.** Đóng gói container image mới, đẩy lên Amazon ECR và cố định image digest để đảm bảo tính bất biến khi triển khai. Khai báo cấu hình task definition cho 3 revision: revision 3 (bản tốt), revision 4 (`FAIL_HEALTH=1`) và revision 5 (`FAIL_APP=1`) cùng cấu hình CPU `256`, RAM `512 MiB`, port `8080`, logging `awslogs` và role `LabRole`. Minh chứng: [Mô tả chuẩn bị task definitions](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/04-deployment-and-results.md), [script khai báo task definitions tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/week03.py).

- **Viết script cấu hình AWS và đo HTTP liên tục — 2 giờ.**
  - Xây dựng [infra/aws/week03.py](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/week03.py) tự động hóa quy trình kiểm tra account Learner Lab, tạo 4 CloudWatch alarms, cấu hình CodeDeploy automatic rollback, đăng ký task definitions và tạo deployment.
  - Xây dựng [infra/aws/monitor.mjs](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/monitor.mjs) gửi HTTP request `/version` liên tục mỗi 1 giây vào ALB production, ghi nhận latency, HTTP status code và version trả về. Kết quả đo kiểm:
    - Triển khai bản tốt: 891/891 request thành công (`100%`).
    - Lỗi health check: 481/481 request production thành công (`100%`), người dùng không gặp gián đoạn vì bản lỗi chưa nhận traffic production.
    - Lỗi ứng dụng (canary 10%): ghi nhận đúng 21 response HTTP 500 trong thời gian canary trước khi CodeDeploy ngắt lưu lượng và rollback an toàn về bản tốt (30/30 request sau rollback đạt HTTP 200).
  Minh chứng: [Script tự động hóa week03.py](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/week03.py), [script đo HTTP monitor.mjs](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/monitor.mjs), [bảng số liệu đo HTTP chi tiết](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/04-deployment-and-results.md).

- **Tổng hợp báo cáo Word và các mục Markdown — 1,5 giờ.** Hoàn thiện toàn bộ báo cáo Word tuần 3 [reports/week-03/baoCaoTuan3.docx](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/baoCaoTuan3.docx), biên soạn 6 tài liệu Markdown chi tiết theo từng mục từ mục tiêu, kiến trúc bảo mật đến số liệu kiểm thử trên kho mã nguồn. Minh chứng: [Báo cáo Word Tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/baoCaoTuan3.docx), [mục lục báo cáo Markdown](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/README.md), [worklog chi tiết Tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/05-worklog.md).

## 4. Phạm vi hoàn thành Tuần 3

- Đã hoàn thành 100% các nội dung theo yêu cầu bắt buộc và nhắc nhở của GVHD từ tuần 2: cấu hình CloudWatch Metric Alarms, kích hoạt CodeDeploy Automatic Rollback và kiểm thử kịch bản triển khai lỗi.
- Đã thắt chặt bảo mật mạng: Security group của Task ECS chỉ mở cổng `8080` duy nhất cho Security group của ALB; ALB chỉ chấp nhận truy cập từ IP demo máy kiểm thử (`/32`).
- Đã thiết lập 4 CloudWatch metric alarms (`UnHealthyHostCount` và `HTTPCode_Target_5XX_Count`) trên cả hai Target Groups và liên kết vào CodeDeploy Deployment Group.
- Đã kiểm chứng thành công deployment bản tốt (`d-69JC4V9GM` Succeeded, chuyển 100% traffic sang revision 3 an toàn).
- Đã kiểm chứng thành công hai kịch bản tự động rollback:
  - Lỗi health check (`FAIL_HEALTH=1`, deployment `d-PIW6KA9GM` bị alarm dừng, rollback `d-9NAW3E9GM` thành công, không làm gián đoạn người dùng production).
  - Lỗi ứng dụng (`FAIL_APP=1`, deployment `d-W7U8H29GM` trả HTTP 500 trong giai đoạn 10% canary, alarm 5xx kích hoạt, rollback `d-1AUF3FAGM` thành công, hệ thống tự động quay lại revision 3).
- Bộ kiểm thử tự động đạt `9 pass, 0 fail` (tăng 2 test case so với tuần 2).

Chi tiết: [Mục tiêu và kết quả tuần 3](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/01-objectives-and-results.md), [kết quả triển khai và kiểm thử](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/04-deployment-and-results.md), [9 ảnh minh chứng thực tế](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/reports/week-03/06-evidence.md).

## 5. Kế hoạch Tuần 4

Tiếp thu nhắc nhở của GVHD tại buổi đánh giá Tuần 2, nhóm tách riêng kế hoạch công việc cho Tuần 4 như sau:

- **Xây dựng slide thuyết trình và chuẩn bị kịch bản bảo vệ đồ án:** Tóm tắt kiến trúc hệ thống Blue/Green trên ECS Fargate, luồng dịch chuyển traffic với CodeDeploy Canary và cơ chế giám sát CloudWatch kích hoạt tự động rollback.
- **Quay video minh họa (screencast demo):** Ghi lại toàn bộ quá trình triển khai canary và tình huống tự động rollback khi ứng dụng gặp sự cố để phục vụ buổi báo cáo cuối kỳ.
- **Tổng kết chi phí trên AWS Learner Lab và dọn dẹp tài nguyên:** Thống kê lượng tín chỉ (credit) đã sử dụng trong suốt 3 tuần thực nghiệm; thực hiện quy trình hủy dịch vụ an toàn (cleanup ALB, ECS service, target groups, CloudWatch alarms) để kết thúc môn học mà không vượt ngân sách.
- **Rà soát và đóng gói repository:** Kiểm tra lại toàn bộ mã nguồn, tài liệu hướng dẫn và báo cáo cuối kỳ trước khi nộp sản phẩm hoàn chỉnh.

## 6. Khai báo sử dụng AI

- **Công cụ sử dụng:** LLM / AI code assistant (Google Gemini / Antigravity).
- **Phạm vi hỗ trợ:** Hỗ trợ gợi ý cú pháp script cấu hình AWS CLI bằng Python ([infra/aws/week03.py](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/week03.py)), kịch bản đo kiểm HTTP liên tục ([infra/aws/monitor.mjs](https://github.com/toilacongkhoa/Final-cloud-computing/blob/main/infra/aws/monitor.mjs)), rà soát mã nguồn kiểm thử và định dạng tài liệu báo cáo.
- **Cam kết của sinh viên:** Toàn bộ quá trình thao tác trên AWS Learner Lab (cấu hình CodeDeploy, kích hoạt CloudWatch Alarm, tạo deployment, đo đạc lưu lượng, kiểm chứng rollback và chụp 9 ảnh minh chứng thực tế) đều do hai sinh viên trực tiếp thực hiện và xác nhận kết quả trên tài khoản Lab thật.
