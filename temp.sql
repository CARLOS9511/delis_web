--
-- Create model User
--
CREATE TABLE `usuarios_user` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime(6) NULL, `is_superuser` bool NOT NULL, `username` varchar(150) NOT NULL UNIQUE, `first_name` varchar(150) NOT NULL, `last_name` varchar(150) NOT NULL, `email` varchar(254) NOT NULL, `is_staff` bool NOT NULL, `is_active` bool NOT NULL, `date_joined` datetime(6) NOT NULL);
CREATE TABLE `usuarios_user_groups` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` bigint NOT NULL, `group_id` integer NOT NULL);
CREATE TABLE `usuarios_user_user_permissions` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` bigint NOT NULL, `permission_id` integer NOT NULL);
ALTER TABLE `usuarios_user_groups` ADD CONSTRAINT `usuarios_user_groups_user_id_group_id_7ca6624e_uniq` UNIQUE (`user_id`, `group_id`);
ALTER TABLE `usuarios_user_groups` ADD CONSTRAINT `usuarios_user_groups_user_id_327741ca_fk_usuarios_user_id` FOREIGN KEY (`user_id`) REFERENCES `usuarios_user` (`id`);
ALTER TABLE `usuarios_user_groups` ADD CONSTRAINT `usuarios_user_groups_group_id_ce48ebfd_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `usuarios_user_user_permissions` ADD CONSTRAINT `usuarios_user_user_permi_user_id_permission_id_801d2da9_uniq` UNIQUE (`user_id`, `permission_id`);
ALTER TABLE `usuarios_user_user_permissions` ADD CONSTRAINT `usuarios_user_user_p_user_id_6770e840_fk_usuarios_` FOREIGN KEY (`user_id`) REFERENCES `usuarios_user` (`id`);
ALTER TABLE `usuarios_user_user_permissions` ADD CONSTRAINT `usuarios_user_user_p_permission_id_32dd035e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
