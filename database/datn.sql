
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `is_enabled` bit(1) NOT NULL,
  `is_locked` bit(1) NOT NULL,
  `create_at` datetime(6) DEFAULT NULL,
  `update_at` datetime(6) DEFAULT NULL,
  `account_provider` enum('GOOGLE','LOCAL') DEFAULT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `gender` enum('FEMALE','MALE','OTHER') DEFAULT NULL,
  `gmail` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `phone_number` varchar(255) DEFAULT NULL,
  `role` enum('ADMIN','USER') DEFAULT NULL,
  `url_image` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`gmail`),
  UNIQUE KEY (`username`)
);

CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`name`)
);

CREATE TABLE `sizes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(255) DEFAULT NULL,
  `name` enum('LARGE','MEDIUM','SMALL','XLARGE','XXLARGE') DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`name`)
);


CREATE TABLE `vouchers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `minimum_purchase_amount` double NOT NULL,
  `usage_count` int NOT NULL,
  `usage_limit` int NOT NULL,
  `voucher_value` double NOT NULL,
  `end_at` datetime(6) DEFAULT NULL,
  `start_at` datetime(6) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `discount_type` enum('AMOUNT','FREE_SHIPPING','PERCENTAGE') DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`code`)
);


CREATE TABLE `token_refresh` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reset_required` bit(1) NOT NULL,
  `user_id` int DEFAULT NULL,
  `expiration_date` datetime(6) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`user_id`),
  UNIQUE KEY (`token`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);


CREATE TABLE `otpset_password` (
  `id` int NOT NULL AUTO_INCREMENT,
--   `used` bit(1) NOT NULL,
  `user_id` int DEFAULT NULL,
  `expiration_time` datetime(6) DEFAULT NULL,
  `otp_value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`user_id`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `products` (
`category_id` int DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `create_at` datetime(6) DEFAULT NULL,
  `price` bigint NOT NULL,
  `quantity` bigint NOT NULL,
  `quantity_sold` bigint NOT NULL,
  `update_at` datetime(6) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
);

CREATE TABLE `product_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
);

CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `is_visible` bit(1) NOT NULL,
  `product_id` int DEFAULT NULL,
  `rate` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `create_at` datetime(6) DEFAULT NULL,
  `content` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `orders` (
  `discount_amount` double NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `total_amount` double NOT NULL,
  `user_id` int DEFAULT NULL,
  `voucher_id` int DEFAULT NULL,
  `order_date` datetime(6) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `payment_method` enum('BANK_TRANSFER','CASH_ON_DELIVERY','CREDIT_CARD') DEFAULT NULL,
  `phone_number` varchar(255) DEFAULT NULL,
  `shipping_address` varchar(255) DEFAULT NULL,
  `status` enum('CANCELLED','CONFIRMED','DELIVERED','IN_TRANSIT','PACKAGING','REFUNDED','RETURN_EXCHANGE','UNCONFIRMED') DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT FOREIGN KEY (`voucher_id`) REFERENCES `vouchers` (`id`)
);

CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `unit_price` double NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
);

CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `unit_price` double NOT NULL,
  `user_id` int DEFAULT NULL,
  `create_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `product_size` (
  `product_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `quantity_sold` int NOT NULL,
  `size_id` int DEFAULT NULL,
  `id` bigint NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`size_id`) REFERENCES `sizes` (`id`),
  CONSTRAINT FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ;

CREATE TABLE `address` (
  `user_id` int DEFAULT NULL,
    `phone_number` varchar(255) DEFAULT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `id` bigint NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)




