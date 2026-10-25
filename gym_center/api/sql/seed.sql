-- Idempotent reference data for Iron Việt Fitness.
INSERT OR IGNORE INTO branches (branch_id, name, address, hours) VALUES
('quan-7', 'Iron Việt Fitness — Quận 7', '123 Nguyễn Thị Thập, Quận 7, TP.HCM', '06:00-22:00 (T2-T6), 07:00-21:00 (T7-CN/ngày lễ)'),
('quan-4', 'Iron Việt Fitness — Quận 4', '456 Khánh Hội, Quận 4, TP.HCM', '06:00-22:00 (T2-T6), 07:00-21:00 (T7-CN/ngày lễ)');

INSERT OR IGNORE INTO payment_methods (method_id, display_name, enabled) VALUES
('bank_transfer', 'Chuyển khoản ngân hàng', 1),
('card', 'Thẻ ngân hàng', 1),
('cash', 'Tiền mặt tại quầy', 1);

INSERT OR IGNORE INTO activity_types (activity_type, display_name) VALUES
('class', 'Lớp tập nhóm'),
('pt', 'Huấn luyện cá nhân (PT)');
