-- SoLove Backend - MySQL 表结构（与 app/models/models.py 对齐）
-- 执行前请先：CREATE DATABASE ... utf8mb4; 并 USE 目标库。
-- 引擎 InnoDB，字符集 utf8mb4。

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `conversations`;
DROP TABLE IF EXISTS `checkins`;
DROP TABLE IF EXISTS `user_tasks`;
DROP TABLE IF EXISTS `task_templates`;
DROP TABLE IF EXISTS `users`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `openid` VARCHAR(64) NOT NULL COMMENT '用户唯一标识',
  `nickname` VARCHAR(64) DEFAULT NULL COMMENT '昵称',
  `avatar_url` VARCHAR(255) DEFAULT NULL COMMENT '头像 URL',
  `mood_baseline` DOUBLE DEFAULT 5.0 COMMENT '基础情绪分值 (1-10)',
  `preferences` TEXT DEFAULT NULL COMMENT '用户偏好 (JSON)',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `is_premium` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否付费会员',
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` DATETIME(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `task_templates` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NOT NULL COMMENT '任务名称',
  `description` TEXT DEFAULT NULL COMMENT '任务描述',
  `category` VARCHAR(64) DEFAULT NULL COMMENT '分类：运动/阅读/冥想/社交/自我关怀',
  `difficulty` VARCHAR(16) NOT NULL DEFAULT 'easy' COMMENT '难度：easy/medium/hard',
  `estimated_time` INT NOT NULL DEFAULT 10 COMMENT '预计耗时 (分钟)',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_tasks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `template_id` INT DEFAULT NULL,
  `name` VARCHAR(128) NOT NULL COMMENT '任务名称',
  `description` TEXT DEFAULT NULL COMMENT '任务描述',
  `date` DATETIME(6) NOT NULL COMMENT '任务日期',
  `status` VARCHAR(16) NOT NULL DEFAULT 'pending' COMMENT '状态：pending/completed/skipped',
  `completed_at` DATETIME(6) DEFAULT NULL COMMENT '完成时间',
  `feedback` TEXT DEFAULT NULL COMMENT '完成后的反馈/感受',
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  KEY `ix_user_tasks_user_id` (`user_id`),
  KEY `ix_user_tasks_template_id` (`template_id`),
  CONSTRAINT `fk_user_tasks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_tasks_template` FOREIGN KEY (`template_id`) REFERENCES `task_templates` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `checkins` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `task_id` INT NOT NULL,
  `notes` TEXT DEFAULT NULL COMMENT '打卡备注',
  `mood_before` DOUBLE DEFAULT NULL COMMENT '打卡前情绪分 (1-10)',
  `mood_after` DOUBLE DEFAULT NULL COMMENT '打卡后情绪分 (1-10)',
  `checkin_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '打卡时间',
  PRIMARY KEY (`id`),
  KEY `ix_checkins_user_id` (`user_id`),
  KEY `ix_checkins_task_id` (`task_id`),
  CONSTRAINT `fk_checkins_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_checkins_task` FOREIGN KEY (`task_id`) REFERENCES `user_tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `conversations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `message` TEXT NOT NULL COMMENT '用户消息',
  `response` TEXT NOT NULL COMMENT 'AI 回复',
  `generated_tasks` TEXT DEFAULT NULL COMMENT '生成的任务 (JSON)',
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  KEY `ix_conversations_user_id` (`user_id`),
  CONSTRAINT `fk_conversations_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
