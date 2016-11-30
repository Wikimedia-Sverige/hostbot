CREATE TABLE `th_up_invitees` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `user_name` varbinary(200) DEFAULT NULL,
  `user_registration` varbinary(14) DEFAULT NULL,
  `user_editcount` int(11) DEFAULT NULL,
  `sample_date` datetime DEFAULT NULL,
  `invite_status` tinyint(1) DEFAULT NULL,
  `hostbot_skipped` tinyint(1) DEFAULT NULL,
  `user_talkpage` int(11) DEFAULT NULL,
  `ut_is_redirect` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
