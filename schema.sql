CREATE TABLE `keys` (
  `uuid` VARCHAR(36) NOT NULL,
  `ip` VARCHAR(45) NULL,
  `private_key` BLOB NOT NULL,
  `aes_key` BLOB,
  `aes_iv` BLOB,
  `created_at` INTEGER NOT NULL,
  `locked` INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (`uuid`)
);
