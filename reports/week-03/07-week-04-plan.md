# 7 Kế hoạch tuần 4

Tuần 4 là giai đoạn nghiệm thu đồ án môn học. Nhóm tập trung vào các công việc thực tế, bám sát hiện trạng hệ thống ECS Blue/Green và CodeDeploy đã hoàn thiện ở tuần 3:

1. **Chuẩn bị kịch bản và môi trường demo nghiệm thu:**
   - Duy trì hệ thống ECS Fargate, Application Load Balancer và 4 CloudWatch Alarms ở trạng thái sẵn sàng.
   - Chuẩn bị sẵn kịch bản demo trực tiếp hai tình huống: (1) Triển khai Canary 10% phiên bản tốt chuyển đổi an toàn; (2) Kích hoạt lỗi tự động rollback về phiên bản ổn định (cả trường hợp health check thất bại và lỗi HTTP 500 từ ứng dụng).

2. **Quay video minh chứng (screencast demo):**
   - Thực hiện quay video ghi lại toàn bộ quy trình: đẩy image lên ECR, CodeDeploy tạo deployment, CloudWatch kích hoạt alarm khi phát hiện lỗi, và quá trình tự động rollback khôi phục lưu lượng phục vụ người dùng mà không cần can thiệp thủ công.
   - Video dùng làm tài liệu minh chứng dự phòng cho buổi nghiệm thu đề tài.

3. **Hoàn thiện tài liệu tổng kết và slide thuyết trình:**
   - Biên soạn slide báo cáo nghiệm thu: sơ đồ kiến trúc Blue/Green trên AWS Fargate, bảng số liệu đo kiểm độ trễ/mã phản hồi HTTP, phân tích cơ chế rollback của CodeDeploy kết hợp ALB Metric Alarms.
   - Rà soát, chuẩn hóa báo cáo tổng kết toàn bộ môn học và đóng gói mã nguồn dự án trên GitHub repository.

4. **Tổng kết chi phí và dọn dẹp tài nguyên môi trường (Resource Cleanup):**
   - Thống kê tổng chi phí sử dụng thực tế trên AWS Learner Lab qua các tuần triển khai (ALB, ECS Fargate, CloudWatch, ECR).
   - Sau khi hoàn thành nghiệm thu với giảng viên, tiến hành xóa và hủy các tài nguyên chạy liên tục (ALB, ECS service/tasks, target groups, log groups, alarms) để giải phóng môi trường và bảo đảm không vượt hạn mức tín chỉ 100 USD của Learner Lab.

[Quay lại mục lục báo cáo tuần 3](README.md)
