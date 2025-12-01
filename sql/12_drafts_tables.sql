-- ============================================
-- AIReportLab IMS 草稿和报告表
-- 文件: 12_drafts_tables.sql
-- 描述: 报告撰写功能的数据库表
-- ============================================

USE `aireportlab_db`;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 草稿/报告表
-- ============================================
DROP TABLE IF EXISTS `drafts`;
CREATE TABLE `drafts` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL COMMENT '报告标题',
    `user_id` INT NOT NULL COMMENT '创建者ID',
    `template_file_id` INT DEFAULT NULL COMMENT '使用的模板文件ID',
    `data_file_id` INT DEFAULT NULL COMMENT '关联的数据文件ID',
    `content` LONGTEXT DEFAULT NULL COMMENT '报告内容（Markdown或HTML）',
    `status` ENUM('draft', 'completed') NOT NULL DEFAULT 'draft' COMMENT '状态：draft-草稿，completed-已完成',
    `current_version` INT NOT NULL DEFAULT 1 COMMENT '当前版本号',
    `word_count` INT NOT NULL DEFAULT 0 COMMENT '字数统计',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    PRIMARY KEY (`id`),
    KEY `ix_drafts_user_id` (`user_id`),
    KEY `ix_drafts_status` (`status`),
    CONSTRAINT `fk_drafts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_drafts_template_file_id` FOREIGN KEY (`template_file_id`) REFERENCES `files` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_drafts_data_file_id` FOREIGN KEY (`data_file_id`) REFERENCES `files` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='草稿/报告表';

-- ============================================
-- 2. 草稿版本历史表（支持回溯）
-- ============================================
DROP TABLE IF EXISTS `draft_versions`;
CREATE TABLE `draft_versions` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `draft_id` INT NOT NULL COMMENT '关联的草稿ID',
    `version` INT NOT NULL COMMENT '版本号',
    `content` LONGTEXT NOT NULL COMMENT '该版本的内容',
    `word_count` INT NOT NULL DEFAULT 0 COMMENT '字数统计',
    `change_summary` VARCHAR(255) DEFAULT NULL COMMENT '变更摘要',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `ix_draft_version` (`draft_id`, `version`),
    KEY `ix_draft_versions_draft_id` (`draft_id`),
    CONSTRAINT `fk_draft_versions_draft_id` FOREIGN KEY (`draft_id`) REFERENCES `drafts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='草稿版本历史表';

SET FOREIGN_KEY_CHECKS = 1;

SELECT '草稿表创建成功！' AS message;
