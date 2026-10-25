# 1 Mục tiêu và kết quả tuần 3

Tuần 3 hoàn thiện tích hợp, bảo mật, giám sát CloudWatch và tự động hóa cho hệ thống ECS Blue/Green. Đã tạo bốn alarm, bật automatic rollback, triển khai bản tốt và kiểm chứng hai tình huống lỗi trên AWS. Cả hai phép thử lỗi đều được CodeDeploy tự động rollback thành công.

Ứng dụng có 9/9 test pass. Deployment tốt ghi nhận 891/891 request HTTP thành công; phép thử lỗi health ghi nhận 481/481 request production thành công. Phép thử lỗi ứng dụng có 21 response HTTP 500 đúng chủ đích trước khi trở về bản tốt.

[Quay lại mục lục báo cáo tuần 3](README.md)
